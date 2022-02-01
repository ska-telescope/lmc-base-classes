"""
This module provided reference implementations of a BaseComponentManager.

It is provided for explanatory purposes, and to support testing of this
package.
"""
import threading
from time import sleep

from ska_tango_base.base import (
    TaskExecutorComponentManager,
    check_communicating,
)
from ska_tango_base.executor import TaskStatus

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import CommunicationStatus, PowerState


class FakeBaseComponent:
    """
    A fake component for the component manager to work with.

    NOTE: There is usually no need to implement a component object.
    The "component" is an element of the external system under
    control, such as a piece of hardware or an external service. The
    component manager object communicates with the component in order to
    monitor and control it.

    This is a very simple fake component with a power state and a fault
    state. When either of these aspects of state changes, it lets the
    component manager know by calling its `state_change_callback`.

    It can be directly controlled via `off()`, `standby()`, `on()` and
    `reset()` methods. For testing purposes, it can also be told to
    simulate a spontaneous state change via simulate_power_state` and
    `simulate_fault` methods.

    When one of these command method is invoked, the component simulates
    communications latency by sleeping for a short time. It then
    returns, but simulates any asynchronous work it needs to do by
    delaying updating task and component state for a short time.
    """

    def __init__(
        self,
        time_to_return=0.05,
        time_to_complete=0.4,
        power=PowerState.OFF,
        fault=None,
        **state_kwargs,
    ):
        """
        Initialise a new instance.

        :param time_to_return: the amount of time to delay before
            returning from a command method. This simulates latency in
            communication.
        :param time_to_complete: the amount of time to delay before the
            component calls a task callback to let it know that the task
            has been completed
        :param power: initial power state of this component
        :param fault: initial fault state of this component
        """
        self._state_change_callback = None
        self._state_lock = threading.Lock()
        self._state = dict(state_kwargs)
        self._state["power"] = power
        self._state["fault"] = fault

        self._time_to_return = time_to_return or 0
        self._time_to_complete = time_to_complete or 0

    def set_state_change_callback(self, state_change_callback):
        """
        Set a callback to be called when the state of this component changes.

        :param state_change_callback: a callback to be call when the
            state of the component changes
        """
        self._state_change_callback = state_change_callback
        if state_change_callback is None:
            return

        # Let's wait a short time before we call this callback.
        self._simulate_latency()

        self._state_change_callback(**self._state)

    def _simulate_latency(self):
        sleep(self._time_to_return)

    def _simulate_task_execution(
        self, task_callback, task_abort_event, result, **state_kwargs
    ):

        # Simulate the synchronous latency cost of communicating with this component.
        self._simulate_latency()

        # Kick off asynchronous processing, then return immediately. The asynchronous
        # processing will immediately report the task as IN_PROGRESS. Shortly afterwards
        # it will report 33% progress, then 66% progress. We'll then see a state change
        # resulting from the task execution e.g. if the task was to turn the component
        # on, then we'll see the component come on. Finally, the asynchronous processing
        # will report the task as COMPLETE, and publish a result.
        def simulate_async_task_execution():
            if task_callback is not None:
                task_callback(status=TaskStatus.IN_PROGRESS)

            if task_abort_event is not None and task_abort_event.is_set():
                task_callback(status=TaskStatus.ABORTED)
                return

            sleep(self._time_to_complete / 3)

            if task_abort_event is not None and task_abort_event.is_set():
                task_callback(status=TaskStatus.ABORTED)
                return

            if task_callback is not None:
                task_callback(progress=33)

            sleep(self._time_to_complete / 3)

            if task_abort_event is not None and task_abort_event.is_set():
                task_callback(status=TaskStatus.ABORTED)
                return

            if task_callback is not None:
                task_callback(progress=66)

            self._update_state(**state_kwargs)

            sleep(self._time_to_complete / 3)

            if task_abort_event is not None and task_abort_event.is_set():
                task_callback(status=TaskStatus.ABORTED)
                return

            if task_callback is not None:
                task_callback(status=TaskStatus.COMPLETED, result=result)

        threading.Thread(target=simulate_async_task_execution).start()

    def _simulate_power_command_execution(
        self, command_name, power_state, task_callback, task_abort_event
    ):
        self._simulate_task_execution(
            task_callback,
            task_abort_event,
            (ResultCode.OK, f"{command_name} command completed OK"),
            power=power_state,
        )

    def off(self, task_callback, task_abort_event):
        """
        Turn the component off.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        self._simulate_power_command_execution(
            "Off", PowerState.OFF, task_callback, task_abort_event
        )

    def standby(self, task_callback, task_abort_event):
        """
        Put the component into low-power standby mode.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        self._simulate_power_command_execution(
            "Standby", PowerState.STANDBY, task_callback, task_abort_event
        )

    def on(self, task_callback, task_abort_event):
        """
        Turn the component on.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        self._simulate_power_command_execution(
            "On", PowerState.ON, task_callback, task_abort_event
        )

    def simulate_power_state(self, power_state):
        """
        Simulate a change in component power state.

        This could occur as a result of the Off command, or because
        of some external event/action.
        """
        self._update_state(power=power_state)

    def reset(self, task_callback, task_abort_event):
        """
        Reset the component (from fault state).

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        self._simulate_task_execution(
            task_callback,
            task_abort_event,
            (ResultCode.OK, "Reset command completed OK"),
            fault=False,
        )

    def simulate_fault(self, fault_state):
        """
        Tell the component to simulate (or stop simulating) a fault.

        :param fault_state: whether faulty or not.
        """
        self._update_state(fault=fault_state)

    def _update_state(self, **kwargs):
        callback_kwargs = {}
        with self._state_lock:
            for key, value in kwargs.items():
                if value is not None and self._state[key] != value:
                    self._state[key] = value
                    callback_kwargs[key] = value
            if self._state_change_callback is None:
                return
            self._state_change_callback(**callback_kwargs)

    @property
    def faulty(self):
        """
        Return whether this component is faulty.

        :return: whether this component is faulty.
        """
        return self._state["fault"]

    @property
    def power_state(self):
        """
        Return the power state of this component.

        :return: the power state of this component.
        """
        return self._state["power"]


