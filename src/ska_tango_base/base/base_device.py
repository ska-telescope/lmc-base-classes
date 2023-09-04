# pylint: disable=invalid-name, too-many-lines  # TODO: split this module
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
This module implements a generic base model and device for SKA.

It exposes the generic attributes, properties and commands of an SKA
device.
"""
from __future__ import annotations

import inspect
import itertools
import json
import logging
import logging.handlers
import queue
import threading
import traceback
from functools import partial
from types import FunctionType, MethodType
from typing import Any, Callable, Generic, TypedDict, TypeVar, cast

import debugpy
import ska_ser_logging
from ska_control_model import (
    AdminMode,
    CommunicationStatus,
    ControlMode,
    HealthState,
    LoggingLevel,
    PowerState,
    ResultCode,
    SimulationMode,
    TaskStatus,
    TestMode,
)
from tango import DebugIt, DevState, is_omni_thread
from tango.server import Device, attribute, command, device_property

from .. import release
from ..commands import DeviceInitCommand, FastCommand, SlowCommand, SubmittedSlowCommand
from ..faults import GroupDefinitionsError, LoggingLevelError
from ..utils import generate_command_id, get_groups_from_json
from .admin_mode_model import AdminModeModel
from .component_manager import BaseComponentManager
from .logging import (
    _LMC_TO_PYTHON_LOGGING_LEVEL,
    _LMC_TO_TANGO_LOGGING_LEVEL,
    LoggingUtils,
)
from .op_state_model import OpStateModel

DevVarLongStringArrayType = tuple[list[ResultCode], list[str]]

MAX_REPORTED_CONCURRENT_COMMANDS = 16
MAX_REPORTED_QUEUED_COMMANDS = 64


_DEBUGGER_PORT = 5678


__all__ = ["SKABaseDevice", "main", "CommandTracker"]


class _CommandData(TypedDict):
    name: str
    status: TaskStatus
    progress: int | None
    completed_callback: Callable[[], None] | None


class CommandTracker:  # pylint: disable=too-many-instance-attributes
    """A class for keeping track of the state and progress of commands."""

    def __init__(  # pylint: disable=too-many-arguments
        self: CommandTracker,
        queue_changed_callback: Callable[[list[tuple[str, str]]], None],
        status_changed_callback: Callable[[list[tuple[str, TaskStatus]]], None],
        progress_changed_callback: Callable[[list[tuple[str, int]]], None],
        result_callback: Callable[[str, tuple[ResultCode, str]], None],
        exception_callback: Callable[[str, Exception], None] | None = None,
        removal_time: float = 10.0,
    ) -> None:
        """
        Initialise a new instance.

        :param queue_changed_callback: called when the queue changes
        :param status_changed_callback: called when the status changes
        :param progress_changed_callback: called when the progress changes
        :param result_callback: called when command finishes
        :param exception_callback: called in the event of an exception
        :param removal_time: timer
        """
        self.__lock = threading.RLock()
        self._queue_changed_callback = queue_changed_callback
        self._status_changed_callback = status_changed_callback
        self._progress_changed_callback = progress_changed_callback
        self._result_callback = result_callback
        self._most_recent_result: tuple[
            str, tuple[ResultCode, str] | None
        ] | None = None
        self._exception_callback = exception_callback
        self._most_recent_exception: tuple[str, Exception] | None = None
        self._commands: dict[str, _CommandData] = {}
        self._removal_time = removal_time

    def new_command(
        self: CommandTracker,
        command_name: str,
        completed_callback: Callable[[], None] | None = None,
    ) -> str:
        """
        Create a new command.

        :param command_name: the command name
        :param completed_callback: an optional callback for command completion

        :return: a unique command id
        """
        command_id = generate_command_id(command_name)

        self._commands[command_id] = {
            "name": command_name,
            "status": TaskStatus.STAGING,
            "progress": None,
            "completed_callback": completed_callback,
        }
        self._queue_changed_callback(self.commands_in_queue)
        return command_id

    def _schedule_removal(self: CommandTracker, command_id: str) -> None:
        def remove(command_id: str) -> None:
            del self._commands[command_id]
            self._queue_changed_callback(self.commands_in_queue)

        threading.Timer(self._removal_time, remove, (command_id,)).start()

    def update_command_info(  # pylint: disable=too-many-arguments
        self: CommandTracker,
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
        with self.__lock:
            if exception is not None:
                self._most_recent_exception = (command_id, exception)
                if self._exception_callback is not None:
                    self._exception_callback(command_id, exception)
            if result is not None:
                self._most_recent_result = (command_id, result)
                self._result_callback(command_id, result)
            if progress is not None:
                self._commands[command_id]["progress"] = progress
                self._progress_changed_callback(self.command_progresses)
            if status is not None:
                self._commands[command_id]["status"] = status
                self._status_changed_callback(self.command_statuses)

                if status == TaskStatus.COMPLETED:
                    completed_callback = self._commands[command_id][
                        "completed_callback"
                    ]
                    if completed_callback is not None:
                        completed_callback()
                if status in [
                    TaskStatus.ABORTED,
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                    TaskStatus.REJECTED,
                ]:
                    self._commands[command_id]["progress"] = None
                    self._schedule_removal(command_id)

    @property
    def commands_in_queue(self: CommandTracker) -> list[tuple[str, str]]:
        """
        Return a list of commands in the queue.

        :return: a list of (command_id, command_name) tuples, ordered by
            when invoked.
        """
        with self.__lock:
            return list(
                (command_id, command["name"])
                for command_id, command in self._commands.items()
                if command["name"] is not None
            )

    @property
    def command_statuses(self: CommandTracker) -> list[tuple[str, TaskStatus]]:
        """
        Return a list of command statuses for commands in the queue.

        :return: a list of (command_id, status) tuples, ordered by when
            invoked.
        """
        with self.__lock:
            return list(
                (command_id, command["status"])
                for command_id, command in self._commands.items()
                if command["status"] is not None
            )

    @property
    def command_progresses(self: CommandTracker) -> list[tuple[str, int]]:
        """
        Return a list of command progresses for commands in the queue.

        :return: a list of (command_id, progress) tuples, ordered by
            when invoked.
        """
        with self.__lock:
            return list(
                (command_id, command["progress"])
                for command_id, command in self._commands.items()
                if command["progress"] is not None
            )

    @property
    def command_result(
        self: CommandTracker,
    ) -> tuple[str, tuple[ResultCode, str] | None] | None:
        """
        Return the result of the most recently completed command.

        :return: a (command_id, result) tuple. If no command has
            completed yet, then None.
        """
        return self._most_recent_result

    @property
    def command_exception(self: CommandTracker) -> tuple[str, Exception] | None:
        """
        Return the most recent exception, if any.

        :return: a (command_id, exception) tuple. If no command has
            raised an uncaught exception, then None.
        """
        return self._most_recent_exception

    def get_command_status(self: CommandTracker, command_id: str) -> TaskStatus:
        """
        Return the current status of a running command.

        :param command_id: the unique command id

        :return: a status of the asynchronous task.
        """
        if command_id in self._commands:
            return self._commands[command_id]["status"]
        return TaskStatus.NOT_FOUND


ComponentManagerT = TypeVar("ComponentManagerT", bound=BaseComponentManager)


# pylint: disable-next=too-many-instance-attributes, too-many-public-methods
class SKABaseDevice(
    Device,  # type: ignore[misc]  # Cannot subclass Device (has type Any)
    Generic[ComponentManagerT],
):
    # pylint: disable=attribute-defined-outside-init  # Tango devices have init_device
    """A generic base device for SKA."""

    _global_debugger_listening = False
    _global_debugger_allocated_port = 0

    class InitCommand(DeviceInitCommand):
        """A class for the SKABaseDevice's init_device() "command"."""

        def do(
            self: SKABaseDevice.InitCommand,
            *args: Any,
            **kwargs: Any,
        ) -> tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.

            :param args: positional arguments to this do method
            :param kwargs: keyword arguments to this do method

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            message = "SKABaseDevice Init command completed OK"
            self.logger.info(message)
            self._completed()
            return (ResultCode.OK, message)

    _logging_config_lock = threading.Lock()
    _logging_configured = False

    def _init_logging(self: SKABaseDevice[ComponentManagerT]) -> None:  # noqa: C901
        """Initialize the logging mechanism, using default properties."""
        # TODO: This comment stops black adding a blank line here,
        # causing flake8-docstrings D202 error.

        # pylint: disable-next=too-few-public-methods
        class EnsureTagsFilter(logging.Filter):
            """
            Ensure all records have a "tags" field.

            The tag will be the empty string if a tag is not provided.
            """

            def filter(  # noqa: A003
                self: EnsureTagsFilter, record: logging.LogRecord
            ) -> bool:
                if not hasattr(record, "tags"):
                    record.tags = ""
                return True

        # There may be multiple devices in a single device server - these will all be
        # starting at the same time, so use a lock to prevent race conditions, and
        # a flag to ensure the SKA standard logging configuration is only applied once.
        with SKABaseDevice._logging_config_lock:
            if not SKABaseDevice._logging_configured:
                ska_ser_logging.configure_logging(tags_filter=EnsureTagsFilter)
                SKABaseDevice._logging_configured = True

        device_name = self.get_name()
        self.logger = logging.getLogger(device_name)
        # device may be reinitialised, so remove existing handlers and filters
        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)
        for filt in list(self.logger.filters):
            self.logger.removeFilter(filt)

        # add a filter with this device's name
        device_name_tag = f"tango-device:{device_name}"

        # pylint: disable-next=too-few-public-methods
        class TangoDeviceTagsFilter(logging.Filter):
            """Filter that adds tango device name to the emitted record."""

            def filter(  # noqa: A003
                self: TangoDeviceTagsFilter, record: logging.LogRecord
            ) -> bool:
                record.tags = device_name_tag
                return True

        self.logger.addFilter(TangoDeviceTagsFilter())
        # before setting targets, give Python logger a reference to the log4tango logger
        # to support the TangoLoggingServiceHandler target option

        self.logger.tango_logger = self.get_logger()  # type: ignore[attr-defined]

        # initialise using defaults in device properties
        self._logging_level: LoggingLevel | None = None
        self.set_logging_level(self.LoggingLevelDefault)
        self.set_logging_targets(self.LoggingTargetsDefault)
        self.logger.debug("Logger initialised")

        # monkey patch Tango Logging Service streams so they go to the Python
        # logger instead

        def _debug_patch(
            *args: Any,
            source: str | None = None,  # pylint: disable=unused-argument
            **kwargs: Any,
        ) -> None:
            self.logger.debug(*args, **kwargs)

        self.debug_stream = _debug_patch

        def _info_patch(
            *args: Any,
            source: str | None = None,  # pylint: disable=unused-argument
            **kwargs: Any,
        ) -> None:
            self.logger.info(*args, **kwargs)

        self.info_stream = _info_patch

        def _warn_patch(
            *args: Any,
            source: str | None = None,  # pylint: disable=unused-argument
            **kwargs: Any,
        ) -> None:
            self.logger.warning(*args, **kwargs)

        self.warn_stream = _warn_patch

        def _error_patch(
            *args: Any,
            source: str | None = None,  # pylint: disable=unused-argument
            **kwargs: Any,
        ) -> None:
            self.logger.error(*args, **kwargs)

        self.error_stream = _error_patch

        def _fatal_patch(
            *args: Any,
            source: str | None = None,  # pylint: disable=unused-argument
            **kwargs: Any,
        ) -> None:
            self.logger.critical(*args, **kwargs)

        self.fatal_stream = _fatal_patch

    # -----------------
    # Device Properties
    # -----------------

    SkaLevel = device_property(dtype="int16", default_value=4)
    """
    Device property.

    Indication of importance of the device in the SKA hierarchy to
    support drill-down navigation: 1..6, with 1 highest.
    """

    GroupDefinitions = device_property(
        dtype=("str",),
    )
    """
    Device property.

    Each string in the list is a JSON serialised dict defining the ``group_name``,
    ``devices`` and ``subgroups`` in the group.  A Tango Group object is created
    for each item in the list, according to the hierarchy defined.  This provides
    easy access to the managed devices in bulk, or individually.

    The general format of the list is as follows, with optional ``devices`` and
    ``subgroups`` keys::

        [ {"group_name": "<name>",
           "devices": ["<dev name>", ...]},
          {"group_name": "<name>",
           "devices": ["<dev name>", "<dev name>", ...],
           "subgroups" : [{<nested group>},
                            {<nested group>}, ...]},
          ...
          ]

    For example, a hierarchy of racks, servers and switches::

        [ {"group_name": "servers",
           "devices": ["elt/server/1", "elt/server/2",
                         "elt/server/3", "elt/server/4"]},
          {"group_name": "switches",
           "devices": ["elt/switch/A", "elt/switch/B"]},
          {"group_name": "pdus",
           "devices": ["elt/pdu/rackA", "elt/pdu/rackB"]},
          {"group_name": "racks",
           "subgroups": [
                {"group_name": "rackA",
                 "devices": ["elt/server/1", "elt/server/2",
                               "elt/switch/A", "elt/pdu/rackA"]},
                {"group_name": "rackB",
                 "devices": ["elt/server/3", "elt/server/4",
                               "elt/switch/B", "elt/pdu/rackB"],
                 "subgroups": []}
           ]} ]
    """

    LoggingLevelDefault = device_property(
        dtype="uint16", default_value=LoggingLevel.INFO
    )
    """
    Device property.

    Default logging level at device startup. See
    :py:class:`~ska_control_model.LoggingLevel`
    """

    LoggingTargetsDefault = device_property(
        dtype="DevVarStringArray", default_value=["tango::logger"]
    )
    """
    Device property.

    Default logging targets at device startup. See the project readme
    for details.
    """

    # ---------
    # Callbacks
    # ---------
    def _update_state(
        self: SKABaseDevice[ComponentManagerT],
        state: DevState,
        status: str | None = None,
    ) -> None:
        """
        Perform Tango operations in response to a change in op state.

        This helper method is passed to the op state model as a
        callback, so that the model can trigger actions in the Tango
        device.

        :param state: the new state value
        :param status: an optional new status string
        """
        self.set_state(state)
        self.push_change_event("state")
        self.push_archive_event("state")
        self.set_status(status or f"The device is in {state} state.")
        self.push_change_event("status")
        self.push_archive_event("status")

    def _update_admin_mode(
        self: SKABaseDevice[ComponentManagerT], admin_mode: AdminMode
    ) -> None:
        self._admin_mode = admin_mode
        self.push_change_event("adminMode", self._admin_mode)
        self.push_archive_event("adminMode", self._admin_mode)

    def _update_health_state(
        self: SKABaseDevice[ComponentManagerT], health_state: HealthState
    ) -> None:
        self._health_state = health_state
        self.push_change_event("healthState", self._health_state)
        self.push_archive_event("healthState", self._health_state)

    def _update_commands_in_queue(
        self: SKABaseDevice[ComponentManagerT], commands_in_queue: list[tuple[str, str]]
    ) -> None:
        if commands_in_queue:
            command_ids, command_names = zip(*commands_in_queue)
            self._command_ids_in_queue = [
                str(command_id) for command_id in command_ids
            ][:MAX_REPORTED_QUEUED_COMMANDS]
            self._commands_in_queue = [
                str(command_name) for command_name in command_names
            ][:MAX_REPORTED_QUEUED_COMMANDS]
        else:
            self._command_ids_in_queue = []
            self._commands_in_queue = []
        self.push_change_event("longRunningCommandsInQueue", self._commands_in_queue)
        self.push_archive_event("longRunningCommandsInQueue", self._commands_in_queue)
        self.push_change_event(
            "longRunningCommandIDsInQueue", self._command_ids_in_queue
        )
        self.push_archive_event(
            "longRunningCommandIDsInQueue", self._command_ids_in_queue
        )

    def _update_command_statuses(
        self: SKABaseDevice[ComponentManagerT],
        command_statuses: list[tuple[str, TaskStatus]],
    ) -> None:
        statuses = [(uid, status.name) for (uid, status) in command_statuses]
        self._command_statuses = [
            str(item) for item in itertools.chain.from_iterable(statuses)
        ][: (MAX_REPORTED_CONCURRENT_COMMANDS * 2)]
        self.push_change_event("longRunningCommandStatus", self._command_statuses)
        self.push_archive_event("longRunningCommandStatus", self._command_statuses)

    def _update_command_progresses(
        self: SKABaseDevice[ComponentManagerT],
        command_progresses: list[tuple[str, int]],
    ) -> None:
        self._command_progresses = [
            str(item) for item in itertools.chain.from_iterable(command_progresses)
        ][: (MAX_REPORTED_CONCURRENT_COMMANDS * 2)]
        self.push_change_event("longRunningCommandProgress", self._command_progresses)
        self.push_archive_event("longRunningCommandProgress", self._command_progresses)

    def _update_command_result(
        self: SKABaseDevice[ComponentManagerT],
        command_id: str,
        command_result: tuple[ResultCode, str],
    ) -> None:
        self._command_result = (command_id, json.dumps(command_result))
        self.push_change_event("longRunningCommandResult", self._command_result)
        self.push_archive_event("longRunningCommandResult", self._command_result)

    def _update_command_exception(
        self: SKABaseDevice[ComponentManagerT],
        command_id: str,
        command_exception: Exception,
    ) -> None:
        self.logger.error(
            f"Command '{command_id}' raised exception {command_exception}"
        )
        self._command_result = (command_id, str(command_exception))
        self.push_change_event("longRunningCommandResult", self._command_result)
        self.push_archive_event("longRunningCommandResult", self._command_result)

    def _communication_state_changed(
        self: SKABaseDevice[ComponentManagerT], communication_state: CommunicationStatus
    ) -> None:
        action_map = {
            CommunicationStatus.DISABLED: "component_disconnected",
            CommunicationStatus.NOT_ESTABLISHED: "component_unknown",
            CommunicationStatus.ESTABLISHED: None,  # wait for a component state update
        }
        action = action_map[communication_state]
        if action is not None:
            self.op_state_model.perform_action(action)

    def _component_state_changed(
        self: SKABaseDevice[ComponentManagerT],
        fault: bool | None = None,
        power: PowerState | None = None,
    ) -> None:
        if power is not None:
            action_map = {
                PowerState.UNKNOWN: None,
                PowerState.OFF: "component_off",
                PowerState.STANDBY: "component_standby",
                PowerState.ON: "component_on",
            }
            action = action_map[power]
            if action is not None:
                self.op_state_model.perform_action(action)

        if fault is not None:
            if fault:
                self.op_state_model.perform_action("component_fault")
            else:
                self.op_state_model.perform_action("component_no_fault")

    # ---------------
    # General methods
    # ---------------
    def init_device(self: SKABaseDevice[ComponentManagerT]) -> None:
        """
        Initialise the tango device after startup.

        Subclasses that have no need to override the default
        implementation of state management may leave ``init_device()``
        alone.  Override the ``do()`` method on the nested class
        ``InitCommand`` instead.
        """
        try:
            super().init_device()

            self._omni_queue: queue.SimpleQueue[
                tuple[str, Any, Any]
            ] = queue.SimpleQueue()

            # this can be removed when cppTango issue #935 is implemented
            self._init_active = True
            self.poll_command("ExecutePendingOperations", 5)

            self._init_logging()

            self._admin_mode = AdminMode.OFFLINE
            self._health_state = HealthState.UNKNOWN
            self._control_mode = ControlMode.REMOTE
            self._simulation_mode = SimulationMode.FALSE
            self._test_mode = TestMode.NONE

            self._command_ids_in_queue = []
            self._commands_in_queue = []
            self._command_statuses = []
            self._command_progresses = []
            self._command_result = ("", "")

            self._build_state = (
                f"{release.name}, {release.version}, {release.description}"
            )
            self._version_id = release.version
            self._methods_patched_for_debugger = False

            for attribute_name in [
                "state",
                "status",
                "adminMode",
                "healthState",
                "controlMode",
                "simulationMode",
                "testMode",
                "longRunningCommandsInQueue",
                "longRunningCommandIDsInQueue",
                "longRunningCommandStatus",
                "longRunningCommandProgress",
                "longRunningCommandResult",
            ]:
                self.set_change_event(attribute_name, True)
                self.set_archive_event(attribute_name, True)

            try:
                # create Tango Groups dict, according to property
                self.logger.debug(f"Groups definitions: {self.GroupDefinitions}")
                self.groups = get_groups_from_json(self.GroupDefinitions)
                self.logger.info(f"Groups loaded: {sorted(self.groups.keys())}")
            except GroupDefinitionsError:
                self.logger.debug(f"No Groups loaded for device: {self.get_name()}")

            self._init_state_model()

            self.component_manager = self.create_component_manager()
            self.op_state_model.perform_action("init_invoked")
            self.InitCommand(
                self,
                logger=self.logger,
            )()

            self.init_command_objects()
        except Exception as exc:  # pylint: disable=broad-except
            # Deliberately catching all exceptions here, because an uncaught
            # exception would take our execution thread down.
            if hasattr(self, "logger"):
                self.logger.exception("init_device() failed.")
            else:
                traceback.print_exc()
                print(f"ERROR: init_device failed, and no logger: {exc}.")
            self._update_state(
                DevState.FAULT,
                "The device is in FAULT state - init_device failed.",
            )

    def _init_state_model(self: SKABaseDevice[ComponentManagerT]) -> None:
        """Initialise the state model for the device."""
        self._command_tracker = CommandTracker(
            queue_changed_callback=self._update_commands_in_queue,
            status_changed_callback=self._update_command_statuses,
            progress_changed_callback=self._update_command_progresses,
            result_callback=self._update_command_result,
            exception_callback=self._update_command_exception,
        )
        self.op_state_model = OpStateModel(
            logger=self.logger,
            callback=self._update_state,
        )
        self.admin_mode_model = AdminModeModel(
            logger=self.logger, callback=self._update_admin_mode
        )

    def set_logging_level(
        self: SKABaseDevice[ComponentManagerT], value: LoggingLevel
    ) -> None:
        """
        Set the logging level for the device.

        Both the Python logger and the Tango logger are updated.

        :param value: Logging level for logger

        :raises LoggingLevelError: for invalid value
        """
        try:
            lmc_logging_level = LoggingLevel(value)
        except ValueError as value_error:
            raise LoggingLevelError(
                f"Invalid level - {value} - must be one of "
                f"{list(LoggingLevel.__members__.values())} "
            ) from value_error
        self._logging_level = lmc_logging_level
        self.logger.setLevel(_LMC_TO_PYTHON_LOGGING_LEVEL[lmc_logging_level])
        self.logger.tango_logger.set_level(  # type: ignore[attr-defined]
            _LMC_TO_TANGO_LOGGING_LEVEL[lmc_logging_level]
        )
        self.logger.info(
            "Logging level set to %s on Python and Tango loggers", lmc_logging_level
        )

    def set_logging_targets(
        self: SKABaseDevice[ComponentManagerT], targets: list[str]
    ) -> None:
        """
        Set the additional logging targets for the device.

        Note that this excludes the handlers provided by the ska_ser_logging
        library defaults.

        :param targets: Logging targets for logger
        """
        device_name = self.get_name()
        valid_targets = LoggingUtils.sanitise_logging_targets(targets, device_name)
        LoggingUtils.update_logging_handlers(valid_targets, self.logger)

    def create_component_manager(
        self: SKABaseDevice[ComponentManagerT],
    ) -> ComponentManagerT:
        """
        Create and return a component manager for this device.

        :raises NotImplementedError: for no implementation
        """
        raise NotImplementedError(
            "SKABaseDevice is abstract; implement 'create_component_manager` method in "
            "a subclass."
        )

    def register_command_object(
        self: SKABaseDevice[ComponentManagerT],
        command_name: str,
        command_object: FastCommand[Any] | SlowCommand[Any],
    ) -> None:
        """
        Register an object as a handler for a command.

        :param command_name: name of the command for which the object is
            being registered
        :param command_object: the object that will handle invocations
            of the given command
        """
        self._command_objects[command_name] = command_object

    def get_command_object(
        self: SKABaseDevice[ComponentManagerT], command_name: str
    ) -> FastCommand[Any] | SlowCommand[Any]:
        """
        Return the command object (handler) for a given command.

        :param command_name: name of the command for which a command
            object (handler) is sought

        :return: the registered command object (handler) for the command
        """
        return self._command_objects[command_name]

    def init_command_objects(self: SKABaseDevice[ComponentManagerT]) -> None:
        """Register command objects (handlers) for this device's commands."""
        self._command_objects: dict[str, FastCommand[Any] | SlowCommand[Any]] = {}

        for command_name, method_name in [
            ("Off", "off"),
            ("Standby", "standby"),
            ("On", "on"),
            ("Reset", "reset"),
        ]:
            self.register_command_object(
                command_name,
                SubmittedSlowCommand(
                    command_name,
                    self._command_tracker,
                    self.component_manager,
                    method_name,
                    logger=None,
                ),
            )

        self.register_command_object(
            "AbortCommands",
            self.AbortCommandsCommand(self.component_manager, self.logger),
        )
        self.register_command_object(
            "CheckLongRunningCommandStatus",
            self.CheckLongRunningCommandStatusCommand(
                self._command_tracker, self.logger
            ),
        )
        self.register_command_object(
            "DebugDevice",
            self.DebugDeviceCommand(self, logger=self.logger),
        )

    # ----------
    # Attributes
    # ----------

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype="str"
    )
    def buildState(self: SKABaseDevice[ComponentManagerT]) -> str:
        """
        Read the Build State of the device.

        :return: the build state of the device
        """
        return self._build_state

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype="str"
    )
    def versionId(self: SKABaseDevice[ComponentManagerT]) -> str:
        """
        Read the Version Id of the device.

        :return: the version id of the device
        """
        return self._version_id

    @attribute(dtype=LoggingLevel)
    def loggingLevel(self: SKABaseDevice[ComponentManagerT]) -> LoggingLevel:
        """
        Read the logging level of the device.

        Initialises to LoggingLevelDefault on startup.
        See :py:class:`~ska_control_model.LoggingLevel`

        :return:  Logging level of the device.
        """
        return self._logging_level

    @loggingLevel.write  # type: ignore[no-redef]
    def loggingLevel(
        self: SKABaseDevice[ComponentManagerT], value: LoggingLevel
    ) -> None:
        """
        Set the logging level for the device.

        Both the Python logger and the Tango logger are updated.

        :param value: Logging level for logger
        """
        self.set_logging_level(value)

    @attribute(dtype=("str",), max_dim_x=4)
    def loggingTargets(self: SKABaseDevice[ComponentManagerT]) -> list[str]:
        """
        Read the additional logging targets of the device.

        Note that this excludes the handlers provided by the ska_ser_logging
        library defaults - initialises to LoggingTargetsDefault on startup.

        :return:  Logging level of the device.
        """
        return [str(handler.name) for handler in self.logger.handlers]

    @loggingTargets.write  # type: ignore[no-redef]
    def loggingTargets(
        self: SKABaseDevice[ComponentManagerT], value: list[str]
    ) -> None:
        """
        Set the additional logging targets for the device.

        Note that this excludes the handlers provided by the ska_ser_logging
        library defaults.

        :param value: Logging targets for logger
        """
        self.set_logging_targets(value)

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=HealthState
    )
    def healthState(self: SKABaseDevice[ComponentManagerT]) -> HealthState:
        """
        Read the Health State of the device.

        It interprets the current device condition and condition of
        all managed devices to set this. Most possibly an aggregate attribute.

        :return: Health State of the device
        """
        return self._health_state

    @attribute(dtype=AdminMode, memorized=True, hw_memorized=True)
    def adminMode(self: SKABaseDevice[ComponentManagerT]) -> AdminMode:
        """
        Read the Admin Mode of the device.

        It may interpret the current device condition and condition of all managed
         devices to set this. Most possibly an aggregate attribute.

        :return: Admin Mode of the device
        """
        return self._admin_mode

    @adminMode.write  # type: ignore[no-redef]
    def adminMode(self: SKABaseDevice[ComponentManagerT], value: AdminMode) -> None:
        """
        Set the Admin Mode of the device.

        :param value: Admin Mode of the device.

        :raises ValueError: for unknown adminMode
        """
        if value == AdminMode.NOT_FITTED:
            self.admin_mode_model.perform_action("to_notfitted")
        elif value == AdminMode.OFFLINE:
            self.admin_mode_model.perform_action("to_offline")
            self.component_manager.stop_communicating()
        elif value == AdminMode.MAINTENANCE:
            self.admin_mode_model.perform_action("to_maintenance")
            self.component_manager.start_communicating()
        elif value == AdminMode.ONLINE:
            self.admin_mode_model.perform_action("to_online")
            self.component_manager.start_communicating()
        elif value == AdminMode.RESERVED:
            self.admin_mode_model.perform_action("to_reserved")
        else:
            raise ValueError(f"Unknown adminMode {value}")

    @attribute(dtype=ControlMode, memorized=True, hw_memorized=True)
    def controlMode(self: SKABaseDevice[ComponentManagerT]) -> ControlMode:
        """
        Read the Control Mode of the device.

        The control mode of the device are REMOTE, LOCAL
        Tango Device accepts only from a ‘local’ client and ignores commands and
        queries received from TM or any other ‘remote’ clients. The Local clients
        has to release LOCAL control before REMOTE clients can take control again.

        :return: Control Mode of the device
        """
        return self._control_mode

    @controlMode.write  # type: ignore[no-redef]
    def controlMode(self: SKABaseDevice[ComponentManagerT], value: ControlMode) -> None:
        """
        Set the Control Mode of the device.

        :param value: Control mode value
        """
        self._control_mode = value

    @attribute(dtype=SimulationMode, memorized=True, hw_memorized=True)
    def simulationMode(self: SKABaseDevice[ComponentManagerT]) -> SimulationMode:
        """
        Read the Simulation Mode of the device.

        Some devices may implement
        both modes, while others will have simulators that set simulationMode
        to True while the real devices always set simulationMode to False.

        :return: Simulation Mode of the device.
        """
        return self._simulation_mode

    @simulationMode.write  # type: ignore[no-redef]
    def simulationMode(
        self: SKABaseDevice[ComponentManagerT], value: SimulationMode
    ) -> None:
        """
        Set the Simulation Mode of the device.

        :param value: SimulationMode
        """
        self._simulation_mode = value

    @attribute(dtype=TestMode, memorized=True, hw_memorized=True)
    def testMode(self: SKABaseDevice[ComponentManagerT]) -> TestMode:
        """
        Read the Test Mode of the device.

        Either no test mode or an indication of the test mode.

        :return: Test Mode of the device
        """
        return self._test_mode

    @testMode.write  # type: ignore[no-redef]
    def testMode(self: SKABaseDevice[ComponentManagerT], value: TestMode) -> None:
        """
        Set the Test Mode of the device.

        :param value: Test Mode
        """
        self._test_mode = value

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=("str",), max_dim_x=MAX_REPORTED_QUEUED_COMMANDS
    )
    def longRunningCommandsInQueue(self: SKABaseDevice[ComponentManagerT]) -> list[str]:
        """
        Read the long running commands in the queue.

         Keep track of which commands are in the queue.
         Pop off from front as they complete.

        :return: tasks in the queue
        """
        return self._commands_in_queue

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=("str",), max_dim_x=MAX_REPORTED_QUEUED_COMMANDS
    )
    def longRunningCommandIDsInQueue(
        self: SKABaseDevice[ComponentManagerT],
    ) -> list[str]:
        """
        Read the IDs of the long running commands in the queue.

        Every client that executes a command will receive a command ID as response.
        Keep track of IDs in the queue. Pop off from front as they complete.

        :return: unique ids for the enqueued commands
        """
        return self._command_ids_in_queue

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=("str",), max_dim_x=MAX_REPORTED_CONCURRENT_COMMANDS * 2  # 2 per command
    )
    def longRunningCommandStatus(self: SKABaseDevice[ComponentManagerT]) -> list[str]:
        """
        Read the status of the currently executing long running commands.

        ID, status pair of the currently executing command.
        Clients can subscribe to on_change event and wait for the
        ID they are interested in.

        :return: ID, status pairs of the currently executing commands
        """
        return self._command_statuses

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=("str",), max_dim_x=MAX_REPORTED_CONCURRENT_COMMANDS * 2  # 2 per command
    )
    def longRunningCommandProgress(self: SKABaseDevice[ComponentManagerT]) -> list[str]:
        """
        Read the progress of the currently executing long running command.

        ID, progress of the currently executing command.
        Clients can subscribe to on_change event and wait
        for the ID they are interested in.

        :return: ID, progress of the currently executing command.
        """
        return self._command_progresses

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=("str",),
        max_dim_x=2,  # Always the last result (unique_id, JSON-encoded result)
    )
    def longRunningCommandResult(
        self: SKABaseDevice[ComponentManagerT],
    ) -> tuple[str, str]:
        """
        Read the result of the completed long running command.

        Reports unique_id, json-encoded result.
        Clients can subscribe to on_change event and wait for
        the ID they are interested in.

        :return: ID, result.
        """
        return self._command_result

    # --------
    # Commands
    # --------
    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out=("str",)
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def GetVersionInfo(self: SKABaseDevice[ComponentManagerT]) -> list[str]:
        """
        Return the version information of the device.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: The result code and the command unique ID
        """
        return [f"{self.__class__.__name__}, {self._build_state}"]

    def is_Reset_allowed(self: SKABaseDevice[ComponentManagerT]) -> bool:
        """
        Return whether the `Reset` command may be called in the current device state.

        :return: whether the command may be called in the current device
            state
        """
        return self.get_state() in [
            DevState.STANDBY,
            DevState.ON,
            DevState.FAULT,
        ]

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarLongStringArray"
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def Reset(self: SKABaseDevice[ComponentManagerT]) -> DevVarLongStringArrayType:
        """
        Reset the device.

        To modify behaviour for this command, modify the do() method of
        the command class.

        For a device that directly monitors and controls hardware, this
        command should put that hardware into a known state, for example
        by clearing buffers and loading default values into registers,
        or if necessary even by power-cycling and re-initialising the
        hardware.

        Logical devices should generally implement this command to
        perform a sensible reset of that logical device. For example,
        aborting any current activities and clearing internal state.

        `Reset` generally should not change the power state of the
        device or its hardware:

        * If invoking `Reset()` from `STANDBY` state, the device would
          usually be expected to remain in `STANDBY`.
        * If invoking `Reset()` from `ON` state, the device would
          usually be expected to remain in `ON`.
        * If invoking `Reset()` from `FAULT` state, the device would
          usually be expected to transition to `ON` or remain in
          `FAULT`, depending on whether the reset was successful in
          clearing then fault.

        `Reset` generally should *not* propagate to subservient devices.
        For example, a subsystem controller device should implement
        `Reset` to reset the subsystem as a whole, but that probably
        should not result in all of the subsystem's hardware being
        power-cycled.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        """
        handler = self.get_command_object("Reset")
        result_code, unique_id = handler()
        return ([result_code], [unique_id])

    def is_Standby_allowed(self: SKABaseDevice[ComponentManagerT]) -> bool:
        """
        Return whether the `Standby` command may be called in the current device state.

        :return: whether the command may be called in the current device
            state
        """
        return self.get_state() in [
            DevState.OFF,
            DevState.STANDBY,
            DevState.ON,
            DevState.UNKNOWN,
        ]

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarLongStringArray"
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def Standby(self: SKABaseDevice[ComponentManagerT]) -> DevVarLongStringArrayType:
        """
        Put the device into standby mode.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        """
        if self.get_state() == DevState.STANDBY:
            return ([ResultCode.REJECTED], ["Device is already in STANDBY state."])

        handler = self.get_command_object("Standby")
        result_code, unique_id = handler()
        return ([result_code], [unique_id])

    def is_Off_allowed(self: SKABaseDevice[ComponentManagerT]) -> bool:
        """
        Return whether the `Off` command may be called in the current device state.

        :return: whether the command may be called in the current device
            state
        """
        return self.get_state() in [
            DevState.OFF,
            DevState.STANDBY,
            DevState.ON,
            DevState.UNKNOWN,
            DevState.FAULT,
        ]

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarLongStringArray"
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def Off(self: SKABaseDevice[ComponentManagerT]) -> DevVarLongStringArrayType:
        """
        Turn the device off.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        """
        if self.get_state() == DevState.OFF:
            return ([ResultCode.REJECTED], ["Device is already in OFF state."])

        handler = self.get_command_object("Off")
        result_code, unique_id = handler()

        return ([result_code], [unique_id])

    def is_On_allowed(self: SKABaseDevice[ComponentManagerT]) -> bool:
        """
        Return whether the `On` command may be called in the current device state.

        :return: whether the command may be called in the current device
            state
        """
        return self.get_state() in [
            DevState.OFF,
            DevState.STANDBY,
            DevState.ON,
            DevState.UNKNOWN,
        ]

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarLongStringArray"
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def On(self: SKABaseDevice[ComponentManagerT]) -> DevVarLongStringArrayType:
        """
        Turn device on.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        """
        if self.get_state() == DevState.ON:
            return ([ResultCode.REJECTED], ["Device is already in ON state."])

        handler = self.get_command_object("On")
        result_code, unique_id = handler()
        return ([result_code], [unique_id])

    class AbortCommandsCommand(SlowCommand[tuple[ResultCode, str]]):
        """The command class for the AbortCommand command."""

        def __init__(
            self: SKABaseDevice.AbortCommandsCommand,
            component_manager: ComponentManagerT,
            logger: logging.Logger | None = None,
        ) -> None:
            """
            Initialise a new AbortCommandsCommand instance.

            :param component_manager: contains the queue manager which
                manages the worker thread and the LRC attributes
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            """
            self._component_manager = component_manager
            super().__init__(None, logger=logger)

        def do(
            self: SKABaseDevice.AbortCommandsCommand,
            *args: Any,
            **kwargs: Any,
        ) -> tuple[ResultCode, str]:
            """
            Abort long running commands.

            Abort the currently executing LRC and remove all enqueued
            LRCs.

            :param args: positional arguments to this do method
            :param kwargs: keyword arguments to this do method

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            self._component_manager.abort_commands()
            return (ResultCode.STARTED, "Aborting commands")

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarLongStringArray"
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def AbortCommands(
        self: SKABaseDevice[ComponentManagerT],
    ) -> DevVarLongStringArrayType:
        """
        Empty out long running commands in queue.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        """
        handler = self.get_command_object("AbortCommands")
        (return_code, message) = handler()
        return ([return_code], [message])

    class CheckLongRunningCommandStatusCommand(FastCommand[str]):
        """The command class for the CheckLongRunningCommandStatus command."""

        def __init__(
            self: SKABaseDevice.CheckLongRunningCommandStatusCommand,
            command_tracker: CommandTracker,
            logger: logging.Logger | None = None,
        ) -> None:
            """
            Initialise a new CheckLongRunningCommandStatusCommand instance.

            :param command_tracker: command tracker
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            """
            self._command_tracker = command_tracker
            super().__init__(logger=logger)

        def do(
            self: SKABaseDevice.CheckLongRunningCommandStatusCommand,
            *args: Any,
            **kwargs: Any,
        ) -> str:
            """
            Determine the status of the command ID passed in, if any.

            - Check `command_result` to see if it's finished.
            - Check `command_status` to see if it's in progress
            - Check `command_ids_in_queue` to see if it's queued

            :param args: positional arguments to this do method. There
                should be only one: the command_id.
            :param kwargs: keyword arguments to this do method

            :return: The string of the TaskStatus
            """
            command_id = args[0]
            enum_status = self._command_tracker.get_command_status(command_id)
            return TaskStatus(enum_status).name

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=str, dtype_out=str
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def CheckLongRunningCommandStatus(
        self: SKABaseDevice[ComponentManagerT], argin: str
    ) -> str:
        """
        Check the status of a long running command by ID.

        :param argin: the command id

        :return: command status
        """
        handler = cast(
            Callable[[str], str],
            self.get_command_object("CheckLongRunningCommandStatus"),
        )
        return handler(argin)

    class DebugDeviceCommand(FastCommand[int]):
        # pylint: disable=protected-access  # command classes are friend classes
        """A class for the SKABaseDevice's DebugDevice() command."""

        def __init__(
            self: SKABaseDevice.DebugDeviceCommand,
            device: Device,
            logger: logging.Logger | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param device: the device to which this command belongs.
            :param logger: a logger for this command to use.
            """
            self._device = device
            super().__init__(logger)

        def do(
            self: SKABaseDevice.DebugDeviceCommand,
            *args: Any,
            **kwargs: Any,
        ) -> int:
            """
            Stateless hook for device DebugDevice() command.

            Starts the ``debugpy`` debugger listening for remote connections
            (via Debugger Adaptor Protocol), and patches all methods so that
            they can be debugged.

            If the debugger is already listening, additional execution of this
            command will trigger a breakpoint.

            :param args: positional arguments to this do method
            :param kwargs: keyword arguments to this do method

            :return: The TCP port the debugger is listening on.
            """
            if not SKABaseDevice._global_debugger_listening:
                allocated_port = self.start_debugger_and_get_port(_DEBUGGER_PORT)
                SKABaseDevice._global_debugger_listening = True
                SKABaseDevice._global_debugger_allocated_port = allocated_port
            if not self._device._methods_patched_for_debugger:
                self.monkey_patch_all_methods_for_debugger()
                self._device._methods_patched_for_debugger = True
            else:
                self.logger.warning("Triggering debugger breakpoint...")
                debugpy.breakpoint()

            return SKABaseDevice._global_debugger_allocated_port

        def start_debugger_and_get_port(
            self: SKABaseDevice.DebugDeviceCommand, port: int
        ) -> int:
            """
            Start the debugger and return the allocated port.

            :param port: port to listen on

            :return: allocated port
            """
            self.logger.warning("Starting debugger...")
            interface, allocated_port = cast(
                tuple[str, int], debugpy.listen(("0.0.0.0", port))
            )
            self.logger.warning(
                f"Debugger listening on {interface}:{allocated_port}. Performance may "
                "be degraded."
            )
            return allocated_port

        def monkey_patch_all_methods_for_debugger(
            self: SKABaseDevice.DebugDeviceCommand,
        ) -> None:
            """Monkeypatch methods that need to be patched for the debugger."""
            all_methods = self.get_all_methods()
            patched = []
            for owner, name, method in all_methods:
                if self.method_must_be_patched_for_debugger(owner, method):
                    self.patch_method_for_debugger(owner, name, method)
                    patched.append(
                        f"{owner} {method.__func__.__qualname__} in "
                        f"{method.__func__.__module__}"
                    )
            self.logger.info("Patched %s of %s methods", len(patched), len(all_methods))
            self.logger.debug("Patched methods: %s", sorted(patched))

        def get_all_methods(
            self: SKABaseDevice.DebugDeviceCommand,
        ) -> list[tuple[object, str, Any]]:
            """
            Return a list of the device's methods.

            :return: list of device methods
            """
            methods = []
            for name, method in inspect.getmembers(self._device, inspect.ismethod):
                methods.append((self._device, name, method))

            for command_object in self._device._command_objects.values():
                for name, method in inspect.getmembers(
                    command_object, inspect.ismethod
                ):
                    methods.append((command_object, name, method))
            return methods

        @staticmethod
        def method_must_be_patched_for_debugger(
            owner: object, method: MethodType
        ) -> bool:
            """
            Determine if methods are worth debugging.

            The goal is to find all the user's Python methods, but not
            the lower level PyTango device and Boost extension methods.
            The `types.FunctionType` check excludes the Boost methods.

            :param owner: owner
            :param method: the name

            :return: True if the method contains more than the skipped
                modules.
            """
            skip_module_names = [
                "tango.device_server",
                "tango.server",
                "logging",
            ]
            skip_owner_types = [SKABaseDevice.DebugDeviceCommand]
            return (
                isinstance(method.__func__, FunctionType)
                and method.__func__.__module__ not in skip_module_names
                and type(owner) not in skip_owner_types
            )

        def patch_method_for_debugger(
            self: SKABaseDevice.DebugDeviceCommand,
            owner: object,
            name: str,
            method: Callable[..., Any],
        ) -> None:
            """
            Ensure method calls trigger the debugger.

            Most methods in a device are executed by calls from threads
            spawned by the cppTango layer.  These threads are not known
            to Python, so we have to explicitly inform the debugger
            about them.

            :param owner: owner
            :param name: the name
            :param method: method
            """

            def debug_thread_wrapper(
                orig_method: Callable[..., Any], *args: Any, **kwargs: Any
            ) -> Any:
                debugpy.debug_this_thread()
                return orig_method(*args, **kwargs)

            patched_method = partial(debug_thread_wrapper, method)
            setattr(owner, name, patched_method)

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevUShort",
        doc_out="The TCP port the debugger is listening on.",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def DebugDevice(self: SKABaseDevice[ComponentManagerT]) -> int:
        """
        Enable remote debugging of this device.

        To modify behaviour for this command, modify the do() method of
        the command class: :py:class:`.DebugDeviceCommand`.

        :return: the  port the debugger is listening on
        """
        command_object = cast(Callable[[], int], self.get_command_object("DebugDevice"))
        return command_object()

    def set_state(self: SKABaseDevice[ComponentManagerT], state: DevState) -> None:
        """
        Set the device server state.

        This is dependent on whether the set state call has been
        actioned from a native python thread or a tango omni thread

        :param state: the new device state
        """
        self._submit_tango_operation("set_state", state)

    def set_status(self: SKABaseDevice[ComponentManagerT], status: str) -> None:
        """
        Set the device server status string.

        This is dependent on whether the set status call has been
        actioned from a native python thread or a tango omni thread

        :param status: the new device status
        """
        self._submit_tango_operation("set_status", status)

    def push_change_event(
        self: SKABaseDevice[ComponentManagerT], name: str, value: Any = None
    ) -> None:
        """
        Push a device server change event.

        This is dependent on whether the push_change_event call has been
        actioned from a native python thread or a tango omni thread

        :param name: the event name
        :param value: the event value
        """
        if name.lower() in ["state", "status"]:
            self._submit_tango_operation("push_change_event", name)
        else:
            self._submit_tango_operation("push_change_event", name, value)

    def push_archive_event(
        self: SKABaseDevice[ComponentManagerT], name: str, value: Any = None
    ) -> None:
        """
        Push a device server archive event.

        This is dependent on whether the push_archive_event call has
        been actioned from a native python thread or a tango omnithread.

        :param name: the event name
        :param value: the event value
        """
        if name.lower() in ["state", "status"]:
            self._submit_tango_operation("push_archive_event", name)
        else:
            self._submit_tango_operation("push_archive_event", name, value)

    def add_attribute(
        self: SKABaseDevice[ComponentManagerT], *args: Any, **kwargs: Any
    ) -> None:
        """
        Add a device attribute.

        This is dependent on whether the push_archive_event call has been
        actioned from a native python thread or a tango omni thread

        :param args: positional args
        :param kwargs: keyword args
        """
        self._submit_tango_operation("add_attribute", *args, *kwargs)

    def set_change_event(
        self: SKABaseDevice[ComponentManagerT],
        name: str,
        implemented: bool,
        detect: bool = True,
    ) -> None:
        """
        Set an attribute's change event.

        This is dependent on whether the push_archive_event call has been
        actioned from a native python thread or a tango omni thread

        :param name: name of the attribute
        :param implemented: whether the device pushes change events
        :param detect: whether the Tango layer should verify the change
            event property
        """
        self._submit_tango_operation("set_change_event", name, implemented, detect)

    def _submit_tango_operation(
        self: SKABaseDevice[ComponentManagerT],
        command_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if is_omni_thread() and self._omni_queue.empty():
            getattr(super(), command_name)(*args, **kwargs)
        else:
            self._omni_queue.put((command_name, args, kwargs))

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        polling_period=5
    )
    def ExecutePendingOperations(self: SKABaseDevice[ComponentManagerT]) -> None:
        """
        Execute any Tango operations that have been pushed on the queue.

        The poll time is initially 5ms, to circumvent the problem of
        device initialisation, but is reset to 100ms after the first
        pass.
        """
        # this can be removed when cppTango issue #935 is implemented
        if self._init_active:
            self._init_active = False
            self.poll_command("ExecutePendingOperations", 100)
        while not self._omni_queue.empty():
            (command_name, args, kwargs) = self._omni_queue.get_nowait()
            getattr(super(), command_name)(*args, **kwargs)


# ----------
# Run server
# ----------


def main(*args: str, **kwargs: str) -> int:
    """
    Entry point for module.

    :param args: positional arguments
    :param kwargs: named arguments

    :return: exit code
    """
    return cast(int, SKABaseDevice.run_server(args=args or None, **kwargs))


if __name__ == "__main__":
    main()
