# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
This module provides an abstract component manager for SKA Tango base devices.

The basic model is:

* Every Tango device has a *component* that it monitors and/or
  controls. That component could be, for example:

  * Hardware such as an antenna, APIU, TPM, switch, subrack, etc.

  * An external software system such as a cluster manager

  * A software routine, possibly implemented within the Tango device
    itself

  * In a hierarchical system, a pool of lower-level Tango devices.

* A Tango device will usually need to establish and maintain
  *communication* with its component. This connection may be deliberately
  broken by the device, or it may fail.

* A Tango device *controls* its component by issuing commands that cause
  the component to change behaviour and/or state; and it *monitors* its
  component by keeping track of its state.
"""
from __future__ import annotations

import functools
import logging
import threading
from typing import Any, Callable, Protocol, TypeVar, cast

from ska_control_model import CommunicationStatus, PowerState, TaskStatus

from ..faults import ComponentError

Wrapped = TypeVar("Wrapped", bound=Callable[..., Any])


def check_communicating(func: Wrapped) -> Wrapped:
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
    def _wrapper(
        component_manager: BaseComponentManager,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Check for component communication before calling the function.

        This is a wrapper function that implements the functionality of
        the decorator.

        :param component_manager: the component manager to check
        :param args: positional arguments to the wrapped function
        :param kwargs: keyword arguments to the wrapped function

        :raises ConnectionError: if communication with the component has
            not been established.
        :return: whatever the wrapped function returns
        """
        if component_manager.communication_state != CommunicationStatus.ESTABLISHED:
            raise ConnectionError(
                f"Cannot execute '{type(component_manager).__name__}.{func.__name__}'. "
                "Communication with component is not established."
            )
        return func(component_manager, *args, **kwargs)

    return cast(Wrapped, _wrapper)


