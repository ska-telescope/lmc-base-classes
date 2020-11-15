# -*- coding: utf-8 -*-
#
# This file is part of the CspSubElementObsDevice project
#

""" CspSubElementObsDevice

General observing device for SKA CSP Subelement.
"""

# PROTECTED REGION ID(CspSubElementObsDevice.additionnal_import) ENABLED START #
import json
import warnings
import numpy as np
from json.decoder import JSONDecodeError

# Tango imports 
import tango
from tango import DebugIt, DevState, AttrWriteType
from tango.server import run, attribute, command, device_property

# SKA specific imports
from ska.base import SKAObsDevice, ObsDeviceStateModel
from ska.base.commands import ResultCode, ActionCommand
from ska.base.csp_commands import  InputValidatedCommand
from ska.base.control_model import ObsState
from ska.base.faults import CommandError
from ska.base.csp_subelement_state_machine import CspSubElementObsDeviceStateMachine

__all__ = ["CspSubElementObsDevice", "CspSubElementObsDeviceStateModel", "main"]

class CspSubElementObsDeviceStateModel(ObsDeviceStateModel):
    """
    Implements the state model for the CspSubElementObsDevice.

    :param logger: the logger to be used by this state model.
    :type logger: a logger that implements the standard library
       logger interface
    :param op_state_callback: A callback to be called when a
       transition implies a change to op state
    :type op_state_callback: callable
    :param admin_mode_callback: A callback to be called when a
       transition causes a change to device admin_mode
    :type admin_mode_callback: callable
    :param obs_state_callback: A callback to be called when a
       transition causes a change to device obs_state
    :type obs_state_callback: callable
    """

    def __init__(
        self,
        logger,
        op_state_callback=None,
        admin_mode_callback=None,
        obs_state_callback=None,
    ):
        action_breakdown = {
            # "action": ("action_on_obs_machine", "action_on_superclass"),
            "off_succeeded": ("to_IDLE", "off_succeeded"),
            "off_failed": ("to_IDLE", "off_failed"),
            "on_succeeded": (None, "on_succeeded"),
            "on_failed": ("to_IDLE", "on_failed"),
            "configure_started": ("configure_started", None),
            "configure_succeeded": ("configure_succeeded", None),
            "configure_failed": ("configure_failed", None),
            "configure_rejected_to_idle": ("configure_rejected_to_idle", None),
            "configure_rejected": ("configure_rejected", None),
            "scan_started": ("scan_started", None),
            "scan_succeeded": ("scan_succeeded", None),
            "scan_rejected": ("scan_rejected", None),
            "scan_failed": ("scan_failed", None),
            "end_scan_succeeded": ("end_scan_succeeded", None),
            "end_scan_failed": ("end_scan_failed", None),
            "end_succeeded": ("end_succeeded", None),
            "end_failed": ("end_failed", None),
            "abort_started": ("abort_started", None),
            "abort_succeeded": ("abort_succeeded", None),
            "abort_failed": ("abort_failed", None),
            "obs_reset_succeeded": ("reset_succeeded", None),
            "obs_reset_failed": ("reset_failed", None),
            "fatal_error": ("fatal_error", None),
          }
        super().__init__(
            action_breakdown,
            CspSubElementObsDeviceStateMachine,
            logger,
            op_state_callback=op_state_callback,
            admin_mode_callback=admin_mode_callback,
            obs_state_callback=obs_state_callback,
        )

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

    configurationID = attribute(
        dtype='DevString',
        label="configurationID",
        doc="The configuration ID specified into the JSON configuration.",
    )

    deviceID = attribute(
        dtype='DevUShort',
        label="deviceID",
        doc="The observing device ID.",
    )

    lastScanConfiguration = attribute(
        dtype='DevString',
        label="lastScanConfiguration",
        doc="The last valid scan configuration.",
    )

    sdpDestinationAddresses = attribute(
        dtype='DevString',
        label="sdpDestinationAddresses",
        doc="JSON formatted string\nReport the list of all the SDP addresses provided by SDP"
            " to receive the output products.\nSpecifies the Mac, IP, Port for each resource:\nCBF:"
            " visibility channels\nPSS ? Pss pipelines\nPST ? PSTBeam\nNot used by al CSP Sub-element"
            " observing device (for ex. Mid CBF VCCs)",
    )

    sdpLinkCapacity = attribute(
        dtype='DevFloat',
        label="sdpLinkCapacity",
        doc="The SDP link capavity in GB/s.",
    )

    sdpLinkActive = attribute(
        dtype=('DevBoolean',),
        max_dim_x=100,
        label="sdpLinkActive",
        doc="Flag reporting if the SDP link is active.\nTrue: active\nFalse:down",
    )

    healthFailureMessage = attribute(
        dtype='DevString',
        label="healthFailureMessage",
        doc="Message providing info about device health failure.",
    )


    # ---------------
    # General methods
    # ---------------

    def _init_state_model(self):
        """
        Sets up the state model for the device
        """
        self.state_model = CspSubElementObsDeviceStateModel(
            logger=self.logger,
            op_state_callback=self._update_state,
            admin_mode_callback=self._update_admin_mode,
            obs_state_callback=self._update_obs_state,
        )

    def init_command_objects(self):
        """
        Sets up the command objects
        """
        super().init_command_objects()
        device_args = (self, self.state_model, self.logger)
        self.register_command_object(
            "ConfigureScan", self.ConfigureScanCommand(*device_args)
        )
        self.register_command_object(
            "Scan", self.ScanCommand(*device_args)
        )
        self.register_command_object(
            "EndScan", self.EndScanCommand(*device_args)
        )
        self.register_command_object(
            "GoToIdle", self.GoToIdleCommand(*device_args)
        )
        self.register_command_object(
            "Abort", self.AbortCommand(*device_args)
        )
        self.register_command_object(
            "ObsReset", self.ObsResetCommand(*device_args)
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
            device._scan_id = 0

            device._sdp_addresses = {"outputHost":[], "outputMac": [], "outputPort":[]}
            device._sdp_links_active = []
            device._sdp_links_capacity = 0.

            device._config_id = ''
            device._last_scan_configuration = ''
            device._health_failure_msg = ''

            message = "CspSubElementObsDevice Init command completed OK"
            device.logger.info(message)
            return (ResultCode.OK, message)

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
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
        return self._scan_id 
        # PROTECTED REGION END #    //  CspSubElementObsDevice.scanID_read

    def read_configurationID(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.configurationID_read) ENABLED START #
        """Return the configurationID attribute."""
        return self._config_id
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
    
    
    class ConfigureScanCommand(InputValidatedCommand):
        """
        A class for the CspSubElementObsDevices's ConfigureScan command.
        """
        def __init__(self, target, state_model, logger=None):
            """
            Constructor for ConfigureScanCommand

            :param target: the object that this command acts upon; for
                example, the CspSubElementObsDevice device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`CspSubElementObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "configure", start_action=True, logger=logger
            )

        def do(self, argin):
            """
            Stateless hook for ConfigureScan() command functionality.

            :param argin: The configuration as JSON formatted string
            :type argin: str

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            :raises: ``CommandError`` if the configuration data validation fails. 
            """
            device = self.target
            # store the configuration on command success
            device._last_scan_configuration = argin
            return (ResultCode.OK, "Configure command completed OK")

        def validate_input(self, argin):
            """
            Validate the configuration parameters against allowed values, as needed.
            The developer is free to return a FAULT code or raise an exception taking into
            account that in the first case the observing state of the device transits
            to FAULT while in the second case it is restored the observing state of the device
            as it was before the command was invoked.

            :param argin: The JSON formatted string with configuration for the device.
            :type argin: 'DevString'
            :return: A tuple containing a return code and a string message. 
            :rtype: (ResultCode, str)
            :raises: ``CommandError`` exception when wrong type or range values are specified for
                the configuration data. In this case the device restores the observing
                state before command was invoked.
            """
            device = self.target
            try: 
                configuration_dict = json.loads(argin)
                device._config_id = configuration_dict['id']
                # call the method to validate the data sent with
                # the configuration, as needed.
                return (ResultCode.OK, "ConfigureScan arguments validation successfull")
            except (KeyError, JSONDecodeError)  as err:
                msg = "Validate configuration failed with error:{}".format(err)
            except Exception as other_errs:
                msg = "Validate configuration failed with unknown error:{}".format(other_errs)
                self.logger.error(msg)
            raise CommandError(msg)

    class ScanCommand(InputValidatedCommand):
        """
        A class for the CspSubElementObsDevices's Scan command.
        """
        def __init__(self, target, state_model, logger=None):
            """
            Constructor for ScanCommand

            :param target: the object that this command acts upon; for
                example, the CspSubElementObsDevice device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`CspSubElementObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "scan", start_action=True, logger=logger
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
            device = self.target
            device._scan_id = int(argin)
            return (ResultCode.STARTED, "Scan command started")

        def validate_input(self, argin):
            """
            Validate the command input argument.

            :param argin: the scan id
            :type argin: string
            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            :raises: ``CommandError`` exception when wrong type or value arguments
                are specified.
            """
            if not argin.isdigit():
                msg = f"Input argument '{argin}' is not an integer" 
                self.logger.error(msg)
                raise CommandError(msg)
            return (ResultCode.OK, "Scan arguments validation successfull")
        
    class EndScanCommand(ActionCommand):
        """
        A class for the CspSubElementObsDevices's EndScan command.
        """
        def __init__(self, target, state_model, logger=None):
            """
            Constructor for EndScanCommand

            :param target: the object that this command acts upon; for
                example, the CspSubElementObsDevice device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`CspSubElementObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "end_scan", logger=logger
            )

        def do(self):
            """
            Stateless hook for EndScan() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            return (ResultCode.OK, "EndScan command completed OK")
        
    class GoToIdleCommand(ActionCommand):
        """
        A class for the CspSubElementObsDevices's GoToIdle command.
        """
        def __init__(self, target, state_model, logger=None):
            """
            Constructor for GoToIdle Command.

            :param target: the object that this command acts upon; for
                example, the CspSubElementObsDevice device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`CspSubElementObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "end", logger=logger
            )

        def do(self):
            """
            Stateless hook for GoToIdle() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device = self.target
            if device.state_model.obs_state == ObsState.IDLE:
                return (ResultCode.OK, "GoToIdle command completed OK. Device already IDLE")
            # reset to default values the configurationID and scanID
            device._config_id = ''
            device._scan_id = 0
            device._last_scan_configuration = ''
            return (ResultCode.OK, "GoToIdle command completed OK")
        
    class ObsResetCommand(ActionCommand):
        """
        A class for the CspSubElementObsDevices's ObsReset command.
        """
        def __init__(self, target, state_model, logger=None):
            """
            Constructor for ObsReset Command.

            :param target: the object that this command acts upon; for
                example, the CspSubElementObsDevice device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`CspSubElementObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "obs_reset", logger=logger
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
        

    class AbortCommand(ActionCommand):
        """
        A class for the CspSubElementObsDevices's Abort command.
        """
        def __init__(self, target, state_model, logger=None):
            """
            Constructor for Abort Command.

            :param target: the object that this command acts upon; for
                example, the CspSubElementObsDevice device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`CspSubElementObsStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "abort", start_action=True, logger=logger
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
        (return_code, message) = command(argin)
        return [[return_code], [message]]
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
