# -*- coding: utf-8 -*-
#
# This file is part of the SKA Low MCCS project
#
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE for more info.
"""
This module provided reference implementations of a BaseComponentManager.

It is provided for explanatory purposes, and to support testing of this
package.
"""
from __future__ import annotations

import functools
import logging
import threading
from time import sleep
from typing import Any, Callable, Generic, TypeVar, cast

from ska_control_model import CommunicationStatus, PowerState, ResultCode, TaskStatus
from ska_tango_testing.mock import MockCallableGroup

from ...base import (
    CommunicationStatusCallbackType,
    JSONData,
    TaskCallbackType,
    check_communicating,
)
from ...executor import TaskExecutorComponentManager
from ...faults import CommandError


def wait_until_done(command: Callable[..., None]) -> Callable[..., None]:
    """
    Wait until the command is done before the device may continue with other tasks.

    The waited on threading event is set when the callback is called with command status
    equal to COMPLETED, ABORTED, FAILED or REJECTED. This is only done if the command
    has been passed a real task callback, and not a mock callback or no callback at all.

    :param command: Command method.
    :return: Wrapped command method.
    """

    @functools.wraps(command)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        task_callback = kwargs.get("task_callback")
        if task_callback is not None and not isinstance(
            task_callback,
            MockCallableGroup._Callable,  # pylint: disable=protected-access
        ):
            done_event = threading.Event()

            def decorate_task_callback(
                task_callback: TaskCallbackType,
            ) -> Callable[..., TaskCallbackType]:
                def wrap_task_callback(
                    status: TaskStatus | None = None,
                    **kwargs: Any,
                ) -> Any:
                    if status is not None and status in [
                        TaskStatus.COMPLETED,
                        TaskStatus.ABORTED,
                        TaskStatus.FAILED,
                        TaskStatus.REJECTED,
                    ]:
                        done_event.set()
                    return task_callback(status=status, **kwargs)

                return wrap_task_callback

            kwargs["task_callback"] = decorate_task_callback(task_callback)
            command(*args, **kwargs)
            done_event.wait()
        else:
            command(*args, **kwargs)

    return wrapper


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

    PROGRESS_REPORTING_POINTS = ["33", "66"]

    def __init__(
        self: FakeBaseComponent,
        time_to_return: float = 0.05,
        time_to_complete: float = 0.4,
        power: PowerState = PowerState.OFF,
        fault: bool | None = None,
        **state_kwargs: Any,
    ) -> None:
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
        :param state_kwargs: extra keyword arguments
        """
        self._state_change_callback: Callable[..., None] | None = None
        self._state_lock = threading.Lock()
        self._state = dict(state_kwargs)
        self._state["power"] = power
        self._state["fault"] = fault

        self._time_to_return = time_to_return or 0
        self._time_to_complete = time_to_complete or 0

    def set_state_change_callback(
        self: FakeBaseComponent,
        state_change_callback: Callable[..., None] | None,
    ) -> None:
        """
        Set a callback to be called when the state of this component changes.

        :param state_change_callback: a callback to be call when the
            state of the component changes
        """
        self._state_change_callback = state_change_callback
        if self._state_change_callback is None:
            return

        # Let's wait a short time before we call this callback.
        self._simulate_latency()

        self._state_change_callback(**self._state)

    def _simulate_latency(self: FakeBaseComponent) -> None:
        sleep(self._time_to_return)

    def _simulate_task_execution(
        self: FakeBaseComponent,
        task_callback: TaskCallbackType | None,
        task_abort_event: threading.Event,
        result: JSONData,
        **state_kwargs: Any,
    ) -> None:
        # Simulate the synchronous latency cost of communicating with this component.
        self._simulate_latency()

        # Kick off asynchronous processing, then return immediately. The asynchronous
        # processing will immediately report the task as IN_PROGRESS. Shortly afterwards
        # it will report a number of progress points. We'll then see a state change
        # resulting from the task execution e.g. if the task was to turn the component
        # on, then we'll see the component come on. Finally, the asynchronous processing
        # will report the task as COMPLETE, and publish a result.
        def simulate_async_task_execution() -> None:
            def _call_task_callback(*args: Any, **kwargs: Any) -> None:
                if task_callback is not None:
                    task_callback(*args, **kwargs)

            _call_task_callback(status=TaskStatus.IN_PROGRESS)

            if task_abort_event.is_set():
                _call_task_callback(
                    status=TaskStatus.ABORTED,
                    result=(ResultCode.ABORTED, "Command has been aborted"),
                )
                return

            sleep_time = self._time_to_complete / (
                len(self.PROGRESS_REPORTING_POINTS) + 1
            )
            for progress_point in self.PROGRESS_REPORTING_POINTS:
                sleep(sleep_time)

                if task_abort_event.is_set():
                    _call_task_callback(
                        status=TaskStatus.ABORTED,
                        result=(ResultCode.ABORTED, "Command has been aborted"),
                    )
                    return

                _call_task_callback(progress=progress_point)

            self._update_state(**state_kwargs)

            sleep(sleep_time)

            if task_abort_event.is_set():
                _call_task_callback(
                    status=TaskStatus.ABORTED,
                    result=(ResultCode.ABORTED, "Command has been aborted"),
                )
                return

            _call_task_callback(status=TaskStatus.COMPLETED, result=result)

        threading.Thread(target=simulate_async_task_execution).start()

    def _simulate_power_command_execution(
        self: FakeBaseComponent,
        command_name: str,
        power_state: PowerState,
        task_callback: TaskCallbackType,
        task_abort_event: threading.Event,
    ) -> None:
        self._simulate_task_execution(
            task_callback,
            task_abort_event,
            (ResultCode.OK, f"{command_name} command completed OK"),
            power=power_state,
        )

    @wait_until_done
    def off(
        self: FakeBaseComponent,
        task_callback: TaskCallbackType,
        task_abort_event: threading.Event,
    ) -> None:
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

    @wait_until_done
    def standby(
        self: FakeBaseComponent,
        task_callback: TaskCallbackType,
        task_abort_event: threading.Event,
    ) -> None:
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

    @wait_until_done
    def on(
        self: FakeBaseComponent,
        task_callback: TaskCallbackType,
        task_abort_event: threading.Event,
    ) -> None:
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

    def simulate_power_state(self: FakeBaseComponent, power_state: PowerState) -> None:
        """
        Simulate a change in component power state.

        This could occur as a result of the Off command, or because of
        some external event/action.

        :param power_state: the power state
        """
        self._update_state(power=power_state)

    def reset(
        self: FakeBaseComponent,
        task_callback: TaskCallbackType,
        task_abort_event: threading.Event,
    ) -> None:
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

    def simulate_command_error(
        self: FakeBaseComponent,
        task_callback: TaskCallbackType,
        task_abort_event: threading.Event,
    ) -> None:
        """
        Simulate a command that raises a CommandError during execution.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        :raises CommandError: simulating an invalid argument.
        """
        raise CommandError("Command encountered unexpected error")

    def simulate_is_cmd_allowed_error(
        self: FakeBaseComponent,
        task_callback: TaskCallbackType,
        task_abort_event: threading.Event,
    ) -> None:
        """
        Simulate a command with a is_cmd_allowed method that raises an Exception.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        self._simulate_task_execution(
            task_callback,
            task_abort_event,
            (ResultCode.OK, "SimulateIsCmdAllowedError command completed OK"),
        )

    def simulate_fault(self: FakeBaseComponent, fault_state: bool) -> None:
        """
        Tell the component to simulate (or stop simulating) a fault.

        :param fault_state: whether faulty or not.
        """
        self._update_state(fault=fault_state)

    def _update_state(self: FakeBaseComponent, **kwargs: Any) -> None:
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
    def faulty(self: FakeBaseComponent) -> bool:
        """
        Return whether this component is faulty.

        :return: whether this component is faulty.
        """
        return cast(bool, self._state["fault"])

    @property
    def power_state(self: FakeBaseComponent) -> PowerState:
        """
        Return the power state of this component.

        :return: the power state of this component.
        """
        return cast(PowerState, self._state["power"])


