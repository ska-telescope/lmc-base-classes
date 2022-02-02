# -*- coding: utf-8 -*-
#
# This file is part of the CspSubElementSubarray project
#
#
# Distributed under the terms of the BSD3 license.
# See LICENSE.txt for more info.

"""
CspSubElementSubarray.

Subarray device for SKA CSP SubElement
"""

# PROTECTED REGION ID(CspSubElementSubarray.additionnal_import) ENABLED START #
import json
from json.decoder import JSONDecodeError
from collections import defaultdict

# Tango imports
from tango import DebugIt
from tango.server import run
from tango.server import attribute, command
from tango import AttrWriteType

# SKA import
from ska_tango_base import SKASubarray
from ska_tango_base.commands import ResultCode, SubmittedSlowCommand
from ska_tango_base.control_model import ObsState
from ska_tango_base.faults import StateModelError

# Additional import
# PROTECTED REGION END #    //  CspSubElementSubarray.additionnal_import

__all__ = ["CspSubElementSubarray", "main"]


class CspSubElementSubarray(SKASubarray):
    """Subarray device for SKA CSP SubElement."""

    # PROTECTED REGION ID(CspSubElementSubarray.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  CspSubElementSubarray.class_variable

    # -----------------
    # Device Properties
    # -----------------

    # ----------
    # Attributes
    # ----------

    scanID = attribute(
        dtype="DevULong64",
        label="scanID",
        doc="The scan identification number to be inserted in the output products.",
    )
    """Device attribute."""

    configurationID = attribute(
        dtype="DevString",
        label="configurationID",
        doc="The configuration ID specified into the JSON configuration.",
    )
    """Device attribute."""

    sdpDestinationAddresses = attribute(
        dtype="DevString",
        access=AttrWriteType.READ_WRITE,
        label="sdpDestinationAddresses",
        doc="JSON formatted string.\nReport the list of all the SDP addresses provided "
        "by SDP to receive the output products.\nSpecifies the Mac, IP, Port for each "
        "resource:CBF visibility channels, Pss pipelines, PSTBeam",
    )
    """Device attribute."""

    outputDataRateToSdp = attribute(
        dtype="DevFloat",
        label="outputDataRateToSdp",
        unit="GB/s",
        doc="The output data rate (GB/s) on the link for each scan.",
    )
    """Device attribute."""

    lastScanConfiguration = attribute(
        dtype="DevString",
        label="lastScanConfiguration",
        doc="The last valid scan configuration.",
    )
    """Device attribute."""

    sdpLinkActive = attribute(
        dtype=("DevBoolean",),
        max_dim_x=100,
        label="sdpLinkActive",
        doc="Flag reporting if the SDP links are active.",
    )
    """Device attribute."""

    listOfDevicesCompletedTasks = attribute(
        dtype="DevString",
        label="listOfDevicesCompletedTasks",
        doc="JSON formatted string reporting for each task/command the list of devices"
        "\nthat completed successfully the task.\nEx.\n{``cmd1``: [``device1``, "
        "``device2``], ``cmd2``: [``device2``, ``device3``]}",
    )
    """Device attribute."""

    configureScanMeasuredDuration = attribute(
        dtype="DevFloat",
        label="configureScanMeasuredDuration",
        unit="sec",
        doc="The measured time (sec) taken to execute the command",
    )
    """Device attribute."""

    configureScanTimeoutExpiredFlag = attribute(
        dtype="DevBoolean",
        label="configureScanTimeoutExpiredFlag",
        doc="Flag reporting  ConfigureScan command timeout expiration.",
    )
    """Device attribute."""

    assignResourcesMaximumDuration = attribute(
        dtype="DevFloat",
        access=AttrWriteType.READ_WRITE,
        label="assignResourcesMaximumDuration",
        unit="sec",
        doc="The maximum expected command duration.",
    )
    """Device attribute."""

    assignResourcesMeasuredDuration = attribute(
        dtype="DevFloat",
        label="assignResourcesMeasuredDuration",
        unit="sec",
        doc="The measured command execution duration.",
    )
    """Device attribute."""

    assignResourcesProgress = attribute(
        dtype="DevUShort",
        label="assignResourcesProgress",
        max_value=100,
        min_value=0,
        doc="The percentage progress of the command in the [0,100].",
    )
    """Device attribute."""

    assignResourcesTimeoutExpiredFlag = attribute(
        dtype="DevBoolean",
        label="assignResourcesTimeoutExpiredFlag",
        doc="Flag reporting  AssignResources command timeout expiration.",
    )
    """Device attribute."""

    releaseResourcesMaximumDuration = attribute(
        dtype="DevFloat",
        access=AttrWriteType.READ_WRITE,
        label="releaseResourcesMaximumDuration",
        unit="sec",
        doc="The maximum expected command duration.",
    )
    """Device attribute."""

    releaseResourcesMeasuredDuration = attribute(
        dtype="DevFloat",
        label="releaseResourcesMeasuredDuration",
        unit="sec",
        doc="The measured command execution duration.",
    )
    """Device attribute."""

    releaseResourcesProgress = attribute(
        dtype="DevUShort",
        label="releaseResourcesProgress",
        max_value=100,
        min_value=0,
        doc="The percentage progress of the command in the [0,100].",
    )
    """Device attribute."""

    releaseResourcesTimeoutExpiredFlag = attribute(
        dtype="DevBoolean",
        label="timeoutExpiredFlag",
        doc="Flag reporting  command timeout expiration.",
    )
    """Device attribute."""

    # ---------------
    # General methods
    # ---------------

    def init_command_objects(self):
        """Set up the command objects."""
        super().init_command_objects()

        self.register_command_object(
            "ConfigureScan",
            self.ConfigureScanCommand(
                self._command_tracker,
                self.component_manager,
                callback=lambda running: self.obs_state_model.perform_action(
                    f"configure_{'invoked' if running else 'completed'}"
                ),
                logger=self.logger,
            ),
        )
        self.register_command_object(
            "GoToIdle",
            SubmittedSlowCommand(
                "GoToIdle",
                self._command_tracker,
                self.component_manager,
                "deconfigure",
                logger=self.logger,
            ),
        )

    class InitCommand(SKASubarray.InitCommand):
        """A class for the CspSubElementObsDevice's init_device() "command"."""

        def do(self):
            """
            Stateless hook for device initialisation.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            super().do()

            self._device._scan_id = 0

            self._device._sdp_addresses = {
                "outputHost": [],
                "outputMac": [],
                "outputPort": [],
            }
            self._device._sdp_links_active = [
                False,
            ]
            self._device._sdp_output_data_rate = 0.0

            self._device._config_id = ""

            # JSON string, deliberately left in Tango layer
            self._device._last_scan_configuration = ""

            # _list_of_devices_completed_task: for each task/command reports
            # the list of the devices that successfully completed the task.
            # Implemented as a defualt dictionary:
            # keys: the command name in lower case (configurescan, assignresources, etc.)
            # values: the list of devices' FQDN
            self._device._list_of_devices_completed_task = defaultdict(list)

            # _cmd_progress: command execution's progress percentage
            # implemented as a default dictionary:
            # keys: the command name in lower case(configurescan,..)
            # values: the progress percentage (default 0)
            self._device._cmd_progress = defaultdict(int)

            # _cmd_maximun_duration: command execution's expected maximum duration (sec.)
            # implemented as a default dictionary:
            # keys: the command name in lower case(configurescan, assignresources,..)
            # values: the expected maximum duration in sec.
            self._device._cmd_maximum_duration = defaultdict(float)

            # _cmd_measure_duration: command execution's measured duration (sec.)
            # implemented as a default dictionary:
            # keys: the command name in lower case(configurescan, assignresources,..)
            # values: the measured execution time (sec.)
            self._device._cmd_measured_duration = defaultdict(float)

            # _timeout_expired: boolean flag to signal timeout during command execution.
            # To check and reset before a command execution.
            # keys: the command name in lower case(configurescan, assignresources,..)
            # values: True/False
            self._device._timeout_expired = defaultdict(bool)
            # configure the flags to push event from the device server
            self._device.set_change_event("configureScanTimeoutExpiredFlag", True, True)
            self._device.set_archive_event(
                "configureScanTimeoutExpiredFlag", True, True
            )
            self._device.set_change_event(
                "assignResourcesTimeoutExpiredFlag", True, True
            )
            self._device.set_archive_event(
                "assignResourcesTimeoutExpiredFlag", True, True
            )
            self._device.set_change_event(
                "releaseResourcesTimeoutExpiredFlag", True, True
            )
            self._device.set_archive_event(
                "releaseResourcesTimeoutExpiredFlag", True, True
            )

            message = "CspSubElementSubarray Init command completed OK"
            self._device.logger.info(message)
            self._completed()
            return (ResultCode.OK, message)

    def always_executed_hook(self):
        """
        Perform actions that are executed before every device command.

        This is a Tango hook.
        """
        # PROTECTED REGION ID(CspSubElementSubarray.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  CspSubElementSubarray.always_executed_hook

    def delete_device(self):
        """
        Clean up any resources prior to device deletion.

        This method is a Tango hook that is called by the device
        destructor and by the device Init command. It allows for any
        memory or other resources allocated in the init_device method to
        be released prior to device deletion.
        """
        # PROTECTED REGION ID(CspSubElementSubarray.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  CspSubElementSubarray.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_scanID(self):
        # PROTECTED REGION ID(CspSubElementSubarray.scanID_read) ENABLED START #
        """Return the scanID attribute."""
        return self.component_manager.scan_id
        # PROTECTED REGION END #    //  CspSubElementSubarray.scanID_read

    def read_configurationID(self):
        # PROTECTED REGION ID(CspSubElementSubarray.configurationID_read) ENABLED START #
        """Return the configurationID attribute."""
        return self.component_manager.config_id
        # PROTECTED REGION END #    //  CspSubElementSubarray.configurationID_read

    def read_sdpDestinationAddresses(self):
        # PROTECTED REGION ID(CspSubElementSubarray.sdpDestinationAddresses_read) ENABLED START #
        """Return the sdpDestinationAddresses attribute."""
        return self._sdp_addresses
        # PROTECTED REGION END #    //  CspSubElementSubarray.sdpDestinationAddresses_read

    def write_sdpDestinationAddresses(self, value):
        # PROTECTED REGION ID(CspSubElementSubarray.sdpDestinationAddresses_write) ENABLED START #
        """Set the sdpDestinationAddresses attribute."""
        self._sdp_addresses = value
        # PROTECTED REGION END #    //  CspSubElementSubarray.sdpDestinationAddresses_write

    def read_outputDataRateToSdp(self):
        # PROTECTED REGION ID(CspSubElementSubarray.outputDataRateToSdp_read) ENABLED START #
        """Return the outputDataRateToSdp attribute."""
        return self._sdp_output_data_rate
        # PROTECTED REGION END #    //  CspSubElementSubarray.outputDataRateToSdp_read

    def read_lastScanConfiguration(self):
        # PROTECTED REGION ID(CspSubElementSubarray.lastScanConfiguration_read) ENABLED START #
        """Return the lastScanConfiguration attribute."""
        return self._last_scan_configuration
        # PROTECTED REGION END #    //  CspSubElementSubarray.lastScanConfiguration_read

    def read_configureScanMeasuredDuration(self):
        # PROTECTED REGION ID(CspSubElementSubarray.configureScanMeasuredDuration_read) ENABLED START #
        """Return the configureScanMeasuredDuration attribute."""
        return self._cmd_measured_duration["configurescan"]
        # PROTECTED REGION END #    //  CspSubElementSubarray.configureScanMeasuredDuration_read

    def read_configureScanTimeoutExpiredFlag(self):
        # PROTECTED REGION ID(CspSubElementSubarray.configureScanTimeoutExpiredFlag_read) ENABLED START #
        """Return the configureScanTimeoutExpiredFlag attribute."""
        return self._timeout_expired["configurescan"]
        # PROTECTED REGION END #    //  CspSubElementSubarray.configureScanTimeoutExpiredFlag_read

    def read_listOfDevicesCompletedTasks(self):
        # PROTECTED REGION ID(CspSubElementSubarray.listOfDevicesCompletedTasks_read) ENABLED START #
        """Return the listOfDevicesCompletedTasks attribute."""
        dict_to_string = json.dumps(self._list_of_devices_completed_task)
        return dict_to_string
        # PROTECTED REGION END #    //  CspSubElementSubarray.listOfDevicesCompletedTasks_read

    def read_assignResourcesMaximumDuration(self):
        # PROTECTED REGION ID(CspSubElementSubarray.assignResourcesMaximumDuration_read) ENABLED START #
        """Return the assignResourcesMaximumDuration attribute."""
        return self._cmd_maximum_duration["assignresources"]
        # PROTECTED REGION END #    //  CspSubElementSubarray.assignResourcesMaximumDuration_read

    def write_assignResourcesMaximumDuration(self, value):
        # PROTECTED REGION ID(CspSubElementSubarray.assignResourcesMaximumDuration_write) ENABLED START #
        """Set the assignResourcesMaximumDuration attribute."""
        self._cmd_maximum_duration["assignresources"] = value
        # PROTECTED REGION END #    //  CspSubElementSubarray.assignResourcesMaximumDuration_write

    def read_assignResourcesMeasuredDuration(self):
        # PROTECTED REGION ID(CspSubElementSubarray.assignResourcesMeasuredDuration_read) ENABLED START #
        """Return the assignResourcesMeasuredDuration attribute."""
        return self._cmd_measured_duration["assignresources"]
        # PROTECTED REGION END #    //  CspSubElementSubarray.assignResourcesMeasuredDuration_read

    def read_assignResourcesProgress(self):
        # PROTECTED REGION ID(CspSubElementSubarray.assignResourcesProgress_read) ENABLED START #
        """Return the assignResourcesProgress attribute."""
        return self._cmd_progress["assignresources"]
        # PROTECTED REGION END #    //  CspSubElementSubarray.assignResourcesProgress_read

    def read_assignResourcesTimeoutExpiredFlag(self):
        # PROTECTED REGION ID(CspSubElementSubarray.assignResourcesTimeoutExpiredFlag_read) ENABLED START #
        """Return the assignResourcesTimeoutExpiredFlag attribute."""
        return self._timeout_expired["assignresources"]
        # PROTECTED REGION END #    //  CspSubElementSubarray.assignResourcesTimeoutExpiredFlag_read

    def read_releaseResourcesMaximumDuration(self):
        # PROTECTED REGION ID(CspSubElementSubarray.releaseResourcesMaximumDuration_read) ENABLED START #
        """Return the releaseResourcesMaximumDuration attribute."""
        return self._cmd_maximum_duration["releaseresources"]
        # PROTECTED REGION END #    //  CspSubElementSubarray.releaseResourcesMaximumDuration_read

    def write_releaseResourcesMaximumDuration(self, value):
        # PROTECTED REGION ID(CspSubElementSubarray.releaseResourcesMaximumDuration_write) ENABLED START #
        """Set the releaseResourcesMaximumDuration attribute."""
        self._cmd_maximum_duration["releaseresources"] = value
        # PROTECTED REGION END #    //  CspSubElementSubarray.releaseResourcesMaximumDuration_write

    def read_releaseResourcesMeasuredDuration(self):
        # PROTECTED REGION ID(CspSubElementSubarray.releaseResourcesMeasuredDuration_read) ENABLED START #
        """Return the releaseResourcesMeasuredDuration attribute."""
        return self._cmd_measured_duration["releaseresources"]
        # PROTECTED REGION END #    //  CspSubElementSubarray.releaseResourcesMeasuredDuration_read

    def read_releaseResourcesProgress(self):
        # PROTECTED REGION ID(CspSubElementSubarray.releaseResourcesProgress_read) ENABLED START #
        """Return the releaseResourcesProgress attribute."""
        return self._cmd_progress["releaseresources"]
        # PROTECTED REGION END #    //  CspSubElementSubarray.releaseResourcesProgress_read

    def read_releaseResourcesTimeoutExpiredFlag(self):
        # PROTECTED REGION ID(CspSubElementSubarray.releaseResourcesTimeoutExpiredFlag_read) ENABLED START #
        """Return the releaseResourcesTimeoutExpiredFlag attribute."""
        return self._timeout_expired["releaseresources"]
        # PROTECTED REGION END #    //  CspSubElementSubarray.releaseResourcesTimeoutExpiredFlag_read

    def read_sdpLinkActive(self):
        # PROTECTED REGION ID(CspSubElementSubarray.sdpLinkActive_read) ENABLED START #
        """Return the sdpLinkActive attribute."""
        return (False,)
        # PROTECTED REGION END #    //  CspSubElementSubarray.sdpLinkActive_read

    # --------
    # Commands
    # --------

    class ConfigureScanCommand(SubmittedSlowCommand):
        """A class for the CspSubElementObsDevices's ConfigureScan command."""

        def __init__(self, command_tracker, component_manager, callback, logger=None):
            """
            Initialise a new ConfigureScanCommand instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: callback to be called when this command
                states and finishes
            :param logger: a logger for this command object to yuse
            """
            super().__init__(
                "ConfigureScan",
                command_tracker,
                component_manager,
                "configure",
                callback=callback,
                logger=logger,
            )

        def validate_input(self, argin):
            """
            Validate the configuration parameters against allowed values, as needed.

            :param argin: The JSON formatted string with configuration for the device.
            :type argin: 'DevString'
            :return: A tuple containing a return code and a string message.
            :rtype: (ResultCode, str)
            """
            try:
                configuration_dict = json.loads(argin)
                _ = configuration_dict["id"]
            except (KeyError, JSONDecodeError) as err:
                msg = f"Validate configuration failed with error:{err}"
                self.logger.error(msg)
                return (None, ResultCode.FAILED, msg)
            except Exception as other_errs:
                msg = f"Validate configuration failed with unknown error:{other_errs}"
                self.logger.error(msg)
                return (None, ResultCode.FAILED, msg)

            return (
                configuration_dict,
                ResultCode.OK,
                "ConfigureScan arguments validation successful",
            )

    def is_ConfigureScan_allowed(self):
        """
        Return whether the `Configure` command may be called in the current state.

        :return: whether the command may be called in the current device
            state
        :rtype: bool
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "ConfigureScan not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state not in [ObsState.IDLE, ObsState.READY]:
            raise StateModelError(
                f"ConfigureScan command not permitted in observation state {self._obs_state.name}"
            )
        return True

    @command(
        dtype_in="DevString",
        doc_in="A Json-encoded string with the scan configuration.",
        dtype_out="DevVarLongStringArray",
        doc_out="A tuple containing a return code and a string message indicating status."
        "The message is for information purpose only.",
    )
    @DebugIt()
    def ConfigureScan(self, argin):
        # PROTECTED REGION ID(CspSubElementSubarray.ConfigureScan) ENABLED START #
        """
        Configure a complete scan for the subarray.

        :param argin: JSON formatted string with the scan configuration.
        :type argin: 'DevString'

        :return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        :rtype: (ResultCode, str)
        """
        handler = self.get_command_object("ConfigureScan")

        (configuration, result_code, message) = handler.validate_input(argin)
        if result_code == ResultCode.OK:
            # store the configuration on command success
            self._last_scan_configuration = argin
            (result_code, message) = handler(configuration)

        return [[result_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementSubarray.Configure

    def is_Configure_allowed(self):
        """
        Return whether the `Configure` command may be called in the current state.

        :return: whether the command may be called in the current device
            state
        :rtype: bool
        """
        return self.is_ConfigureScan_allowed()

    @command(
        dtype_in="DevString",
        doc_in="A Json-encoded string with the scan configuration.",
        dtype_out="DevVarLongStringArray",
        doc_out="A tuple containing a return code and a string message indicating status."
        "The message is for information purpose only.",
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(CspSubElementSubarray.Configure) ENABLED START #
        """
        Redirect to ConfigureScan method. Configure a complete scan for the subarray.

        :param argin: JSON configuration string

        :return:'DevVarLongStringArray'
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        """
        return self.ConfigureScan(argin)
        # PROTECTED REGION END #    //  CspSubElementSubarray.Configure

    def is_GoToIdle_allowed(self):
        """
        Return whether the `GoToIdle` command may be called in the current device state.

        :return: whether the command may be called in the current device
            state
        :rtype: bool
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "ConfigureScan not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state not in [ObsState.IDLE, ObsState.READY]:
            raise StateModelError(
                f"GoToIdle command not permitted in observation state {self._obs_state.name}"
            )
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="A tuple containing a return code and a string  message indicating status."
        "The message is for information purpose only.",
    )
    @DebugIt()
    def GoToIdle(self):
        # PROTECTED REGION ID(CspSubElementSubarray.GoToIdle) ENABLED START #
        """
        Transit the subarray from READY to IDLE obsState.

        :return:'DevVarLongStringArray'
            A tuple containing a return code and a string  message indicating status.
            The message is for information purpose only.
        """
        self._last_scan_configuration = ""

        handler = self.get_command_object("GoToIdle")
        (result_code, message) = handler()
        return [[result_code], [message]]

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="A tuple containing a return code and a string  message indicating status."
        "The message is for information purpose only.",
    )
    @DebugIt()
    def End(self):
        # PROTECTED REGION ID(CspSubElementSubarray.End) ENABLED START #
        """
        Transit the subarray from READY to IDLE obsState. Redirect to GoToIdle command.

        :return:'DevVarLongStringArray'
            A tuple containing a return code and a string  message indicating status.
            The message is for information purpose only.
        """
        return self.GoToIdle()
        # PROTECTED REGION END #    //  CspSubElementSubarray.End


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Run the CspSubElementSubarray module."""
    # PROTECTED REGION ID(CspSubElementSubarray.main) ENABLED START #
    return run((CspSubElementSubarray,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspSubElementSubarray.main


if __name__ == "__main__":
    main()
