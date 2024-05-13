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

import functools
import json
import logging
import warnings
from typing import Any, Callable, Generic, TypeVar

import jsonschema
from ska_control_model import ResultCode, TaskStatus
from tango.server import Device
from typing_extensions import Protocol

from .base.base_component_manager import BaseComponentManager

__all__ = [
    "ResultCode",
    "FastCommand",
    "SlowCommand",
    "DeviceInitCommand",
    "SubmittedSlowCommand",
    "CommandTrackerProtocol",
    "ArgumentValidator",
    "JsonValidator",
]

module_logger = logging.getLogger(__name__)


class CommandTrackerProtocol(Protocol):
    """All things to do with commands."""

    def new_command(
        self: CommandTrackerProtocol,
        command_name: str,
        completed_callback: Callable[[], None] | None = None,
    ) -> str:
        """
        Create a new command.

        :param command_name: the command name
        :param completed_callback: an optional callback for command completion
        """

    def update_command_info(  # pylint: disable=too-many-arguments
        self: CommandTrackerProtocol,
        command_id: str,
        status: TaskStatus | None = None,
        progress: int | None = None,
        result: tuple[ResultCode, str] | None = None,
        exception: Exception | None = None,
    ) -> None:
        """
        Update status information on the command.

        :param command_id: the unique command id
        :param status: the status of the asynchronous task
        :param progress: the progress of the asynchronous task
        :param result: the result of the completed asynchronous task
        :param exception: any exception caught in the running task
        """


class ArgumentValidator:  # pylint: disable=too-few-public-methods
    """Base class for command argument validators."""

    def validate(
        self: ArgumentValidator, *args: Any, **kwargs: Any
    ) -> tuple[tuple[Any, ...], dict[str, Any]]:
        """
        Parse and/or validate the call arguments.

        This is a default implementation that performs no parsing or
        validating, and simply returns the arguments as received.

        Subclasses may override this method to parse, validate and
        transform the arguments.

        :param args: positional args to the command
        :param kwargs: keyword args to the command

        :return: an (args, kwargs) tuple with which to invoke the do()
            hook. This default implementation simply returns the
            arguments as received.
        """
        return (args, kwargs)


