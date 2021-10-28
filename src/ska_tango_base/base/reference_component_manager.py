"""
This module provided reference implementations of a BaseComponentManager.

It is provided for explanatory purposes, and to support testing of this
package.
"""
import functools

from ska_tango_base.base import BaseComponentManager
from ska_tango_base.control_model import PowerMode
from ska_tango_base.faults import ComponentFault


def check_communicating(func):
    """
    Return a function that checks component communication before calling a function.

    The component manager needs to have established communications with
    the component, in order for the function to be called.

    This function is intended to be used as a decorator:

    .. code-block:: python

        @check_communicating
        def scan(self):
            ...

    :param func: the wrapped function

    :return: the wrapped function
    """

    @functools.wraps(func)
    def _wrapper(component_manager, *args, **kwargs):
        """
        Check for component communication before calling the function.

        This is a wrapper function that implements the functionality of
        the decorator.

        :param component_manager: the component manager to check
        :param args: positional arguments to the wrapped function
        :param kwargs: keyword arguments to the wrapped function

        :return: whatever the wrapped function returns
        """
        if not component_manager.is_communicating:
            raise ConnectionError("Not connected")
        return func(component_manager, *args, **kwargs)

    return _wrapper


class ReferenceBaseComponentManager(BaseComponentManager):
    """
    A component manager for Tango devices.

    It supports:

    * Maintaining a connection to its component

    * Controlling its component via commands like Off(), Standby(),
      On(), etc.

    * Monitoring its component, e.g. detect that it has been turned off
      or on

    The current implementation is intended to

    * illustrate the model

    * enable testing of these base classes

    It should not generally be used in concrete devices; instead, write
    a component manager specific to the component managed by the device.
    """

    class _Component:
        """
        An example component for the component manager to work with.

        It can be directly controlled via off(), standby(), on() and
        reset() command methods.

        For testing purposes, it can also be told to simulate a
        spontaneous state change via simulate_off(), simulate_standby(),
        simulate_on() and simulate_fault() methods.

        When a component changes power mode, it lets the component
        manager know by calling its ``component_off``,
        ``component_standby`` and ``component_on`` callback methods.

        When a component starts simulating a fault, it lets the
        component manager know by calling its ``component_fault``
        callback method.
        """

        def __init__(self, _power_mode=PowerMode.OFF, _faulty=False):
            """
            Initialise a new instance.

            :param _power_mode: initial power mode of this component
                (for testing only)
            :param _faulty: whether this component should initially
                simulate a fault (for testing only)
            """
            self._power_mode = _power_mode
            self._power_callback = None

            self._faulty = _faulty
            self._fault_callback = None

        def set_op_callbacks(self, power_mode_callback, fault_callback):
            """
            Set callbacks for the underlying component.

            :param power_mode_callback: a callback to call when the
                power mode of the component changes
            :param fault_callback: a callback to call when the component
                experiences a fault
            """
            self._power_callback = power_mode_callback
            self._fault_callback = fault_callback

        @property
        def faulty(self):
            """
            Return whether this component is currently experiencing a fault.

            :return: whether this component is faulting
            :rtype: bool
            """
            return self._faulty

        @property
        def power_mode(self):
            """
            Return the current power mode of the component.

            :return: power mode of the component
            :rtype: :py:class:`ska_tango_base.control_model.PowerMode`
            """
            if self.faulty:
                raise ComponentFault()
            return self._power_mode

        def off(self):
            """Turn the component off."""
            self.simulate_off()

        def standby(self):
            """Put the component into low-power standby mode."""
            self.simulate_standby()

        def on(self):
            """Turn the component on."""
            self.simulate_on()

        def reset(self):
            """Reset the component (from fault state)."""
            self._update_faulty(False)

        def simulate_off(self):
            """
            Simulate the component being turned off.

            This could occur as a result of the Off command, or because
            of some external event/action.
            """
            if self.faulty:
                raise ComponentFault()
            self._update_power_mode(PowerMode.OFF)

        def simulate_standby(self):
            """
            Simulate the component going into low-power standby mode.

            This could occur as a result of the Standby command, or
            because of some external event/action.
            """
            if self.faulty:
                raise ComponentFault()
            self._update_power_mode(PowerMode.STANDBY)

        def simulate_on(self):
            """
            Simulate the component being turned on.

            This could occur as a result of the On command, or because
            of some external event/action.
            """
            if self.faulty:
                raise ComponentFault()
            self._update_power_mode(PowerMode.ON)

        def _invoke_power_callback(self):
            """Invoke the callback when the power mode of the component changes."""
            if not self.faulty:
                if self._power_callback is not None:
                    self._power_callback(self._power_mode)

        def _update_power_mode(self, power_mode):
            """
            Update the power mode of the component.

            This helper method will also ensure that callbacks are
            called as required.

            :param power_mode: new value for the power mode
            :type power_mode:
                :py:class:`ska_tango_base.control_model.PowerMode`
            """
            if self._power_mode != power_mode:
                self._power_mode = power_mode
                self._invoke_power_callback()

        def simulate_fault(self):
            """Tell the component to simulate a fault."""
            self._update_faulty(True)

        def _invoke_fault_callback(self):
            """Invoke the callback when the component experiences a fault."""
            if self.faulty and self._fault_callback is not None:
                self._fault_callback()

        def _update_faulty(self, faulty):
            """
            Update whether the component is faulty or not.

            This helper method will also ensure that callbacks are
            called as required.

            :param fault: new value for whether the component is
                faulting or not
            :type faulting: bool
            """
            if self._faulty != faulty:
                self._faulty = faulty
                self._invoke_fault_callback()

    def __init__(self, op_state_model, *args, logger=None, _component=None, **kwargs):
        """
        Initialise a new ComponentManager instance.

        :param op_state_model: the op state model used by this component
            manager
        :param logger: a logger for this component manager
        :param _component: allows setting of the component to be
            managed; for testing purposes only
        """
        self.logger = logger

        self._connected = False
        self._fail_communicate = False

        self._component = _component or self._Component()

        super().__init__(op_state_model, *args, **kwargs)

    def start_communicating(self):
        """Establish communication with the component, then start monitoring."""
        if self._connected:
            return

        # trigger transition to UNKNOWN (e.g. from DISABLE) first,
        # before trying to connect, because connection might take a
        # little while, and we want to be in UNKNOWN state meanwhile.
        self.op_state_model.perform_action("component_unknown")

        # Now connect to the component. Here we simply consult the
        # _fail_communicate attribute and either pretend to fail or pretend
        # to succeed.
        if self._fail_communicate:
            raise ConnectionError("Failed to connect")

        self._connected = True
        self._component.set_op_callbacks(
            self.component_power_mode_changed, self.component_fault
        )
        # we've been disconnected and we might have missed some
        # changes, so we need to check the component's state, and
        # make our state model correspond
        if self._component.faulty:
            self.component_fault()
        else:
            self.component_power_mode_changed(self._component.power_mode)

    def stop_communicating(self):
        """Cease monitoring the component, and break off all communication with it."""
        if not self._connected:
            return

        self._connected = False
        self._component.set_op_callbacks(None, None)
        self.op_state_model.perform_action("component_disconnected")

    @property
    def is_communicating(self):
        """
        Whether there is currently a connection to the component.

        :return: whether there is currently a connection to the
            component
        :rtype: bool
        """
        return self._connected

    def simulate_communication_failure(self, fail_communicate):
        """
        Simulate (or stop simulating) a failure to communicate with the component.

        :param fail_communicate: whether the connection to the component
            is failing
        """
        self._fail_communicate = fail_communicate
        if fail_communicate and self._connected:
            self._connected = False
            self._component.set_op_callbacks(None, None)
            self.op_state_model.perform_action("component_unknown")

    @property
    @check_communicating
    def power_mode(self):
        """
        Power mode of the component.

        :return: the power mode of the component
        """
        return self._component.power_mode

    @property
    @check_communicating
    def faulty(self):
        """
        Whether the component is currently faulting.

        :return: whether the component is faulting
        """
        return self._component.faulty

    @check_communicating
    def off(self):
        """Turn the component off."""
        self.logger.info("Turning component off")
        self._component.off()

    @check_communicating
    def standby(self):
        """Put the component into low-power standby mode."""
        self.logger.info("Putting component into standby mode")
        self._component.standby()

    @check_communicating
    def on(self):
        """Turn the component on."""
        self.logger.info("Turning component on")
        self._component.on()

    @check_communicating
    def reset(self):
        """Reset the component (from fault state)."""
        self.logger.info("Resetting component")
        self._component.reset()

    action_map = {
        PowerMode.OFF: "component_off",
        PowerMode.STANDBY: "component_standby",
        PowerMode.ON: "component_on",
    }

    def component_power_mode_changed(self, power_mode):
        """
        Handle notification that the component's power mode has changed.

        This is a callback hook.

        :param power_mode: the new power mode of the component
        :type power_mode:
            :py:class:`ska_tango_base.control_model.PowerMode`
        """
        action = self.action_map[power_mode]
        self.op_state_model.perform_action(action)

    def component_fault(self):
        """
        Handle notification that the component has faulted.

        This is a callback hook.
        """
        self.op_state_model.perform_action("component_fault")