class ReferenceBaseComponentManager(TaskExecutorComponentManager):
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

    def __init__(
        self,
        logger,
        communication_state_callback,
        component_state_callback,
        *args,
        _component=None,
        **kwargs,
    ):
        """
        Initialise a new ComponentManager instance.

        :param logger: a logger for this component manager
        :param _component: allows setting of the component to be
            managed. Note: the component will normally be a part of the
            external system under control, such as a piece of hardware
            or an external service. So there normally will not be a
            "component" software object to pass in here. Instead, you
            would pass in information needed to establish communication
            with your component, such as an FQDN, or an IP address/port.
        """
        self._fail_communicate = False

        self._component = _component or FakeBaseComponent()

        super().__init__(
            logger,
            communication_state_callback,
            component_state_callback,
            *args,
            power=PowerState.UNKNOWN,
            fault=None,
            **kwargs,
        )

    def start_communicating(self):
        """Establish communication with the component, then start monitoring."""
        if self.communication_state == CommunicationStatus.ESTABLISHED:
            return
        if self.communication_state == CommunicationStatus.DISABLED:
            self._update_communication_state(CommunicationStatus.NOT_ESTABLISHED)

        # The component would normally be an element of the system under control. In
        # order to establish communication with it, we might need, for example, to
        # establishing a network connection to the component, then start a polling loop
        # to continually poll over that connection.
        # But here, we're faking the component with an object, so all we need to do is
        # register some callbacks.
        # And in order to fake communications failure, we just return without
        # registering them.
        if self._fail_communicate:
            return

        self._update_communication_state(CommunicationStatus.ESTABLISHED)
        self._component.set_state_change_callback(self._update_component_state)

    def stop_communicating(self):
        """Break off communication with the component."""
        if self.communication_state == CommunicationStatus.DISABLED:
            return

        self._component.set_state_change_callback(None)
        self._update_component_state(power=PowerState.UNKNOWN, fault=None)
        self._update_communication_state(CommunicationStatus.DISABLED)

    def simulate_communication_failure(self, fail_communicate):
        """
        Simulate (or stop simulating) a failure to communicate with the component.

        :param fail_communicate: whether the connection to the component
            is failing
        """
        self._fail_communicate = fail_communicate
        if (
            fail_communicate
            and self.communication_state == CommunicationStatus.ESTABLISHED
        ):
            self._component.set_state_change_callback(None)
            self._update_communication_state(CommunicationStatus.NOT_ESTABLISHED)
        elif (
            not fail_communicate
            and self.communication_state == CommunicationStatus.NOT_ESTABLISHED
        ):
            self._update_communication_state(CommunicationStatus.ESTABLISHED)
            self._component.set_state_change_callback(self._update_component_state)

    @property
    def power_state(self):
        """
        Power mode of the component.

        This is just a bit of syntactic sugar for
        `self.component_state["power"]`.

        :return: the power mode of the component
        """
        return self._component_state["power"]

    @property
    def fault_state(self):
        """
        Whether the component is currently faulting.

        :return: whether the component is faulting
        """
        return self._component_state["fault"]

    @check_communicating
    def off(self, task_callback=None):
        """Turn the component off."""
        return self.submit_task(self._component.off, task_callback=task_callback)

    @check_communicating
    def standby(self, task_callback=None):
        """Put the component into low-power standby mode."""
        return self.submit_task(self._component.standby, task_callback=task_callback)

    @check_communicating
    def on(self, task_callback=None):
        """Turn the component on."""
        return self.submit_task(self._component.on, task_callback=task_callback)

    @check_communicating
    def reset(self, task_callback=None):
        """Reset the component (from fault state)."""
        return self.submit_task(self._component.reset, task_callback=task_callback)