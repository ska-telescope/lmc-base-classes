# -*- coding: utf-8 -*-
#
# This file is part of the CspSubElementObsDevice project
#

""" CspSubElementObsDevice

General observing device for SKA CSP Subelement.
"""

# PROTECTED REGION ID(CspSubElementObsDevice.additionnal_import) ENABLED START #
import json
from json.decoder import JSONDecodeError

# Tango imports
from tango import DebugIt
from tango.server import run, attribute, command, device_property

# SKA specific imports
from ska_tango_base import SKAObsDevice
from ska_tango_base.commands import (
    ResultCode,
    CompletionCommand,
    ObservationCommand,
    ResponseCommand,
)
from ska_tango_base.control_model import ObsState
from ska_tango_base.csp.obs import CspObsComponentManager, CspSubElementObsStateModel


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
    # PROTECTED REGION ID(CspSubElementObsDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  CspSubElementObsDevice.class_variable

    # -----------------
    # Device Properties
    # -----------------

    DeviceID = device_property(
        dtype='DevUShort', default_value=1
    )

    # ----------
    # Attributes
    # ----------

    scanID = attribute(
        dtype='DevULong64',
        label="scanID",
        doc="The scan identification number to be inserted in the output\nproducts.",
    )
    """Device attribute."""

    configurationID = attribute(
        dtype='DevString',
        label="configurationID",
        doc="The configuration ID specified into the JSON configuration.",
    )
    """Device attribute."""

    deviceID = attribute(
        dtype='DevUShort',
        label="deviceID",
        doc="The observing device ID.",
    )
    """Device attribute."""

    lastScanConfiguration = attribute(
        dtype='DevString',
        label="lastScanConfiguration",
        doc="The last valid scan configuration.",
    )
    """Device attribute."""

    sdpDestinationAddresses = attribute(
        dtype='DevString',
        label="sdpDestinationAddresses",
        doc="JSON formatted string\nReport the list of all the SDP addresses provided by SDP"
            " to receive the output products.\nSpecifies the Mac, IP, Port for each resource:\nCBF:"
            " visibility channels\nPSS ? Pss pipelines\nPST ? PSTBeam\nNot used by al CSP Sub-element"
            " observing device (for ex. Mid CBF VCCs)",
    )
    """Device attribute."""

    sdpLinkCapacity = attribute(
        dtype='DevFloat',
        label="sdpLinkCapacity",
        doc="The SDP link capavity in GB/s.",
    )
    """Device attribute."""

    sdpLinkActive = attribute(
        dtype=('DevBoolean',),
        max_dim_x=100,
        label="sdpLinkActive",
        doc="Flag reporting if the SDP link is active.\nTrue: active\nFalse:down",
    )
    """Device attribute."""

    healthFailureMessage = attribute(
        dtype='DevString',
        label="healthFailureMessage",
        doc="Message providing info about device health failure.",
    )
    """Device attribute."""

    # ---------------
    # General methods
    # ---------------

    def _init_state_model(self):
        """
        Sets up the state model for the device
        """
        super()._init_state_model()
        self.obs_state_model = CspSubElementObsStateModel(
            logger=self.logger,
            callback=self._update_obs_state,
        )

    def create_component_manager(self):
        return CspObsComponentManager(self.op_state_model, self.obs_state_model)

    def init_command_objects(self):
        """
        Sets up the command objects
        """
        super().init_command_objects()

        for (command_name, command_class) in [
            ("ConfigureScan", self.ConfigureScanCommand),
            ("Scan", self.ScanCommand),
            ("EndScan", self.EndScanCommand),
            ("GoToIdle", self.GoToIdleCommand),
            ("Abort", self.AbortCommand),
            ("ObsReset", self.ObsResetCommand),
        ]:
            self.register_command_object(
                command_name,
                command_class(
                    self.component_manager,
                    self.op_state_model,
                    self.obs_state_model,
                    self.logger,
                )
            )

    class InitCommand(SKAObsDevice.InitCommand):
        """
        A class for the CspSubElementObsDevice's init_device() "command".
        """

        def do(self):
            """
            Stateless hook for device initialisation.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            super().do()

            device = self.target
            device._obs_state = ObsState.IDLE

            device._sdp_addresses = {"outputHost": [], "outputMac": [], "outputPort": []}
            # a sub-element obsdevice can have more than one link to the SDP
            # (for ex. Mid.CBF FSP)
            device._sdp_links_active = [False, ]
            device._sdp_links_capacity = 0.

            # JSON string, deliberately left in Tango layer
            device._last_scan_configuration = ''
            device._health_failure_msg = ''

            message = "CspSubElementObsDevice Init command completed OK"
            device.logger.info(message)
            return (ResultCode.OK, message)

    def always_executed_hook(self):
        """Method always executed before any Tango command is executed."""
        # PROTECTED REGION ID(CspSubElementObsDevice.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  CspSubElementObsDevice.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(CspSubElementObsDevice.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  CspSubElementObsDevice.delete_device
    # ------------------
    # Attributes methods
    # ------------------

    def read_scanID(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.scanID_read) ENABLED START #
        """Return the scanID attribute."""
        return self.component_manager.scan_id  #pylint: disable=no-member
        # PROTECTED REGION END #    //  CspSubElementObsDevice.scanID_read

    def read_configurationID(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.configurationID_read) ENABLED START #
        """Return the configurationID attribute."""
        return self.component_manager.config_id  #pylint: disable=no-member
        # PROTECTED REGION END #    //  CspSubElementObsDevice.configurationID_read

    def read_deviceID(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.deviceID_read) ENABLED START #
        """Return the deviceID attribute."""
        return self.DeviceID
        # PROTECTED REGION END #    //  CspSubElementObsDevice.deviceID_read

    def read_lastScanConfiguration(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.lastScanConfiguration_read) ENABLED START #
        """Return the lastScanConfiguration attribute."""
        return self._last_scan_configuration
        # PROTECTED REGION END #    //  CspSubElementObsDevice.lastScanConfiguration_read

    def read_sdpDestinationAddresses(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.sdpDestinationAddresses_read) ENABLED START #
        """Return the sdpDestinationAddresses attribute."""
        return json.dumps(self._sdp_addresses)
        # PROTECTED REGION END #    //  CspSubElementObsDevice.sdpDestinationAddresses_read

    def read_sdpLinkCapacity(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.sdpLinkCapacity_read) ENABLED START #
        """Return the sdpLinkCapacity attribute."""
        return self._sdp_links_capacity
        # PROTECTED REGION END #    //  CspSubElementObsDevice.sdpLinkCapacity_read

    def read_sdpLinkActive(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.sdpLinkActive_read) ENABLED START #
        """Return the sdpLinkActive attribute."""
        return self._sdp_links_active
        # PROTECTED REGION END #    //  CspSubElementObsDevice.sdpLinkActive_read

    def read_healthFailureMessage(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.healthFailureMessage_read) ENABLED START #
        """Return the healthFailureMessage attribute."""
        return self._health_failure_msg
        # PROTECTED REGION END #    //  CspSubElementObsDevice.healthFailureMessage_read

    # --------
    # Commands
    # --------

    class ConfigureScanCommand(ObservationCommand, ResponseCommand, CompletionCommand):
        """
        A class for the CspSubElementObsDevices's ConfigureScan command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for ConfigureScanCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`CspSubElementObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "configure", op_state_model, logger=logger
            )

        def do(self, argin):
            """
            Stateless hook for ConfigureScan() command functionality.

            :param argin: The configuration
            :type argin: dict

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            component_manager.configure_scan(argin)
            return (ResultCode.OK, "Configure command completed OK")

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
                msg = f"Validate configuration failed with unknown error: {other_errs}"
                return (None, ResultCode.FAILED, msg)

            return (configuration_dict, ResultCode.OK, "ConfigureScan arguments validation successful")

    class ScanCommand(ObservationCommand, ResponseCommand):
        """
        A class for the CspSubElementObsDevices's Scan command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for ScanCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`SubarrayObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "scan", op_state_model, logger=logger
            )

        def do(self, argin):
            """
            Stateless hook for Scan() command functionality.

            :param argin: The scan ID.
            :type argin: str

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            (result_code, msg) = self.validate_input(argin)
            if result_code == ResultCode.OK:
                component_manager.scan(int(argin))
                return (ResultCode.STARTED, "Scan command started")
            return(result_code, msg)

        def validate_input(self, argin):
            """
            Validate the command input argument.

            :param argin: the scan id
            :type argin: string
            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            if not argin.isdigit():
                msg = f"Input argument '{argin}' is not an integer"
                self.logger.error(msg)
                return (ResultCode.FAILED, msg)
            return (ResultCode.OK, "Scan arguments validation successfull")

    class EndScanCommand(ObservationCommand, ResponseCommand):
        """
        A class for the CspSubElementObsDevices's EndScan command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for EndScanCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`SubarrayObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "end_scan", op_state_model, logger=logger
            )

        def do(self):
            """
            Stateless hook for EndScan() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            component_manager.end_scan()
            return (ResultCode.OK, "EndScan command completed OK")

    class GoToIdleCommand(ObservationCommand, ResponseCommand):
        """
        A class for the CspSubElementObsDevices's GoToIdle command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for EndCommand

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`SubarrayObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "end", op_state_model, logger=logger
            )

        def do(self):
            """
            Stateless hook for GoToIdle() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            component_manager = self.target
            component_manager.deconfigure()
            return (ResultCode.OK, "GoToIdle command completed OK")

    class ObsResetCommand(ObservationCommand, ResponseCommand, CompletionCommand):
        """
        A class for the CspSubElementObsDevices's ObsReset command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for ObsReset Command.

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`CspSubElementObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "obsreset", op_state_model, logger=logger
            )

        def do(self):
            """
            Stateless hook for ObsReset() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "ObsReset command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    class AbortCommand(ObservationCommand, ResponseCommand, CompletionCommand):
        """
        A class for the CspSubElementObsDevices's Abort command.
        """

        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            """
            Constructor for Abort Command.

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the op state model that this command
                uses to check that it is allowed to run
            :type op_state_model: :py:class:`OpStateModel`
            :param obs_state_model: the observation state model that
                 this command uses to check that it is allowed to run,
                 and that it drives with actions.
            :type obs_state_model: :py:class:`CspSubElementObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, obs_state_model, "abort", op_state_model, logger=logger
            )

        def do(self):
            """
            Stateless hook for Abort() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            return (ResultCode.OK, "Abort command completed OK")

    @command(
        dtype_in='DevString',
        doc_in="JSON formatted string with the scan configuration.",
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string message indicating status. "
                "The message is for information purpose only.",
    )
    @DebugIt()
    def ConfigureScan(self, argin):
        # PROTECTED REGION ID(CspSubElementObsDevice.ConfigureScan) ENABLED START #
        """
        Configure the observing device parameters for the current scan.

        :param argin: JSON formatted string with the scan configuration.
        :type argin: 'DevString'

        :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("ConfigureScan")

        (configuration, result_code, message) = command.validate_input(argin)
        if result_code == ResultCode.OK:
            # store the configuration on command success
            self._last_scan_configuration = argin
            (result_code, message) = command(configuration)

        return [[result_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementObsDevice.ConfigureScan

    @command(
        dtype_in='DevString',
        doc_in="A string with the scan ID",
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string message indicating status."
                "The message is for information purpose only.",
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(CspSubElementObsDevice.Scan) ENABLED START #
        """
        Start an observing scan.

        :param argin: A string with the scan ID
        :type argin: 'DevString'

        :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("Scan")
        (return_code, message) = command(argin)
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementObsDevice.Scan

    @command(
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string message indicating status."
                "The message is for information purpose only.",
    )
    @DebugIt()
    def EndScan(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.EndScan) ENABLED START #
        """
        End a running scan.

        :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("EndScan")
        (return_code, message) = command()
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementObsDevice.EndScan

    @command(
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string  message indicating status."
                "The message is for information purpose only.",
    )
    @DebugIt()
    def GoToIdle(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.GoToIdle) ENABLED START #
        """
        Transit the device from READY to IDLE obsState.

        :return: A tuple containing a return code and a string  message indicating status.
            The message is for information purpose only.
        :rtype: (ResultCode, str)
        """
        self._last_scan_configuration = ''

        command = self.get_command_object("GoToIdle")
        (return_code, message) = command()
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementObsDevice.GoToIdle

    @command(
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string message indicating status."
                "The message is for information purpose only.",
    )
    @DebugIt()
    def ObsReset(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.ObsReset) ENABLED START #
        """
        Reset the observing device from a FAULT/ABORTED obsState to IDLE.

        :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("ObsReset")
        (return_code, message) = command()
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementObsDevice.ObsReset

    @command(
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string message indicating status."
                "The message is for information purpose only.",
    )
    @DebugIt()
    def Abort(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.Abort) ENABLED START #
        """
        Abort the current observing process and move the device
        to ABORTED obsState.

        :return: A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("Abort")
        (return_code, message) = command()
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementObsDevice.Abort

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the CspSubElementObsDevice module."""
    # PROTECTED REGION ID(CspSubElementObsDevice.main) ENABLED START #
    return run((CspSubElementObsDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspSubElementObsDevice.main


if __name__ == '__main__':
    main()
