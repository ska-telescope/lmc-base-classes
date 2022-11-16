# type: ignore
# pylint: skip-file  # TODO: Incrementally lint this repo
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubElementObsDevice project
#

"""
CspSubElementObsDevice.

General observing device for SKA CSP Subelement.
"""

import functools
import json
from json.decoder import JSONDecodeError
from typing import Tuple

from ska_control_model import ObsState, TaskStatus
from tango import DebugIt
from tango.server import attribute, command, device_property, run

from ska_tango_base.commands import ResultCode, SlowCommand, SubmittedSlowCommand
from ska_tango_base.csp.obs.obs_state_model import CspSubElementObsStateModel
from ska_tango_base.faults import StateModelError
from ska_tango_base.obs import SKAObsDevice

__all__ = ["CspSubElementObsDevice", "main"]


class CspSubElementObsDevice(SKAObsDevice):
    """
    General observing device for SKA CSP Subelement.

    **Properties:**

    - Device Property
        DeviceID
            - Identification number of the observing device.
            - Type:'DevUShort'
    """

    # -----------------
    # Device Properties
    # -----------------

    DeviceID = device_property(dtype="DevUShort", default_value=1)

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

    deviceID = attribute(
        dtype="DevUShort",
        label="deviceID",
        doc="The observing device ID.",
    )
    """Device attribute."""

    lastScanConfiguration = attribute(
        dtype="DevString",
        label="lastScanConfiguration",
        doc="The last valid scan configuration.",
    )
    """Device attribute."""

    sdpDestinationAddresses = attribute(
        dtype="DevString",
        label="sdpDestinationAddresses",
        doc=(
            "JSON formatted string\n"
            "Report the list of all the SDP addresses provided by SDP to receive the "
            "output products.\n"
            "Specifies the Mac, IP, Port for each resource:\n"
            "CBF: visibility channels\n"
            "PSS ? Pss pipelines\n"
            "PST ? PSTBeam\n"
            "Not used by al CSP Sub-element observing device (for ex. Mid CBF VCCs)"
        ),
    )
    """Device attribute."""

    sdpLinkCapacity = attribute(
        dtype="DevFloat",
        label="sdpLinkCapacity",
        doc="The SDP link capavity in GB/s.",
    )
    """Device attribute."""

    sdpLinkActive = attribute(
        dtype=("DevBoolean",),
        max_dim_x=100,
        label="sdpLinkActive",
        doc="Flag reporting if the SDP link is active.\nTrue: active\nFalse:down",
    )
    """Device attribute."""

    healthFailureMessage = attribute(
        dtype="DevString",
        label="healthFailureMessage",
        doc="Message providing info about device health failure.",
    )
    """Device attribute."""

    # ---------------
    # General methods
    # ---------------

    def _init_state_model(self):
        """Set up the state model for the device."""
        super()._init_state_model()
        self.obs_state_model = CspSubElementObsStateModel(
            logger=self.logger,
            callback=self._update_obs_state,
        )

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
            "Scan",
            self.ScanCommand(
                self._command_tracker,
                self.component_manager,
                logger=self.logger,
            ),
        )

        def _callback(hook, running):
            action = "invoked" if running else "completed"
            self.obs_state_model.perform_action(f"{hook}_{action}")

        for (command_name, method_name, state_model_hook) in [
            ("ObsReset", "obsreset", "obsreset"),
            ("EndScan", "end_scan", None),
            ("GoToIdle", "deconfigure", None),
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

    class InitCommand(SKAObsDevice.InitCommand):
        """A class for the CspSubElementObsDevice's init_device() "command"."""

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            super().do()

            self._device._obs_state = ObsState.IDLE

            self._device._sdp_addresses = {
                "outputHost": [],
                "outputMac": [],
                "outputPort": [],
            }
            # a sub-element obsdevice can have more than one link to the SDP
            # (for ex. Mid.CBF FSP)
            self._device._sdp_links_active = [
                False,
            ]
            self._device._sdp_links_capacity = 0.0

            # JSON string, deliberately left in Tango layer
            self._device._last_scan_configuration = ""
            self._device._health_failure_msg = ""

            message = "CspSubElementObsDevice Init command completed OK"
            self.logger.info(message)
            self._completed()
            return (ResultCode.OK, message)

    # ------------------
    # Attributes methods
    # ------------------
    def read_scanID(self):
        """
        Return the scanID attribute.

        :return: the scanID attribute.
        """
        return self.component_manager.scan_id

    def read_configurationID(self):
        """
        Return the configurationID attribute.

        :return: the configurationID attribute.
        """
        return self.component_manager.config_id

    def read_deviceID(self):
        """
        Return the deviceID attribute.

        :return: the deviceID attribute.
        """
        return self.DeviceID

    def read_lastScanConfiguration(self):
        """
        Return the lastScanConfiguration attribute.

        :return: the lastScanConfiguration attribute.
        """
        return self._last_scan_configuration

    def read_sdpDestinationAddresses(self):
        """
        Return the sdpDestinationAddresses attribute.

        :return: the sdpDestinationAddresses attribute.
        """
        return json.dumps(self._sdp_addresses)

    def read_sdpLinkCapacity(self):
        """
        Return the sdpLinkCapacity attribute.

        :return: the sdpLinkCapacity attribute.
        """
        return self._sdp_links_capacity

    def read_sdpLinkActive(self):
        """
        Return the sdpLinkActive attribute.

        :return: the sdpLinkActive attribute.
        """
        return self._sdp_links_active

    def read_healthFailureMessage(self):
        """
        Return the healthFailureMessage attribute.

        :return: the healthFailureMessage attribute.
        """
        return self._health_failure_msg

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
                "configure_scan",
                callback=callback,
                logger=logger,
            )

        def validate_input(self, argin: str) -> Tuple[dict, ResultCode, str]:
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
            except Exception as other_errs:
                msg = f"Validate configuration failed with unknown error: {other_errs}"
                return (None, ResultCode.FAILED, msg)

            return (
                configuration_dict,
                ResultCode.OK,
                "ConfigureScan arguments validation successful",
            )

    class ScanCommand(SubmittedSlowCommand):
        """A class for the CspSubElementObsDevices's Scan command."""

        def __init__(self, command_tracker, component_manager, logger=None):
            """
            Initialise a new ScanCommand instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param logger: a logger for this command object to yuse
            """
            super().__init__(
                "Scan",
                command_tracker,
                component_manager,
                "scan",
                logger=logger,
            )

        def validate_input(self, argin: str) -> Tuple[ResultCode, str]:
            """
            Validate the command input argument.

            :param argin: the scan id
            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            if not argin.isdigit():
                msg = f"Input argument '{argin}' is not an integer"
                self.logger.error(msg)
                return (ResultCode.FAILED, msg)
            return (ResultCode.OK, "Scan arguments validation successfull")

    class AbortCommand(SlowCommand):
        """A class for the CspSubElementObsDevices's Abort command."""

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

        def do(self) -> Tuple[ResultCode, str]:
            """
            Stateless hook for Abort() command functionality.

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

    def is_ConfigureScan_allowed(self) -> bool:
        """
        Return whether the `ConfigureScan` command may be called in the current state.

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
        doc_in="JSON formatted string with the scan configuration.",
        dtype_out="DevVarLongStringArray",
        doc_out=(
            "A tuple containing a return code and a string message "
            "indicating status. The message is for information purpose "
            "only."
        ),
    )
    @DebugIt()
    def ConfigureScan(self, argin: str) -> Tuple[ResultCode, str]:
        """
        Configure the observing device parameters for the current scan.

        :param argin: JSON formatted string with the scan configuration.

        :return: A tuple containing a return code and a string message
            indicating status. The message is for information purpose
            only.
        """
        handler = self.get_command_object("ConfigureScan")

        (configuration, result_code, message) = handler.validate_input(argin)
        if result_code == ResultCode.OK:
            # store the configuration on command success
            self._last_scan_configuration = argin
            (result_code, message) = handler(configuration)

        return [[result_code], [message]]

    def is_Scan_allowed(self) -> bool:
        """
        Return whether the `Scan` command may be called in the current device state.

        :raises StateModelError: if the command is not allowed

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "Scan not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state != ObsState.READY:
            raise StateModelError(
                "Scan command not permitted in observation state "
                f"{self._obs_state.name}"
            )
        return True

    @command(
        dtype_in="DevString",
        doc_in="A string with the scan ID",
        dtype_out="DevVarLongStringArray",
        doc_out=(
            "A tuple containing a return code and a string message "
            "indicating status. The message is for information purpose "
            "only."
        ),
    )
    @DebugIt()
    def Scan(self, argin: str) -> Tuple[ResultCode, str]:
        """
        Start an observing scan.

        :param argin: A string with the scan ID

        :return: A tuple containing a return code and a string message
            indicating status. The message is for information purpose
            only.
        """
        handler = self.get_command_object("Scan")

        try:
            scan_id = int(argin)
        except ValueError:
            return [[ResultCode.FAILED], ["scan ID is not an integer."]]

        (result_code, message) = handler(scan_id)
        return [[result_code], [message]]

    def is_EndScan_allowed(self) -> bool:
        """
        Return whether the `EndScan` command may be called in the current device state.

        :raises StateModelError: if the command is not allowed

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "EndScan not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state != ObsState.SCANNING:
            raise StateModelError(
                "EndScan command not permitted in observation state "
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
    def EndScan(self) -> Tuple[ResultCode, str]:
        """
        End a running scan.

        :return: A tuple containing a return code and a string message
            indicating status. The message is for information purpose
            only.
        """
        handler = self.get_command_object("EndScan")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_GoToIdle_allowed(self) -> bool:
        """
        Return whether the `GoToIdle` command may be called in the current device state.

        :raises StateModelError: if the command is not allowed

        :return: whether the command may be called in the current device
            state
        """
        # If we return False here, Tango will raise an exception that incorrectly blames
        # refusal on device state.
        # e.g. "GoToIdle not allowed when the device is in ON state".
        # So let's raise an exception ourselves.
        if self._obs_state != ObsState.READY:
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
    def GoToIdle(self) -> Tuple[ResultCode, str]:
        """
        Transit the device from READY to IDLE obsState.

        :return: A tuple containing a return code and a string message
            indicating status. The message is for information purpose
            only.
        """
        self._last_scan_configuration = ""

        handler = self.get_command_object("GoToIdle")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_ObsReset_allowed(self) -> bool:
        """
        Return whether the `ObsReset` command may be called in the current device state.

        :raises StateModelError: if the command is not allowed

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

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out=(
            "A tuple containing a return code and a string message "
            "indicating status. The message is for information purpose "
            "only."
        ),
    )
    @DebugIt()
    def ObsReset(self) -> Tuple[ResultCode, str]:
        """
        Reset the observing device from a FAULT/ABORTED obsState to IDLE.

        :return: A tuple containing a return code and a string message
            indicating status. The message is for information purpose
            only.
        """
        handler = self.get_command_object("ObsReset")
        (result_code, message) = handler()
        return [[result_code], [message]]

    def is_Abort_allowed(self) -> bool:
        """
        Return whether the `Abort` command may be called in the current device state.

        :raises StateModelError: if the command is not allowed

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
                "Abort command not permitted in observation state "
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
    def Abort(self) -> Tuple[ResultCode, str]:
        """
        Abort the current observing process and move to ABORTED obsState.

        :return: A tuple containing a return code and a string message
            indicating status. The message is for information purpose
            only.
        """
        handler = self.get_command_object("Abort")
        (result_code, message) = handler()
        return [[result_code], [message]]

    # ----------
    # Callbacks
    # ----------

    def _component_state_changed(
        self,
        fault=None,
        power=None,
        configured=None,
        scanning=None,
    ):
        super()._component_state_changed(fault=fault, power=power)

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
    return run((CspSubElementObsDevice,), args=args or None, **kwargs)


if __name__ == "__main__":
    main()