def check_on(func: Wrapped) -> Wrapped:
    """
    Return a function that checks the component state then calls another function.

    The component needs to be turned on, and not faulty, in order for
    the function to be called.

    This function is intended to be used as a decorator:

    .. code-block:: python

        @check_on
        def scan(self):
            ...

    :param func: the wrapped function

    :return: the wrapped function
    """

    @functools.wraps(func)
    def _wrapper(component: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Check that the component is on and not faulty before calling the function.

        This is a wrapper function that implements the functionality of
        the decorator.

        :param component: the component to check
        :param args: positional arguments to the wrapped function
        :param kwargs: keyword arguments to the wrapped function

        :raises ComponentError: when not powered on

        :return: whatever the wrapped function returns
        """
        if component.power_state != PowerState.ON:
            raise ComponentError("Component is not powered ON")
        return func(component, *args, **kwargs)

    return cast(Wrapped, _wrapper)


CommunicationStatusCallbackType = Callable[[CommunicationStatus], None]


class TaskCallbackType(Protocol):  # pylint: disable=too-few-public-methods
    """Structural subtyping protocol for a TaskCallback."""

    def __call__(
        self: TaskCallbackType,
        status: TaskStatus | None = None,
        progress: int | None = None,
        result: Any = None,
        exception: Exception | None = None,
    ) -> None:
        """
        Call the callback with an update on the task.

        :param status: status of the task.
        :param progress: progress of the task.
        :param result: result of the task.
        :param exception: an exception raised from the task.
        """


# pylint: disable=too-many-instance-attributes
class BaseComponentManager:
    """
    An abstract base class for a component manager for SKA Tango devices.

    It supports:

    * Maintaining a connection to its component

    * Controlling its component via commands like Off(), Standby(),
      On(), etc.

    * Monitoring its component, e.g. detect that it has been turned off
      or on
    """

    def __init__(
        self: BaseComponentManager,
        logger: logging.Logger,
        communication_state_callback: CommunicationStatusCallbackType | None = None,
        component_state_callback: Callable[..., None] | None = None,
        **state: Any,
    ) -> None:
        """
        Initialise a new ComponentManager instance.

        :param logger: the logger to be used by this manager
        :param communication_state_callback: callback to be called when
            the status of communications between the component manager
            and its component changes.
        :param component_state_callback: callback to be called when the
            monitored state of the component changes
        :param state: key/value pairs
        """
        self.logger = logger

        self._communication_state_lock = threading.Lock()
        self._communication_state = CommunicationStatus.DISABLED
        self._communication_state_callback = communication_state_callback

        self._component_state_lock = threading.Lock()
        self._component_state = dict(state)
        self._component_state_callback = component_state_callback

        self._max_queued_tasks = 0
        self._max_executing_tasks = 1

    @property
    def max_queued_tasks(self) -> int:
        """
        Get the task queue size.

        :return: The task queue size
        """
        return self._max_queued_tasks

    @max_queued_tasks.setter
    def max_queued_tasks(self, size: int) -> None:
        """
        Set the task queue size.

        :param: size: the new queue size
        """
        self._max_queued_tasks = size

    @property
    def max_executing_tasks(self) -> int:
        """
        Get the max number of tasks that can be executing at once.

        :return: max number of simultaneously executing tasks.
        """
        return self._max_executing_tasks

    @max_executing_tasks.setter
    def max_executing_tasks(self, maximum: int) -> None:
        """
        Set the max number of tasks that can be executing at once.

        :param: maximum: the max number of simultaneously executing tasks.
        """
        self._max_executing_tasks = maximum

    def start_communicating(self: BaseComponentManager) -> None:
        """
        Establish communication with the component, then start monitoring.

        This is the place to do things like:

        * Initiate a connection to the component (if your communication
          is connection-oriented)
        * Subscribe to component events (if using "pull" model)
        * Start a polling loop to monitor the component (if using a
          "push" model)

        :raises NotImplementedError: Not implemented it's an abstract class
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    def stop_communicating(self: BaseComponentManager) -> None:
        """
        Cease monitoring the component, and break off all communication with it.

        For example,

        * If you are communicating over a connection, disconnect.
        * If you have subscribed to events, unsubscribe.
        * If you are running a polling loop, stop it.

        :raises NotImplementedError: Not implemented it's an abstract class
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @property
    def communication_state(self: BaseComponentManager) -> CommunicationStatus:
        """
        Return the communication status of this component manager.

        :return: status of the communication channel with the component.
        """
        return self._communication_state

    def _update_communication_state(
        self: BaseComponentManager,
        communication_state: CommunicationStatus,
    ) -> None:
        """
        Handle a change in communication status.

        This is a helper method for use by subclasses.

        :param communication_state: the new communication status of the
            component manager.
        """
        with self._communication_state_lock:
            if self._communication_state != communication_state:
                self._communication_state = communication_state
                self._push_communication_state_update(communication_state)

    def _push_communication_state_update(
        self: BaseComponentManager, communication_state: CommunicationStatus
    ) -> None:
        if self._communication_state_callback is not None:
            self._communication_state_callback(communication_state)

    @property
    def component_state(self: BaseComponentManager) -> dict[str, Any]:
        """
        Return the state of this component manager's component.

        :return: state of the component.
        """
        return dict(self._component_state)

    def _update_component_state(
        self: BaseComponentManager,
        **kwargs: Any,
    ) -> None:
        """
        Handle a change in component state.

        This is a helper method for use by subclasses.

        :param kwargs: key/values for state
        """
        callback_kwargs = {}

        with self._component_state_lock:
            for key, value in kwargs.items():
                if self._component_state[key] != value:
                    self._component_state[key] = value
                    callback_kwargs[key] = value
            if callback_kwargs:
                self._push_component_state_update(**callback_kwargs)

    def _push_component_state_update(self: BaseComponentManager, **kwargs: Any) -> None:
        if self._component_state_callback is not None:
            self._component_state_callback(**kwargs)

    @check_communicating
    def off(
        self: BaseComponentManager, task_callback: TaskCallbackType | None = None
    ) -> tuple[TaskStatus, str]:
        """
        Turn the component off.

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: Not implemented it's an abstract class
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @check_communicating
    def standby(
        self: BaseComponentManager, task_callback: TaskCallbackType | None = None
    ) -> tuple[TaskStatus, str]:
        """
        Put the component into low-power standby mode.

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: Not implemented it's an abstract class
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @check_communicating
    def on(
        self: BaseComponentManager, task_callback: TaskCallbackType | None = None
    ) -> tuple[TaskStatus, str]:
        """
        Turn the component on.

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: Not implemented it's an abstract class
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @check_communicating
    def reset(
        self: BaseComponentManager, task_callback: TaskCallbackType | None = None
    ) -> tuple[TaskStatus, str]:
        """
        Reset the component (from fault state).

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: Not implemented it's an abstract class
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @check_communicating
    def abort_commands(
        self: BaseComponentManager, task_callback: TaskCallbackType | None = None
    ) -> tuple[TaskStatus, str]:
        """
        Abort all tasks queued & running.

        :param task_callback: callback to be called whenever the status
            of the task changes.

        :raises NotImplementedError: Not implemented it's an abstract class
        """
        raise NotImplementedError("BaseComponentManager is abstract.")
