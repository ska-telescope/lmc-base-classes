# -*- coding: utf-8 -*-
#
# This file is part of the SKAController project
#
#
#

"""
SKAController.

Controller device
"""
# PROTECTED REGION ID(SKAController.additionnal_import) ENABLED START #
# Tango imports
from tango import DebugIt
from tango.server import run, attribute, command, device_property

# SKA specific imports
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import FastCommand, DeviceInitCommand, ResultCode
from ska_tango_base.utils import (
    validate_capability_types,
    validate_input_sizes,
    convert_dict_to_list,
)


# PROTECTED REGION END #    //  SKAController.additionnal_imports

__all__ = ["SKAController", "main"]


class SKAController(SKABaseDevice):
    """Controller device."""

    def init_command_objects(self):
        """Set up the command objects."""
        super().init_command_objects()
        self.register_command_object(
            "IsCapabilityAchievable",
            self.IsCapabilityAchievableCommand(self, self.logger),
        )

    class InitCommand(DeviceInitCommand):
        """A class for the SKAController's init_device() "command"."""

        def do(self):
            """
            Stateless hook for device initialisation.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            self._device._element_logger_address = ""
            self._device._element_alarm_address = ""
            self._device._element_tel_state_address = ""
            self._device._element_database_address = ""
            self._device._element_alarm_device = ""
            self._device._element_tel_state_device = ""
            self._device._element_database_device = ""
            self._device._max_capabilities = {}
            if self._device.MaxCapabilities:
                for max_capability in self._device.MaxCapabilities:
                    capability_type, max_capability_instances = max_capability.split(
                        ":"
                    )
                    self._device._max_capabilities[capability_type] = int(
                        max_capability_instances
                    )
            self._device._available_capabilities = self._device._max_capabilities.copy()

            message = "SKAController Init command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    # PROTECTED REGION ID(SKAController.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.class_variable

    # -----------------
    # Device Properties
    # -----------------

    # List of maximum number of instances per capability type provided by this Element;
    # CORRELATOR=512, PSS-BEAMS=4, PST-BEAMS=6, VLBI-BEAMS=4  or for DSH it can be:
    # BAND-1=1, BAND-2=1, BAND3=0, BAND-4=0, BAND-5=0 (if only bands 1&amp;2 is installed)
    MaxCapabilities = device_property(
        dtype=("str",),
    )

    # ----------
    # Attributes
    # ----------

    elementLoggerAddress = attribute(
        dtype="str",
        doc="FQDN of Element Logger",
    )
    """Device attribute."""

    elementAlarmAddress = attribute(
        dtype="str",
        doc="FQDN of Element Alarm Handlers",
    )
    """Device attribute."""

    elementTelStateAddress = attribute(
        dtype="str",
        doc="FQDN of Element TelState device",
    )
    """Device attribute."""

    elementDatabaseAddress = attribute(
        dtype="str",
        doc="FQDN of Element Database device",
    )
    """Device attribute."""

    maxCapabilities = attribute(
        dtype=("str",),
        max_dim_x=20,
        doc=(
            "Maximum number of instances of each capability type,"
            " e.g. 'CORRELATOR:512', 'PSS-BEAMS:4'."
        ),
    )
    """Device attribute."""

    availableCapabilities = attribute(
        dtype=("str",),
        max_dim_x=20,
        doc="A list of available number of instances of each capability type, "
        "e.g. 'CORRELATOR:512', 'PSS-BEAMS:4'.",
    )
    """Device attribute."""

    # ---------------
    # General methods
    # ---------------

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKAController.always_executed_hook) ENABLED START #
        """
        Perform actions that are executed before every device command.

        This is a Tango hook.
        """
        pass
        # PROTECTED REGION END #    //  SKAController.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKAController.delete_device) ENABLED START #
        """
        Clean up any resources prior to device deletion.

        This method is a Tango hook that is called by the device
        destructor and by the device Init command. It allows for any
        memory or other resources allocated in the init_device method to
        be released prior to device deletion.
        """
        pass
        # PROTECTED REGION END #    //  SKAController.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_elementLoggerAddress(self):
        # PROTECTED REGION ID(SKAController.elementLoggerAddress_read) ENABLED START #
        """Read FQDN of Element Logger device."""
        return self._element_logger_address
        # PROTECTED REGION END #    //  SKAController.elementLoggerAddress_read

    def read_elementAlarmAddress(self):
        # PROTECTED REGION ID(SKAController.elementAlarmAddress_read) ENABLED START #
        """Read FQDN of Element Alarm device."""
        return self._element_alarm_address
        # PROTECTED REGION END #    //  SKAController.elementAlarmAddress_read

    def read_elementTelStateAddress(self):
        # PROTECTED REGION ID(SKAController.elementTelStateAddress_read) ENABLED START #
        """Read FQDN of Element TelState device."""
        return self._element_tel_state_address
        # PROTECTED REGION END #    //  SKAController.elementTelStateAddress_read

    def read_elementDatabaseAddress(self):
        # PROTECTED REGION ID(SKAController.elementDatabaseAddress_read) ENABLED START #
        """Read FQDN of Element Database device."""
        return self._element_database_address
        # PROTECTED REGION END #    //  SKAController.elementDatabaseAddress_read

    def read_maxCapabilities(self):
        # PROTECTED REGION ID(SKAController.maxCapabilities_read) ENABLED START #
        """Read maximum number of instances of each capability type."""
        return convert_dict_to_list(self._max_capabilities)
        # PROTECTED REGION END #    //  SKAController.maxCapabilities_read

    def read_availableCapabilities(self):
        # PROTECTED REGION ID(SKAController.availableCapabilities_read) ENABLED START #
        """Read list of available number of instances of each capability type."""
        return convert_dict_to_list(self._available_capabilities)
        # PROTECTED REGION END #    //  SKAController.availableCapabilities_read

    # --------
    # Commands
    # --------

    class IsCapabilityAchievableCommand(FastCommand):
        """A class for the SKAController's IsCapabilityAchievable() command."""

        def __init__(self, device, logger=None):
            """
            Initialise a new instance.

            :param device: the device that this command acts upon.
            :param logger: a logger for this command to log with.
            """
            self._device = device
            super().__init__(logger=logger)

        def do(self, argin):
            """
            Stateless hook for device IsCapabilityAchievable() command.

            :return: Whether the capability is achievable
            :rtype: bool
            """
            command_name = "isCapabilityAchievable"
            capabilities_instances, capability_types = argin
            validate_input_sizes(command_name, argin)
            validate_capability_types(
                command_name,
                capability_types,
                list(self._device._max_capabilities.keys()),
            )

            for capability_type, capability_instances in zip(
                capability_types, capabilities_instances
            ):
                if (
                    not self._device._available_capabilities[capability_type]
                    >= capability_instances
                ):
                    return False
            return True

    @command(
        dtype_in="DevVarLongStringArray",
        doc_in="[nrInstances][Capability types]",
        dtype_out=bool,
        doc_out="(ResultCode, 'Command unique ID')",
    )
    @DebugIt()
    def isCapabilityAchievable(self, argin):
        # PROTECTED REGION ID(SKAController.isCapabilityAchievable) ENABLED START #
        """
        Check if provided capabilities can be achieved by the resource(s).

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: An array consisting pair of

            * [nrInstances]: DevLong. Number of instances of the capability.
            * [Capability types]: DevString. Type of capability.

        :type argin: :py:class:`tango.DevVarLongStringArray`.

        :return: result_code, unique_id
        :rtype: DevVarLongStringArray
        """
        handler = self.get_command_object("IsCapabilityAchievable")
        return handler(argin)
        # PROTECTED REGION END #    //  SKAController.isCapabilityAchievable


# ----------
# Run server
# ----------
def main(args=None, **kwargs):
    """Launch an SKAController Tango device."""
    # PROTECTED REGION ID(SKAController.main) ENABLED START #
    return run((SKAController,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKAController.main


if __name__ == "__main__":
    main()