ComponentT = TypeVar("ComponentT", bound=FakeBaseComponent)


class GenericBaseComponentManager(TaskExecutorComponentManager, Generic[ComponentT]):
    """
    A generic component manager for Tango devices.

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
        self: GenericBaseComponentManager[ComponentT],
        component: ComponentT,
        logger: logging.Logger,
        communication_state_callback: CommunicationStatusCallbackType,
        component_state_callback: Callable[[], None],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialise a new ComponentManager instance.

        :param component: the component that this component manager
            manages.
        :param logger: a logger for this component manager
        :param communication_state_callback: callback for communication state
        :param component_state_callback: callback for component state
        :param args: extra arguments
        :param kwargs: extra keyword arguments
        """
        self._fail_communicate = False

        self._component = component

        super().__init__(
            logger,
            communication_state_callback,
            component_state_callback,
            *args,
            power=PowerState.UNKNOWN,
            fault=None,
            **kwargs,
        )

    def start_communicating(self: GenericBaseComponentManager[ComponentT]) -> None:
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

    def stop_communicating(self: GenericBaseComponentManager[ComponentT]) -> None:
        """Break off communication with the component."""
        if self.communication_state == CommunicationStatus.DISABLED:
            return

        self._component.set_state_change_callback(None)
        self._update_component_state(power=PowerState.UNKNOWN, fault=None)
        self._update_communication_state(CommunicationStatus.DISABLED)

    def simulate_communication_failure(
        self: GenericBaseComponentManager[ComponentT], fail_communicate: bool
    ) -> None:
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
    def power_state(self: GenericBaseComponentManager[ComponentT]) -> PowerState:
        """
        Power mode of the component.

        This is just a bit of syntactic sugar for
        `self.component_state["power"]`.

        :return: the power mode of the component
        """
        return cast(PowerState, self._component_state["power"])

    @property
    def fault_state(self: GenericBaseComponentManager[ComponentT]) -> bool:
        """
        Whether the component is currently faulting.

        :return: whether the component is faulting
        """
        return cast(bool, self._component_state["fault"])

    @check_communicating
    def off(
        self: GenericBaseComponentManager[ComponentT],
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Turn the component off.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: TaskStatus and message
        """
        return self.submit_task(self._component.off, task_callback=task_callback)

    @check_communicating
    def standby(
        self: GenericBaseComponentManager[ComponentT],
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Put the component into low-power standby mode.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: TaskStatus and message
        """
        return self.submit_task(self._component.standby, task_callback=task_callback)

    @check_communicating
    def on(
        self: GenericBaseComponentManager[ComponentT],
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Turn the component on.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: TaskStatus and message
        """
        return self.submit_task(self._component.on, task_callback=task_callback)

    @check_communicating
    def reset(
        self: GenericBaseComponentManager[ComponentT],
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Reset the component (from fault state).

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: TaskStatus and message
        """
        return self.submit_task(self._component.reset, task_callback=task_callback)

    @check_communicating
    def simulate_command_error(
        self: GenericBaseComponentManager[ComponentT],
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Simulate a command that raises a CommandError during execution.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :return: TaskStatus and message
        """
        return self.submit_task(
            self._component.simulate_command_error, task_callback=task_callback
        )

    @check_communicating
    def simulate_is_cmd_allowed_error(
        self: GenericBaseComponentManager[ComponentT],
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Simulate a command with a is_cmd_allowed method that raises an Exception.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :return: TaskStatus and message
        """
        return self.submit_task(
            self._component.simulate_is_cmd_allowed_error,
            is_cmd_allowed=self._is_simulate_is_cmd_allowed_error_allowed,
            task_callback=task_callback,
        )

    def _is_simulate_is_cmd_allowed_error_allowed(
        self: GenericBaseComponentManager[ComponentT],
    ) -> bool:
        """
        Return whether the `SimulateIsCmdAllowedError` command may be called.

        :return: whether the command may be called.
        :raises ValueError: to simulate an exception occuring in this method.
        """
        if self.power_state == PowerState.ON:
            raise ValueError("'is_cmd_allowed' method encountered unexpected error")
        return False


class ReferenceBaseComponentManager(GenericBaseComponentManager[FakeBaseComponent]):
    """A reference base component manager for Tango devices."""

    def __init__(
        self: ReferenceBaseComponentManager,
        logger: logging.Logger,
        communication_state_callback: CommunicationStatusCallbackType,
        component_state_callback: Callable[[], None],
        *args: Any,
        _component: FakeBaseComponent | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialise a new ComponentManager instance.

        :param logger: a logger for this component manager
        :param communication_state_callback: callback for communication state
        :param component_state_callback: callback for component state
        :param args: extra arguments
        :param _component: allows setting of the component to be
            managed. Note: the component will normally be a part of the
            external system under control, such as a piece of hardware
            or an external service. So there normally will not be a
            "component" software object to pass in here. Instead, you
            would pass in information needed to establish communication
            with your component, such as an FQDN, or an IP address/port.
        :param kwargs: extra keyword arguments
        """
        super().__init__(
            _component or FakeBaseComponent(),
            logger,
            communication_state_callback,
            component_state_callback,
            *args,
            **kwargs,
        )
