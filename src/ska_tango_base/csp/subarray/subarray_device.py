# pylint: disable=invalid-name
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
from __future__ import annotations

import json
import logging
from collections import defaultdict
from json.decoder import JSONDecodeError
from typing import Any, Callable, List, Optional, Tuple, cast

from ska_control_model import ObsState, ResultCode
from tango import AttrWriteType, DebugIt
from tango.server import attribute, command, run

from ...base import CommandTracker
from ...commands import SubmittedSlowCommand
from ...faults import StateModelError
from ...subarray.subarray_device import SKASubarray

__all__ = ["CspSubElementSubarray", "main"]

DevVarLongStringArrayType = Tuple[List[ResultCode], List[str]]


# TODO: This is an abstract class because it does not define
# `create_component_manager` and therefore inherits the abstract method from the
# base device. There's no point implementing `create_component_manager` because
# the SubarrayComponentManager is itself abstract.
# pylint: disable-next=abstract-method, too-many-public-methods
class CspSubElementSubarray(SKASubarray):
    # pylint: disable=attribute-defined-outside-init  # Tango devices have init_device
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

    def init_command_objects(self: CspSubElementSubarray) -> None:
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

    # pylint: disable-next=too-few-public-methods
    class InitCommand(SKASubarray.InitCommand):
        # pylint: disable=protected-access  # command classes are friend classes
        """A class for the CspSubElementObsDevice's init_device() "command"."""

        def do(
            self: CspSubElementSubarray.InitCommand,
            *args: Any,
            **kwargs: Any,
        ) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.

            :param args: positional arguments to this do method
            :param kwargs: keyword arguments to this do method

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            super().do(*args, **kwargs)

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
            # keys: the command name in lower case (configurescan,
            # assignresources, etc.)
            # values: the list of devices' FQDN
            self._device._list_of_devices_completed_task = defaultdict(list)

            # _cmd_progress: command execution's progress percentage
            # implemented as a default dictionary:
            # keys: the command name in lower case(configurescan,..)
            # values: the progress percentage (default 0)
            self._device._cmd_progress = defaultdict(int)

            # _cmd_maximun_duration: command execution's expected maximum
            # duration (sec.) implemented as a default dictionary:
            # keys: the command name in lower case (configurescan,
            # assignresources, ...)
            # values: the expected maximum duration in sec.
            self._device._cmd_maximum_duration = defaultdict(float)

            # _cmd_measure_duration: command execution's measured duration
            # (sec.) implemented as a default dictionary:
            # keys: the command name in lower case (configurescan,
            # assignresources, ...)
            # values: the measured execution time (sec.)
            self._device._cmd_measured_duration = defaultdict(float)

            # _timeout_expired: boolean flag to signal timeout during command
            # execution. To check and reset before a command execution.
            # keys: the command name in lower case (configurescan,
            # assignresources,..)
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
    def read_scanID(self: CspSubElementSubarray) -> int:
        """
        Return the scanID attribute.

        :return: the scanID attribute.
        """
        # TODO: Cannot cast this because the component manager class doesn't exist yet!
        return self.component_manager.scan_id  # type: ignore[attr-defined]

    def read_configurationID(self: CspSubElementSubarray) -> str:
        """
        Return the configurationID attribute.

        :return: the configurationID attribute.
        """
        # TODO: Cannot cast this because the component manager class doesn't exist yet!
        return self.component_manager.config_id  # type: ignore[attr-defined]

    def read_sdpDestinationAddresses(self: CspSubElementSubarray) -> str:
        """
        Return the sdpDestinationAddresses attribute.

        :return: the sdpDestinationAddresses attribute.
        """
        return self._sdp_addresses

    def write_sdpDestinationAddresses(self: CspSubElementSubarray, value: str) -> None:
        """
        Set the sdpDestinationAddresses attribute.

        :param value: the SDP destination addresses
        """
        self._sdp_addresses = value

    def read_outputDataRateToSdp(self: CspSubElementSubarray) -> float:
        """
        Return the outputDataRateToSdp attribute.

        :return: the outputDataRateToSdp attribute.
        """
        return self._sdp_output_data_rate

    def read_lastScanConfiguration(self: CspSubElementSubarray) -> str:
        """
        Return the lastScanConfiguration attribute.

        :return: the lastScanConfiguration attribute.
        """
        return self._last_scan_configuration

    def read_configureScanMeasuredDuration(self: CspSubElementSubarray) -> float:
        """
        Return the configureScanMeasuredDuration attribute.

        :return: the configureScanMeasuredDuration attribute.
        """
        return self._cmd_measured_duration["configurescan"]

    def read_configureScanTimeoutExpiredFlag(self: CspSubElementSubarray) -> bool:
        """
        Return the configureScanTimeoutExpiredFlag attribute.

        :return: the configureScanTimeoutExpiredFlag attribute.
        """
        return self._timeout_expired["configurescan"]

    def read_listOfDevicesCompletedTasks(self: CspSubElementSubarray) -> str:
        """
        Return the listOfDevicesCompletedTasks attribute.

        :return: the listOfDevicesCompletedTasks attribute.
        """
        dict_to_string = json.dumps(self._list_of_devices_completed_task)
        return dict_to_string

    def read_assignResourcesMaximumDuration(self: CspSubElementSubarray) -> float:
        """
        Return the assignResourcesMaximumDuration attribute.

        :return: the assignResourcesMaximumDuration attribute.
        """
        return self._cmd_maximum_duration["assignresources"]

    def write_assignResourcesMaximumDuration(
        self: CspSubElementSubarray, value: float
    ) -> None:
        """
        Set the assignResourcesMaximumDuration attribute.

        :param value: the new maximum duration
        """
        self._cmd_maximum_duration["assignresources"] = value

    def read_assignResourcesMeasuredDuration(self: CspSubElementSubarray) -> float:
        """
        Return the assignResourcesMeasuredDuration attribute.

        :return: the assignResourcesMeasuredDuration attribute.
        """
        return self._cmd_measured_duration["assignresources"]

    def read_assignResourcesProgress(self: CspSubElementSubarray) -> int:
        """
        Return the assignResourcesProgress attribute.

        :return: the assignResourcesProgress attribute.
        """
        return self._cmd_progress["assignresources"]

    def read_assignResourcesTimeoutExpiredFlag(self: CspSubElementSubarray) -> bool:
        """
        Return the assignResourcesTimeoutExpiredFlag attribute.

        :return: the assignResourcesTimeoutExpiredFlag attribute.
        """
        return self._timeout_expired["assignresources"]

    def read_releaseResourcesMaximumDuration(self: CspSubElementSubarray) -> float:
        """
        Return the releaseResourcesMaximumDuration attribute.

        :return: the releaseResourcesMaximumDuration attribute.
        """
        return self._cmd_maximum_duration["releaseresources"]

    def write_releaseResourcesMaximumDuration(
        self: CspSubElementSubarray, value: float
    ) -> None:
        """
        Set the releaseResourcesMaximumDuration attribute.

        :param value: the new maximum duration.
        """
        self._cmd_maximum_duration["releaseresources"] = value

    def read_releaseResourcesMeasuredDuration(self: CspSubElementSubarray) -> float:
        """
        Return the releaseResourcesMeasuredDuration attribute.

        :return: the releaseResourcesMeasuredDuration attribute.
        """
        return self._cmd_measured_duration["releaseresources"]

    def read_releaseResourcesProgress(self: CspSubElementSubarray) -> int:
        """
        Return the releaseResourcesProgress attribute.

        :return: the releaseResourcesProgress attribute.
        """
        return self._cmd_progress["releaseresources"]

    def read_releaseResourcesTimeoutExpiredFlag(self: CspSubElementSubarray) -> bool:
        """
        Return the releaseResourcesTimeoutExpiredFlag attribute.

        :return: the releaseResourcesTimeoutExpiredFlag attribute.
        """
        return self._timeout_expired["releaseresources"]

    def read_sdpLinkActive(self: CspSubElementSubarray) -> list[bool]:
        """
        Return the sdpLinkActive attribute.

        :return: the sdpLinkActive attribute.
        """
        return [False]

    # --------
    # Commands
    # --------

    class ConfigureScanCommand(SubmittedSlowCommand):
        """A class for the CspSubElementObsDevices's ConfigureScan command."""

        def __init__(  # type: ignore[no-untyped-def]
            self: CspSubElementSubarray.ConfigureScanCommand,
            command_tracker: CommandTracker,
            component_manager,  # Can't type-hint this because the class doesn't exist!
            callback: Callable,
            logger: Optional[logging.Logger] = None,
        ):
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

        def validate_input(
            self: CspSubElementSubarray.ConfigureScanCommand, argin: str
        ) -> Tuple[Optional[dict], ResultCode, str]:
            """
            Validate the configuration parameters against allowed values, as needed.

            :param argin: The JSON formatted string with configuration for the device.

            :return: A tuple containing a return code and a string message.
            """
            try:
                configuration_dict = json.loads(argin)
                _ = configuration_dict["id"]
            except (KeyError, JSONDecodeError) as err:
                msg = f"Validate configuration failed with error:{err}"
                self.logger.error(msg)
                return (None, ResultCode.FAILED, msg)
            except Exception as other_errs:  # pylint: disable=broad-except
                msg = f"Validate configuration failed with unknown error:{other_errs}"
                self.logger.error(msg)
                return (None, ResultCode.FAILED, msg)

            return (
                configuration_dict,
                ResultCode.OK,
                "ConfigureScan arguments validation successful",
            )

    def is_ConfigureScan_allowed(self: CspSubElementSubarray) -> bool:
        """
        Return whether the `Configure` command may be called in the current state.

        :raises StateModelError: if the command is not allowed

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "ConfigureScan not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state not in [ObsState.IDLE, ObsState.READY]:
            raise StateModelError(
                "ConfigureScan command not permitted in observation state "
                f"{self._obs_state.name}"
            )
        return True

    @command(
        dtype_in="DevString",
        doc_in="A Json-encoded string with the scan configuration.",
        dtype_out="DevVarLongStringArray",
        doc_out=(
            "A tuple containing a return code and a string message "
            "indicating status. The message is for information purpose "
            "only."
        ),
    )
    @DebugIt()
    def ConfigureScan(
        self: CspSubElementSubarray, argin: str
    ) -> DevVarLongStringArrayType:
        """
        Configure a complete scan for the subarray.

        :param argin: JSON formatted string with the scan configuration.

        :return:
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        """
        handler = cast(
            CspSubElementSubarray.ConfigureScanCommand,
            self.get_command_object("ConfigureScan"),
        )

        (configuration, result_code, message) = handler.validate_input(argin)
        if result_code == ResultCode.OK:
            # store the configuration on command success
            self._last_scan_configuration = argin
            (result_code, message) = handler(configuration)

        return ([result_code], [message])

    def is_Configure_allowed(self: CspSubElementSubarray) -> bool:
        """
        Return whether the `Configure` command may be called in the current state.

        :return: whether the command may be called in the current device
            state
        """
        return self.is_ConfigureScan_allowed()

    @command(
        dtype_in="DevString",
        doc_in="A Json-encoded string with the scan configuration.",
        dtype_out="DevVarLongStringArray",
        doc_out=(
            "A tuple containing a return code and a string message "
            "indicating status. The message is for information purpose "
            "only."
        ),
    )
    @DebugIt()
    def Configure(self: CspSubElementSubarray, argin: str) -> DevVarLongStringArrayType:
        """
        Redirect to ConfigureScan method. Configure a complete scan for the subarray.

        :param argin: JSON configuration string

        :return:'DevVarLongStringArray'
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        """
        return self.ConfigureScan(argin)

    def is_GoToIdle_allowed(self: CspSubElementSubarray) -> bool:
        """
        Return whether the `GoToIdle` command may be called in the current device state.

        :raises StateModelError: if the command is not allowed

        :return: whether the command may be called in the current device
            state. Can only return True, because an exception is raised
            in the case of False.
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "ConfigureScan not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state not in [ObsState.IDLE, ObsState.READY]:
            raise StateModelError(
                "GoToIdle command not permitted in observation state "
                f"{self._obs_state.name}"
            )
        return True

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out=(
            "A tuple containing a return code and a string message "
            "indicating status. The message is for information purpose "
            "only."
        ),
    )
    @DebugIt()
    def GoToIdle(self: CspSubElementSubarray) -> DevVarLongStringArrayType:
        """
        Transit the subarray from READY to IDLE obsState.

        :return:'DevVarLongStringArray'
            A tuple containing a return code and a string  message indicating status.
            The message is for information purpose only.
        """
        self._last_scan_configuration = ""

        handler = self.get_command_object("GoToIdle")
        (result_code, message) = handler()
        return ([result_code], [message])

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out=(
            "A tuple containing a return code and a string message "
            "indicating status. The message is for information purpose "
            "only."
        ),
    )
    @DebugIt()
    def End(self: CspSubElementSubarray) -> DevVarLongStringArrayType:
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


def main(*args: str, **kwargs: str) -> int:
    """
    Entry point for module.

    :param args: positional arguments
    :param kwargs: named arguments

    :return: exit code
    """
    return run((CspSubElementSubarray,), args=args or None, **kwargs)


if __name__ == "__main__":
    main()
