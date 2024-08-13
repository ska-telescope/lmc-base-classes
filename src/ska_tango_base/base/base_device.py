# pylint: disable=invalid-name, too-many-lines
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
This module implements a generic base model and device for SKA.

It exposes the generic attributes, properties and commands of an SKA device.
"""
from __future__ import annotations

import inspect
import itertools
import json
import logging
import logging.handlers
import queue
import sys
import threading
import traceback
from enum import Enum
from functools import partial
from types import FunctionType, MethodType
from typing import Any, Callable, Generic, Iterable, TypeVar, cast
from warnings import warn

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
from tango import AttReqType, AttributeProxy, DebugIt, DevState, Except, is_omni_thread
from tango.server import Device, attribute, command, device_property

from .. import release
from ..commands import DeviceInitCommand, FastCommand, SlowCommand, SubmittedSlowCommand
from ..faults import GroupDefinitionsError, LoggingLevelError
from ..long_running_commands_api import _SUPPORTED_LRC_PROTOCOL_VERSIONS
from ..utils import get_groups_from_json
from .admin_mode_model import AdminModeModel
from .base_component_manager import BaseComponentManager
from .command_tracker import LRC_FINISHED_MAX_LENGTH, CommandTracker, LrcAttrType
from .logging import (
    _LMC_TO_PYTHON_LOGGING_LEVEL,
    _LMC_TO_TANGO_LOGGING_LEVEL,
    LoggingUtils,
)
from .op_state_model import OpStateModel

__all__ = ["SKABaseDevice", "main"]

DevVarLongStringArrayType = tuple[list[ResultCode], list[str]]
ComponentManagerT = TypeVar("ComponentManagerT", bound=BaseComponentManager)

_DEBUGGER_PORT = 5678
_MINIMUM_STATUS_QUEUE_SIZE = 32


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
        """Initialize the logging mechanism, using default properties."""  # noqa:D202

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

    # -----------
    # Init device
    # -----------
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

            self._omni_queue: queue.SimpleQueue[tuple[str, Any, Any]] = (
                queue.SimpleQueue()
            )

            # this can be removed when cppTango issue #935 is implemented
            self._init_active = True
            self.poll_command("ExecutePendingOperations", 5)

            self._init_logging()

            self._admin_mode = AdminMode.OFFLINE
            self._health_state = HealthState.UNKNOWN
            self._control_mode = ControlMode.REMOTE
            self._simulation_mode = SimulationMode.FALSE
            self._test_mode = TestMode.NONE
            self._test_mode_overrides: dict[str, Any] = {}
            self._test_mode_overrides_changed: Callable[[], None] | None = None
            self._commanded_state = "None"
            self._command_ids_in_queue: list[str] = []
            self._commands_in_queue: list[str] = []
            self._command_statuses: list[str] = []
            self._commands_ids_in_progress: list[str] = []
            self._commands_in_progress: list[str] = []
            self._command_progresses: list[str] = []
            self._command_result: tuple[str, str] = ("", "")
            self._lrc_queue: list[str] = []
            self._lrc_executing: list[str] = []
            self._lrc_finished: list[str] = []

            self._build_state = (
                f"{release.name}, {release.version}, {release.description}"
            )
            self._version_id = release.version
            self._methods_patched_for_debugger = False
            self._status_queue_size = 0

            self._init_state_model()

            self.component_manager = self.create_component_manager()
            self._create_lrc_attributes()

            for attribute_name in [
                "state",
                "commandedState",
                "status",
                "adminMode",
                "healthState",
                "controlMode",
                "simulationMode",
                "testMode",
                "longRunningCommandsInQueue",
                "longRunningCommandIDsInQueue",
                "longRunningCommandStatus",
                "longRunningCommandInProgress",
                "longRunningCommandProgress",
                "longRunningCommandResult",
                "lrcQueue",
                "lrcExecuting",
                "lrcFinished",
            ]:
                self.set_change_event(attribute_name, True)
                self.set_archive_event(attribute_name, True)
            self.set_change_event("_lrcEvent", True)

            try:
                # create Tango Groups dict, according to property
                self.logger.debug(f"Groups definitions: {self.GroupDefinitions}")
                self.groups = get_groups_from_json(self.GroupDefinitions)
                self.logger.info(f"Groups loaded: {sorted(self.groups.keys())}")
            except GroupDefinitionsError:
                self.logger.debug(f"No Groups loaded for device: {self.get_name()}")

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

    def _create_lrc_attributes(self: SKABaseDevice[ComponentManagerT]) -> None:
        """
        Create attributes for the long running commands.

        :raises AssertionError: if max_queued_tasks or max_executing_tasks is not
            equal to or greater than 0 or 1 respectively.
        """
        # For the attributes which report both queued and executing commands
        # (longRunningCommandStatus, longRunningCommandsInQueue and
        # longRunningCommandIDsInQueue), we need space for at least as many
        # commands as we can have in the queue, plus the maximum number of
        # simultaneously executing tasks. That gets us to
        # `ComponentManager.max_queued_tasks` + `ComponentManager.max_executing_tasks`.
        # However, when a command is finished (i.e one of COMPLETED, ABORTED,
        # REJECTED, FAILED) it hangs around with the LRC attributes
        # `CommandTracker._removal_time` seconds, so we need a buffer.
        # We choose a buffer of `ComponentManager.max_queued_tasks` to be able to
        # handle the situation where a client fills the queue with commands that all
        # get rejected because the command isn't allowed then queues up the correct
        # command straight after. We also have a minimum of _MINIMUM_STATUS_QUEUE_SIZE
        # for when max_queued_tasks=0, i.e. a device that doesn't allow queuing tasks,
        # because finished tasks will still hang around.
        # NB: `update_command_statuses` and `update_commands_in_queue` will prune the
        # oldest commands from the list if we reach the limit.
        assert (
            self.component_manager.max_queued_tasks >= 0
        ), "max_queued_tasks property must be equal to or greater than 0."
        assert (
            self.component_manager.max_executing_tasks >= 1
        ), "max_executing_tasks property must be equal to or greater than 1."

        max_executing_tasks = self.component_manager.max_executing_tasks
        if max_executing_tasks == 1:
            warning_msg = (
                "'max_executing_tasks' will be required to be at least 2 in a future "
                "release of ska-tango-base (found 1).  A device must support the "
                "'Abort()' command and at least one other command executing "
                "simulanteously."
            )
            warn(warning_msg, FutureWarning)
            if self.logger:
                self.logger.warning(warning_msg)

            max_executing_tasks = 2

        self._status_queue_size = max(
            self.component_manager.max_queued_tasks * 2 + max_executing_tasks,
            _MINIMUM_STATUS_QUEUE_SIZE,
        )
        # TODO: This private variable may be overridden by SKABaseDevice to support
        # a longer length of the deprecated LRC attributes, until they are removed.
        if self._status_queue_size > LRC_FINISHED_MAX_LENGTH:
            # pylint: disable=protected-access
            self._command_tracker._lrc_finished_max_length = self._status_queue_size
        self._create_attribute(
            "lrcQueue",
            self._status_queue_size,
            self.lrcQueue,
        )
        self._create_attribute(
            "lrcExecuting",
            self.component_manager.max_executing_tasks + 1,  # for Abort command
            self.lrcExecuting,
        )
        self._create_attribute(
            "longRunningCommandStatus",
            self._status_queue_size * 2,  # 2 per command
            self.longRunningCommandStatus,
        )
        self._create_attribute(
            "longRunningCommandsInQueue",
            self._status_queue_size,
            self.longRunningCommandsInQueue,
        )
        self._create_attribute(
            "longRunningCommandIDsInQueue",
            self._status_queue_size,
            self.longRunningCommandIDsInQueue,
        )
        self._create_attribute(
            "longRunningCommandInProgress",
            self.component_manager.max_executing_tasks,
            self.longRunningCommandInProgress,
        )
        self._create_attribute(
            "longRunningCommandProgress",
            max_executing_tasks * 2,  # cmd name and progress for each command
            self.longRunningCommandProgress,
        )

    def _create_attribute(
        self: SKABaseDevice[ComponentManagerT],
        name: str,
        max_dim_x: int,
        fget: Callable[[Any], None],
    ) -> None:
        attr = attribute(
            name=name,
            dtype=(str,),
            max_dim_x=max_dim_x,
            fget=fget,
        )
        self.add_attribute(attr)

    def _get_override_value(
        self: SKABaseDevice[ComponentManagerT], attr_name: str, default: Any = None
    ) -> Any:
        """
        Read a value from our overrides, use a default value when not overridden.

        Used where we use possibly-overridden internal values within the device server
        (i.e. reading member variables, not via the Tango attribute read mechanism).

        e.g.
        ``my_thing = self._get_override_value("thing", self._my_thing_true_value)``

        :param attr_name: Tango Attribute name.
        :param default: Default value to return if no override in effect.
        :returns: Active override value or ``default``.
        """
        if (
            self._test_mode != TestMode.TEST
            or attr_name not in self._test_mode_overrides
        ):
            return default
        return _override_value_convert(attr_name, self._test_mode_overrides[attr_name])

    def _init_state_model(self: SKABaseDevice[ComponentManagerT]) -> None:
        """Initialise the state model for the device."""
        self._command_tracker = CommandTracker(
            queue_changed_callback=self._update_commands_in_queue,
            status_changed_callback=self._update_command_statuses,
            progress_changed_callback=self._update_command_progresses,
            result_callback=self._update_command_result,
            exception_callback=self._log_command_exception,
            event_callback=self._update_lrc_event,
            update_user_attributes_callback=self._update_user_lrc_attributes,
        )
        self.op_state_model = OpStateModel(
            logger=self.logger,
            callback=self._update_state,
        )
        self.admin_mode_model = AdminModeModel(
            logger=self.logger, callback=self._update_admin_mode
        )

    def _prune_completed_commands(
        self: SKABaseDevice[ComponentManagerT], command_list: list[tuple[str, str]]
    ) -> list[tuple[str, str]]:
        """
        Prune a command list of any lingering completed tasks.

        :param command_list: list of (cmd_id, <info>) tuples of commands to prune
        :return: the pruned list with the oldest completed commands removed
        """
        if len(command_list) <= self._status_queue_size:
            # Nothing to do
            return command_list

        # Determine which commands have completed by looking at the
        # current command statuses
        completed_commands = [
            uid
            for (uid, status) in self._command_tracker.command_statuses
            if status.name
            in [
                TaskStatus.ABORTED.name,
                TaskStatus.COMPLETED.name,
                TaskStatus.REJECTED.name,
                TaskStatus.FAILED.name,
            ]
        ]

        # Create a pruned list by removing the oldest completed commands
        number_to_remove = len(command_list) - self._status_queue_size
        pruned_list = command_list
        prune_candidates = [
            (uid, info)
            for (uid, info) in sorted(
                command_list, key=lambda item: item[0].split(sep="_")[0]
            )
            if uid in completed_commands
        ]
        for item in prune_candidates[0:number_to_remove]:
            # This gets called many times so we
            # keep track of which ones we have already logged
            if self._command_tracker.evict_command(item[0]):
                self.logger.warning(f"Status queue too big: removing item {item[0]}")
            pruned_list.remove(item)

        return pruned_list

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
            command_ids, command_names = zip(
                *self._prune_completed_commands(commands_in_queue)
            )
            self._command_ids_in_queue = [str(command_id) for command_id in command_ids]
            self._commands_in_queue = [
                str(command_name) for command_name in command_names
            ]
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
            str(item)
            for item in itertools.chain.from_iterable(
                self._prune_completed_commands(statuses)
            )
        ]
        self.push_change_event("longRunningCommandStatus", self._command_statuses)
        self.push_archive_event("longRunningCommandStatus", self._command_statuses)

        # Check for commands starting and ending execution
        for command_id, status in command_statuses:
            if (
                status == TaskStatus.IN_PROGRESS
                and command_id not in self._commands_ids_in_progress
            ):
                self._update_commands_in_progress(command_id, True)
                self._update_commanded_state(command_id.split("_")[-1])
            elif (
                status
                in [
                    TaskStatus.ABORTED,
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                ]
                and command_id in self._commands_ids_in_progress
            ):
                self._update_commands_in_progress(command_id, False)

    def _update_commands_in_progress(
        self: SKABaseDevice[ComponentManagerT], command_id: str, in_progress: bool
    ) -> None:
        # Pass a reference to a new object for the push events, as this callback can be
        # called multiple times before the event is pushed in the tango omni thread.
        commands_ids_in_progress = self._commands_ids_in_progress.copy()
        if in_progress:
            commands_ids_in_progress.append(command_id)
        elif command_id in commands_ids_in_progress:
            commands_ids_in_progress.remove(command_id)
        self._commands_ids_in_progress = commands_ids_in_progress
        self._commands_in_progress = [
            uid.split("_")[-1] for uid in commands_ids_in_progress
        ]
        self.push_change_event(
            "longRunningCommandInProgress", self._commands_in_progress
        )
        self.push_archive_event(
            "longRunningCommandInProgress", self._commands_in_progress
        )

    def _update_commanded_state(
        self: SKABaseDevice[ComponentManagerT], command_name: str
    ) -> None:
        # Update commandedState after a SKABaseDevice command's status is 'IN_PROGRESS'
        if command_name in ["Off", "Standby", "On", "Reset"]:
            self._commanded_state = command_name.upper()
            if command_name == "Reset":
                current_state = self.get_state()
                if current_state == DevState.FAULT:
                    self._commanded_state = "ON"
                else:
                    self._commanded_state = current_state.name
            self.push_change_event("commandedState", self._commanded_state)
            self.push_archive_event("commandedState", self._commanded_state)

    def _update_command_progresses(
        self: SKABaseDevice[ComponentManagerT],
        command_progresses: list[tuple[str, int]],
    ) -> None:
        self._command_progresses = [
            str(item) for item in itertools.chain.from_iterable(command_progresses)
        ]
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

    def _update_lrc_event(
        self: SKABaseDevice[ComponentManagerT],
        command_id: str,
        event: dict[str, Any],
    ) -> None:
        self.push_change_event("_lrcEvent", [command_id, json.dumps(event)])

    def _update_user_lrc_attributes(
        self: SKABaseDevice[ComponentManagerT],
        lrc_queue: LrcAttrType,
        lrc_executing: LrcAttrType,
        lrc_finished: LrcAttrType,
    ) -> None:
        self._lrc_queue = self._get_json_list_of_lrc_attributes(
            lrc_queue,
            allowed_keys=["uid", "name", "sumbitted_time"],
        )
        self.push_change_event("lrcQueue", self._lrc_queue)
        self.push_archive_event("lrcQueue", self._lrc_queue)
        self._lrc_executing = self._get_json_list_of_lrc_attributes(
            lrc_executing,
            allowed_keys=["uid", "name", "sumbitted_time", "started_time", "progress"],
        )
        self.push_change_event("lrcExecuting", self._lrc_executing)
        self.push_archive_event("lrcExecuting", self._lrc_executing)
        self._lrc_finished = self._get_json_list_of_lrc_attributes(
            lrc_finished,
            allowed_keys=[
                "uid",
                "name",
                "sumbitted_time",
                "started_time",
                "finished_time",
                "status",
                "result",
                "progress",
            ],
        )[
            -LRC_FINISHED_MAX_LENGTH:
        ]  # TODO: The passed dict should be the correct max length in future after the
        #          deprecated LRC attributes have been removed.
        self.push_change_event("lrcFinished", self._lrc_finished)
        self.push_archive_event("lrcFinished", self._lrc_finished)

    def _log_command_exception(
        self: SKABaseDevice[ComponentManagerT],
        command_id: str,
        command_exception: Exception,
    ) -> None:
        if isinstance(command_exception, Exception):
            exc_info = command_exception
            message = (
                f"Command '{command_id}' raised exception with args "
                f"'{command_exception}'"
            )
        else:
            self.logger.warning(
                f"command_exception is not an Exception. Found {command_exception!r}."
            )
            # Add exc_info if we are in an "except:" block
            exc_info = sys.exc_info() != (None, None, None)
            message = f"Command '{command_id}' failed: {command_exception}"
        self.logger.error(message, exc_info=exc_info, stack_info=True)

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
            "Abort",
            self.AbortCommand(
                self._command_tracker, self.component_manager, None, self.logger
            ),
        )
        # TODO: Deprecated command, remove in future release
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

    @staticmethod
    def _get_json_list_of_lrc_attributes(
        lrc_attr: LrcAttrType, allowed_keys: list[str]
    ) -> list[str]:
        """
        Get a list of JSON formatted strings representing the LRC attribute.

        Serialises each key-value pair that's in the allowed_keys list of the LRC's data
        dict to a flat JSON dict.

        :param lrc_attr: Dict of LRC IDs as keys and their nested CommandData dicts.
        :param allowed_keys: List of allowed keys to include from the JSON dicts.
        :return: A list of JSON strings containing a serialised info dict for each LRC.
        """
        if lrc_attr:  # Check for empty dict
            return [
                json.dumps(
                    {
                        "uid": command_id,
                        **{
                            key: val.name if isinstance(val, Enum) else val
                            for key, val in data.items()
                            if key in allowed_keys
                        },
                    }
                )
                for command_id, data in lrc_attr.items()
            ]
        return []

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
        elif value == AdminMode.ENGINEERING:
            self.admin_mode_model.perform_action("to_engineering")
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

        Reset our test mode override values when leaving test mode.

        :param value: Test Mode
        """
        if value == TestMode.NONE:
            overrides_being_removed = list(self._test_mode_overrides.keys())
            self._test_mode_overrides = {}
            self._push_events_overrides_removed(overrides_being_removed)
            # call downstream callback function to deal with override changes
            if self._test_mode_overrides_changed is not None:
                self._test_mode_overrides_changed()

        self._test_mode = value

    @attribute(
        dtype=str,
        doc="Attribute value overrides (JSON dict)",
    )  # type: ignore[misc]
    def test_mode_overrides(self: SKABaseDevice[ComponentManagerT]) -> str:
        """
        Read the current override configuration.

        :return: JSON-encoded dictionary (attribute name: value)
        """
        return json.dumps(self._test_mode_overrides)

    # TODO @test_mode_overrides.is_allowed looks nice, check if it works here
    def is_test_mode_overrides_allowed(
        self: SKABaseDevice[ComponentManagerT], request_type: AttReqType
    ) -> bool:
        """
        Control access to test_mode_overrides attribute.

        Writes to the attribute are allowed only if test mode is active.

        :param request_type: Attribute request type
        :returns: If in test mode
        """
        if request_type == AttReqType.READ_REQ:
            return True
        return self._test_mode == TestMode.TEST

    @test_mode_overrides.write  # type: ignore[no-redef, misc]
    def test_mode_overrides(
        self: SKABaseDevice[ComponentManagerT], value_str: str
    ) -> None:
        """
        Write new override configuration.

        :param value_str: JSON-encoded dict of overrides (attribute name: value)
        """
        value_dict = json.loads(value_str)
        assert isinstance(value_dict, dict), "expected JSON-encoded dict"
        overrides_being_removed = self._test_mode_overrides.keys() - value_dict.keys()
        # we could call _override_value_convert on incoming values here, but I prefer to
        # leave as-is, so the user can read back the same thing they wrote in
        self._test_mode_overrides = value_dict
        self._push_events_overrides_removed(overrides_being_removed)

        # send events for all overrides
        # only *need* to send new or changed overrides but that's annoying to determine
        # i.e. premature optimisation
        for attr_name, value in value_dict.items():
            value = _override_value_convert(attr_name, value)
            attr_cfg = self.get_device_attr().get_attr_by_name(attr_name)
            if attr_cfg.is_change_event():
                self.push_change_event(attr_name, value)
            if attr_cfg.is_archive_event():
                self.push_archive_event(attr_name, value)

        # call downstream callback function to deal with override changes
        if self._test_mode_overrides_changed is not None:
            self._test_mode_overrides_changed()

    def _push_events_overrides_removed(
        self: SKABaseDevice[ComponentManagerT], attrs_to_refresh: Iterable[str]
    ) -> None:
        """
        Push true value events for attributes that were previously overridden.

        :param attrs_to_refresh: Names of our attributes that are no longer overridden
        """
        for attr_name in attrs_to_refresh:
            # Read configuration of attribute
            attr_cfg = self.get_device_attr().get_attr_by_name(attr_name)
            manual_event = attr_cfg.is_change_event() or attr_cfg.is_archive_event()

            if not manual_event:
                continue

            # Read current state of attribute
            attr = AttributeProxy(f"{self.get_name()}/{attr_name}").read()
            if attr_cfg.is_change_event():
                self.push_change_event(attr_name, attr.value, attr.time, attr.quality)
            if attr_cfg.is_archive_event():
                self.push_archive_event(attr_name, attr.value, attr.time, attr.quality)

    # ---------------------
    # Long Running Commands
    # ---------------------
    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=("int",), max_dim_x=2
    )
    def lrcProtocolVersions(
        self: SKABaseDevice[ComponentManagerT],
    ) -> tuple[int, int]:
        """
        Return supported protocol versions.

        :return: A tuple containing the lower and upper bounds of supported long running
            command protocol versions.
        """
        return _SUPPORTED_LRC_PROTOCOL_VERSIONS

    # The following LRC attributes are instantiated in init_device() to make use of the
    # max_queued_tasks and max_executing_tasks properties to compute their max_dim_x

    def lrcQueue(self: SKABaseDevice[ComponentManagerT], attr: attribute) -> None:
        """
        Read info of the long running commands in queue.

        Returns a list of info JSON blobs of the commands in queue.

        :param attr: Tango attribute being read
        """
        attr.set_value(self._lrc_queue)

    def lrcExecuting(self: SKABaseDevice[ComponentManagerT], attr: attribute) -> None:
        """
        Read info of the currently executing long running commands.

        Returns a list of info JSON blobs of the currently executing commands.

        :param attr: Tango attribute being read
        """
        attr.set_value(self._lrc_executing)

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=("str",), max_dim_x=LRC_FINISHED_MAX_LENGTH
    )
    def lrcFinished(self: SKABaseDevice[ComponentManagerT]) -> list[str]:
        """
        Read info of the finished long running commands.

        :return: a list of info JSON blobs of the finished long running commands.
        """
        return self._lrc_finished

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=("str",), max_dim_x=2
    )
    def _lrcEvent(self: SKABaseDevice[ComponentManagerT]) -> list[str]:
        """
        Read the long running commands events. Always returns an empty list.

        :return: empty list.
        """
        return []

    def longRunningCommandsInQueue(
        self: SKABaseDevice[ComponentManagerT], attr: attribute
    ) -> None:
        """
        Read the long running commands in the queue.

        Keep track of which commands are that are currently known about.
        Entries are removed `self._command_tracker._removal_time` seconds
        after they have finished.

        :param attr: Tango attribute being read
        """
        attr.set_value(self._commands_in_queue)

    def longRunningCommandIDsInQueue(
        self: SKABaseDevice[ComponentManagerT], attr: attribute
    ) -> None:
        """
        Read the IDs of the long running commands in the queue.

        Every client that executes a command will receive a command ID as response.
        Keep track of IDs currently allocated.
        Entries are removed `self._command_tracker._removal_time` seconds
        after they have finished.

        :param attr: Tango attribute being read
        """
        attr.set_value(self._command_ids_in_queue)

    def longRunningCommandStatus(
        self: SKABaseDevice[ComponentManagerT],
        attr: attribute,
    ) -> None:
        """
        Read the status of the currently executing long running commands.

        ID, status pairs of the currently executing commands.
        Clients can subscribe to on_change event and wait for the
        ID they are interested in.

        :param attr: Tango attribute being read
        """
        attr.set_value(self._command_statuses)

    def longRunningCommandInProgress(
        self: SKABaseDevice[ComponentManagerT],
        attr: attribute,
    ) -> None:
        """
        Read the name(s) of the currently executing long running command(s).

        Name(s) of command and possible abort in progress or empty string(s).
        :param attr: Tango attribute being read
        """
        attr.set_value(self._commands_in_progress)

    def longRunningCommandProgress(
        self: SKABaseDevice[ComponentManagerT], attr: attribute
    ) -> None:
        """
        Read the progress of the currently executing long running command(s).

        ID, progress of the currently executing command(s).
        Clients can subscribe to on_change event and wait
        for the ID they are interested in.

        :param attr: Tango attribute being read
        """
        attr.set_value(self._command_progresses)

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

    @attribute(dtype=str)  # type: ignore[misc]
    def commandedState(self: SKABaseDevice[ComponentManagerT]) -> str:
        """
        Read the last commanded operating state of the device.

        Initial string is "None". Only other strings it can change to is "OFF",
        "STANDBY" or "ON", following the start of the Off(), Standby(), On() or Reset()
        long running commands.

        :return: commanded operating state string.
        """
        return self._commanded_state

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

    class AbortCommand(SlowCommand[tuple[ResultCode, str]]):
        """A class for SKASubarray's Abort() command."""

        def __init__(
            self: SKABaseDevice.AbortCommand,
            command_tracker: CommandTracker,
            component_manager: BaseComponentManager,
            callback: Callable[[bool], None] | None,
            logger: logging.Logger | None = None,
        ) -> None:
            """
            Initialise a new AbortCommand instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: callback to be called when this command
                starts and finishes
            :param logger: a logger for this command object to use
            """
            self._command_tracker = command_tracker
            self._component_manager = component_manager
            super().__init__(callback=callback, logger=logger)

        def do(
            self: SKABaseDevice.AbortCommand,
            *args: Any,
            **kwargs: Any,
        ) -> tuple[ResultCode, str]:
            """
            Stateless hook for Abort() command functionality.

            :param args: positional arguments to the command. This
                command does not take any, so this should be empty.
            :param kwargs: keyword arguments to the command. This
                command does not take any, so this should be empty.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            command_id = self._command_tracker.new_command(
                "Abort", completed_callback=self._completed
            )
            status, _ = self._component_manager.abort(
                partial(self._command_tracker.update_command_info, command_id)
            )
            assert status == TaskStatus.IN_PROGRESS

            return ResultCode.STARTED, command_id

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarLongStringArray"
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def Abort(self: SKABaseDevice[ComponentManagerT]) -> DevVarLongStringArrayType:
        """
        Abort any executing long running command(s) and empty the queue.

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("Abort")
        (result_code, message) = handler()
        return ([result_code], [message])

    # TODO: Deprecated command, remove in future release
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
            self._abort_commands_overriden = False
            if (
                type(component_manager).abort_commands
                != BaseComponentManager.abort_commands
            ):
                self._abort_commands_overriden = True
                warning_msg = (
                    "'abort_commands' is deprecated and will be removed in the "
                    "next major release. Either rename 'abort_commands' in your "
                    "component manager to 'abort_tasks' or override the "
                    "'SKABaseDevice.Abort' command instead."
                )
                warn(warning_msg, DeprecationWarning)
                if logger:
                    logger.warning(warning_msg)
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
            if self._abort_commands_overriden:
                self._component_manager.abort_commands()
            else:
                self._component_manager.abort_tasks()
            return (ResultCode.STARTED, "Aborting commands")

    # TODO: Deprecated command, remove in future release
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
        warning_msg = (
            "'AbortCommands' is deprecated and will be removed in the next major "
            "release. The client should call the tracked 'Abort' long running command "
            "instead."
        )
        warn(warning_msg, DeprecationWarning)
        self.logger.warning(warning_msg)
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
        self: SKABaseDevice[ComponentManagerT], name: str, *args: Any
    ) -> None:
        # pylint: disable=line-too-long
        """
        Push a device server change event.

        This is dependent on whether the push_change_event call has been
        actioned from a native python thread or a tango omni thread

        This is an "overloaded" function which can be called with
        multiple signatures supported.  These are dispatched based on
        the types passed.

        In the overloads below `Scalar` refers to any data type that can be
        converted to a tango scalar. `Any` refers to
        `Scalar | Sequence[Scalar] | Sequence[Sequence[Scalar]]`.

        - push_change_event(self, name: str)

            Push a device server change event for the "state" or "status".

            Raises a tango.DevFailed if name is not "state" or "status".

        - push_change_event(self, name: str, expection: DevFailed)

            Push a device server change event for an attribute with
            an exception.

            exception: exception to send to client

        - push_change_event(self, name: str, data: Any)

            Push a device server change event for an attribute.

            data: value to send to client

        - push_change_event(self, name: str, data: Sequence[Scalar], dim_x: int)

            Push a device server change event for a spectrum attribute with truncation.

            A copy of `data` will be truncated before being sent to clients.

            Requires `dim_x <= len(data)`.

            data: value to send to client
            dim_x: length to truncate value to

        - push_change_event(self, name: str, data: Sequence[Scalar], dim_x: int, dim_y: int)

            Push a device server change event for a image attribute with reshaping.

            A copy of `data` will be reshaped to `(dim_x, dim_y)` before being
            sent to clients.

            Note that `data` must be flat.

            Requires `dim_x * dim_y <= len(data)`.

            data: value to send to client
            dim_x: x dimension to reshape to
            dim_y: y dimension to reshape to

        - push_change_event(self, name: str, str_data: str, data: bytes | str)

            Push a device server change event for an encoded attribute.

            str_data: encoding format for data
            data: encoded data to send

        - push_change_event(self, name: str, data: Any, timestamp: float, quality: tango.AttrQuality)

            Push a device server change event for an attribute with timestamp
            and quality.

            data: value to send
            timestamp: unix timestamp
            quality: quality of attribute

        - push_change_event(self, name: str, data: Sequence[Scalar], timestamp: float, quality: tango.AttrQuality, dim_x: int)

            Push a device server change event for a spectrum attribute with truncation,
            timestamp and quality.

            A copy of `data` will be truncated before being sent to clients.

            Requires `dim_x <= len(data)`.

            data: value to send
            timestamp: unix timestamp
            quality: quality of attribute
            dim_x: length to truncate value to

        - push_change_event(self, name: str, data: Scalar, timestamp: float, quality: tango.AttrQuality, dim_x: int, dim_y: int)

            Push a device server change event for a image attribute with reshaping,
            timestampe and quality.

            A copy of `data` will be reshaped to `(dim_x, dim_y)` before being
            sent to clients.

            Note that `data` must be flat.

            Requires `dim_x * dim_y <= len(data)`.

            data: value to send
            timestamp: unix timestamp
            quality: quality of attribute
            dim_x: x dimension to reshape to
            dim_y: y dimension to reshape to

        - push_change_event(self, name: str, str_data: str, data: bytes | str, timestamp: double, quality: tango.AttrQuality)

            Push a device server change event for a encoded attribute with timestamp
            and quality.

            str_data: encoding format for data
            data: encoded data to send
            timestamp: unix timestamp
            quality: quality of attribute

        :param name: the attribute name
        :param args: the arguments to dispatch on
        """  # noqa: E501
        self._submit_tango_operation("push_change_event", name, *args)

    def push_archive_event(
        self: SKABaseDevice[ComponentManagerT], name: str, *args: Any
    ) -> None:
        # pylint: disable=line-too-long
        """
        Push a device server archive event.

        This is dependent on whether the push_archive_event call has
        been actioned from a native python thread or a tango omnithread.

        This is an "overloaded" function which can be called with
        multiple signatures supported.  These are dispatched based on
        the types passed.

        In the overloads below `Scalar` refers to any data type that can be
        converted to a tango scalar. `Any` refers to
        `Scalar | Sequence[Scalar] | Sequence[Sequence[Scalar]]`.

        - push_archive_event(self, name: str)

            Push a device server archive event for the "state" or "status".

            Raises a DevFailed if name is not "state" or "status".

        - push_archive_event(self, name: str, expection: DevFailed)

            Push a device server archive event for an attribute with
            an exception.

            exception: exception to send to client

        - push_archive_event(self, name: str, data: Any)

            Push a device server archive event for an attribute.

            data: value to send to client

        - push_archive_event(self, name: str, data: Sequence[Scalar], dim_x: int)

            Push a device server archive event for a spectrum attribute with truncation.

            A copy of `data` will be truncated before being sent to clients.

            Requires `dim_x <= len(data)`.

            data: value to send to client
            dim_x: length to truncate value to

        - push_archive_event(self, name: str, data: Sequence[Scalar], dim_x: int, dim_y: int)

            Push a device server archive event for a image attribute with reshaping.

            A copy of `data` will be reshaped to `(dim_x, dim_y)` before being
            sent to clients.

            Note that `data` must be flat.

            Requires `dim_x * dim_y <= len(data)`.

            data: value to send to client
            dim_x: x dimension to reshape to
            dim_y: y dimension to reshape to

        - push_archive_event(self, name: str, str_data: str, data: bytes | str)

            Push a device server archive event for an encoded attribute.

            str_data: encoding format for data
            data: encoded data to send

        - push_archive_event(self, name: str, data: Any, timestamp: float, quality: tango.AttrQuality)

            Push a device server archive event for an attribute with timestamp
            and quality.

            data: value to send
            timestamp: unix timestamp
            quality: quality of attribute

        - push_archive_event(self, name: str, data: Sequence[Scalar], timestamp: float, quality: tango.AttrQuality, dim_x: int)

            Push a device server archive event for a spectrum attribute with truncation,
            timestamp and quality.

            A copy of `data` will be truncated before being sent to clients.

            Requires `dim_x <= len(data)`.

            data: value to send
            timestamp: unix timestamp
            quality: quality of attribute
            dim_x: length to truncate value to

        - push_archive_event(self, name: str, data: Scalar, timestamp: float, quality: tango.AttrQuality, dim_x: int, dim_y: int)

            Push a device server archive event for a image attribute with reshaping,
            timestampe and quality.

            A copy of `data` will be reshaped to `(dim_x, dim_y)` before being
            sent to clients.

            Note that `data` must be flat.

            Requires `dim_x * dim_y <= len(data)`.

            data: value to send
            timestamp: unix timestamp
            quality: quality of attribute
            dim_x: x dimension to reshape to
            dim_y: y dimension to reshape to

        - push_archive_event(self, name: str, str_data: str, data: bytes | str, timestamp: double, quality: tango.AttrQuality)

            Push a device server archive event for a encoded attribute with timestamp
            and quality.

            str_data: encoding format for data
            data: encoded data to send
            timestamp: unix timestamp
            quality: quality of attribute

        :param name: the attribute name
        :param args: the arguments to dispatch on
        """  # noqa: E501
        has_data_arg = len(args) > 0
        is_state_or_status = name.lower() in ["state", "status"]

        # Work around pytango#589.  Note this is only required for
        if not is_state_or_status and not has_data_arg:
            desc = (
                "push_archive_event without a data parameter is only allowed"
                + " for state and status attributes"
            )
            Except.throw_exception(
                "PyDs_InvalidCall", desc, "SKABaseDevice.push_archive_event"
            )

        self._submit_tango_operation("push_archive_event", name, *args)

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
        if (
            is_omni_thread()
            and self._omni_queue.empty()
            and not self._command_tracker.has_current_thread_locked()
        ):
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
        # TODO: this can be removed when cppTango issue #935 is implemented
        if self._init_active:
            self._init_active = False
            self.poll_command("ExecutePendingOperations", 100)
        while not self._omni_queue.empty():
            (command_name, args, kwargs) = self._omni_queue.get_nowait()
            getattr(super(), command_name)(*args, **kwargs)


