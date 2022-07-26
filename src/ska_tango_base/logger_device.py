# pylint: skip-file  # TODO: Incrementally lint this repo
# -*- coding: utf-8 -*-
#
# This file is part of the SKALogger project
#
#
#
"""
This module implements SKALogger device, a generic base device for logging for SKA.

It enables to view on-line logs through the Tango Logging Services and
to store logs using Python logging. It configures the log levels of
remote logging for selected devices.
"""
# PROTECTED REGION ID(SKALogger.additionnal_import) ENABLED START #
from typing import List, Tuple

from tango import DebugIt, DevFailed, DeviceProxy
from tango.server import command, run

from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import FastCommand, ResultCode
from ska_tango_base.control_model import LoggingLevel

# PROTECTED REGION END #    //  SKALogger.additionnal_import

__all__ = ["SKALogger", "main"]


class SKALogger(SKABaseDevice):
    """A generic base device for Logging for SKA."""

    # PROTECTED REGION ID(SKALogger.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.class_variable

    # -----------------
    # Device Properties
    # -----------------

    # ----------
    # Attributes
    # ----------

    # ---------------
    # General methods
    # ---------------
    def init_command_objects(self):
        """Set up the command objects."""
        super().init_command_objects()
        self.register_command_object(
            "SetLoggingLevel",
            self.SetLoggingLevelCommand(self.logger),
        )

    def create_component_manager(self):
        """Create and return the component manager for this device."""
        return None  # This device doesn't have a component manager yet

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKALogger.always_executed_hook) ENABLED START #
        """
        Perform actions that are executed before every device command.

        This is a Tango hook.
        """
        pass
        # PROTECTED REGION END #    //  SKALogger.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKALogger.delete_device) ENABLED START #
        """
        Clean up any resources prior to device deletion.

        This method is a Tango hook that is called by the device
        destructor and by the device Init command. It allows for any
        memory or other resources allocated in the init_device method to
        be released prior to device deletion.
        """
        pass
        # PROTECTED REGION END #    //  SKALogger.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    # --------
    # Commands
    # --------
    class SetLoggingLevelCommand(FastCommand):
        """A class for the SKALoggerDevice's SetLoggingLevel() command."""

        def do(self, argin):
            """
            Stateless hook for SetLoggingLevel() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            logging_levels = argin[0][:]
            logging_devices = argin[1][:]
            for level, device in zip(logging_levels, logging_devices):
                try:
                    new_level = LoggingLevel(level)
                    self.logger.info(
                        "Setting logging level %s for %s", new_level, device
                    )
                    dev_proxy = DeviceProxy(device)
                    dev_proxy.loggingLevel = new_level
                except DevFailed:
                    self.logger.exception(
                        "Failed to set logging level %s for %s", level, device
                    )

            message = "SetLoggingLevel command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    @command(
        dtype_in="DevVarLongStringArray",
        doc_in="Logging level for selected devices:"
        "(0=OFF, 1=FATAL, 2=ERROR, 3=WARNING, 4=INFO, 5=DEBUG)."
        "Example: [[4, 5], ['my/dev/1', 'my/dev/2']].",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def SetLoggingLevel(self, argin: Tuple[List[int], List[str]]):
        # PROTECTED REGION ID(SKALogger.SetLoggingLevel) ENABLED START #
        """
        Set the logging level of the specified devices.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: Array consisting of

            * argin[0]: list of DevLong. Desired logging level.
            * argin[1]: list of DevString. Desired tango device.

        :returns: None.
        """
        handler = self.get_command_object("SetLoggingLevel")
        (result_code, message) = handler(argin)
        return [[result_code], [message]]

        # PROTECTED REGION END #    //  SKALogger.SetLoggingLevel


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKALogger.main) ENABLED START #
    """Launch an SKALogger device."""
    return run((SKALogger,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKALogger.main


if __name__ == "__main__":
    main()
