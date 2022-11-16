# type: ignore
# pylint: skip-file  # TODO: Incrementally lint this repo
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
from collections import defaultdict
from typing import List, Tuple

import tango
from ska_control_model import AdminMode
from tango import AttrWriteType, DebugIt
from tango.server import attribute, command, device_property, run

from ska_tango_base import SKAController
from ska_tango_base.commands import FastCommand, ResultCode

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
            """
            super().do()

            # _cmd_progress: command execution's progress percentage
            # implemented as a default dictionary:
            # keys: the command name in lower case(on, off, standby,..)
            # values: the progress percentage (default 0)
            self._device._cmd_progress = defaultdict(int)

            # _cmd_maximun_duration: command execution's expected maximum
            # duration (msec.) implemented as a default dictionary:
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
            self._device._power_delay_standby_on = self._device.PowerDelayStandbyOn
            self._device._power_delay_standby_off = self._device.PowerDelayStandbyOff

            message = "CspSubElementController Init command completed OK"
            self._device.logger.info(message)
            self._completed()
            return (ResultCode.OK, message)

    # ------------------
    # Attributes methods
    # ------------------
    def read_powerDelayStandbyOn(self):
        """
        Return the powerDelayStandbyOn attribute.

        :return: the powerDelayStandbyOn attribute.
        """
        return self._power_delay_standby_on

    def write_powerDelayStandbyOn(self, value):
        """
        Set the powerDelayStandbyOn attribute.

        :param value: the new standby-on power delay.
        """
        self._power_delay_standby_on = value

    def read_onProgress(self):
        """
        Return the onProgress attribute.

        :return: the onProgress attribute.
        """
        return self._cmd_progress["on"]

    def read_onMaximumDuration(self):
        """
        Return the onMaximumDuration attribute.

        :return: the onMaximumDuration attribute.
        """
        return self._cmd_maximum_duration["on"]

    def write_onMaximumDuration(self, value):
        """
        Set the onMaximumDuration attribute.

        :param value: the new maximum duration
        """
        self._cmd_maximum_duration["on"] = value

    def read_onMeasuredDuration(self):
        """
        Return the onMeasuredDuration attribute.

        :return: the onMeasuredDuration attribute.
        """
        return self._cmd_measured_duration["on"]

    def read_standbyProgress(self):
        """
        Return the standbyProgress attribute.

        :return: the standbyProgress attribute.
        """
        return self._cmd_progress["standby"]

    def read_standbyMaximumDuration(self):
        """
        Return the standbyMaximumDuration attribute.

        :return: the standbyMaximumDuration attribute.
        """
        return self._cmd_maximum_duration["standby"]

    def write_standbyMaximumDuration(self, value):
        """
        Set the standbyMaximumDuration attribute.

        :param value: the new maximum duration
        """
        self._cmd_maximum_duration["standby"] = value

    def read_standbyMeasuredDuration(self):
        """
        Return the standbyMeasuredDuration attribute.

        :return: the standbyMeasuredDuration attribute.
        """
        return self._cmd_measured_duration["standby"]

    def read_offProgress(self):
        """
        Return the offProgress attribute.

        :return: the offProgress attribute.
        """
        return self._cmd_progress["off"]

    def read_offMaximumDuration(self):
        """
        Return the offMaximumDuration attribute.

        :return: the offMaximumDuration attribute.
        """
        return self._cmd_maximum_duration["off"]

    def write_offMaximumDuration(self, value):
        """
        Set the offMaximumDuration attribute.

        :param value: the new maximum duration.
        """
        self._cmd_maximum_duration["off"] = value

    def read_offMeasuredDuration(self):
        """
        Return the offMeasuredDuration attribute.

        :return: the offMeasuredDuration attribute.
        """
        return self._cmd_measured_duration["off"]

    def read_totalOutputDataRateToSdp(self):
        """
        Return the totalOutputDataRateToSdp attribute.

        :return: the totalOutputDataRateToSdp attribute.
        """
        return self._total_output_rate_to_sdp

    def read_powerDelayStandbyOff(self):
        """
        Return the powerDelayStandbyOff attribute.

        :return: the powerDelayStandbyOff attribute.
        """
        return self._power_delay_standby_off

    def write_powerDelayStandbyOff(self, value):
        """
        Set the powerDelayStandbyOff attribute.

        :param value: the new standby-off power delay.
        """
        self._power_delay_standby_off = value

    def read_loadFirmwareProgress(self):
        """
        Return the loadFirmwareProgress attribute.

        :return: the loadFirmwareProgress attribute.
        """
        return self._cmd_progress["loadfirmware"]

    def read_loadFirmwareMaximumDuration(self):
        """
        Return the loadFirmwareMaximumDuration attribute.

        :return: the loadFirmwareMaximumDuration attribute.
        """
        return self._cmd_maximum_duration["loadfirmware"]

    def write_loadFirmwareMaximumDuration(self, value):
        """
        Set the loadFirmwareMaximumDuration attribute.

        :param value: the new maximum duration.
        """
        self._cmd_maximum_duration["loadfirmware"] = value

    def read_loadFirmwareMeasuredDuration(self):
        """
        Return the loadFirmwareMeasuredDuration attribute.

        :return: the loadFirmwareMeasuredDuration attribute.
        """
        return self._cmd_measured_duration["loadfirmware"]

    # --------
    # Commands
    # --------
    class LoadFirmwareCommand(FastCommand):
        """A class for the LoadFirmware command."""

        def __init__(self, logger=None):
            """
            Initialise a new LoadFirmwareCommand instance.

            :param logger: a logger for the command to log with
            """
            super().__init__(logger=logger)

        def do(self, argin) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device LoadFirmware() command.

            :param argin: argument to command, currently unused

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            message = "LoadFirmware command completed OK"
            return (ResultCode.OK, message)

    class PowerOnDevicesCommand(FastCommand):
        """A class for the CspSubElementController's PowerOnDevices command."""

        def __init__(self, logger=None):
            """
            Initialise a new `PowerOnDevicesCommand``` instance.

            :param logger: a logger for the command to log with
            """
            super().__init__(logger=logger)

        def do(self, argin) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device PowerOnDevices() command.

            :param argin: argument to command, currently unused

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            message = "PowerOnDevices command completed OK"
            return (ResultCode.OK, message)

    class PowerOffDevicesCommand(FastCommand):
        """A class for the CspSubElementController's PowerOffDevices command."""

        def __init__(self, logger=None):
            """
            Initialise a new ``PowerOffDevicesCommand`` instance.

            :param logger: a logger for the command to log with
            """
            super().__init__(logger=logger)

        def do(self, argin) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device PowerOffDevices() command.

            :param argin: argument to command, currently unused

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            message = "PowerOffDevices command completed OK"
            return (ResultCode.OK, message)

    class ReInitDevicesCommand(FastCommand):
        """A class for the CspSubElementController's ReInitDevices command."""

        def __init__(self, logger=None):
            """
            Initialise a new ``ReInitDevicesCommand`` instance.

            :param logger: a logger for the command to log with
            """
            super().__init__(logger=logger)

        def do(self, argin) -> Tuple[ResultCode, str]:
            """
            Stateless hook for device ReInitDevices() command.

            :param argin: argument to command, currently unused

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            message = "ReInitDevices command completed OK"
            return (ResultCode.OK, message)

    def is_LoadFirmware_allowed(self) -> bool:
        """
        Check if the LoadFirmware command is allowed in the current state.

        :return: ``True`` if command is allowed
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
    def LoadFirmware(self, argin: List[str]) -> Tuple[ResultCode, str]:
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
        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        """
        handler = self.get_command_object("LoadFirmware")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    def is_PowerOnDevices_allowed(self) -> bool:
        """
        Check if the PowerOnDevice command is allowed in the current state.

        :return: ``True`` if command is allowed
        """
        return self.get_state() == tango.DevState.ON

    @command(
        dtype_in="DevVarStringArray",
        doc_in="The list of FQDNs to power-up",
        dtype_out="DevVarLongStringArray",
        doc_out="ReturnType, `informational message`",
    )
    @DebugIt()
    def PowerOnDevices(self, argin: List[str]) -> Tuple[ResultCode, str]:
        """
        Power-on a selected list of devices.

        :param argin: List of devices (FQDNs) to power-on.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        """
        handler = self.get_command_object("PowerOnDevices")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    def is_PowerOffDevices_allowed(self) -> bool:
        """
        Check if the PowerOffDevices command is allowed in the current state.

        :return: ``True`` if command is allowed
        """
        return self.get_state() == tango.DevState.ON

    @command(
        dtype_in="DevVarStringArray",
        doc_in="List of FQDNs to power-off",
        dtype_out="DevVarLongStringArray",
        doc_out="ReturnType, `informational message`",
    )
    @DebugIt()
    def PowerOffDevices(self, argin: List[str]) -> Tuple[ResultCode, str]:
        """
        Power-off a selected list of devices.

        :param argin: List of devices (FQDNs) to power-off.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        """
        handler = self.get_command_object("PowerOffDevices")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

    def is_ReInitDevices_allowed(self) -> bool:
        """
        Check if the ReInitDevices command is allowed in the current state.

        :return: ``True`` if command is allowed
        """
        return self.get_state() == tango.DevState.ON

    @command(
        dtype_in="DevVarStringArray",
        doc_in="List of devices to re-initialize",
        dtype_out="DevVarLongStringArray",
        doc_out="ReturnType, `informational message`",
    )
    @DebugIt()
    def ReInitDevices(self, argin: List[str]) -> Tuple[ResultCode, str]:
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

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        """
        handler = self.get_command_object("ReInitDevices")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]


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
    return run((CspSubElementController,), args=args or None, **kwargs)


if __name__ == "__main__":
    main()
