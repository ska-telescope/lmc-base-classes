# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
This module provides abstract base classes for device commands, and a ResultCode enum.

The following command classes are provided:

* **FastCommand**: implements the common pattern for fast commands; that
  is, commands that do not perform any blocking action. These commands
  call their callback to indicate that they have started, then execute
  their do hook, and then immediately call their callback to indicate
  that they have completed.

* **DeviceInitCommand**: Implements the common pattern for device Init
    commands. This is just a FastCommands, with a fixed signature for
    the ``__init__`` method.

* **SlowCommand**: implements the common pattern for slow commands; that
  is, commands that need to perform a blocking action, such as file I/O,
  network I/O, waiting for a shared resource, etc. These commands call
  their callback to indicate that they have started, then execute their
  do hook. However they do not immediately call their callback to
  indicate completion. They assume that the do hook will launch work in
  an asynchronous context (such as a thread), and make it the
  responsibility of that asynchronous context to call the command's
  ``completed`` method when it finishes.


* **SubmittedSlowCommand**: ``whereas SlowCommand`` makes no assumptions
    about how the command will be implemented, ``SubmittedSlowCommand``
    assumes the current device structure: i.e. a command tracker, and a
    component manager with support for submitting tasks.
"""
from __future__ import annotations

import enum
import functools
import logging
from typing import Any, Callable, Optional

from tango.server import Device
from typing_extensions import Protocol

from ska_tango_base.base.component_manager import BaseComponentManager
from ska_tango_base.executor import TaskStatus

__all__ = [
    "ResultCode",
    "FastCommand",
    "SlowCommand",
    "DeviceInitCommand",
    "SubmittedSlowCommand",
    "CommandTrackerProtocol",
]

module_logger = logging.getLogger(__name__)


class CommandTrackerProtocol(Protocol):
    """All things to do with commands."""

    def new_command(
        self: CommandTrackerProtocol,
        command_name: str,
        completed_callback: Optional[Callable[[], None]] = None,
    ) -> str:
        """
        Create a new command.

        :param command_name: the command name
        :param completed_callback: an optional callback for command completion
        """
        ...

    def update_command_info(
        self: CommandTrackerProtocol,
        command_id: str,
        status: Optional[TaskStatus] = None,
        progress: Optional[int] = None,
        result: Optional[tuple[ResultCode, str]] = None,
        exception: Optional[Exception] = None,
    ) -> None:
        """
        Update status information on the command.

        :param command_id: the unique command id
        :param status: the status of the asynchronous task
        :param progress: the progress of the asynchronous task
        :param result: the result of the completed asynchronous task
        :param exception: any exception caught in the running task
        """
        ...


class ResultCode(enum.IntEnum):
    """Python enumerated type for command return codes."""

    OK = 0
    """
    The command was executed successfully.
    """

    STARTED = 1
    """
    The command has been accepted and will start immediately.
    """

    QUEUED = 2
    """
    The command has been accepted and will be executed at a future time
    """

    FAILED = 3
    """
    The command could not be executed.
    """

    UNKNOWN = 4
    """
    The status of the command is not known.
    """

    REJECTED = 5
    """
    The command execution has been rejected.
    """

    NOT_ALLOWED = 6
    """
    The command is not allowed to be executed
    """

    ABORTED = 7
    """
    The command in progress has been aborted
    """


class _BaseCommand:
    """
    Abstract base class for Tango device server commands.

    Checks that the command is allowed to run in the current state, and
    runs the command.
    """

    def __init__(self: _BaseCommand, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialise a new BaseCommand instance.

        :param logger: the logger to be used by this Command. If not
            provided, then a default module logger will be used.
        """
        self._name = self.__class__.__name__
        self.logger = logger or module_logger

    def __call__(self: _BaseCommand, *args: Any, **kwargs: Any) -> Any:
        """
        Invoke the command.

        This is implemented to simply call the do() hook, thus running
        the user-specified functionality therein.

        :param args: positional args to the component manager method
        :param kwargs: keyword args to the component manager method

        :raises NotImplementedError: method does not exist
        """
        raise NotImplementedError(
            "_BaseCommand is abstract; __call__() needs to be implemented by a "
            "subclass; try FastCommand or SlowCommand instead."
        )

    def do(self: _BaseCommand, *args: Any, **kwargs: Any) -> Any:
        """
        Perform the user-specified functionality of the command.

        This class provides stub functionality; subclasses should
        subclass this method with their command functionality.

        :param args: positional args to the component manager method
        :param kwargs: keyword args to the component manager method

        :raises NotImplementedError: method does not exist
        """
        raise NotImplementedError(
            "BaseCommand is abstract; do() needs to be implemented by a subclass."
        )


class FastCommand(_BaseCommand):
    """
    An abstract class for Tango device server commands that execute quickly.

    That is, they do not perform any blocking operation, so can be
    safely run synchronously.
    """

    def __call__(self: FastCommand, *args: Any, **kwargs: Any) -> Any:
        """
        Invoke the command.

        This is implemented to simply call the do() hook, thus running
        the user-specified functionality therein.

        :param args: positional args to the component manager method
        :param kwargs: keyword args to the component manager method

        :raises Exception: method does not exist

        :return: result of command
        """
        try:
            return self.do(*args, **kwargs)
        except Exception:
            self.logger.exception(
                f"Error executing command {self._name} with args '{args}', kwargs '{kwargs}'."
            )
            raise