#################################################################
# Support for overriding Tango attributes when TestMode is TEST #
#################################################################
enum_attrs = {  # TODO - confirm we can change this downstream, may need to refactor?
    "healthState": HealthState,
}
"""Tango attribute and enum class, for string conversion in TestMode overrides."""


def overridable(
    func: Callable[[object, Any, Any], None]
) -> Callable[[object, Any, Any], None] | Any:
    """
    Decorate attribute with test mode overrides.

    :param func: Tango attribute
    :return: Overridden value or original function
    """
    attr_name = func.__name__

    def override_attr_in_test_mode(
        self: SKABaseDevice[ComponentManagerT], *args: Any, **kwargs: Any
    ) -> Callable[[object, Any, Any], None] | Any:
        """
        Override attribute when test mode is active and value specified.

        :param self: SKABaseDevice
        :param args: Any positional arguments
        :param kwargs: Any keyword arguments
        :return: Tango attribute
        """
        # pylint: disable=protected-access
        if self._test_mode == TestMode.TEST and attr_name in self._test_mode_overrides:
            return _override_value_convert(
                attr_name, self._test_mode_overrides[attr_name]
            )

        # Test Mode not active, normal attribute behaviour
        return func(self, *args, **kwargs)

    return override_attr_in_test_mode


def _override_value_convert(attr_name: str, value: Any) -> Any:
    """
    Automatically convert types for attr overrides (e.g. enum label -> int).

    :param attr_name: Attribute name
    :param value: Value to convert
    :return: Converted value
    """
    if attr_name in enum_attrs and isinstance(value, str):
        return enum_attrs[attr_name][value]

    # default to no conversion
    return value


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
