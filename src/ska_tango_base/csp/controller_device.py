# -*- coding: utf-8 -*-
#
# This file is part of the CspSubElementController project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""
CspSubElementController.

Controller device for SKA CSP Subelement.
"""
# PROTECTED REGION ID(CspSubElementController.additionnal_import) ENABLED START #
# Python standard library
from collections import defaultdict

# Tango imports
import tango
from tango import DebugIt, AttrWriteType
from tango.server import run, attribute, command, device_property

# SKA specific imports

from ska_tango_base import SKAController
from ska_tango_base.commands import ResultCode, FastCommand
from ska_tango_base.control_model import AdminMode

# PROTECTED REGION END #    //  CspSubElementController.additionnal_import

__all__ = ["CspSubElementController", "main"]


class CspSubElementController(SKAController):
    """
    Controller device for SKA CSP Subelement.

     **Properties:**

    - Device Property
        PowerDelayStandbyOn
            - Delay in sec between  power-up stages in Standby<-> On transitions.
            - Type:'DevFloat'

        PowerDelayStandByOff
            - Delay in sec between  power-up stages in Standby-> Off transition.
            - Type:'DevFloat'
    """

    # PROTECTED REGION ID(CspSubElementController.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  CspSubElementController.class_variable

    # -----------------
    # Device Properties
    # -----------------

    PowerDelayStandbyOn = device_property(dtype="DevFloat", default_value=2.0)

    PowerDelayStandbyOff = device_property(dtype="DevFloat", default_value=1.5)

    # ----------
    # Attributes
    # ----------

    powerDelayStandbyOn = attribute(
        dtype="DevFloat",
        access=AttrWriteType.READ_WRITE,
        label="powerDelayStandbyOn",
        unit="sec.",
        doc="Delay in sec between the power-up stages in Standby<->On transitions.",
    )
    """Device attribute."""

    powerDelayStandbyOff = attribute(
        dtype="DevFloat",
        access=AttrWriteType.READ_WRITE,
        label="powerDelayStandbyOff",
        unit="sec",
        doc="Delay in sec between the power-up stages in Standby->Off transitions.",
    )
    """Device attribute."""

    onProgress = attribute(
        dtype="DevUShort",
        label="onProgress",
        max_value=100,
        min_value=0,
        doc="Progress percentage of the command execution.",
    )
    """Device attribute."""

    onMaximumDuration = attribute(
        dtype="DevFloat",
        access=AttrWriteType.READ_WRITE,
        label="onMaximumDuration",
        unit="sec.",
        doc="The expected maximum duration (sec.) to execute the On command.",
    )
    """Device attribute."""

    onMeasuredDuration = attribute(
        dtype="DevFloat",
        label="onMeasuredDuration",
        unit="sec",
        doc="The measured time (sec) taken to execute the command.",
    )
    """Device attribute."""

    standbyProgress = attribute(
        dtype="DevUShort",
        label="standbyProgress",
        max_value=100,
        min_value=0,
        doc="Progress percentage of the command execution.",
    )
    """Device attribute."""

    standbyMaximumDuration = attribute(
        dtype="DevFloat",
        access=AttrWriteType.READ_WRITE,
        label="standbyMaximumDuration",
        unit="sec.",
        doc="The expected maximum duration (sec.) to execute the Standby command.",
    )
    """Device attribute."""

    standbyMeasuredDuration = attribute(
        dtype="DevFloat",
        label="standbyMeasuredDuration",
        unit="sec",
        doc="The measured time (sec) taken to execute the Standby command.",
    )
    """Device attribute."""

    offProgress = attribute(
        dtype="DevUShort",
        label="offProgress",
        max_value=100,
        min_value=0,
        doc="Progress percentage of the command execution.",
    )
    """Device attribute."""

    offMaximumDuration = attribute(
        dtype="DevFloat",
        access=AttrWriteType.READ_WRITE,
        label="offMaximumDuration",
        unit="sec.",
        doc="The expected maximum duration (sec.) to execute the Off command.",
    )
    """Device attribute."""

    offMeasuredDuration = attribute(
        dtype="DevFloat",
        label="offMeasuredDuration",
        unit="sec",
        doc="The measured time (sec) taken to execute the Off command.",
    )
    """Device attribute."""

    totalOutputDataRateToSdp = attribute(
        dtype="DevFloat",
        label="totalOutputDataRateToSdp",
        unit="GB/s",
        doc="Report the total link expected  output data rate.",
    )
    """Device attribute."""

    loadFirmwareProgress = attribute(
        dtype="DevUShort",
        label="loadFirmwareProgress",
        max_value=100,
        min_value=0,
        doc="The command progress percentage.",
    )
    """Device attribute."""

    loadFirmwareMaximumDuration = attribute(
        dtype="DevFloat",
        access=AttrWriteType.READ_WRITE,
        label="loadFirmwareMaximumDuration",
        unit="sec",
        doc="The expected maximum duration (in sec) for command execution.",
    )
    """Device attribute."""

    loadFirmwareMeasuredDuration = attribute(
        dtype="DevFloat",
        label="loadFirmwareMeasuredDuration",
        unit="sec",
        doc="The command execution measured duration (in sec).",
    )
    """Device attribute."""

    # ---------------
    # General methods
    # ---------------

    def init_command_objects(self):
        """Set up the command objects."""
        super().init_command_objects()
        self.register_command_object(
            "LoadFirmware", self.LoadFirmwareCommand(logger=self.logger)
        )
        self.register_command_object(
            "PowerOnDevices", self.PowerOnDevicesCommand(logger=self.logger)
        )
        self.register_command_object(
            "PowerOffDevices", self.PowerOffDevicesCommand(logger=self.logger)
        )
        self.register_command_object(
            "ReInitDevices", self.ReInitDevicesCommand(logger=self.logger)
        )

    class InitCommand(SKAController.InitCommand):
        """A class for the CspSubElementController's init_device() "command"."""

        def do(self):
            """
            Stateless hook for device initialisation.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            super().do()

            # _cmd_progress: command execution's progress percentage
            # implemented as a default dictionary:
            # keys: the command name in lower case(on, off, standby,..)
            # values: the progress percentage (default 0)
            self._device._cmd_progress = defaultdict(int)

            # _cmd_maximun_duration: command execution's expected maximum duration (msec.)
            # implemented as a default dictionary:
            # keys: the command name in lower case(on, off, standby,..)
            # values: the expected maximum duration in sec.
            self._device._cmd_maximum_duration = defaultdict(float)

            # _cmd_measure_duration: command execution's measured duration (msec.)
            # implemented as a default dictionary:
            # keys: the command name in lower case(on, off, standby,..)
            # values: the measured execution time (sec.)
            self._device._cmd_measured_duration = defaultdict(float)

            self._device._total_output_rate_to_sdp = 0.0

            # initialise using defaults in device properties
            self._device._power_delay_standy_on = self._device.PowerDelayStandbyOn
            self._device._power_delay_standy_off = self._device.PowerDelayStandbyOff

            message = "CspSubElementController Init command completed OK"
            self._device.logger.info(message)
            return (ResultCode.OK, message)

    def always_executed_hook(self):
        """
        Perform actions always executed before any Tango command is executed.

        This is a Tango hook.
        """
        # PROTECTED REGION ID(CspSubElementController.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  CspSubElementController.always_executed_hook

    def delete_device(self):
        """
        Clean up any resources prior to device deletion.

        This method is a Tango hook that is called by the device
        destructor and by the device Init command. It allows for any
        memory or other resources allocated in the init_device method to
        be released prior to device deletion.
        """
        # PROTECTED REGION ID(CspSubElementController.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  CspSubElementController.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_powerDelayStandbyOn(self):
        # PROTECTED REGION ID(CspSubElementController.powerDelayStandbyOn_read) ENABLED START #
        """Return the powerDelayStandbyOn attribute."""
        return self._power_delay_standy_on
        # PROTECTED REGION END #    //  CspSubElementController.powerDelayStandbyOn_read

    def write_powerDelayStandbyOn(self, value):
        # PROTECTED REGION ID(CspSubElementController.powerDelayStandbyOn_write) ENABLED START #
        """Set the powerDelayStandbyOn attribute."""
        self._power_delay_standy_on = value
        # PROTECTED REGION END #    //  CspSubElementController.powerDelayStandbyOn_write

    def read_onProgress(self):
        # PROTECTED REGION ID(CspSubElementController.onProgress_read) ENABLED START #
        """Return the onProgress attribute."""
        return self._cmd_progress["on"]
        # PROTECTED REGION END #    //  CspSubElementController.onProgress_read

    def read_onMaximumDuration(self):
        # PROTECTED REGION ID(CspSubElementController.onMaximumDuration_read) ENABLED START #
        """Return the onMaximumDuration attribute."""
        return self._cmd_maximum_duration["on"]
        # PROTECTED REGION END #    //  CspSubElementController.onMaximumDuration_read

    def write_onMaximumDuration(self, value):
        # PROTECTED REGION ID(CspSubElementController.onMaximumDuration_write) ENABLED START #
        """Set the onMaximumDuration attribute."""
        self._cmd_maximum_duration["on"] = value
        # PROTECTED REGION END #    //  CspSubElementController.onMaximumDuration_write

    def read_onMeasuredDuration(self):
        # PROTECTED REGION ID(CspSubElementController.onMeasuredDuration_read) ENABLED START #
        """Return the onMeasuredDuration attribute."""
        return self._cmd_measured_duration["on"]
        # PROTECTED REGION END #    //  CspSubElementController.onMeasuredDuration_read

    def read_standbyProgress(self):
        # PROTECTED REGION ID(CspSubElementController.standbyProgress_read) ENABLED START #
        """Return the standbyProgress attribute."""
        return self._cmd_progress["standby"]
        # PROTECTED REGION END #    //  CspSubElementController.standbyProgress_read

    def read_standbyMaximumDuration(self):
        # PROTECTED REGION ID(CspSubElementController.standbyMaximumDuration_read) ENABLED START #
        """Return the standbyMaximumDuration attribute."""
        return self._cmd_maximum_duration["standby"]
        # PROTECTED REGION END #    //  CspSubElementController.standbyMaximumDuration_read

    def write_standbyMaximumDuration(self, value):
        # PROTECTED REGION ID(CspSubElementController.standbyMaximumDuration_write) ENABLED START #
        """Set the standbyMaximumDuration attribute."""
        self._cmd_maximum_duration["standby"] = value
        # PROTECTED REGION END #    //  CspSubElementController.standbyMaximumDuration_write

    def read_standbyMeasuredDuration(self):
        # PROTECTED REGION ID(CspSubElementController.standbyMeasuredDuration_read) ENABLED START #
        """Return the standbyMeasuredDuration attribute."""
        return self._cmd_measured_duration["standby"]
        # PROTECTED REGION END #    //  CspSubElementController.standbyMeasuredDuration_read

    def read_offProgress(self):
        # PROTECTED REGION ID(CspSubElementController.offProgress_read) ENABLED START #
        """Return the offProgress attribute."""
        return self._cmd_progress["off"]
        # PROTECTED REGION END #    //  CspSubElementController.offProgress_read

    def read_offMaximumDuration(self):
        # PROTECTED REGION ID(CspSubElementController.offMaximumDuration_read) ENABLED START #
        """Return the offMaximumDuration attribute."""
        return self._cmd_maximum_duration["off"]
        # PROTECTED REGION END #    //  CspSubElementController.offMaximumDuration_read

    def write_offMaximumDuration(self, value):
        # PROTECTED REGION ID(CspSubElementController.offMaximumDuration_write) ENABLED START #
        """Set the offMaximumDuration attribute."""
        self._cmd_maximum_duration["off"] = value
        # PROTECTED REGION END #    //  CspSubElementController.offMaximumDuration_write

    def read_offMeasuredDuration(self):
        # PROTECTED REGION ID(CspSubElementController.offMeasuredDuration_read) ENABLED START #
        """Return the offMeasuredDuration attribute."""
        return self._cmd_measured_duration["off"]
        # PROTECTED REGION END #    //  CspSubElementController.offMeasuredDuration_read

    def read_totalOutputDataRateToSdp(self):
        # PROTECTED REGION ID(CspSubElementController.totalOutputDataRateToSdp_read) ENABLED START #
        """Return the totalOutputDataRateToSdp attribute."""
        return self._total_output_rate_to_sdp
        # PROTECTED REGION END #    //  CspSubElementController.totalOutputDataRateToSdp_read

    def read_powerDelayStandbyOff(self):
        # PROTECTED REGION ID(CspSubElementController.powerDelayStandbyOff_read) ENABLED START #
        """Return the powerDelayStandbyOff attribute."""
        return self._power_delay_standy_off
        # PROTECTED REGION END #    //  CspSubElementController.powerDelayStandbyOff_read

    def write_powerDelayStandbyOff(self, value):
        # PROTECTED REGION ID(CspSubElementController.powerDelayStandbyOff_write) ENABLED START #
        """Set the powerDelayStandbyOff attribute."""
        self._power_delay_standy_off = value
        # PROTECTED REGION END #    //  CspSubElementController.powerDelayStandbyOff_write

    def read_loadFirmwareProgress(self):
        # PROTECTED REGION ID(CspSubElementController.loadFirmwareProgress_read) ENABLED START #
        """Return the loadFirmwareProgress attribute."""
        return self._cmd_progress["loadfirmware"]
        # PROTECTED REGION END #    //  CspSubElementController.loadFirmwareProgress_read

    def read_loadFirmwareMaximumDuration(self):
        # PROTECTED REGION ID(CspSubElementController.loadFirmwareMaximumDuration_read) ENABLED START #
        """Return the loadFirmwareMaximumDuration attribute."""
        return self._cmd_maximum_duration["loadfirmware"]
        # PROTECTED REGION END #    //  CspSubElementController.loadFirmwareMaximumDuration_read

    def write_loadFirmwareMaximumDuration(self, value):
        # PROTECTED REGION ID(CspSubElementController.loadFirmwareMaximumDuration_write) ENABLED START #
        """Set the loadFirmwareMaximumDuration attribute."""
        self._cmd_maximum_duration["loadfirmware"] = value
        # PROTECTED REGION END #    //  CspSubElementController.loadFirmwareMaximumDuration_write

    def read_loadFirmwareMeasuredDuration(self):
        # PROTECTED REGION ID(CspSubElementController.loadFirmwareMeasuredDuration_read) ENABLED START #
        """Return the loadFirmwareMeasuredDuration attribute."""
        return self._cmd_measured_duration["loadfirmware"]
        # PROTECTED REGION END #    //  CspSubElementController.loadFirmwareMeasuredDuration_read

    # --------
    # Commands
    # --------
    class LoadFirmwareCommand(FastCommand):
        """A class for the LoadFirmware command."""

        def __init__(self, logger=None):
            """Initialise a new LoadFirmwareCommand instance."""
            super().__init__(logger=logger)

        def do(self, argin):
            """
            Stateless hook for device LoadFirmware() command.

            :param argin: argument to command, currently unused

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "LoadFirmware command completed OK"
            return (ResultCode.OK, message)

    class PowerOnDevicesCommand(FastCommand):
        """A class for the CspSubElementController's PowerOnDevices command."""

        def __init__(self, logger=None):
            """Initialise a new `PowerOnDevicesCommand``` instance."""
            super().__init__(logger=logger)

        def do(self, argin):
            """
            Stateless hook for device PowerOnDevices() command.

            :param argin: argument to command, currently unused

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "PowerOnDevices command completed OK"
            return (ResultCode.OK, message)

    class PowerOffDevicesCommand(FastCommand):
        """A class for the CspSubElementController's PowerOffDevices command."""

        def __init__(self, logger=None):
            """Initialise a new ``PowerOffDevicesCommand`` instance."""
            super().__init__(logger=logger)

        def do(self, argin):
            """
            Stateless hook for device PowerOffDevices() command.

            :param argin: argument to command, currently unused

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "PowerOffDevices command completed OK"
            return (ResultCode.OK, message)

    class ReInitDevicesCommand(FastCommand):
        """A class for the CspSubElementController's ReInitDevices command."""

        def __init__(self, logger=None):
            """Initialise a new ``ReInitDevicesCommand`` instance."""
            super().__init__(logger=logger)

        def do(self, argin):
            """
            Stateless hook for device ReInitDevices() command.

            :param argin: argument to command, currently unused

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "ReInitDevices command completed OK"
            return (ResultCode.OK, message)

    def is_LoadFirmware_allowed(self):
        """
        Check if the LoadFirmware command is allowed in the current state.

        :return: ``True`` if command is allowed
        :rtype: boolean
        """
        return (
            self.get_state() == tango.DevState.OFF
            and self.admin_mode_model.admin_mode == AdminMode.MAINTENANCE
        )

    @command(
        dtype_in="DevVarStringArray",
        doc_in="The file name or a pointer to the filename , "
        "the list of components that use software or firmware package (file),"
        "checksum or signing",
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def LoadFirmware(self, argin):
        # PROTECTED REGION ID(CspSubElementController.LoadFirmware) ENABLED START #
        """
        Deploy new versions of software and firmware.

        After deployment, a restart is triggers so that a Component
        initializes using a newly deployed version.

        :param argin: A list of three strings:
            - The file name or a pointer to the filename specified as URL.
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
        handler = self.get_command_object("LoadFirmware")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementController.LoadFirmware

    def is_PowerOnDevices_allowed(self):
        """
        Check if the PowerOnDevice command is allowed in the current state.

        :return: ``True`` if command is allowed
        :rtype: boolean
        """
        return self.get_state() == tango.DevState.ON

    @command(
        dtype_in="DevVarStringArray",
        doc_in="The list of FQDNs to power-up",
        dtype_out="DevVarLongStringArray",
        doc_out="ReturnType, `informational message`",
    )
    @DebugIt()
    def PowerOnDevices(self, argin):
        # PROTECTED REGION ID(CspSubElementController.PowerOnDevices) ENABLED START #
        """
        Power-on a selected list of devices.

        :param argin: List of devices (FQDNs) to power-on.
        :type argin: 'DevVarStringArray'

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        handler = self.get_command_object("PowerOnDevices")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementController.PowerOnDevices

    def is_PowerOffDevices_allowed(self):
        """
        Check if the PowerOffDevices command is allowed in the current state.

        :return: ``True`` if command is allowed
        :rtype: boolean
        """
        return self.get_state() == tango.DevState.ON

    @command(
        dtype_in="DevVarStringArray",
        doc_in="List of FQDNs to power-off",
        dtype_out="DevVarLongStringArray",
        doc_out="ReturnType, `informational message`",
    )
    @DebugIt()
    def PowerOffDevices(self, argin):
        # PROTECTED REGION ID(CspSubElementController.PowerOffDevices) ENABLED START #
        """
        Power-off a selected list of devices.

        :param argin: List of devices (FQDNs) to power-off.
        :type argin: 'DevVarStringArray'

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        handler = self.get_command_object("PowerOffDevices")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

        # PROTECTED REGION END #    //  CspSubElementController.PowerOffDevices

    def is_ReInitDevices_allowed(self):
        """
        Check if the ReInitDevices command is allowed in the current state.

        :return: ``True`` if command is allowed
        :rtype: boolean
        """
        return self.get_state() == tango.DevState.ON

    @command(
        dtype_in="DevVarStringArray",
        doc_in="List of devices to re-initialize",
        dtype_out="DevVarLongStringArray",
        doc_out="ReturnType, `informational message`",
    )
    @DebugIt()
    def ReInitDevices(self, argin):
        # PROTECTED REGION ID(CspSubElementController.ReInitDevices) ENABLED START #
        """
        Reinitialize the devices passed in the input argument.

        The exact functionality may vary for different devices
        and sub-systems, each Tango Device/Server should define
        what does ReInitDevices means.
        Ex:
        ReInitDevices FPGA -> reset
        ReInitDevices Controller -> Restart
        ReInitDevices Leaf PC -> reboot

        :param argin: List of devices (FQDNs) to re-initialize.
        :type argin: 'DevVarStringArray'

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        handler = self.get_command_object("ReInitDevices")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]
        # PROTECTED REGION END #    //  CspSubElementController.ReInitDevices


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """
    Entry point for the CspSubElementController module.

    :param args: str
    :param kwargs: str

    :return: exit code
    """
    # PROTECTED REGION ID(CspSubElementController.main) ENABLED START #
    return run((CspSubElementController,), args=args, **kwargs)
    # PROTECTED REGION END #    //  CspSubElementController.main


if __name__ == "__main__":
    main()
