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
from ska.base.commands import ResultCode, ResponseCommand, ActionCommand
from ska.base.control_model import ObsState
#from ska.base.csp_subelement_state_machine import CspObservationStateMachine
from ska.base.faults import StateModelError

# State Machine imports
from transitions import State
from transitions.extensions import LockedMachine as Machine
# PROTECTED REGION END #    //  CspSubElementObsDevice.additionnal_import

__all__ = ["CspSubElementObsDevice", 
           "CspSubElementObsDeviceStateModel", 
           "CspSubElementObsDeviceStateMachine",
           "main"
          ]


class CspSubElementObsDeviceStateMachine(Machine):
    """
    The observation state machine used by a generic CSP 
    Sub-element ObsDevice (derived from SKAObsDevice).
    """

    def __init__(self, callback=None, **extra_kwargs):
        """
        Initialises the model.

        :param callback: A callback to be called when the state changes
        :type callback: callable
        :param extra_kwargs: Additional keywords arguments to pass to super class
            initialiser (useful for graphing)
        """
        self._callback = callback

        states = [
            "IDLE",
            "CONFIGURING",
            "READY",
            "SCANNING",
            "ABORTING",
            "ABORTED",
            "FAULT",
        ]
        transitions = [
            {
                "source": "*",
                "trigger": "fatal_error",
                "dest": "FAULT",
            },
            {
                "source": ["IDLE", "READY"],
                "trigger": "configure_started",
                "dest": "CONFIGURING",
            },
            {
                "source": "CONFIGURING",
                "trigger": "configure_succeeded",
                "dest": "READY",
            },
            {
                "source": "CONFIGURING",
                "trigger": "configure_failed",
                "dest": "FAULT",
            },
            {
                "source": "READY",
                "trigger": "end_succeeded",
                "dest": "IDLE",
            },
            {
                "source": "READY",
                "trigger": "end_failed",
                "dest": "FAULT",
            },
            {
                "source": "READY",
                "trigger": "scan_started",
                "dest": "SCANNING",
            },
            {
                "source": "SCANNING",
                "trigger": "scan_succeeded",
                "dest": "READY",
            },
            {
                "source": "SCANNING",
                "trigger": "scan_failed",
                "dest": "FAULT",
            },
            {
                "source": "SCANNING",
                "trigger": "end_scan_succeeded",
                "dest": "READY",
            },
            {
                "source": "SCANNING",
                "trigger": "end_scan_failed",
                "dest": "FAULT",
            },
            {
                "source": [
                    "CONFIGURING",
                    "READY",
                    "SCANNING",
                    "IDLE",
                ],
                "trigger": "abort_started",
                "dest": "ABORTING",
            },
            {
                "source": "ABORTING",
                "trigger": "abort_succeeded",
                "dest": "ABORTED",
            },
            {
                "source": "ABORTING",
                "trigger": "abort_failed",
                "dest": "FAULT",
            },
            {
                "source": ["ABORTED", "FAULT"],
                "trigger": "reset_succeeded",
                "dest": "IDLE",
            },
            {
                "source": ["ABORTED", "FAULT"],
                "trigger": "reset_failed",
                "dest": "FAULT",
            },
        ]

        super().__init__(
            states=states,
            initial="IDLE",
            transitions=transitions,
            after_state_change=self._state_changed,
            **extra_kwargs,
        )
        self._state_changed()

    def _state_changed(self):
        """
        State machine callback that is called every time the obs_state
        changes. Responsible for ensuring that callbacks are called.
        """
        if self._callback is not None:
            self._callback(self.state)

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
            "scan_started": ("scan_started", None),
            "scan_succeeded": ("scan_succeeded", None),
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
        dtype='DevUShort',
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

    # --------
    # Commands
    # --------

    class ConfigureScanCommand(ActionCommand):
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
            """
            device = self.target
            result_code, msg = self.validate_configuration_data(argin)
            if result_code == ResultCode.FAILED:
                return (result_code, msg)
            # store the configuration on command success
            device._last_scan_configuration = argin
            return (ResultCode.OK, "Configure command completed OK")

        def validate_configuration_data(self, argin):
            """
            Validate the configuration parameters against allowed values, as needed.
            :param argin:
                The JSON formatted string with configuration for the device.
            : type argin: 'DevString'
            :return: A tuple containing a return code and a string message.
            :rtype: (ResultCode, str)
            """
            device = self.target
            try: 
                configuration_dict = json.loads(argin)
                device._config_id = configuration_dict['id']
                return (ResultCode.OK, "Configuration validated with success")
            except KeyError as key_err:
                msg = f"Key {key_err} not present in scan configuration"
            except JSONDecodeError as json_err:
                msg = f"Json decode error: {json_err}"
            self.logger.error(msg)
            return (ResultCode.FAILED, msg)

    class ScanCommand(ActionCommand):
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
            if not argin.isdigit():
                msg = f"Input argument '{argin}' is not an integer" 
                self.logger.error(msg)
                return (ResultCode.FAILED, msg)
            device._scan_id = int(argin)
            return (ResultCode.STARTED, "Scan command started")
        
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
            # reset to default values the configurationID and scanID
            device._config_id = ''
            device._scan_id = 0
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

        :return:
            A tuple containing a return code and a string message indicating status. 
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

        :return:
            A tuple containing a return code and a string message indicating status.
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

        :return:'DevVarLongStringArray'
            A tuple containing a return code and a string message indicating status.
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

        :return:
            A tuple containing a return code and a string  message indicating status.
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

        :return:
            A tuple containing a return code and a string message indicating status.
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

        :return:
            A tuple containing a return code and a string message indicating status.
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
