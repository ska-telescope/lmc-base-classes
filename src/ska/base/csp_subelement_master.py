# -*- coding: utf-8 -*-
#
# This file is part of the CspSubElementMaster project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" CspSubElementMaster

Master device for SKA CSP Subelement.
"""
# PROTECTED REGION ID(CspSubElementMaster.additionnal_import) ENABLED START #
# Python standard library
from collections import defaultdict
# Tango imports
import tango
from tango import DebugIt, AttrWriteType
from tango.server import run, attribute, command, device_property

# SKA specific imports

from ska.base import SKAMaster
from ska.base.commands import ResultCode, ResponseCommand
from ska.base.control_model import AdminMode
from ska.base.faults import CommandError
# PROTECTED REGION END #    //  CspSubElementMaster.additionnal_import

__all__ = ["CspSubElementMaster", "main"]


class CspSubElementMaster(SKAMaster):
    """
    Master device for SKA CSP Subelement.

    **Properties:**

    - Device Property
        PowerDelayStandbyOn
            - Delay in ms between power-up stages in Standby <-> On transition.
            - Type:'DevUShort'
        PowerDelayStandByOff
            - Delay in ms between power-up stages in Standby -> Off transition.
            - Type:'DevUShort'
    """
    # PROTECTED REGION ID(CspSubElementMaster.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  CspSubElementMaster.class_variable

    # -----------------
    # Device Properties
    # -----------------

    PowerDelayStandbyOn = device_property(
        dtype='DevUShort',
    )

    PowerDelayStandbyOff = device_property(
        dtype='DevUShort',
    )

    # ----------
    # Attributes
    # ----------

    powerDelayStandbyOn = attribute(
        dtype='DevUShort',
        access=AttrWriteType.READ_WRITE,
        label="powerDelayStandbyOn",
        unit="msec.",
        doc="Delay in msec between the power-up stages in Standby<->On transitions.",
    )

    onProgress = attribute(
        dtype='DevUShort',
        label="onProgress",
        max_value=100,
        min_value=0,
        doc="Progress percentage of the task execution.",
    )

    onMaximumDuration = attribute(
        dtype='DevUShort',
        access=AttrWriteType.READ_WRITE,
        label="onMaximumDuration",
        unit="msec.",
        doc="The maximum duration (msec.) to execute the On command.",
    )

    onMeasuredDuration = attribute(
        dtype='DevUShort',
        label="OnCmdMeasuredDuration",
        unit="msec",
        doc="The measured time (msec) taken to execute the command.",
    )

    standbyProgress = attribute(
        dtype='DevUShort',
        label="standbyProgress",
        max_value=100,
        min_value=0,
        doc="Progress percentage of the task execution.",
    )

    standbyMaximumDuration = attribute(
        dtype='DevUShort',
        access=AttrWriteType.READ_WRITE,
        label="standbyMaximumDuration",
        unit="msec.",
        doc="The maximum duration (msec.) to execute the Standby command.",
    )

    standbyMeasuredDuration = attribute(
        dtype='DevUShort',
        label="OnCmdMeasuredDuration",
        unit="msec",
        doc="The measured time (msec) taken to execute the Standby command.",
    )

    offProgress = attribute(
        dtype='DevUShort',
        label="offProgress",
        max_value=100,
        min_value=0,
        doc="Progress percentage of the task execution.",
    )

    offMaximumDuration = attribute(
        dtype='DevUShort',
        access=AttrWriteType.READ_WRITE,
        label="offMaximumDuration",
        unit="msec.",
        doc="The maximum duration (msec.) to execute the Off command.",
    )

    offMeasuredDuration = attribute(
        dtype='DevUShort',
        label="OnCmdMeasuredDuration",
        unit="msec",
        doc="The measured time (msec) taken to execute the Off command.",
    )

    totalOutputDataRateToSdp = attribute(
        dtype='DevFloat',
        label="totalOutputDataRateToSdp",
        unit="GB/s",
        doc="Report the total link expected  output data rate.",
    )

    powerDelayStandbyOff = attribute(
        dtype='DevUShort',
        access=AttrWriteType.READ_WRITE,
        label="powerDelayStandbyOff",
        unit="msec",
        doc="Delay in msec between the power-up stages in Standby->Off transitions.",
    )

    loadFirmwareProgress = attribute(
        dtype='DevUShort',
        label="loadFirmwareProgress",
        max_value=100,
        min_value=0,
        doc="The task progress percentage.",
    )

    loadFirmwareMaximumDuration = attribute(
        dtype='DevUShort',
        access=AttrWriteType.READ_WRITE,
        label="loadFirmwareMaximumDuration",
        unit="msec",
        doc="The expected maximum duration (in msec) for task execution.",
    )

    loadFirmwareMeasuredDuration = attribute(
        dtype='DevUShort',
        label="loadFirmwareMeasuredDuration",
        unit="msec",
        doc="The task execution measured duration (in msec).",
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
            "LoadFirmware", self.LoadFirmwareCommand(*device_args)
        )
        self.register_command_object(
            "PowerOnDevices", self.PowerOnDevicesCommand(*device_args)
        )
        self.register_command_object(
            "PowerOffDevices", self.PowerOffDevicesCommand(*device_args)
        )
        self.register_command_object(
            "ReInitDevices", self.ReInitDevicesCommand(*device_args)
        )
    
    class InitCommand(SKAMaster.InitCommand):
        """
        A class for the CspSubElementMaster's init_device() "command".
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

            # _task_progress: task execution's progress percentage
            # implemented as a default dictionary:
            # keys: the task name in lower case(on, off, standby,..)
            # values: the progress percentage (default 0)
            device._task_progress = defaultdict(lambda: 0)

            # _task_maximun_duration: task execution's expected maximum duration (msec.)
            # implemented as a default dictionary:
            # keys: the task name in lower case(on, off, standby,..)
            # values: the expected maximum duration in msec.
            device._task_maximum_duration = defaultdict(lambda:0)

            # _task_measure_duration: task execution's measured duration (msec.) 
            # implemented as a default dictionary:
            # keys: the task name in lower case(on, off, standby,..)
            # values: the measured execution time (msec.)
            device._task_measured_duration = defaultdict(lambda: 0)

            device._total_output_rate_to_sdp = 0.0

            # initialise using defaults in device properties
            device._power_delay_standy_on = 0 
            device._power_delay_standy_off = 0
            if device.PowerDelayStandbyOn:
                device._power_delay_standy_on =  device.PowerDelayStandbyOn
                device.write_powerDelayStandbyOn(device._power_delay_standy_on)
            if device.PowerDelayStandbyOff:
                device._power_delay_standy_off =  device.PowerDelayStandbyOff
                device.write_powerDelayStandbyOff(device._power_delay_standy_off)

            message = "CspSubElementMaster Init command completed OK"
            device.logger.info(message)
            return (ResultCode.OK, message)

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(CspSubElementMaster.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  CspSubElementMaster.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(CspSubElementMaster.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  CspSubElementMaster.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_powerDelayStandbyOn(self):
        # PROTECTED REGION ID(CspSubElementMaster.powerDelayStandbyOn_read) ENABLED START #
        """Return the powerDelayStandbyOn attribute."""
        return self._power_delay_standy_on
        # PROTECTED REGION END #    //  CspSubElementMaster.powerDelayStandbyOn_read

    def write_powerDelayStandbyOn(self, value):
        # PROTECTED REGION ID(CspSubElementMaster.powerDelayStandbyOn_write) ENABLED START #
        """Set the powerDelayStandbyOn attribute."""
        self._power_delay_standy_on = value
        # PROTECTED REGION END #    //  CspSubElementMaster.powerDelayStandbyOn_write

    def read_onProgress(self):
        # PROTECTED REGION ID(CspSubElementMaster.onProgress_read) ENABLED START #
        """Return the onProgress attribute."""
        return self._task_progress['on']
        # PROTECTED REGION END #    //  CspSubElementMaster.onProgress_read

    def read_onMaximumDuration(self):
        # PROTECTED REGION ID(CspSubElementMaster.onMaximumDuration_read) ENABLED START #
        """Return the onMaximumDuration attribute."""
        return self._task_maximum_duration['on']
        # PROTECTED REGION END #    //  CspSubElementMaster.onMaximumDuration_read

    def write_onMaximumDuration(self, value):
        # PROTECTED REGION ID(CspSubElementMaster.onMaximumDuration_write) ENABLED START #
        """Set the onMaximumDuration attribute."""
        self._task_maximum_duration['on'] = value
        # PROTECTED REGION END #    //  CspSubElementMaster.onMaximumDuration_write

    def read_onMeasuredDuration(self):
        # PROTECTED REGION ID(CspSubElementMaster.onMeasuredDuration_read) ENABLED START #
        """Return the onMeasuredDuration attribute."""
        return self._task_measured_duration['on']
        # PROTECTED REGION END #    //  CspSubElementMaster.onMeasuredDuration_read

    def read_standbyProgress(self):
        # PROTECTED REGION ID(CspSubElementMaster.standbyProgress_read) ENABLED START #
        """Return the standbyProgress attribute."""
        return self._task_progress['standby']
        # PROTECTED REGION END #    //  CspSubElementMaster.standbyProgress_read

    def read_standbyMaximumDuration(self):
        # PROTECTED REGION ID(CspSubElementMaster.standbyMaximumDuration_read) ENABLED START #
        """Return the standbyMaximumDuration attribute."""
        return self._task_maximum_duration['standby']
        # PROTECTED REGION END #    //  CspSubElementMaster.standbyMaximumDuration_read

    def write_standbyMaximumDuration(self, value):
        # PROTECTED REGION ID(CspSubElementMaster.standbyMaximumDuration_write) ENABLED START #
        """Set the standbyMaximumDuration attribute."""
        self._task_maximum_duration['standby'] = value
        # PROTECTED REGION END #    //  CspSubElementMaster.standbyMaximumDuration_write

    def read_standbyMeasuredDuration(self):
        # PROTECTED REGION ID(CspSubElementMaster.standbyMeasuredDuration_read) ENABLED START #
        """Return the standbyMeasuredDuration attribute."""
        return self._task_measured_duration['standby']
        # PROTECTED REGION END #    //  CspSubElementMaster.standbyMeasuredDuration_read

    def read_offProgress(self):
        # PROTECTED REGION ID(CspSubElementMaster.offProgress_read) ENABLED START #
        """Return the offProgress attribute."""
        return self._task_progress['off']
        # PROTECTED REGION END #    //  CspSubElementMaster.offProgress_read

    def read_offMaximumDuration(self):
        # PROTECTED REGION ID(CspSubElementMaster.offMaximumDuration_read) ENABLED START #
        """Return the offMaximumDuration attribute."""
        return self._task_maximum_duration['off']
        # PROTECTED REGION END #    //  CspSubElementMaster.offMaximumDuration_read

    def write_offMaximumDuration(self, value):
        # PROTECTED REGION ID(CspSubElementMaster.offMaximumDuration_write) ENABLED START #
        """Set the offMaximumDuration attribute."""
        self._task_maximum_duration['off'] = value
        # PROTECTED REGION END #    //  CspSubElementMaster.offMaximumDuration_write

    def read_offMeasuredDuration(self):
        # PROTECTED REGION ID(CspSubElementMaster.offMeasuredDuration_read) ENABLED START #
        """Return the offMeasuredDuration attribute."""
        return self._task_measured_duration['off']
        # PROTECTED REGION END #    //  CspSubElementMaster.offMeasuredDuration_read

    def read_totalOutputDataRateToSdp(self):
        # PROTECTED REGION ID(CspSubElementMaster.totalOutputDataRateToSdp_read) ENABLED START #
        """Return the totalOutputDataRateToSdp attribute."""
        return self._total_output_rate_to_sdp
        # PROTECTED REGION END #    //  CspSubElementMaster.totalOutputDataRateToSdp_read

    def read_powerDelayStandbyOff(self):
        # PROTECTED REGION ID(CspSubElementMaster.powerDelayStandbyOff_read) ENABLED START #
        """Return the powerDelayStandbyOff attribute."""
        return self._power_delay_standy_off
        # PROTECTED REGION END #    //  CspSubElementMaster.powerDelayStandbyOff_read

    def write_powerDelayStandbyOff(self, value):
        # PROTECTED REGION ID(CspSubElementMaster.powerDelayStandbyOff_write) ENABLED START #
        """Set the powerDelayStandbyOff attribute."""
        self._power_delay_standy_off = value
        # PROTECTED REGION END #    //  CspSubElementMaster.powerDelayStandbyOff_write

    def read_loadFirmwareProgress(self):
        # PROTECTED REGION ID(CspSubElementMaster.loadFirmwareProgress_read) ENABLED START #
        """Return the loadFirmwareProgress attribute."""
        return self._task_progress['loadfirmware']
        # PROTECTED REGION END #    //  CspSubElementMaster.loadFirmwareProgress_read

    def read_loadFirmwareMaximumDuration(self):
        # PROTECTED REGION ID(CspSubElementMaster.loadFirmwareMaximumDuration_read) ENABLED START #
        """Return the loadFirmwareMaximumDuration attribute."""
        return self._task_maximum_duration['loadfirmware']
        # PROTECTED REGION END #    //  CspSubElementMaster.loadFirmwareMaximumDuration_read

    def write_loadFirmwareMaximumDuration(self, value):
        # PROTECTED REGION ID(CspSubElementMaster.loadFirmwareMaximumDuration_write) ENABLED START #
        """Set the loadFirmwareMaximumDuration attribute."""
        self._task_maximum_duration['loadfirmware'] = value
        # PROTECTED REGION END #    //  CspSubElementMaster.loadFirmwareMaximumDuration_write

    def read_loadFirmwareMeasuredDuration(self):
        # PROTECTED REGION ID(CspSubElementMaster.loadFirmwareMeasuredDuration_read) ENABLED START #
        """Return the loadFirmwareMeasuredDuration attribute."""
        return self._task_measured_duration['loadfirmware']
        # PROTECTED REGION END #    //  CspSubElementMaster.loadFirmwareMeasuredDuration_read

    # --------
    # Commands
    # --------
    class LoadFirmwareCommand(ResponseCommand):
        """
        A class for the CspSubELmentMaster's LoadFirmware command
        """
        def do(self, argin):
            """
            #Stateless hook for device LoadFirmware() command.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "LoadFirmware command completed OK"
            return (ResultCode.OK, message)

        def check_allowed(self):
            return self.state_model.op_state == tango.DevState.OFF and \
                   self.state_model.admin_mode == AdminMode.MAINTENANCE

    class PowerOnDevicesCommand(ResponseCommand):
        """
        A class for the CspSubELmentMaster's PowerOnDevices command.
        """
        def do(self, argin):
            """
            Stateless hook for device PowerOnDevices() command.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "PowerOnDevices command completed OK"
            return (ResultCode.OK, message)

        def check_allowed(self):
            return self.state_model.op_state == tango.DevState.ON

    class PowerOffDevicesCommand(ResponseCommand):
        """
        A class for the CspSubELmentMaster's PowerOffDevices command.
        """
        def do(self, argin):
            """
            Stateless hook for device PowerOffDevices() command.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "PowerOffDevices command completed OK"
            return (ResultCode.OK, message)

        def check_allowed(self):
            return self.state_model.op_state == tango.DevState.ON

    class ReInitDevicesCommand(ResponseCommand):
        """
        A class for the CspSubELmentMaster's ReInitDevices command.
        """
        def do(self, argin):
            """
            Stateless hook for device ReInitDevices() command.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "ReInitDevices command completed OK"
            return (ResultCode.OK, message)
        
        def check_allowed(self):
            return self.state_model.op_state == tango.DevState.ON

    def is_LoadFirmware_allowed(self):
        """
        Check if the LodFirmware command is allowed in the current 
        state.

        :raises ``CommandError`` if command not allowed
        :return ``True`` if command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("LoadFirmware")
        if not command.check_allowed():
            raise CommandError(f"{command.name} not allowed in {self.state_model.op_state}/{AdminMode(self.state_model.admin_mode).name}.")
        return True

    @command(
        dtype_in='DevVarStringArray',
        doc_in="The file name or a pointer to the filename , "
               "the list of components that use software or firmware package (file),"
               "checksum or signing",
        dtype_out='DevVarLongStringArray',
    )
    @DebugIt()
    def LoadFirmware(self, argin):
        # PROTECTED REGION ID(CspSubElementMaster.LoadFirmware) ENABLED START #
        """
        Deploy new versions of software and firmware and trigger 
        a restart so that a Component initializes using a newly 
        deployed version.

        :param argin: 
            A list of three strings:
            - The file name or a pointer to the filename specifed as URL. 
            - the list of components that use software or firmware package (file),
            - checksum or signing
            Ex: ['file://firmware.txt','test/dev/1, test/dev/2, test/dev/3', 
                 '918698a7fea3fa9da5996db001d33628'] 
        :type argin: 'DevVarStringArray'

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("LoadFirmware")
        (return_code, message) = command(argin)
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementMaster.LoadFirmware

    def is_PowerOnDevices_allowed(self):
        """
        Check if the LodFirmware command is allowed in the current 
        state.

        :raises ``CommandError`` if command not allowed
        :return ``True`` if command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("PowerOnDevices")
        if not command.check_allowed():
            raise CommandError(f'{command.name}: not allowed in {self.state_model.op_state}.')
        return True

    @command(
        dtype_in='DevVarStringArray',
        doc_in="The list of FQDNs to power-up",
        dtype_out='DevVarLongStringArray',
        doc_out="ReturnType, `informational message`",
    )
    @DebugIt()
    def PowerOnDevices(self, argin):
        # PROTECTED REGION ID(CspSubElementMaster.PowerOnDevices) ENABLED START #
        """
        Power-on a selected list of devices.

        :param argin: List of devices (FQDNs) to power-on.
        :type argin: 'DevVarStringArray'

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("PowerOnDevices")
        (return_code, message) = command(argin)
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementMaster.PowerOnDevices

    def is_PowerOffDevices_allowed(self):
        """
        Check if the PowerOffDevices command is allowed in the current 
        state.

        :raises ``CommandError`` if command not allowed
        :return ``True`` if command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("PowerOffDevices")
        if not command.check_allowed():
            raise CommandError(f'{command.name} not allowed in {self.state_model.op_state}.')
        return True

    @command(
        dtype_in='DevVarStringArray',
        doc_in="List of FQDNs to power-off",
        dtype_out='DevVarLongStringArray',
        doc_out="ReturnType, `informational message`",
    )
    @DebugIt()
    def PowerOffDevices(self, argin):
        # PROTECTED REGION ID(CspSubElementMaster.PowerOffDevices) ENABLED START #
        """
        Power-off a selected list of devices.

        :param argin: List of devices (FQDNs) to power-off.
        :type argin: 'DevVarStringArray'

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("PowerOffDevices")
        (return_code, message) = command(argin)
        return [[return_code], [message]]

        # PROTECTED REGION END #    //  CspSubElementMaster.PowerOffDevices

    def is_ReInitDevices_allowed(self):
        """
        Check if the ReInitDevices command is allowed in the current 
        state.

        :raises ``CommandError`` if command not allowed
        :return ``True`` if command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("ReInitDevices")
        if not command.check_allowed():
            raise CommandError(f'{command.name} not allowed in {self.state_model.op_state}.')
        return True

    @command(
        dtype_in='DevVarStringArray',
        doc_in="List of devices to re-initialize",
        dtype_out='DevVarLongStringArray',
        doc_out="ReturnType, `informational message`",
    )
    @DebugIt()
    def ReInitDevices(self, argin):
        # PROTECTED REGION ID(CspSubElementMaster.ReInitDevices) ENABLED START #
        """
        Reinitialize the devices passed in the input argument.
        The exact functionality may vary for different devices 
        and sub-systems, each TANGO Device/Server should define 
        what does ReinitDevices means.
        Ex:
        ReInitDevices FPGA -> reset
        ReInitDevices Master -> Restart
        ReInitDevices Leaf PC -> reboot

        :param argin: List of devices (FQDNs) to re-initialize.
        :type argin: 'DevVarStringArray'

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("ReInitDevices")
        (return_code, message) = command(argin)
        return [[return_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementMaster.ReInitDevices

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the CspSubElementMaster module."""
    # PROTECTED REGION ID(CspSubElementMaster.main) ENABLED START #
    return run((CspSubElementMaster,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspSubElementMaster.main


if __name__ == '__main__':
    main()