class JsonValidator(ArgumentValidator):  # pylint: disable=too-few-public-methods
    """
    An argument validator for JSON commands.

    It checks that the argument is called with no more than one
    positional argument and no keyword arguments, unpacks the positional
    argument (if any) from JSON into a dictionary, and validates against
    JSON schema.
    """

    DEFAULT_SCHEMA: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://example.com/product.schema.json",
        "title": "Default schema",
        "description": "Validates the item as a dictionary",
        "type": "object",
    }

    def __init__(
        self: JsonValidator,
        command_name: str,
        schema: dict[str, Any] | None,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Initialise a new instance.

        :param command_name: name of the command to be validated.
        :param schema: an optional schema against which the JSON
            argument should be validated. If not provided, a warning is
            issued.
        :param logger: a logger for this validator to use
        """
        self._command_name = command_name
        self._logger = logger

        if schema is None:
            warning_msg = (
                f"JSON argument to command {command_name} "
                "will only be validated as a dictionary."
            )
            warnings.warn(warning_msg)
            if logger:
                logger.warn(warning_msg)
        self._schema = schema or self.DEFAULT_SCHEMA

    def validate(
        self: JsonValidator, *args: Any, **kwargs: Any
    ) -> tuple[tuple[Any, ...], dict[str, Any]]:
        """
        Validate the command arguments.

        Checks that there is only one positional argument and no keyword
        arguments; unpacks the positional argument from JSON into a
        dictionary; and validate against the provided JSON schema.

        :param args: positional args to the command
        :param kwargs: keyword args to the command

        :returns: validated args and kwargs
        """
        assert not kwargs, (
            f"Command {self._command_name} was invoked with kwargs. "
            "JSON validation does not permit kwargs"
        )
        if args:
            assert len(args) == 1, (
                f"Command {self._command_name} was invoked with {len(args)} args. "
                "JSON validation only permits one positional argument."
            )

            decoded_dict = json.loads(args[0])
        else:
            decoded_dict = {}
        jsonschema.validate(decoded_dict, self._schema)
        return (), decoded_dict


CommandReturnT = TypeVar("CommandReturnT")


class _BaseCommand(Generic[CommandReturnT]):
    """
    Abstract base class for Tango device server commands.

    Checks that the command is allowed to run in the current state, and
    runs the command.
    """

    def __init__(
        self: _BaseCommand[CommandReturnT],
        logger: logging.Logger | None = None,
        validator: ArgumentValidator | None = None,
    ) -> None:
        """
        Initialise a new BaseCommand instance.

        :param logger: the logger to be used by this Command. If not
            provided, then a default module logger will be used.
        :param validator: an optional validator to use to parse,
            validate and/or unpack command arguments.
        """
        self._name = self.__class__.__name__
        self.logger = logger or module_logger
        self._validator = validator or ArgumentValidator()

    def __call__(
        self: _BaseCommand[CommandReturnT], *args: Any, **kwargs: Any
    ) -> CommandReturnT:
        """
        Handle a call to the command.

        This is implemented to call the parse() hook and then the
        invoke() hook.

        :param args: positional args to the command
        :param kwargs: keyword args to the command

        :return: the result of invoking the user-provided functionality
        """
        (args, kwargs) = self._validator.validate(*args, **kwargs)
        return self.invoke(*args, **kwargs)

    def invoke(
        self: _BaseCommand[CommandReturnT], *args: Any, **kwargs: Any
    ) -> CommandReturnT:
        """
        Invoke the do() hook.

        This default implementation simply calls the do() hook, and
        returns whatever that hook returns.

        Subclasses may override this hook to handle invokation patterns
        such as for asynchronous invokation.

        :param args: positional args to the command
        :param kwargs: keyword args to the command

        :return: the result of calling the do() hook.
        """
        return self.do(*args, **kwargs)

    def do(
        self: _BaseCommand[CommandReturnT], *args: Any, **kwargs: Any
    ) -> CommandReturnT:
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


# pylint: disable-next=abstract-method  # Yes, this is an abstract class.
class FastCommand(_BaseCommand[CommandReturnT]):
    """
    An abstract class for Tango device server commands that execute quickly.

    That is, they do not perform any blocking operation, so can be
    safely run synchronously.
    """

    def invoke(
        self: FastCommand[CommandReturnT], *args: Any, **kwargs: Any
    ) -> CommandReturnT:
        """
        Invoke the command.

        This is implemented to simply call the do() hook, thus running
        the user-specified functionality therein.

        :param args: positional args to the component manager method
        :param kwargs: keyword args to the component manager method

        :raises Exception: any exception that is raised during the
            execution of the self.do method.

        :return: result of command
        """
        try:
            return self.do(*args, **kwargs)
        except Exception:
            self.logger.exception(
                f"Error executing command {self._name} with args '{args}', kwargs "
                f"'{kwargs}'."
            )
            raise


# pylint: disable-next=abstract-method  # Yes, this is an abstract class.
class SlowCommand(_BaseCommand[CommandReturnT]):
    """
    An abstract class for Tango device server commands that execute slowly.

    That is, they perform at least one blocking operation, such as file
    I/O, network I/O, waiting for a shared resources, etc. They
    therefore need to be run asynchronously in order to preserve
    throughput.
    """

    def __init__(
        self: SlowCommand[CommandReturnT],
        callback: Callable[[bool], None] | None,
        logger: logging.Logger | None = None,
        validator: ArgumentValidator | None = None,
    ) -> None:
        """
        Initialise a new BaseCommand instance.

        :param callback: a callback to be called when this command
            starts and finishes.
        :param logger: a logger for this command to log with.
        :param validator: an optional validator to use to parse,
            validate and/or unpack command arguments.
        """
        self._callback = callback
        super().__init__(logger=logger, validator=validator)

    def invoke(
        self: SlowCommand[CommandReturnT], *args: Any, **kwargs: Any
    ) -> CommandReturnT:
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
                f"Error executing command {self._name} with args '{args}', kwargs "
                f"'{kwargs}'."
            )
            self._completed()
            raise

    def _invoked(self: SlowCommand[CommandReturnT]) -> None:
        if self._callback is not None:
            self._callback(True)

    def _completed(self: SlowCommand[CommandReturnT]) -> None:
        if self._callback is not None:
            self._callback(False)


# pylint: disable-next=abstract-method
class DeviceInitCommand(SlowCommand[tuple[ResultCode, str]]):
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
        self: DeviceInitCommand,
        device: Device,
        logger: logging.Logger | None = None,
        validator: ArgumentValidator | None = None,
    ) -> None:
        """
        Initialise a new instance.

        :param device: the device that this command will initialise
        :param logger: a logger for this command to log with.
        :param validator: an optional validator to use to parse,
            validate and/or unpack command arguments.
        """
        self._device = device

        def _callback(running: bool) -> None:
            if running:
                device.op_state_model.perform_action("init_completed")

        super().__init__(callback=_callback, logger=logger, validator=validator)


class SubmittedSlowCommand(SlowCommand[tuple[ResultCode, str]]):
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

    def __init__(  # pylint: disable=too-many-arguments
        self: SubmittedSlowCommand,
        command_name: str,
        command_tracker: CommandTrackerProtocol,
        component_manager: BaseComponentManager,
        method_name: str,
        callback: Callable[[bool], None] | None = None,
        logger: logging.Logger | None = None,
        validator: ArgumentValidator | None = None,
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
        :param validator: an optional validator to use to parse,
            validate and/or unpack command arguments.
        """
        self._command_name = command_name
        self._command_tracker = command_tracker
        self._component_manager = component_manager
        self._method_name = method_name
        super().__init__(callback=callback, logger=logger, validator=validator)

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
        status, message = method(
            *args,
            functools.partial(self._command_tracker.update_command_info, command_id),
            **kwargs,
        )
        if status == TaskStatus.QUEUED:
            return ResultCode.QUEUED, command_id
        if status == TaskStatus.REJECTED:
            return ResultCode.REJECTED, message
        if status == TaskStatus.FAILED:
            return ResultCode.FAILED, message
        return ResultCode.FAILED, "Command could not be executed"
