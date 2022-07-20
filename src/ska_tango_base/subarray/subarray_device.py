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
import json
import logging
from typing import Callable, List, Optional, Tuple

from tango import DebugIt
from tango.server import attribute, command, device_property

# SKA specific imports
from ska_tango_base import SKAObsDevice
from ska_tango_base.base.base_device import CommandTracker
from ska_tango_base.commands import ResultCode, SlowCommand, SubmittedSlowCommand
from ska_tango_base.control_model import ObsState
from ska_tango_base.executor import TaskStatus
from ska_tango_base.faults import StateModelError
from ska_tango_base.subarray import SubarrayComponentManager, SubarrayObsStateModel

DevVarLongStringArrayType = Tuple[List[ResultCode], List[Optional[str]]]

__all__ = ["SKASubarray", "main"]


class SKASubarray(SKAObsDevice):
    """Implements the SKA SubArray device."""

    class InitCommand(SKAObsDevice.InitCommand):
        """A class for the SKASubarray's init_device() "command"."""

        def do(self: SKASubarray.InitCommand) -> tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.

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

    class AbortCommand(SlowCommand):
        """A class for SKASubarray's Abort() command."""

        def __init__(
            self: SKASubarray.AbortCommand,
            command_tracker: CommandTracker,
            component_manager: SubarrayComponentManager,
            callback: Callable[[], None],
            logger: Optional[logging.Logger] = None,
        ) -> None:
            """
            Initialise a new AbortCommand instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: callback to be called when this command
                states and finishes
            :param logger: a logger for this command object to yuse
            """
            print("Abort __init__ **************************")
            self._command_tracker = command_tracker
            self._component_manager = component_manager
            super().__init__(callback=callback, logger=logger)

        def do(  # type: ignore[override]
            self: SKASubarray.AbortCommand,
        ) -> tuple[ResultCode, str]:
            """
            Stateless hook for Abort() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            print("Abort do **************************")
            command_id = self._command_tracker.new_command(
                "Abort", completed_callback=self._completed
            )
            print("Abort do **************************", self._component_manager.abort)
            status, _ = self._component_manager.abort(
                functools.partial(self._command_tracker.update_command_info, command_id)
            )
            assert status == TaskStatus.IN_PROGRESS
            print("Abort do **************************")

            return ResultCode.STARTED, command_id

    def _init_state_model(self: SKASubarray) -> None:
        """Set up the state model for the device."""
        super()._init_state_model()
        self.obs_state_model = SubarrayObsStateModel(
            logger=self.logger, callback=self._update_obs_state
        )

    def init_command_objects(self: SKASubarray) -> None:
        """Set up the command objects."""
        super().init_command_objects()

        def _callback(hook: Callable, running: bool) -> None:
            action = "invoked" if running else "completed"
            self.obs_state_model.perform_action(f"{hook}_{action}")

        for (command_name, method_name, state_model_hook) in [
            ("AssignResources", "assign", "assign"),
            ("ReleaseResources", "release", "release"),
            ("ReleaseAllResources", "release_all", "release"),
            ("Configure", "configure", "configure"),
            ("Scan", "scan", None),
            ("EndScan", "end_scan", None),
            ("End", "deconfigure", None),
            ("ObsReset", "obsreset", "obsreset"),
            ("Restart", "restart", "restart"),
        ]:
            callback = (
                None
                if state_model_hook is None
                else functools.partial(_callback, state_model_hook)
            )
            self.register_command_object(
                command_name,
                SubmittedSlowCommand(
                    command_name,
                    self._command_tracker,
                    self.component_manager,
                    method_name,
                    callback=callback,
                    logger=None,
                ),
            )

        self.register_command_object(
            "Abort",
            self.AbortCommand(
                self._command_tracker,
                self.component_manager,
                callback=functools.partial(_callback, "abort"),
                logger=self.logger,
            ),
        )

    def _component_state_changed(
        self: SKASubarray,
        fault: Optional[bool] = None,
        power: Optional[bool] = None,
        resourced: Optional[bool] = None,
        configured: Optional[bool] = None,
        scanning: Optional[bool] = None,
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

    # ---------------
    # General methods
    # ---------------
    def always_executed_hook(self: SKASubarray) -> None:
        """
        Perform actions that are executed before every device command.

        This is a Tango hook.
        """
        pass

    def delete_device(self: SKASubarray) -> None:
        """
        Clean up any resources prior to device deletion.

        This method is a Tango hook that is called by the device
        destructor and by the device Init command. It allows for any
        memory or other resources allocated in the init_device method to
        be released prior to device deletion.
        """
        pass

    # ----------
    # Attributes
    # ----------
    @attribute(
        dtype="double",
        unit="s",
        standard_unit="s",
        display_unit="s",
    )
    def activationTime(self: SKASubarray) -> float:
        """
        Read the time of activation in seconds since Unix epoch.

        :return: Time of activation in seconds since Unix epoch.
        """
        return self._activation_time

    @attribute(
        dtype=("str",),
        max_dim_x=100,
    )
    def assignedResources(self: SKASubarray) -> list[str]:
        """
        Read the resources assigned to the device.

        The list of resources assigned to the subarray.

        :return: Resources assigned to the device.
        """
        return self.component_manager.assigned_resources

    @attribute(
        dtype=("str",),
        max_dim_x=10,
    )
    def configuredCapabilities(self: SKASubarray) -> list[str]:
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
    def is_AssignResources_allowed(self: SKASubarray) -> bool:
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
                f"AssignResources command not permitted in observation state {self._obs_state.name}"
            )
        return True

    @command(
        dtype_in="DevString",
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def AssignResources(self: SKASubarray, argin: str) -> DevVarLongStringArrayType:
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
        args = json.loads(argin)
        (result_code, message) = handler(args)
        return ([result_code], [message])

    def is_ReleaseResources_allowed(self: SKASubarray) -> bool:
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
                f"ReleaseResources command not permitted in observation state {self._obs_state.name}"
            )
        return True

    @command(
        dtype_in="DevString",
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def ReleaseResources(self: SKASubarray, argin: str) -> DevVarLongStringArrayType:
        """
        Delta removal of assigned resources.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: the resources to be released

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("ReleaseResources")
        args = json.loads(argin)
        (result_code, message) = handler(args)
        return ([result_code], [message])

    def is_ReleaseAllResources_allowed(self: SKASubarray) -> bool:
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
                f"ReleaseAllResources command not permitted in observation state {self._obs_state.name}"
            )
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    @DebugIt()
    def ReleaseAllResources(self: SKASubarray) -> DevVarLongStringArrayType:
        """
        Remove all resources to tear down to an empty subarray.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("ReleaseAllResources")
        (result_code, message) = handler()
        return ([result_code], [message])

    def is_Configure_allowed(self: SKASubarray) -> bool:
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
                f"Configure command not permitted in observation state {self._obs_state.name}"
            )
        return True

    @command(
        dtype_in="DevString",
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def Configure(self: SKASubarray, argin: str) -> DevVarLongStringArrayType:
        """
        Configure the capabilities of this subarray.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: JSON-encoded string with the scan configuration",
            configuration specification

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("Configure")
        args = json.loads(argin)
        (result_code, message) = handler(args)
        return ([result_code], [message])

    def is_Scan_allowed(self: SKASubarray) -> bool:
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
                f"Scan command not permitted in observation state {self._obs_state.name}"
            )
        return True

    @command(
        dtype_in="DevString",
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def Scan(self: SKASubarray, argin: str) -> DevVarLongStringArrayType:
        """
        Start scanning.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: JSON-encoded string with the per-scan configuration

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("Scan")
        args = json.loads(argin)
        (result_code, message) = handler(args)
        return ([result_code], [message])

    def is_EndScan_allowed(self: SKASubarray) -> bool:
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
                f"EndScan command not permitted in observation state {self._obs_state.name}"
            )
        return True

    @command(
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def EndScan(self: SKASubarray) -> DevVarLongStringArrayType:
        """
        End the scan.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("EndScan")
        (result_code, message) = handler()
        return ([result_code], [message])

    def is_End_allowed(self: SKASubarray) -> bool:
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

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def End(self: SKASubarray) -> DevVarLongStringArrayType:
        """
        End the scan block.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("End")
        (result_code, message) = handler()
        return ([result_code], [message])

    def is_Abort_allowed(self: SKASubarray) -> bool:
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
            ObsState.IDLE,
            ObsState.CONFIGURING,
            ObsState.READY,
            ObsState.SCANNING,
            ObsState.RESETTING,
        ]:
            raise StateModelError(
                f"Abort command not permitted in observation state {self._obs_state.name}"
            )
        return True

    @command(dtype_out="DevVarLongStringArray")
    @DebugIt()
    def Abort(self: SKASubarray) -> DevVarLongStringArrayType:
        """
        Abort any long-running command such as ``Configure()`` or ``Scan()``.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("Abort")
        (result_code, message) = handler()
        return ([result_code], [message])

    def is_ObsReset_allowed(self: SKASubarray) -> bool:
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
                f"ObsReset command not permitted in observation state {self._obs_state.name}"
            )
        return True

    @command(
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def ObsReset(self: SKASubarray) -> DevVarLongStringArrayType:
        """
        Reset the current observation process.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        """
        handler = self.get_command_object("ObsReset")
        (result_code, message) = handler()
        return ([result_code], [message])

    def is_Restart_allowed(self: SKASubarray) -> bool:
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
                f"Restart command not permitted in observation state {self._obs_state.name}"
            )
        return True

    @command(
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def Restart(self: SKASubarray) -> DevVarLongStringArrayType:
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
    return SKASubarray.run_server(args=args or None, **kwargs)


if __name__ == "__main__":
    main()
