# flake8: noqa
# pylint: skip-file  # TODO: Incrementally lint this repo
# type: ignore
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

import json
from collections import defaultdict
from json.decoder import JSONDecodeError

from ska_control_model import ObsState
from tango import AttrWriteType, DebugIt
from tango.server import attribute, command, run

from ska_tango_base.commands import ResultCode, SubmittedSlowCommand
from ska_tango_base.faults import StateModelError
from ska_tango_base.subarray import SKASubarray

__all__ = ["CspSubElementSubarray", "main"]


class CspSubElementSubarray(SKASubarray):
    """Subarray device for SKA CSP SubElement."""

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
        doc=(
            "JSON formatted string.\n"
            "Report the list of all the SDP addresses provided by SDP to receive the "
            "output products.\n"
            "Specifies the Mac, IP, Port for each resource:CBF visibility channels, "
            "Pss pipelines, PSTBeam"
        ),
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
        doc=(
            "JSON formatted string reporting for each task/command the list of "
            "devices that completed successfully the task.\n"
            "Ex.\n"
            "{``cmd1``: [``device1``, ``device2``],\n"
            "``cmd2``: [``device2``, ``device3``]}"
        ),
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
        doc="Flag reporting AssignResources command timeout expiration.",
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

    # ------------------
    # Attributes methods
    # ------------------

    def read_scanID(self):
        """Return the scanID attribute."""
        return self.component_manager.scan_id

    def read_configurationID(self):
        """Return the configurationID attribute."""
        return self.component_manager.config_id

    def read_sdpDestinationAddresses(self):
        """Return the sdpDestinationAddresses attribute."""
        return self._sdp_addresses

    def write_sdpDestinationAddresses(self, value):
        """Set the sdpDestinationAddresses attribute."""
        self._sdp_addresses = value

    def read_outputDataRateToSdp(self):
        """Return the outputDataRateToSdp attribute."""
        return self._sdp_output_data_rate

    def read_lastScanConfiguration(self):
        """Return the lastScanConfiguration attribute."""
        return self._last_scan_configuration

    def read_configureScanMeasuredDuration(self):
        """Return the configureScanMeasuredDuration attribute."""
        return self._cmd_measured_duration["configurescan"]

    def read_configureScanTimeoutExpiredFlag(self):
        """Return the configureScanTimeoutExpiredFlag attribute."""
        return self._timeout_expired["configurescan"]

    def read_listOfDevicesCompletedTasks(self):
        """Return the listOfDevicesCompletedTasks attribute."""
        dict_to_string = json.dumps(self._list_of_devices_completed_task)
        return dict_to_string

    def read_assignResourcesMaximumDuration(self):
        """Return the assignResourcesMaximumDuration attribute."""
        return self._cmd_maximum_duration["assignresources"]

    def write_assignResourcesMaximumDuration(self, value):
        """Set the assignResourcesMaximumDuration attribute."""
        self._cmd_maximum_duration["assignresources"] = value

    def read_assignResourcesMeasuredDuration(self):
        """Return the assignResourcesMeasuredDuration attribute."""
        return self._cmd_measured_duration["assignresources"]

    def read_assignResourcesProgress(self):
        """Return the assignResourcesProgress attribute."""
        return self._cmd_progress["assignresources"]

    def read_assignResourcesTimeoutExpiredFlag(self):
        """Return the assignResourcesTimeoutExpiredFlag attribute."""
        return self._timeout_expired["assignresources"]

    def read_releaseResourcesMaximumDuration(self):
        """Return the releaseResourcesMaximumDuration attribute."""
        return self._cmd_maximum_duration["releaseresources"]

    def write_releaseResourcesMaximumDuration(self, value):
        """Set the releaseResourcesMaximumDuration attribute."""
        self._cmd_maximum_duration["releaseresources"] = value

    def read_releaseResourcesMeasuredDuration(self):
        """Return the releaseResourcesMeasuredDuration attribute."""
        return self._cmd_measured_duration["releaseresources"]

    def read_releaseResourcesProgress(self):
        """Return the releaseResourcesProgress attribute."""
        return self._cmd_progress["releaseresources"]

    def read_releaseResourcesTimeoutExpiredFlag(self):
        """Return the releaseResourcesTimeoutExpiredFlag attribute."""
        return self._timeout_expired["releaseresources"]

    def read_sdpLinkActive(self):
        """Return the sdpLinkActive attribute."""
        return (False,)

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
            :type argin: str
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
        """
        Configure a complete scan for the subarray.

        :param argin: JSON formatted string with the scan configuration.
        :type argin: str

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
        """
        Redirect to ConfigureScan method. Configure a complete scan for the subarray.

        :param argin: JSON configuration string

        :return:'DevVarLongStringArray'
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        """
        return self.ConfigureScan(argin)

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
        """
        Transit the subarray from READY to IDLE obsState. Redirect to GoToIdle command.

        :return:'DevVarLongStringArray'
            A tuple containing a return code and a string  message indicating status.
            The message is for information purpose only.
        """
        return self.GoToIdle()


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Run the CspSubElementSubarray module."""
    return run((CspSubElementSubarray,), args=args, **kwargs)


if __name__ == "__main__":
    main()
