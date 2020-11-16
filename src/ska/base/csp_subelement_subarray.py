# -*- coding: utf-8 -*-
#
# This file is part of the CspSubElementSubarray project
#
#
# Distributed under the terms of the BSD3 license.
# See LICENSE.txt for more info.

""" CspSubElementSubarray

Subarray device for SKA CSP SubElement
"""

# PROTECTED REGION ID(CspSubElementSubarray.additionnal_import) ENABLED START #
import json
from json.decoder import JSONDecodeError
from collections import defaultdict
# Tango imports
import tango
from tango import DebugIt
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from tango.server import device_property
from tango import AttrQuality, DispLevel, DevState
from tango import AttrWriteType, PipeWriteType

# SKA import
from ska.base import SKASubarray
from ska.base.commands import ResultCode, ActionCommand
from ska.base.control_model import ObsState
# Additional import
# PROTECTED REGION END #    //  CspSubElementSubarray.additionnal_import

__all__ = ["CspSubElementSubarray", "main"]


class CspSubElementSubarray(SKASubarray):
    """
    Subarray device for SKA CSP SubElement
    """
    # PROTECTED REGION ID(CspSubElementSubarray.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  CspSubElementSubarray.class_variable

    # -----------------
    # Device Properties
    # -----------------

    # ----------
    # Attributes
    # ----------

    scanID = attribute(
        dtype='DevULong64',
        label="scanID",
        doc="The scan identification number to be inserted in the output products.",
    )

    configurationID = attribute(
        dtype='DevString',
        label="configurationID",
        doc="The configuration ID specified into the JSON configuration.",
    )

    sdpDestinationAddresses = attribute(
        dtype='DevString',
        access=AttrWriteType.READ_WRITE,
        label="sdpDestinationAddresses",
        doc="JSON formatted string.\nReport the list of all the SDP addresses provided by SDP to receive the output products.\nSpecifies the Mac, IP, Port for each resource:CBF visibility channels, Pss pipelines, PSTBeam",
    )

    outputDataRateToSdp = attribute(
        dtype='DevFloat',
        label="outputDataRateToSdp",
        doc="The output data rate (GB/s) on the link for each scan.",
    )

    lastScanConfiguration = attribute(
        dtype='DevString',
        label="lastScanConfiguration",
        doc="The last valid scan configuration.",
    )

    sdpLinkActive = attribute(
        dtype=('DevBoolean',),
        max_dim_x=100,
        label="sdpLinkActive",
        doc="Flag reporting if the SDP links are active.",
    )

    listOfDevicesCompletedTasks = attribute(
        dtype='DevString',
        label="listOfDevicesCompletedTasks",
        doc="JSON formatted string reporting for each task/command the list of devices\nthat completed successfully the task.\nEx.\n{``cmd1``: [``device1``, ``device2``], ``cmd2``: [``device2``, ``device3``]}",
    )
    
    configureScanMeasuredDuration = attribute(
        dtype='DevFloat',
        label="configureScanMeasuredDuration",
        unit="sec",
        doc="The measured time (sec) taken to execute the command",
    )

    assignResourcesMaximumDuration = attribute(
        dtype='DevFloat',
        access=AttrWriteType.READ_WRITE,
        label="assignResourcesMaximumDuration",
        unit="sec",
        doc="The maximum expected command duration.",
    )

    assignResourcesMeasuredDuration = attribute(
        dtype='DevFloat',
        label="assignResourcesMeasuredDuration",
        unit="sec",
        doc="The measured command execution duration.",
    )

    assignResourcesProgress = attribute(
        dtype='DevUShort',
        label="assignResourcesProgress",
        max_value=100,
        min_value=0,
        doc="The percentage progress of the command in the [0,100].",
    )

    releaseResourcesMaximumDuration = attribute(
        dtype='DevFloat',
        access=AttrWriteType.READ_WRITE,
        label="releaseResourcesMaximumDuration",
        unit="sec",
        doc="The maximum expected command duration.",
    )

    releaseResourcesMeasuredDuration = attribute(
        dtype='DevFloat',
        label="releaseResourcesMeasuredDuration",
        unit="sec",
        doc="The measured command execution duration.",
    )

    releaseResourcesProgress = attribute(
        dtype='DevUShort',
        label="releaseResourcesProgress",
        max_value=100,
        min_value=0,
        doc="The percentage progress of the command in the [0,100].",
    )

    timeoutExpiredFlag = attribute(
        dtype='DevBoolean',
        label="timeoutExpiredFlag",
        doc="Flag reporting  command timeout expiration.",
    )

    # ---------------
    # General methods
    # ---------------

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
            "GoToIdle", self.GoToIdleCommand(*device_args)
        )
    
    class InitCommand(SKASubarray.InitCommand):
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
            device._scan_id = 0

            device._sdp_addresses = {"outputHost":[], "outputMac": [], "outputPort":[]}
            device._sdp_links_active = []
            device._sdp_output_data_rate = 0.

            device._config_id = ''
            device._last_scan_configuration = ''
            
            # _list_of_devices_completed_task: for eaxh task/command reports
            # the list of the devices that successfully completed the task.
            # Implemented as a defualt dictionary:
            # keys: the command name in lower case (configurescan, assignresources, etc.)
            # values: the list of devices' FQDN
            device._list_of_devices_completed_task = defaultdict(list)
            
            # _cmd_progress: command execution's progress percentage
            # implemented as a default dictionary:
            # keys: the command name in lower case(configurescan,..)
            # values: the progress percentage (default 0)
            device._cmd_progress = defaultdict(int)
            
            # _cmd_maximun_duration: command execution's expected maximum duration (sec.)
            # implemented as a default dictionary:
            # keys: the command name in lower case(configurescan, assignresources,..)
            # values: the expected maximum duration in sec.
            device._cmd_maximum_duration = defaultdict(float)

            # _cmd_measure_duration: command execution's measured duration (sec.) 
            # implemented as a default dictionary:
            # keys: the command name in lower case(configurescan, assignresources,..)
            # values: the measured execution time (sec.)
            device._cmd_measured_duration = defaultdict(float)
            
            # _timeout_expired: boolean flag to signal timeout during command execution.
            # To check and reset before a command execution.
            # Need to implement one for each command?
            device._timeout_expired = False
            # configure the flag to push event from the device server
            device.set_change_event('timeoutExpiredFlag', True, True)
            
            message = "CspSubElementSubarray Init command completed OK"
            device.logger.info(message)
            return (ResultCode.OK, message)

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(CspSubElementSubarray.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  CspSubElementSubarray.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(CspSubElementSubarray.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  CspSubElementSubarray.delete_device
    
    def _fire_timeout_expired_event(self, value):
        """
        Helper method that updates the timeout_expired internal variable and push the event on the 
        timeoutExpiredFlag TANGO attribute.
        
        :param value: the flag value
        :type value: boolean
        """
        self._timeout_expired = value
        self.push_change_event('timeoutExpiredFlag', self._timeout_expired)
        
    # ------------------
    # Attributes methods
    # ------------------

    def read_scanID(self):
        # PROTECTED REGION ID(CspSubElementSubarray.scanID_read) ENABLED START #
        """Return the scanID attribute."""
        return self._scan_id
        # PROTECTED REGION END #    //  CspSubElementSubarray.scanID_read

    def read_configurationID(self):
        # PROTECTED REGION ID(CspSubElementSubarray.configurationID_read) ENABLED START #
        """Return the configurationID attribute."""
        return self._config_id
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
        return self._cmd_measured_duration['configurescan']
        # PROTECTED REGION END #    //  CspSubElementSubarray.configureScanMeasuredDuration_read
        
    def read_listOfDevicesCompletedTasks(self):
        # PROTECTED REGION ID(CspSubElementSubarray.listOfDevicesCompletedTasks_read) ENABLED START #
        """Return the listOfDevicesCompletedTasks attribute."""
        dict_to_string = json.dumps(self._list_of_devices_completed_task)
        return dict_to_string
        # PROTECTED REGION END #    //  CspSubElementSubarray.listOfDevicesCompletedTasks_read

    def read_assignResourcesMaximumDuration(self):
        # PROTECTED REGION ID(CspSubElementSubarray.assignResourcesMaximumDuration_read) ENABLED START #
        """Return the assignResourcesMaximumDuration attribute."""
        return self._cmd_maximum_duration['assignresources']
        # PROTECTED REGION END #    //  CspSubElementSubarray.assignResourcesMaximumDuration_read

    def write_assignResourcesMaximumDuration(self, value):
        # PROTECTED REGION ID(CspSubElementSubarray.assignResourcesMaximumDuration_write) ENABLED START #
        """Set the assignResourcesMaximumDuration attribute."""
        self._cmd_maximum_duration['assignresources'] = value
        # PROTECTED REGION END #    //  CspSubElementSubarray.assignResourcesMaximumDuration_write

    def read_assignResourcesMeasuredDuration(self):
        # PROTECTED REGION ID(CspSubElementSubarray.assignResourcesMeasuredDuration_read) ENABLED START #
        """Return the assignResourcesMeasuredDuration attribute."""
        return self._cmd_measured_duration['assignresources']
        # PROTECTED REGION END #    //  CspSubElementSubarray.assignResourcesMeasuredDuration_read

    def read_assignResourcesProgress(self):
        # PROTECTED REGION ID(CspSubElementSubarray.assignResourcesProgress_read) ENABLED START #
        """Return the assignResourcesProgress attribute."""
        return self._cmd_progress['assignresources']
        # PROTECTED REGION END #    //  CspSubElementSubarray.assignResourcesProgress_read

    def read_releaseResourcesMaximumDuration(self):
        # PROTECTED REGION ID(CspSubElementSubarray.releaseResourcesMaximumDuration_read) ENABLED START #
        """Return the releaseResourcesMaximumDuration attribute."""
        return self._cmd_maximum_duration['releaseresources']
        # PROTECTED REGION END #    //  CspSubElementSubarray.releaseResourcesMaximumDuration_read

    def write_releaseResourcesMaximumDuration(self, value):
        # PROTECTED REGION ID(CspSubElementSubarray.releaseResourcesMaximumDuration_write) ENABLED START #
        """Set the releaseResourcesMaximumDuration attribute."""
        self._cmd_maximum_duration['releaseresources'] = value
        # PROTECTED REGION END #    //  CspSubElementSubarray.releaseResourcesMaximumDuration_write

    def read_releaseResourcesMeasuredDuration(self):
        # PROTECTED REGION ID(CspSubElementSubarray.releaseResourcesMeasuredDuration_read) ENABLED START #
        """Return the releaseResourcesMeasuredDuration attribute."""
        return self._cmd_measured_duration['releaseresources']
        # PROTECTED REGION END #    //  CspSubElementSubarray.releaseResourcesMeasuredDuration_read

    def read_releaseResourcesProgress(self):
        # PROTECTED REGION ID(CspSubElementSubarray.releaseResourcesProgress_read) ENABLED START #
        """Return the releaseResourcesProgress attribute."""
        return self._cmd_progress['releaseresources']
        # PROTECTED REGION END #    //  CspSubElementSubarray.releaseResourcesProgress_read

    def read_timeoutExpiredFlag(self):
        # PROTECTED REGION ID(CspSubElementSubarray.timeoutExpiredFlag_read) ENABLED START #
        """Return the timeoutExpiredFlag attribute."""
        return self._timeout_expired
        # PROTECTED REGION END #    //  CspSubElementSubarray.timeoutExpiredFlag_read

    def read_sdpLinkActive(self):
        # PROTECTED REGION ID(CspSubElementSubarray.sdpLinkActive_read) ENABLED START #
        """Return the sdpLinkActive attribute."""
        return (False,)
        # PROTECTED REGION END #    //  CspSubElementSubarray.sdpLinkActive_read

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
            :type state_model: :py:class:`SKASubarrayStateModel`
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
            :param argin: The JSON formatted string with configuration for the device.
            :type argin: 'DevString'
            :return: A tuple containing a return code and a string message.
            :rtype: (ResultCode, str)
            """
            device = self.target
            try: 
                configuration_dict = json.loads(argin)
                device._config_id = configuration_dict['id']
                return (ResultCode.OK, "Configuration validated with success")
            except (KeyError, JSONDecodeError) as err:
                msg = "Validate configuration failed with error:{}".format(err)
            except Exception as other_errs:
                msg = "Validate configuration failed with unknown error:{}".format(other_errs)
            self.logger.error(msg)
            return (ResultCode.FAILED, msg)


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
            :type state_model: :py:class:`SKASubarrayStateModel`
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
        
    @command(
        dtype_in='DevString',
        doc_in="A Json-encoded string with the scan configuration.",
        dtype_out='DevVarLongStringArray',
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
        command = self.get_command_object("ConfigureScan")
        (return_code, message) = command(argin)
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementSubarray.Configure

    @command(
        dtype_in='DevString',
        doc_in="A Json-encoded string with the scan configuration.",
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string message indicating status."
                "The message is for information purpose only.",
    )
    @DebugIt()
    def Configure(self, argin):
        # PROTECTED REGION ID(CspSubElementSubarray.Configure) ENABLED START #
        """
        Redirect to ConfigureScan method.
        Configure a complete scan for the subarray.

        :return:'DevVarLongStringArray'
            A tuple containing a return code and a string message indicating status.
            The message is for information purpose only.
        """
        command = self.get_command_object("ConfigureScan")
        (return_code, message) = command(argin)
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementSubarray.Configure

    @command(
        dtype_out='DevVarLongStringArray',
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
        command = self.get_command_object("GoToIdle")
        (return_code, message) = command()
        return [[return_code], [message]]

    @command(
        dtype_out='DevVarLongStringArray',
        doc_out="A tuple containing a return code and a string  message indicating status."
                "The message is for information purpose only.",
    )
    @DebugIt()
    def End(self):
        # PROTECTED REGION ID(CspSubElementSubarray.End) ENABLED START #
        """
        Transit the subarray from READY to IDLE obsState.
        Redirect to GoToIdle command.

        :return:'DevVarLongStringArray'
            A tuple containing a return code and a string  message indicating status.
            The message is for information purpose only.
        """
        command = self.get_command_object("GoToIdle")
        (return_code, message) = command()
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementSubarray.End

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the CspSubElementSubarray module."""
    # PROTECTED REGION ID(CspSubElementSubarray.main) ENABLED START #
    return run((CspSubElementSubarray,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspSubElementSubarray.main


if __name__ == '__main__':
    main()
