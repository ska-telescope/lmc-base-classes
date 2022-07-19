# pylint: skip-file  # TODO: Incrementally lint this repo
# -*- coding: utf-8 -*-
#
# This file is part of the SKACapability project
#
#
#
"""
SKACapability.

Capability handling device
"""
# PROTECTED REGION ID(SKACapability.additionnal_import) ENABLED START #
from tango import DebugIt
from tango.server import attribute, command, device_property, run

from ska_tango_base.commands import DeviceInitCommand, FastCommand, ResultCode
from ska_tango_base.obs import SKAObsDevice

# PROTECTED REGION END #    //  SKACapability.additionnal_imports

__all__ = ["SKACapability", "main"]


class SKACapability(SKAObsDevice):
    """
    A Subarray handling device.

    It exposes the instances of configured capabilities.
    """

    def init_command_objects(self):
        """Set up the command objects."""
        super().init_command_objects()
        self.register_command_object(
            "ConfigureInstances",
            self.ConfigureInstancesCommand(self, self.logger),
        )

    class InitCommand(DeviceInitCommand):
        """A class for the CapabilityDevice's init_device() "command"."""

        def do(self):
            """
            Stateless hook for device initialisation.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            self._device._activation_time = 0.0
            self._device._configured_instances = 0
            self._device._used_components = [""]

            message = "SKACapability Init command completed OK"
            self.logger.info(message)
            self._completed()
            return (ResultCode.OK, message)

    # PROTECTED REGION ID(SKACapability.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.class_variable

    # -----------------
    # Device Properties
    # -----------------

    CapType = device_property(
        dtype="str",
    )

    CapID = device_property(
        dtype="str",
    )

    subID = device_property(
        dtype="str",
    )

    # ----------
    # Attributes
    # ----------

    activationTime = attribute(
        dtype="double",
        unit="s",
        standard_unit="s",
        display_unit="s",
        doc="Time of activation in seconds since Unix epoch.",
    )
    """Device attribute."""

    configuredInstances = attribute(
        dtype="uint16",
        doc="Number of instances of this Capability Type currently in use on this subarray.",
    )
    """Device attribute."""

    usedComponents = attribute(
        dtype=("str",),
        max_dim_x=100,
        doc="A list of components with no. of instances in use on this Capability.",
    )
    """Device attribute."""

    # ---------------
    # General methods
    # ---------------

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKACapability.always_executed_hook) ENABLED START #
        """
        Perform actions that are executed before every device command.

        This is a Tango hook.
        """
        pass
        # PROTECTED REGION END #    //  SKACapability.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKACapability.delete_device) ENABLED START #
        """
        Clean up any resources prior to device deletion.

        This method is a Tango hook that is called by the device
        destructor and by the device Init command. It allows for any
        memory or other resources allocated in the init_device method to
        be released prior to device deletion.
        """
        pass
        # PROTECTED REGION END #    //  SKACapability.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activationTime(self):
        # PROTECTED REGION ID(SKACapability.activationTime_read) ENABLED START #
        """
        Read time of activation since Unix epoch.

        :return: Activation time in seconds
        """
        return self._activation_time
        # PROTECTED REGION END #    //  SKACapability.activationTime_read

    def read_configuredInstances(self):
        # PROTECTED REGION ID(SKACapability.configuredInstances_read) ENABLED START #
        """
        Read the number of instances of a capability in the subarray.

        :return: The number of configured instances of a capability in a subarray
        """
        return self._configured_instances
        # PROTECTED REGION END #    //  SKACapability.configuredInstances_read

    def read_usedComponents(self):
        # PROTECTED REGION ID(SKACapability.usedComponents_read) ENABLED START #
        """
        Read the list of components with no.

        of instances in use on this Capability
        :return: The number of components currently in use.
        """
        return self._used_components
        # PROTECTED REGION END #    //  SKACapability.usedComponents_read

    # --------
    # Commands
    # --------

    class ConfigureInstancesCommand(FastCommand):
        """A class for the SKALoggerDevice's SetLoggingLevel() command."""

        def __init__(self, device, logger=None):
            """
            Initialise a new instance.

            :param device: the device to which this command belongs.
            :param logger: a logger for the command to log with
            """
            self._device = device
            super().__init__(logger=logger)

        def do(self, argin):
            """
            Stateless hook for ConfigureInstances()) command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            self._device._configured_instances = argin

            message = "ConfigureInstances command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    @command(
        dtype_in="uint16",
        doc_in="The number of instances to configure for this Capability.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def ConfigureInstances(self, argin):
        # PROTECTED REGION ID(SKACapability.ConfigureInstances) ENABLED START #
        """
        Specify the number of instances of the current capacity to be configured.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: Number of instances to configure
        :return: None.
        """
        handler = self.get_command_object("ConfigureInstances")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]
        # PROTECTED REGION END #    //  SKACapability.ConfigureInstances


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKACapability.main) ENABLED START #
    """Launch an SKACapability device."""
    return run((SKACapability,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKACapability.main


if __name__ == "__main__":
    main()
