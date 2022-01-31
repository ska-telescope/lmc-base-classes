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
import threading
from typing import Any, Callable, Optional, TypeVar, cast

from ska_tango_base.control_model import CommunicationStatus, PowerState
from ska_tango_base.executor import TaskExecutor
from ska_tango_base.faults import ComponentError

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


def check_on(func):
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
    def _wrapper(component, *args, **kwargs):
        """
        Check that the component is on and not faulty before calling the function.

        This is a wrapper function that implements the functionality of
        the decorator.

        :param component: the component to check
        :param args: positional arguments to the wrapped function
        :param kwargs: keyword arguments to the wrapped function

        :return: whatever the wrapped function returns
        """
        if component.power_state != PowerState.ON:
            raise ComponentError("Component is not powered ON")
        return func(component, *args, **kwargs)

    return _wrapper


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
        self,
        logger,
        communication_state_callback,
        component_state_callback,
        **state,
    ):
        """
        Initialise a new ComponentManager instance.

        :param communication_state_callback: callback to be called when
            the status of communications between the component manager
            and its component changes.
        :param component_state_callback: callback to be called when the
            monitored state of the component changes
        """
        self.logger = logger

        self._communication_state_lock = threading.Lock()
        self._communication_state = CommunicationStatus.DISABLED
        self._communication_state_callback = communication_state_callback

        self._component_state_lock = threading.Lock()
        self._component_state = dict(state)
        self._component_state_callback = component_state_callback

    def start_communicating(self):
        """
        Establish communication with the component, then start monitoring.

        This is the place to do things like:

        * Initiate a connection to the component (if your communication
          is connection-oriented)
        * Subscribe to component events (if using "pull" model)
        * Start a polling loop to monitor the component (if using a
          "push" model)
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    def stop_communicating(self):
        """
        Cease monitoring the component, and break off all communication with it.

        For example,

        * If you are communicating over a connection, disconnect.
        * If you have subscribed to events, unsubscribe.
        * If you are running a polling loop, stop it.
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

    def _push_communication_state_update(self, communication_state):
        if self._communication_state_callback is not None:
            self._communication_state_callback(communication_state)

    @property
    def component_state(self: BaseComponentManager) -> dict:
        """
        Return the state of this component manager's component.

        :return: state of the component.
        """
        return dict(self._component_state)

    def _update_component_state(
        self: BaseComponentManager,
        **kwargs,
    ) -> None:
        """
        Handle a change in communication status.

        This is a helper method for use by subclasses.
        """
        callback_kwargs = {}

        with self._component_state_lock:
            for state in kwargs:
                if self._component_state[state] != kwargs[state]:
                    self._component_state[state] = kwargs[state]
                    callback_kwargs[state] = kwargs[state]
            if callback_kwargs:
                self._push_component_state_update(**callback_kwargs)

    def _push_component_state_update(self, **kwargs):
        if self._component_state_callback is not None:
            self._component_state_callback(**kwargs)

    @check_communicating
    def off(self, task_callback):
        """
        Turn the component off.

        :param task_callback: callback to be called when the status of
            the command changes
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @check_communicating
    def standby(self, task_callback):
        """
        Put the component into low-power standby mode.

        :param task_callback: callback to be called when the status of
            the command changes
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @check_communicating
    def on(self, task_callback):
        """
        Turn the component on.

        :param task_callback: callback to be called when the status of
            the command changes
        """
        raise NotImplementedError("BaseComponentManager is abstract.")

    @check_communicating
    def reset(self, task_callback):
        """
        Reset the component (from fault state).

        :param task_callback: callback to be called when the status of
            the command changes
        """
        raise NotImplementedError("BaseComponentManager is abstract.")


class TaskExecutorComponentManager(BaseComponentManager):
    """A component manager with support for asynchronous tasking."""

    def __init__(
        self,
        *args,
        max_workers: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialise a new ComponentManager instance.

        :param args: additional positional arguments
        :param max_workers: option maximum number of workers in the pool
        :param kwargs: additional keyword arguments
        """
        self._task_executor = TaskExecutor(max_workers)
        super().__init__(*args, **kwargs)

    def submit_task(self, func, args=None, kwargs=None, task_callback=None):
        """
        Submit a task to the task executor.

        :param func: function/bound method to be run
        :param args: positional arguments to the function
        :param kwargs: keyword arguments to the function
        :param task_callback: callback to be called whenever the status
            of the task changes.
        """
        return self._task_executor.submit(
            func, args, kwargs, task_callback=task_callback
        )

    def abort_tasks(self, task_callback=None):
        """
        Tell the task executor to abort all tasks.

        :param task_callback: callback to be called whenever the status
            of this abort task changes.
        """
        return self._task_executor.abort(task_callback)
