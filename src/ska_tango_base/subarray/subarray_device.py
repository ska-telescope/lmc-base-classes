# -*- coding: utf-8 -*-
#
# This file is part of the SKASubarray project
#
#
#
"""
SKASubarray.

A SubArray handling device. It allows the assigning/releasing of
resources into/from Subarray, configuring capabilities, and exposes the
related information like assigned resources, configured capabilities,
etc.
"""
# PROTECTED REGION ID(SKASubarray.additionnal_import) ENABLED START #
import functools
import json

from tango import DebugIt
from tango.server import run, attribute, command
from tango.server import device_property

# SKA specific imports
from ska_tango_base import SKAObsDevice
from ska_tango_base.commands import ResultCode, SlowCommand, SubmittedSlowCommand
from ska_tango_base.control_model import ObsState
from ska_tango_base.executor import TaskStatus
from ska_tango_base.faults import StateModelError
from ska_tango_base.subarray import SubarrayObsStateModel


# PROTECTED REGION END #    //  SKASubarray.additionnal_imports

__all__ = ["SKASubarray", "main"]


class SKASubarray(SKAObsDevice):
    """Implements the SKA SubArray device."""

    class InitCommand(SKAObsDevice.InitCommand):
        """A class for the SKASubarray's init_device() "command"."""

        def do(self):
            """
            Stateless hook for device initialisation.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            super().do()

            self._device._activation_time = 0.0

            message = "SKASubarray Init command completed OK"
            self.logger.info(message)
            self._completed()
            return (ResultCode.OK, message)

    class AbortCommand(SlowCommand):
        """A class for SKASubarray's Abort() command."""

        def __init__(self, command_tracker, component_manager, callback, logger=None):
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

        def do(self):
            """
            Stateless hook for Abort() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            command_id = self._command_tracker.new_command(
                "Abort", completed_callback=self._completed
            )
            status, _ = self._component_manager.abort(
                functools.partial(self._command_tracker.update_command_info, command_id)
            )

            assert status == TaskStatus.IN_PROGRESS
            return ResultCode.STARTED, command_id

    # PROTECTED REGION ID(SKASubarray.class_variable) ENABLED START #
    def _init_state_model(self):
        """Set up the state model for the device."""
        super()._init_state_model()
        self.obs_state_model = SubarrayObsStateModel(
            logger=self.logger, callback=self._update_obs_state
        )

    def init_command_objects(self):
        """Set up the command objects."""
        super().init_command_objects()

        def _callback(hook, running):
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
        self,
        fault=None,
        power=None,
        resourced=None,
        configured=None,
        scanning=None,
    ):
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
    activationTime = attribute(
        dtype="double",
        unit="s",
        standard_unit="s",
        display_unit="s",
        doc="Time of activation in seconds since Unix epoch.",
    )
    """Device attribute."""

    assignedResources = attribute(
        dtype=("str",),
        max_dim_x=100,
        doc="The list of resources assigned to the subarray.",
    )
    """Device attribute."""

    configuredCapabilities = attribute(
        dtype=("str",),
        max_dim_x=10,
        doc="A list of capability types with no. of instances "
        "in use on this subarray; "
        "e.g.\nCorrelators:512, PssBeams:4, "
        "PstBeams:4, VlbiBeams:0.",
    )
    """Device attribute."""

    # ---------------
    # General methods
    # ---------------
    def always_executed_hook(self):
        # PROTECTED REGION ID(SKASubarray.always_executed_hook) ENABLED START #
        """
        Perform actions that are executed before every device command.

        This is a Tango hook.
        """
        pass
        # PROTECTED REGION END #    //  SKASubarray.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKASubarray.delete_device) ENABLED START #
        """
        Clean up any resources prior to device deletion.

        This method is a Tango hook that is called by the device
        destructor and by the device Init command. It allows for any
        memory or other resources allocated in the init_device method to
        be released prior to device deletion.
        """
        pass
        # PROTECTED REGION END #    //  SKASubarray.delete_device

    # ------------------
    # Attributes methods
    # ------------------
    def read_activationTime(self):
        # PROTECTED REGION ID(SKASubarray.activationTime_read) ENABLED START #
        """
        Read the time since device is activated.

        :return: Time of activation in seconds since Unix epoch.
        """
        return self._activation_time
        # PROTECTED REGION END #    //  SKASubarray.activationTime_read

    def read_assignedResources(self):
        # PROTECTED REGION ID(SKASubarray.assignedResources_read) ENABLED START #
        """
        Read the resources assigned to the device.

        :return: Resources assigned to the device.
        """
        return self.component_manager.assigned_resources
        # PROTECTED REGION END #    //  SKASubarray.assignedResources_read

    def read_configuredCapabilities(self):
        # PROTECTED REGION ID(SKASubarray.configuredCapabilities_read) ENABLED START #
        """
        Read capabilities configured in the Subarray.

        :return: A list of capability types with no. of instances used
            in the Subarray
        """
        return self.component_manager.configured_capabilities
        # PROTECTED REGION END #    //  SKASubarray.configuredCapabilities_read

    # --------
    # Commands
    # --------
    def is_AssignResources_allowed(self):
        """
        Return whether the `AssignResource` command may be called in the current state.

        :return: whether the command may be called in the current device
            state
        :rtype: bool
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
    def AssignResources(self, argin):
        """
        Assign resources to this subarray.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: the resources to be assigned
        :type argin: list of str

        :return: A tuple containing a result code and a string message. If the result
            code indicates that the command was accepted, the message is the unique ID
            of the task that will execute the command. If the result code indicates that
            the command was not excepted, the message explains why.
        :rtype: ([ResultCode], [str])
        """
        handler = self.get_command_object("AssignResources")
        args = json.loads(argin)
        (result_code, message) = handler(args)
        return [[result_code], [message]]

    def is_ReleaseResources_allowed(self):
        """
        Return whether the `ReleaseResources` command may be called in current state.

        :return: whether the command may be called in the current device
            state
        :rtype: bool
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
    def ReleaseResources(self, argin):
        """
        Delta removal of assigned resources.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: the resources to be released
        :type argin: list of str

        :return: A tuple containing a result code and the unique ID of the command
        :rtype: ([ResultCode], [str])
        """
        handler = self.get_command_object("ReleaseResources")
        args = json.loads(argin)
        (result_code, message) = handler(args)
        return [[result_code], [message]]

    def is_ReleaseAllResources_allowed(self):
        """
        Return whether `ReleaseAllResources` may be called in the current device state.

        :return: whether the command may be called in the current device
            state
        :rtype: bool
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
    def ReleaseAllResources(self):
        """
        Remove all resources to tear down to an empty subarray.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        :rtype: ([ResultCode], [str])
        """
        handler = self.get_command_object("ReleaseAllResources")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_Configure_allowed(self):
        """
        Return whether `Configure` may be called in the current device state.

        :return: whether the command may be called in the current device
            state
        :rtype: bool
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
        doc_in="JSON-encoded string with the scan configuration",
        dtype_out="DevVarLongStringArray",
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    @DebugIt()
    def Configure(self, argin):
        """
        Configure the capabilities of this subarray.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: configuration specification
        :type argin: string

        :return: A tuple containing a result code and the unique ID of the command
        :rtype: ([ResultCode], [str])
        """
        handler = self.get_command_object("Configure")
        args = json.loads(argin)
        (result_code, message) = handler(args)
        return [[result_code], [message]]

    def is_Scan_allowed(self):
        """
        Return whether the `Scan` command may be called in the current device state.

        :return: whether the command may be called in the current device
            state
        :rtype: bool
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
        doc_in="JSON-encoded string with the per-scan configuration",
        dtype_out="DevVarLongStringArray",
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    @DebugIt()
    def Scan(self, argin):
        """
        Start scanning.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: Information about the scan
        :type argin: Array of str

        :return: A tuple containing a result code and the unique ID of the command
        :rtype: ([ResultCode], [str])
        """
        handler = self.get_command_object("Scan")
        args = json.loads(argin)
        (result_code, message) = handler(args)
        return [[result_code], [message]]

    def is_EndScan_allowed(self):
        """
        Return whether the `EndScan` command may be called in the current device state.

        :return: whether the command may be called in the current device
            state
        :rtype: bool
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
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    @DebugIt()
    def EndScan(self):
        """
        End the scan.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        :rtype: ([ResultCode], [str])
        """
        handler = self.get_command_object("EndScan")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_End_allowed(self):
        """
        Return whether the `End` command may be called in the current device state.

        :return: whether the command may be called in the current device
            state
        :rtype: bool
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
    def End(self):
        # PROTECTED REGION ID(SKASubarray.EndSB) ENABLED START #
        """
        End the scan block.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        :rtype: ([ResultCode], [str])
        """
        handler = self.get_command_object("End")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_Abort_allowed(self):
        """
        Return whether the `Abort` command may be called in the current device state.

        :return: whether the command may be called in the current device
            state
        :rtype: bool
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
    def Abort(self):
        """
        Abort any long-running command such as ``Configure()`` or ``Scan()``.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        :rtype: ([ResultCode], [str])
        """
        handler = self.get_command_object("Abort")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_ObsReset_allowed(self):
        """
        Return whether the `ObsReset` command may be called in the current device state.

        :return: whether the command may be called in the current device
            state
        :rtype: bool
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
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    @DebugIt()
    def ObsReset(self):
        """
        Reset the current observation process.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        :rtype: ([ResultCode], [str])
        """
        handler = self.get_command_object("ObsReset")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_Restart_allowed(self):
        """
        Return whether the `Restart` command may be called in the current device state.

        :return: whether the command may be called in the current device
            state
        :rtype: bool
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
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    @DebugIt()
    def Restart(self):
        """
        Restart the subarray. That is, deconfigure and release all resources.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a result code and the unique ID of the command
        :rtype: ([ResultCode], [str])
        """
        handler = self.get_command_object("Restart")
        (result_code, message) = handler()
        return [[result_code], [message]]


# ----------
# Run server
# ----------
def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKASubarray.main) ENABLED START #
    """
    Launch an SKASubarray device.

    :param args: positional args to tango.server.run
    :param kwargs: named args to tango.server.run

    :return: exit code
    """
    return run((SKASubarray,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKASubarray.main


if __name__ == "__main__":
    main()
