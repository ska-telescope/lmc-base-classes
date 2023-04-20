# pylint: disable=invalid-name
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
SKASubarray.

A SubArray handling device. It allows the assigning/releasing of
resources into/from Subarray, configuring capabilities, and exposes the
related information like assigned resources, configured capabilities,
etc.
"""
from __future__ import annotations

import functools
import logging
from typing import Any, Callable, TypeVar, cast

from ska_control_model import (
    ObsState,
    ObsStateModel,
    PowerState,
    ResultCode,
    TaskStatus,
)
from tango import DebugIt
from tango.server import attribute, command, device_property

from ..base import CommandTracker
from ..commands import JsonValidator, SlowCommand, SubmittedSlowCommand
from ..faults import StateModelError
from ..obs import SKAObsDevice
from .component_manager import SubarrayComponentManager

DevVarLongStringArrayType = tuple[list[ResultCode], list[str]]

__all__ = ["SKASubarray", "main"]


ComponentManagerT = TypeVar("ComponentManagerT", bound=SubarrayComponentManager)


# pylint: disable-next=too-many-public-methods
class SKASubarray(SKAObsDevice[ComponentManagerT]):
    """Implements the SKA SubArray device."""

    def __init__(
        self: SKASubarray[ComponentManagerT],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialise a new instance.

        :param args: positional arguments.
        :param kwargs: keyword arguments.
        """
        # This __init__ method is created for type-hinting purposes only.
        # Tango devices are not supposed to have __init__ methods,
        # And they have a strange __new__ method,
        # that calls __init__ when you least expect it.
        # So don't put anything executable in here
        # (other than the super() call).
        self._activation_time: float
        self.obs_state_model: ObsStateModel

        super().__init__(*args, **kwargs)

    class InitCommand(SKAObsDevice.InitCommand):
        # pylint: disable=protected-access  # command classes are friend classes
        """A class for the SKASubarray's init_device() "command"."""

        def do(
            self: SKASubarray.InitCommand,
            *args: Any,
            **kwargs: Any,
        ) -> tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.

            :param args: positional arguments to the command. This
                command does not take any, so this should be empty.
            :param kwargs: keyword arguments to the command. This
                command does not take any, so this should be empty.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            super().do()

            self._device._activation_time = 0.0

            message = "SKASubarray Init command completed OK"
            self.logger.info(message)
            self._completed()
            return (ResultCode.OK, message)

    class AssignResourcesCommand(SubmittedSlowCommand):
        """A class for SKASubarray's AssignResources() command."""

        def __init__(  # pylint: disable=too-many-arguments
            self: SKASubarray.AssignResourcesCommand,
            command_tracker: CommandTracker,
            component_manager: SubarrayComponentManager,
            callback: Callable[[bool], None] | None = None,
            logger: logging.Logger | None = None,
            schema: dict[str, Any] | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: an optional callback to be called when this
                command starts and finishes.
            :param logger: a logger for this command to log with.
            :param schema: an optional JSON schema for the command
                argument.
            """
            super().__init__(
                "AssignResources",
                command_tracker,
                component_manager,
                "assign",
                callback=callback,
                logger=logger,
                validator=JsonValidator("AssignResources", schema, logger=logger),
            )

    class ReleaseResourcesCommand(SubmittedSlowCommand):
        """A class for SKASubarray's ReleaseResources() command."""

        def __init__(  # pylint: disable=too-many-arguments
            self: SKASubarray.ReleaseResourcesCommand,
            command_tracker: CommandTracker,
            component_manager: SubarrayComponentManager,
            callback: Callable[[bool], None] | None = None,
            logger: logging.Logger | None = None,
            schema: dict[str, Any] | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: an optional callback to be called when this
                command starts and finishes.
            :param logger: a logger for this command to log with.
            :param schema: an optional JSON schema for the command
                argument.
            """
            super().__init__(
                "ReleaseResources",
                command_tracker,
                component_manager,
                "release",
                callback=callback,
                logger=logger,
                validator=JsonValidator("ReleaseResources", schema, logger=logger),
            )

    class ReleaseAllResourcesCommand(SubmittedSlowCommand):
        """A class for SKASubarray's ReleaseAllResources() command."""

        def __init__(  # pylint: disable=too-many-arguments
            self: SKASubarray.ReleaseAllResourcesCommand,
            command_tracker: CommandTracker,
            component_manager: SubarrayComponentManager,
            callback: Callable[[bool], None] | None = None,
            logger: logging.Logger | None = None,
            schema: dict[str, Any] | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: an optional callback to be called when this
                command starts and finishes.
            :param logger: a logger for this command to log with.
            :param schema: an optional JSON schema for the command
                argument.
            """
            super().__init__(
                "ReleaseAllResources",
                command_tracker,
                component_manager,
                "release_all",
                callback=callback,
                logger=logger,
                validator=JsonValidator("ReleaseAllResources", schema, logger=logger),
            )

    class ConfigureCommand(SubmittedSlowCommand):
        """A class for SKASubarray's Configure() command."""

        def __init__(  # pylint: disable=too-many-arguments
            self: SKASubarray.ConfigureCommand,
            command_tracker: CommandTracker,
            component_manager: SubarrayComponentManager,
            callback: Callable[[bool], None] | None = None,
            logger: logging.Logger | None = None,
            schema: dict[str, Any] | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: an optional callback to be called when this
                command starts and finishes.
            :param logger: a logger for this command to log with.
            :param schema: an optional JSON schema for the command
                argument.
            """
            super().__init__(
                "Configure",
                command_tracker,
                component_manager,
                "configure",
                callback=callback,
                logger=logger,
                validator=JsonValidator("Configure", schema, logger=logger),
            )

    class ScanCommand(SubmittedSlowCommand):
        """A class for SKASubarray's Scan() command."""

        def __init__(  # pylint: disable=too-many-arguments
            self: SKASubarray.ScanCommand,
            command_tracker: CommandTracker,
            component_manager: SubarrayComponentManager,
            callback: Callable[[bool], None] | None = None,
            logger: logging.Logger | None = None,
            schema: dict[str, Any] | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: an optional callback to be called when this
                command starts and finishes.
            :param logger: a logger for this command to log with.
            :param schema: an optional JSON schema for the command
                argument.
            """
            super().__init__(
                "Scan",
                command_tracker,
                component_manager,
                "scan",
                callback=callback,
                logger=logger,
                validator=JsonValidator("Scan", schema, logger=logger),
            )

    class EndScanCommand(SubmittedSlowCommand):
        """A class for SKASubarray's EndScan() command."""

        def __init__(  # pylint: disable=too-many-arguments
            self: SKASubarray.EndScanCommand,
            command_tracker: CommandTracker,
            component_manager: SubarrayComponentManager,
            callback: Callable[[bool], None] | None = None,
            logger: logging.Logger | None = None,
            schema: dict[str, Any] | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: an optional callback to be called when this
                command starts and finishes.
            :param logger: a logger for this command to log with.
            :param schema: an optional JSON schema for the command
                argument.
            """
            super().__init__(
                "EndScan",
                command_tracker,
                component_manager,
                "end_scan",
                callback=callback,
                logger=logger,
                validator=JsonValidator("EndScan", schema, logger=logger),
            )

    class EndCommand(SubmittedSlowCommand):
        """A class for SKASubarray's End() command."""

        def __init__(  # pylint: disable=too-many-arguments
            self: SKASubarray.EndCommand,
            command_tracker: CommandTracker,
            component_manager: SubarrayComponentManager,
            callback: Callable[[bool], None] | None = None,
            logger: logging.Logger | None = None,
            schema: dict[str, Any] | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: an optional callback to be called when this
                command starts and finishes.
            :param logger: a logger for this command to log with.
            :param schema: an optional JSON schema for the command
                argument.
            """
            super().__init__(
                "End",
                command_tracker,
                component_manager,
                "deconfigure",
                callback=callback,
                logger=logger,
                validator=JsonValidator("End", schema, logger=logger),
            )

    class AbortCommand(SlowCommand[tuple[ResultCode, str]]):
        """A class for SKASubarray's Abort() command."""

        def __init__(
            self: SKASubarray.AbortCommand,
            command_tracker: CommandTracker,
            component_manager: SubarrayComponentManager,
            callback: Callable[[bool], None],
            logger: logging.Logger | None = None,
        ) -> None:
            """
            Initialise a new AbortCommand instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: callback to be called when this command
                states and finishes
            :param logger: a logger for this command object to yuse
            """
            self._command_tracker = command_tracker
            self._component_manager = component_manager
            super().__init__(callback=callback, logger=logger)

        def do(
            self: SKASubarray.AbortCommand,
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
                functools.partial(self._command_tracker.update_command_info, command_id)
            )
            assert status == TaskStatus.IN_PROGRESS

            return ResultCode.STARTED, command_id

    class ObsResetCommand(SubmittedSlowCommand):
        """A class for SKASubarray's ObsReset() command."""

        def __init__(  # pylint: disable=too-many-arguments
            self: SKASubarray.ObsResetCommand,
            command_tracker: CommandTracker,
            component_manager: SubarrayComponentManager,
            callback: Callable[[bool], None] | None = None,
            logger: logging.Logger | None = None,
            schema: dict[str, Any] | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: an optional callback to be called when this
                command starts and finishes.
            :param logger: a logger for this command to log with.
            :param schema: an optional JSON schema for the command
                argument.
            """
            super().__init__(
                "ObsReset",
                command_tracker,
                component_manager,
                "obsreset",
                callback=callback,
                logger=logger,
                validator=JsonValidator("ObsReset", schema, logger=logger),
            )

    class RestartCommand(SubmittedSlowCommand):
        """A class for SKASubarray's Restart() command."""

        def __init__(  # pylint: disable=too-many-arguments
            self: SKASubarray.RestartCommand,
            command_tracker: CommandTracker,
            component_manager: SubarrayComponentManager,
            callback: Callable[[bool], None] | None = None,
            logger: logging.Logger | None = None,
            schema: dict[str, Any] | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: an optional callback to be called when this
                command starts and finishes.
            :param logger: a logger for this command to log with.
            :param schema: an optional JSON schema for the command
                argument.
            """
            super().__init__(
                "Restart",
                command_tracker,
                component_manager,
                "restart",
                callback=callback,
                logger=logger,
                validator=JsonValidator("Restart", schema, logger=logger),
            )

    def create_component_manager(
        self: SKASubarray[ComponentManagerT],
    ) -> ComponentManagerT:
        """
        Create and return a component manager for this device.

        :raises NotImplementedError: because it is not implemented.
        """
        raise NotImplementedError("SKASubarray is abstract.")

    def _init_state_model(self: SKASubarray[ComponentManagerT]) -> None:
        """Set up the state model for the device."""
        super()._init_state_model()
        self.obs_state_model = ObsStateModel(
            logger=self.logger, callback=self._update_obs_state
        )

    def init_command_objects(self: SKASubarray[ComponentManagerT]) -> None:
        """Set up the command objects."""
        super().init_command_objects()

        def _callback(hook: str, running: bool) -> None:
            action = "invoked" if running else "completed"
            self.obs_state_model.perform_action(f"{hook}_{action}")

        for command_name, command_class, state_model_hook in [
            ("AssignResources", self.AssignResourcesCommand, "assign"),
            ("ReleaseResources", self.ReleaseResourcesCommand, "release"),
            ("ReleaseAllResources", self.ReleaseAllResourcesCommand, "release"),
            ("Configure", self.ConfigureCommand, "configure"),
            ("Scan", self.ScanCommand, None),
            ("EndScan", self.EndScanCommand, None),
            ("End", self.EndCommand, None),
            ("Abort", self.AbortCommand, "abort"),
            ("ObsReset", self.ObsResetCommand, "obsreset"),
            ("Restart", self.RestartCommand, "restart"),
        ]:
            callback = (
                None
                if state_model_hook is None
                else functools.partial(_callback, state_model_hook)
            )
            self.register_command_object(
                command_name,
                command_class(
                    self._command_tracker,
                    self.component_manager,
                    callback=callback,
                    logger=None,
                ),
            )

    # pylint: disable-next=too-many-arguments
    def _component_state_changed(
        self: SKASubarray[ComponentManagerT],
        fault: bool | None = None,
        power: PowerState | None = None,
        resourced: bool | None = None,
        configured: bool | None = None,
        scanning: bool | None = None,
    ) -> None:
        super()._component_state_changed(fault=fault, power=power)

        if resourced is not None:
            if resourced:
                self.obs_state_model.perform_action("component_resourced")
            else:
                self.obs_state_model.perform_action("component_unresourced")
        if configured is not None:
            if configured:
                self.obs_state_model.perform_action("component_configured")
            else:
                self.obs_state_model.perform_action("component_unconfigured")
        if scanning is not None:
            if scanning:
                self.obs_state_model.perform_action("component_scanning")
            else:
                self.obs_state_model.perform_action("component_not_scanning")

    # -----------------
    # Device Properties
    # -----------------
    CapabilityTypes = device_property(
        dtype=("str",),
    )

    SubID = device_property(
        dtype="str",
    )

    # ----------
    # Attributes
    # ----------
    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype="double",
        unit="s",
        standard_unit="s",
        display_unit="s",
    )
    def activationTime(self: SKASubarray[ComponentManagerT]) -> float:
        """
        Read the time of activation in seconds since Unix epoch.

        :return: Time of activation in seconds since Unix epoch.
        """
        return self._activation_time

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=("str",),
        max_dim_x=512,
    )
    def assignedResources(self: SKASubarray[ComponentManagerT]) -> list[str]:
        """
        Read the resources assigned to the device.

        The list of resources assigned to the subarray.

        :return: Resources assigned to the device.
        """
        return self.component_manager.assigned_resources

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=("str",),
        max_dim_x=10,
    )
    def configuredCapabilities(self: SKASubarray[ComponentManagerT]) -> list[str]:
        """
        Read capabilities configured in the Subarray.

        A list of capability types with no. of instances in use on this subarray;
        e.g. Correlators:512, PssBeams:4 PstBeams:4, VlbiBeams:0.

        :return: A list of capability types with no. of instances used
            in the Subarray
        """
        return self.component_manager.configured_capabilities

    # --------
    # Commands
    # --------
    def is_AssignResources_allowed(self: SKASubarray[ComponentManagerT]) -> bool:
        """
        Return whether the `AssignResource` command may be called in the current state.

        :raises StateModelError: command not permitted in observation state

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "AssignResources not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state not in [ObsState.EMPTY, ObsState.IDLE]:
            raise StateModelError(
                "AssignResources command not permitted in observation state "
                f"{self._obs_state.name}"
            )
        return True

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in="DevString",
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def AssignResources(
        self: SKASubarray[ComponentManagerT], argin: str
    ) -> DevVarLongStringArrayType:
        """
        Assign resources to this subarray.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: the resources to be assigned

        :return: A tuple containing a result code and a string message. If the result
            code indicates that the command was accepted, the message is the unique ID
            of the task that will execute the command. If the result code indicates that
            the command was not excepted, the message explains why.
        """
        handler = self.get_command_object("AssignResources")
        (result_code, message) = handler(argin)
        return ([result_code], [message])

    def is_ReleaseResources_allowed(self: SKASubarray[ComponentManagerT]) -> bool:
        """
        Return whether the `ReleaseResources` command may be called in current state.

        :raises StateModelError: command not permitted in observation state

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "ReleaseResources not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state not in [ObsState.EMPTY, ObsState.IDLE]:
            raise StateModelError(
                "ReleaseResources command not permitted in observation state "
                f"{self._obs_state.name}"
            )
        return True

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in="DevString",
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def ReleaseResources(
        self: SKASubarray[ComponentManagerT], argin: str
    ) -> DevVarLongStringArrayType:
        """
        Delta removal of assigned resources.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: the resources to be released

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("ReleaseResources")
        (result_code, message) = handler(argin)
        return ([result_code], [message])

    def is_ReleaseAllResources_allowed(self: SKASubarray[ComponentManagerT]) -> bool:
        """
        Return whether `ReleaseAllResources` may be called in the current device state.

        :raises StateModelError: command not permitted in observation state

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "ReleaseResources not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state not in [ObsState.EMPTY, ObsState.IDLE]:
            raise StateModelError(
                "ReleaseAllResources command not permitted in observation state "
                f"{self._obs_state.name}"
            )
        return True

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarLongStringArray",
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def ReleaseAllResources(
        self: SKASubarray[ComponentManagerT],
    ) -> DevVarLongStringArrayType:
        """
        Remove all resources to tear down to an empty subarray.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("ReleaseAllResources")
        (result_code, message) = handler()
        return ([result_code], [message])

    def is_Configure_allowed(self: SKASubarray[ComponentManagerT]) -> bool:
        """
        Return whether `Configure` may be called in the current device state.

        :raises StateModelError: command not permitted in observation state

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "ReleaseResources not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state not in [ObsState.IDLE, ObsState.READY]:
            raise StateModelError(
                "Configure command not permitted in observation state "
                f"{self._obs_state.name}"
            )
        return True

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in="DevString",
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def Configure(
        self: SKASubarray[ComponentManagerT], argin: str
    ) -> DevVarLongStringArrayType:
        """
        Configure the capabilities of this subarray.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: JSON-encoded string with the scan configuration",
            configuration specification

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("Configure")
        (result_code, message) = handler(argin)
        return ([result_code], [message])

    def is_Scan_allowed(self: SKASubarray[ComponentManagerT]) -> bool:
        """
        Return whether the `Scan` command may be called in the current device state.

        :raises StateModelError: command not permitted in observation state

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "ReleaseResources not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state != ObsState.READY:
            raise StateModelError(
                "Scan command not permitted in observation state "
                f"{self._obs_state.name}"
            )
        return True

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in="DevString",
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def Scan(
        self: SKASubarray[ComponentManagerT], argin: str
    ) -> DevVarLongStringArrayType:
        """
        Start scanning.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: JSON-encoded string with the per-scan configuration

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("Scan")
        (result_code, message) = handler(argin)
        return ([result_code], [message])

    def is_EndScan_allowed(self: SKASubarray[ComponentManagerT]) -> bool:
        """
        Return whether the `EndScan` command may be called in the current device state.

        :raises StateModelError: command not permitted in observation state

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "ReleaseResources not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state != ObsState.SCANNING:
            raise StateModelError(
                "EndScan command not permitted in observation state "
                f"{self._obs_state.name}"
            )
        return True

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def EndScan(self: SKASubarray[ComponentManagerT]) -> DevVarLongStringArrayType:
        """
        End the scan.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("EndScan")
        (result_code, message) = handler()
        return ([result_code], [message])

    def is_End_allowed(self: SKASubarray[ComponentManagerT]) -> bool:
        """
        Return whether the `End` command may be called in the current device state.

        :raises StateModelError: command not permitted in observation state

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "ReleaseResources not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state not in [ObsState.IDLE, ObsState.READY]:
            raise StateModelError(
                f"End command not permitted in observation state {self._obs_state.name}"
            )
        return True

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarLongStringArray"
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def End(self: SKASubarray[ComponentManagerT]) -> DevVarLongStringArrayType:
        """
        End the scan block.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("End")
        (result_code, message) = handler()
        return ([result_code], [message])

    def is_Abort_allowed(self: SKASubarray[ComponentManagerT]) -> bool:
        """
        Return whether the `Abort` command may be called in the current device state.

        :raises StateModelError: command not permitted in observation state

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "Abort not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state not in [
            ObsState.RESOURCING,
            ObsState.IDLE,
            ObsState.CONFIGURING,
            ObsState.READY,
            ObsState.SCANNING,
            ObsState.RESETTING,
        ]:
            raise StateModelError(
                "Abort command not permitted in observation state "
                f"{self._obs_state.name}"
            )
        return True

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarLongStringArray"
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def Abort(self: SKASubarray[ComponentManagerT]) -> DevVarLongStringArrayType:
        """
        Abort any long-running command such as ``Configure()`` or ``Scan()``.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("Abort")
        (result_code, message) = handler()
        return ([result_code], [message])

    def is_ObsReset_allowed(self: SKASubarray[ComponentManagerT]) -> bool:
        """
        Return whether the `ObsReset` command may be called in the current device state.

        :raises StateModelError: command not permitted in observation state

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "ObsReset not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state not in [ObsState.FAULT, ObsState.ABORTED]:
            raise StateModelError(
                "ObsReset command not permitted in observation state "
                f"{self._obs_state.name}"
            )
        return True

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def ObsReset(self: SKASubarray[ComponentManagerT]) -> DevVarLongStringArrayType:
        """
        Reset the current observation process.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("ObsReset")
        (result_code, message) = handler()
        return ([result_code], [message])

    def is_Restart_allowed(self: SKASubarray[ComponentManagerT]) -> bool:
        """
        Return whether the `Restart` command may be called in the current device state.

        :raises StateModelError: command not permitted in observation state

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "ObsReset not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state not in [ObsState.FAULT, ObsState.ABORTED]:
            raise StateModelError(
                "Restart command not permitted in observation state "
                f"{self._obs_state.name}"
            )
        return True

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def Restart(self: SKASubarray[ComponentManagerT]) -> DevVarLongStringArrayType:
        """
        Restart the subarray. That is, deconfigure and release all resources.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("Restart")
        (result_code, message) = handler()
        return ([result_code], [message])


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
    return cast(int, SKASubarray.run_server(args=args or None, **kwargs))


if __name__ == "__main__":
    main()
