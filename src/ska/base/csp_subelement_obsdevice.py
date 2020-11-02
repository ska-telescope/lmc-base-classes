# -*- coding: utf-8 -*-
#
# This file is part of the CspSubElementObsDevice project
#

""" CspSubElementObsDevice

General observing device for SKA CSP Subelement.
"""

# PROTECTED REGION ID(CspSubElementObsDevice.additionnal_import) ENABLED START #
# Python library imports
import json
# Tango imports 
import tango
from tango import DebugIt, AttrWriteType
from tango.server import run, attribute, command, device_property

# SKA specific imports
from ska.base import SKAObsDevice
from ska.base.commands import ResultCode, ResponseCommand
from ska.base.control_model import ObsState
from ska.base.faults import CommandError
# PROTECTED REGION END #    //  CspSubElementObsDevice.additionnal_import

__all__ = ["CspSubElementObsDevice", "main"]

class CspSubElementObsDevice(SKAObsDevice):
    """
    General observing device for SKA CSP Subelement.

    **Properties:**

    - Device Property
        DeviceId
            - Identification number of the observing device.
            - Type:'DevUShort'
    """
    # PROTECTED REGION ID(CspSubElementObsDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  CspSubElementObsDevice.class_variable

    # -----------------
    # Device Properties
    # -----------------

    DeviceId = device_property(
        dtype='DevUShort',
    )

    # ----------
    # Attributes
    # ----------

    subarrayMembership = attribute(
        dtype=('DevUShort',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=16,
        label="subarrayMembership",
        doc="Identification number of the affilaited subarray.\nImplemented an array because some  devices can be shared among several subarrays.\n",
    )

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
        doc="The last valid scan confiuration.",
    )

    sdpDestinationAddresses = attribute(
        dtype='DevString',
        label="sdpDestinationAddresses",
        doc="JSON formatted string\nReport the list of all the SDP addresses provided by SDP to receive the output products.\nSpecifies the Mac, IP, Port for each resource:\nCBF: visibility channels\nPSS ? Pss pipelines\nPST ? PSTBeam\nNot used by al CSP Sub-element observing device (for ex. Mid CBF VCCs)",
    )

    sdpLinkCapacity = attribute(
        dtype='DevFloat',
        label="sdpLinkCapacity",
        doc="The SDP link capavity in GB/s.",
    )

    sdpLinkActive = attribute(
        dtype=('DevBoolean',),
        max_dim_x=1000,
        label="sdpLinkActive",
        doc="Flag reporting if the SDP link is active.\nTrue: active\nFalse:down",
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
            device._subarray_id = [0,]

            device._sdp_addresses = ''
            device._sdp_links_active = [False,]
            device._sdp_link_capacity = 0.

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

    def read_subarrayMembership(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.subarrayMembership_read) ENABLED START #
        """Return the subarrayMembership attribute."""
        return self._subarray_id
        # PROTECTED REGION END #    //  CspSubElementObsDevice.subarrayMembership_read
        
    def write_subarrayMembership(self, value):
        # PROTECTED REGION ID(CspSubElementObsDevice.subarrayMembership_write) ENABLED START #
        """Set the subarrayMembership attribute."""
        self._subarray_id = value
        # PROTECTED REGION END #    //  CspSubElementObsDevice.subarrayMembership_write

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
        return self._sdp_addresses
        # PROTECTED REGION END #    //  CspSubElementObsDevice.sdpDestinationAddresses_read

    def read_sdpLinkCapacity(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.sdpLinkCapacity_read) ENABLED START #
        """Return the sdpLinkCapacity attribute."""
        return self._sdp_link_capacity
        # PROTECTED REGION END #    //  CspSubElementObsDevice.sdpLinkCapacity_read

    def read_sdpLinkActive(self):
        # PROTECTED REGION ID(CspSubElementObsDevice.sdpLinkActive_read) ENABLED START #
        """Return the sdpLinkActive attribute."""
        return self._sdp_link_active
        # PROTECTED REGION END #    //  CspSubElementObsDevice.sdpLinkActive_read

    # --------
    # Commands
    # --------

    class ConfigureScanCommand(ResponseCommand):
        """
        A class for the CspSubElementObsDevices's ConfigureScan command.
        """
        def do(self, argin):
            """
            Stateless hook for ConfigureScan() command functionality.

            :param argin: The configuration as JSON formatted string
            :type argin: str

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            :raises: ``CommandError`` if invalid parameters are specified into the 
                configuration passed as argument of the command.
            """
            device = self.target
            result_code, msg = self.validate_configuration_data(argin)
            if result_code == ResultCode.FAILED:
                raise CommandError(msg)
            device._update_obs_state(ObsState.CONFIGURING)
            # configure the device
            # store the programmed configuration
            device._last_valid_configuration = argin
            # set the obsState device to READY if configuration end 
            # with success, otherwise set it to FAULT.
            device._update_obs_state(ObsState.READY)
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
            configuration_dict = json.loads(argin)
            device._config_id = configuration_dict['id']
            return (ResultCode.OK, "Configuration validated with success")

        def check_allowed(self): 
            """
            Check if the command is in the proper state (State/obsState)
            to be executed.
            The observing device has to be in ON/IDLE state to process the
            ConfigureScan command.

            : raises: ``CommandError`` if command not allowed
            : return: ``True`` if the command is allowed.
            : rtype: boolean
            """
            device = self.target
            if (self.state_model.op_state == tango.DevState.ON
                    and device._obs_state == ObsState.IDLE):
                return True
            msg = "{} not allowed in {}/{}".format (self.name,
                                                    self.state_model.op_state,
                                                    ObsState(device._obs_state).name)
            raise CommandError(msg)

    class ScanCommand(ResponseCommand):
        """
        A class for the CspSubElementObsDevices's Scan command.
        """
        def do(self, argin):
            """
            Stateless hook for Scan() command functionality.

            :param argin: The scan ID.
            :type argin: str

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            :raises: ``CommandError`` ifinput argument is invalid.
            """
            device = self.target
            if not argin.isdigit():
                raise CommandError("Scan argument is not an integer")
            device._scan_id = int(argin)
            device._update_obs_state(ObsState.SCANNING)
            return (ResultCode.OK, "Scan command started")
        
        def check_allowed(self): 
            """
            Check if the command is in the proper state (State/obsState)
            to be executed.
            The observing device has to be in ON/READY state to process the
            Scan command.

            : raises: ``CommandError`` if command not allowed
            : return: ``True`` if the command is allowed.
            : rtype: boolean
            """
            device = self.target
            if (self.state_model.op_state == tango.DevState.ON
                    and device._obs_state == ObsState.READY):
                return True
            msg = "{} not allowed in {}/{}".format (self.name,
                                                    self.state_model.op_state,
                                                    ObsState(device._obs_state).name)
            raise CommandError(msg)

    class EndScanCommand(ResponseCommand):
        """
        A class for the CspSubElementObsDevices's EndScan command.
        """
        def do(self):
            """
            Stateless hook for EndScan() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device = self.target
            # set the  obsState device to READY if scan ends with success
            device._update_obs_state(ObsState.READY)
            return (ResultCode.OK, "EndScan command completed OK")
        
        def check_allowed(self): 
            """
            Check if the command is in the proper state (State/obsState)
            to be executed.
            The observing device has to be in ON/SCANNING state to process the
            EndScan command.

            : raises: ``CommandError`` if command not allowed
            : return: ``True`` if the command is allowed.
            : rtype: boolean
            """
            device = self.target
            if (self.state_model.op_state == tango.DevState.ON
                    and device._obs_state == ObsState.SCANNING):
                return True
            msg = "{} not allowed in {}/{}".format (self.name,
                                                    self.state_model.op_state,
                                                    ObsState(device._obs_state).name)
            raise CommandError(msg)

    class GoToIdleCommand(ResponseCommand):
        """
        A class for the CspSubElementObsDevices's GoToIdle command.
        """
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
            # set the obsState device to IDLE if command ends ok
            #device._update_obs_state(ObsState.IDLE)
            return (ResultCode.OK, "GoToIdle command completed OK")
        
        def check_allowed(self): 
            """
            Check if the command is in the proper state (State/obsState)
            to be executed.
            The observing device has to be in ON/READY state to process the
            GoToIdle command.

            : raises: ``CommandError`` if command not allowed
            : return: ``True`` if the command is allowed.
            : rtype: boolean
            """
            self.logger.info("Check GoToIdle")
            device = self.target
            if (self.state_model.op_state == tango.DevState.ON
                    and device._obs_state == ObsState.READY):
                self.logger.info("GoToIdle ok")
                return True
            msg = "{} not allowed in {}/{}".format (self.name,
                                                    self.state_model.op_state,
                                                    ObsState(device._obs_state).name)
            raise CommandError(msg)

    class ObsResetCommand(ResponseCommand):
        """
        A class for the CspSubElementObsDevices's ObsReset command.
        """
        def do(self):
            """
            Stateless hook for ObsReset() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            # enter RESETTING obsState if the device supports this obsState
            # device._update_obs_state(ObsState.RESETTING)
            # reset 
            # set the obsState device to IDLE if command ends ok
            #device._update_obs_state(ObsState.IDLE)
            return (ResultCode.OK, "ObsReset command completed OK")
        
        def check_allowed(self): 
            """
            Check if the command is in the proper state (State/obsState)
            to be executed.
            The observing device has to be in ON/[ABORT, FAULT] state to process the
            ObsReset command.

            : raises: ``CommandError`` if command not allowed
            : return: ``True`` if the command is allowed.
            : rtype: boolean
            """
            device = self.target
            if (self.state_model.op_state == tango.DevState.ON
                    and device._obs_state in [ObsState.ABORTED,
                                            ObsState.FAULT]):
                return True
            msg = "{} not allowed in {}/{}".format (self.name,
                                                    self.state_model.op_state,
                                                    ObsState(device._obs_state).name)
            raise CommandError(msg)

    class AbortCommand(ResponseCommand):
        """
        A class for the CspSubElementObsDevices's Abort command.
        """
        def do(self):
            """
            Stateless hook for Abort() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            # enter the ABORTING obsState if the device supports it.
            # device._update_obs_state(ObsState.ABORTING)
            # handle habort command
            device._update_obs_state(ObsState.ABORTED)
            return (ResultCode.OK, "Abort command completed OK")
        
        def check_allowed(self): 
            """
            Check if the command is in the proper state (State/obsState)
            to be executed.
            The observing device has to be in ON/[READY, SCANNING, CONFIGURING, IDLE]
            state to process the Abort command.

            : raises: ``CommandError`` if command not allowed
            : return: ``True`` if the command is allowed.
            : rtype: boolean
            """
            device = self.target
            if (self.state_model.op_state == tango.DevState.ON
                    and device._obs_state in [ObsState.SCANNING, 
                                            ObsState.CONFIGURING,
                                            ObsState.IDLE,
                                            ObsState.READY]):
                return True
            msg = "{} not allowed in {}/{}".format (self.name,
                                                    self.state_model.op_state,
                                                    ObsState(device._obs_state).name)
            raise CommandError(msg)

    def is_ConfigureScan_allowed(self):
        """
        Check if the ConfigureScan command is allowed in the current 
        state.

        :raises: ``tango.DevFailed`` if command not allowed
        :return: ``True`` if command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("ConfigureScan")
        return command.check_allowed()

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

    def is_Scan_allowed(self):
        """
        Check if the Scan command is allowed in the current 
        state.

        :raises: ``tango.DevFailed`` if command not allowed
        :return: ``True`` if command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Scan")
        return command.check_allowed()

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

    def is_EndScan_allowed(self):
        """
        Check if the EndScan command is allowed in the current 
        state.

        :raises: ``tango.DevFailed`` if command not allowed
        :return: ``True`` if command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("EndScan")
        return command.check_allowed()

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

    def is_GoToIdle_allowed(self):
        """
        Check if the GoToIdle command is allowed in the current 
        state.

        :raises: ``tango.DevFailed`` if command not allowed
        :return: ``True`` if command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("GoToIdle")
        return command.check_allowed()

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

    def is_ObsReset_allowed(self):
        """
        Check if the ObsReset command is allowed in the current 
        state.

        :raises: ``tango.DevFailed`` if command not allowed
        :return: ``True`` if command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("ObsReset")
        return command.check_allowed()

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

    def is_Abort_allowed(self):
        """
        Check if the Abort command is allowed in the current 
        state.

        :raises: ``tango.DevFailed`` if command not allowed
        :return: ``True`` if command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Abort")
        return command.check_allowed()

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
