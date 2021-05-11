"""
This module models component management for SKA Tango devices.

The basic model is:

* Every Tango device has a *component* that it monitors and/or
  controls. That component could be:

  * Hardware such as an antenna, APIU, TPM, switch, subrack, etc.

  * An external software system such as a cluster manager

  * A software routine, possibly implemented within the Tango device
    itself
    
  * In a hierarchical system, a pool of lower-level Tango devices.

* A Tango device will usually need to establish and maintain a
  *connection* to its component. This connection may be deliberately
  broken by the device, or it may fail.

* A Tango device *controls* its component by issuing commands that cause
  the component to change behaviour and/or state; and it *monitors* its
  component by keeping track of its state.
"""
from ska_tango_base.control_model import PowerMode
from ska_tango_base.faults import ComponentFault


def check_connected(func):
    """
    Decorator that makes a method first check that there is a connection
    to the component, before allowing the wrapped function to proceed

    :param func: the wrapped function

    :return: the wrapped function
    """
    def _wrapper(component_manager, *args, **kwargs):
        """
        Wrapper function that checks that their is a connection to the
        component before invoking the wrapped function

        :param component_manager: the component_manager to check
        :param args: positional arguments to the wrapped function
        :param kwargs: keyword arguments to the wrapped function

        :return: whatever the wrapped function returns
        """
        if not component_manager.is_connected:
            raise ConnectionError("Not connected")
        return func(component_manager, *args, **kwargs)

    return _wrapper


class ComponentManager:
    """
    A component manager for Tango devices, supporting:

    * Maintaining a connection to its component

    * Controling its component via commands like Off(), Standby(), On(),
      etc

    * Monitoring its component, e.g. detect that it has been turned off
      or on

    The current implementation is intended to

    * illustrate the model
    
    * enable testing of the base classes

    It should not generally be used in concrete devices; instead, write
    a subclass specific to the component managed by the device.
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

        When a component starts simulating a fault, it lest the
        component manager know by calling its ``component_fault``
        callback method.
        """

        def __init__(self, _power_mode=PowerMode.OFF, _faulty=False):
            """
            Initialise a new instance

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
            Set callbacks for the underlying component

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
            Whether this component is currently experiencing a fault

            :return: whether this component is faulting
            :rtype: bool
            """
            return self._faulty

        @property
        def power_mode(self):
            """
            Current power mode of the component

            :return: power mode of the component
            :rtype: :py:class:`ska_tango_base.control_model.PowerMode`
            """
            if self.faulty:
                raise ComponentFault()
            return self._power_mode

        def off(self):
            """
            Turn the component off
            """
            self.simulate_off()

        def standby(self):
            """
            Put the component into low-power standby mode
            """
            self.simulate_standby()

        def on(self):
            """
            Turn the component on
            """
            self.simulate_on()

        def reset(self):
            """
            Reset the component (from fault state)
            """
            self._update_faulty(False)

        def simulate_off(self):
            """
            Simulate the component being turned off, either
            spontaneously or as a result of the Off command.
            """
            if self.faulty:
                raise ComponentFault()
            self._update_power_mode(PowerMode.OFF)

        def simulate_standby(self):
            """
            Simulate the component going into low-power standby mode,
            either spontaneously or as a result of the Standby command.
            """
            if self.faulty:
                raise ComponentFault()
            self._update_power_mode(PowerMode.STANDBY)

        def simulate_on(self):
            """
            Simulate the component being turned on, either spontaneously
            or as a result of the On command.
            """
            if self.faulty:
                raise ComponentFault()
            self._update_power_mode(PowerMode.ON)

        def _invoke_power_callback(self):
            """
            Helper method that invokes the callback when the power mode
            of the component changes.
            """
            if not self.faulty:
                if self._power_callback is not None:
                    self._power_callback(self._power_mode)

        def _update_power_mode(self, power_mode):
            """
            Helper method that updates the power mode of the component,
            ensuring that callbacks are called as
            required.

            :param power_mode: new value for the power mode of the
                component
            :type power_mode:
                :py:class:`ska_tango_base.control_model.PowerMode`
            """
            if self._power_mode != power_mode:
                self._power_mode = power_mode
                self._invoke_power_callback()

        def simulate_fault(self):
            """
            Tell the component to simulate a fault
            """
            self._update_faulty(True)

        def _invoke_fault_callback(self):
            """
            Helper method that invokes the callback when the component
            experiences a fault.
            """
            if self.faulty and self._fault_callback is not None:
                self._fault_callback()

        def _update_faulty(self, faulty):
            """
            Helper method that updates whether the component is
            faulting or not, ensuring that callbacks are called as
            required.

            :param fault: new value for whether the component is
                faulting or not
            :type faulting: bool
            """
            if self._faulty != faulty:
                self._faulty = faulty
                self._invoke_fault_callback()

    def __init__(self, op_state_model, logger, _component=None):
        """
        Initialise a new ComponentManager instance

        :param op_state_model: the op state model used by this component
            manager
        :param logger: a logger for this component manager
        :param _component: allows setting of the component to be
            managed; for testing purposes only
        """
        self.op_state_model = op_state_model
        self.logger = logger

        self._connected = False
        self._fail_connect = False

        self._component = _component or self._Component()

    def connect(self):
        """
        Establish a connection to the component
        """
        if self._connected:
            return

        if self._fail_connect:
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

    def disconnect(self):
        """
        Disconnect from the component
        """
        if not self._connected:
            return

        self._connected = False
        self._component.set_op_callbacks(None, None)
        self.op_state_model.perform_action("component_disconnected")

    @property
    def is_connected(self):
        """
        Whether there is currently a connection to the component

        :return: whether there is currently a connection to the
            component
        :rtype: bool
        """
        return self._connected

    def simulate_connection_failure(self, fail_connect):
        """
        Simulate (or stop simulating) a component connection failure

        :param fail_connect: whether the connection to the component
            is failing
        """
        self._fail_connect = fail_connect
        if fail_connect and self._connected:
            self._connected = False
            self._component.set_op_callbacks(None, None)
            self.op_state_model.perform_action("component_unknown")

    @property
    @check_connected
    def power_mode(self):
        """
        Power mode of the component

        :return: the power mode of the component
        """
        return self._component.power_mode

    @property
    @check_connected
    def faulty(self):
        """
        Whether the component is currently faulting

        :return: whether the component is faulting
        """
        return self._component.faulty

    @check_connected
    def off(self):
        """
        Turn the component off
        """
        self.logger.info("Turning component off")
        self._component.off()

    @check_connected
    def standby(self):
        """
        Put the component into low-power standby mode
        """
        self.logger.info("Putting component into standby mode")
        self._component.standby()

    @check_connected
    def on(self):
        """
        Turn the component on
        """
        self.logger.info("Turning component on")
        self._component.on()

    @check_connected
    def reset(self):
        """
        Reset the component (from fault state)
        """
        self.logger.info("Resetting component")
        self._component.reset()

    action_map = {
        PowerMode.OFF: "component_off",
        PowerMode.STANDBY: "component_standby",
        PowerMode.ON: "component_on",
    }

    def component_power_mode_changed(self, power_mode):
        """
        Callback hook, called when whether the component power mode
        changes

        :param power_mode: the new power mode of the component
        :type power_mode:
            :py:class:`ska_tango_base.control_model.PowerMode`
        """
        action = self.action_map[power_mode]
        self.op_state_model.perform_action(action)

    def component_fault(self):
        """
        Callback hook, called when the component faults
        """
        self.op_state_model.perform_action("component_fault")