class SlowCommand(_BaseCommand):
    """
    An abstract class for Tango device server commands that execute slowly.

    That is, they perform at least one blocking operation, such as file
    I/O, network I/O, waiting for a shared resources, etc. They
    therefore need to be run asynchronously in order to preserve
    throughput.
    """

    def __init__(
        self: SlowCommand,
        callback: Optional[Callable],
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialise a new BaseCommand instance.

        :param callback: a callback to be called when this command
            starts and finishes.
        :param logger: a logger for this command to log with.
        """
        self._callback = callback
        super().__init__(logger=logger)

    def __call__(self: SlowCommand, *args: Any, **kwargs: Any) -> Any:
        """
        Invoke the command.

        This is implemented to simply call the do() hook, thus running
        the user-specified functionality therein.

        :param args: positional args to the component manager method
        :param kwargs: keyword args to the component manager method

        :raises Exception: method does not exist

        :return: result of command submission
        """
        self._invoked()
        try:
            return self.do(*args, **kwargs)
        except Exception:
            self.logger.exception(
                f"Error executing command {self._name} with args '{args}', kwargs '{kwargs}'."
            )
            self._completed()
            raise

    def _invoked(self: SlowCommand) -> None:
        if self._callback is not None:
            self._callback(True)

    def _completed(self: SlowCommand) -> None:
        if self._callback is not None:
            self._callback(False)


class DeviceInitCommand(SlowCommand):
    """
    A ``SlowCommand`` with a fixed initialisation interface.

    Although most commands have lots of flexibility in how they are
    initialised, device ``InitCommand`` instances are always called in
    the same way. This class fixes that interface. ``InitCommand``
    instances should inherit from this command, rather than directly
    from ``SlowCommand``, to ensure that their initialisation signature
    is correct.
    """

    def __init__(
        self: DeviceInitCommand, device: Device, logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Initialise a new instance.

        :param device: the device that this command will initialise
        :param logger: a logger for this command to log with.
        """
        self._device = device

        def _callback(running: bool) -> None:
            if running:
                device.op_state_model.perform_action("init_completed")

        super().__init__(callback=_callback, logger=logger)


class SubmittedSlowCommand(SlowCommand):
    """
    A SlowCommand with lots of implementation-dependent boilerplate in it.

    Whereas the SlowCommand is generic, and makes no assumptions about
    how the slow command will be executed, this SubmittedSlowCommand
    contains implementation-dependent information about the
    SKABaseDevice model, such as knowledge of the command tracker and
    component manager. It thus implements a lot of boilerplate code, and
    allows us to avoid implementing many identical commands.

    :param command_name: name of the command e.g. "Scan". This is only
        used to ensure that the generated command id contains it.
    :param command_tracker: the device's command tracker
    :param component_manager: the device's component manager
    :param method_name: name of the component manager method to be
        invoked by the do hook
    :param callback: an optional callback to be called when this command
        starts and finishes.
    :param logger: a logger for this command to log with.
    """

    def __init__(
        self: SubmittedSlowCommand,
        command_name: str,
        command_tracker: CommandTrackerProtocol,
        component_manager: BaseComponentManager,
        method_name: str,
        callback: Optional[Callable] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialise a new instance.

        :param command_name: name of the command e.g. "Scan". This is
            only used to ensure that the generated command id contains
            it.
        :param command_tracker: the device's command tracker
        :param component_manager: the device's component manager
        :param method_name: name of the component manager method to be
            invoked by the do hook
        :param callback: an optional callback to be called when this
            command starts and finishes.
        :param logger: a logger for this command to log with.
        """
        self._command_name = command_name
        self._command_tracker = command_tracker
        self._component_manager = component_manager
        self._method_name = method_name
        super().__init__(callback=callback, logger=logger)

    def do(
        self: SubmittedSlowCommand, *args: Any, **kwargs: Any
    ) -> tuple[ResultCode, str]:
        """
        Stateless hook for command functionality.

        :param args: positional args to the component manager method
        :param kwargs: keyword args to the component manager method

        :return: A tuple containing the task status (e.g. QUEUED or
            REJECTED), and a string message containing a command_id (if
            the command has been accepted) or an informational message
            (if the command was rejected)
        """
        command_id = self._command_tracker.new_command(
            self._command_name, completed_callback=self._completed
        )
        method = getattr(self._component_manager, self._method_name)
        result = method(
            *args,
            functools.partial(self._command_tracker.update_command_info, command_id),
            **kwargs,
        )
        status, message = result
        if status == TaskStatus.QUEUED:
            return ResultCode.QUEUED, command_id
        elif status == TaskStatus.REJECTED:
            return ResultCode.REJECTED, message
        # TODO: Drew, can this else block happen or just remove the elif????
        else:
            return ResultCode.FAILED, "Command failed"
