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
# Tango imports
from tango import DebugIt, DeviceProxy, DevFailed
from tango.server import run, command

# SKA specific imports
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResponseCommand, ResultCode
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
            self.SetLoggingLevelCommand(self, self.op_state_model, self.logger),
        )

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
    class SetLoggingLevelCommand(ResponseCommand):
        """A class for the SKALoggerDevice's SetLoggingLevel() command."""

        def __init__(self, target, state_model, logger=None):
            """
            Initialise a new SetLoggingLevelCommand instance.

            :param target: the object that this base command acts upon. For
                example, the device's component manager.
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: SKABaseClassStateModel or a subclass of
                same
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, state_model, logger=logger)

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
    def SetLoggingLevel(self, argin):
        # PROTECTED REGION ID(SKALogger.SetLoggingLevel) ENABLED START #
        """
        Set the logging level of the specified devices.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: Array consisting of

            * argin[0]: list of DevLong. Desired logging level.
            * argin[1]: list of DevString. Desired tango device.

        :type argin: :py:class:`tango.DevVarLongStringArray`

        :returns: None.
        """
        command = self.get_command_object("SetLoggingLevel")
        (return_code, message) = command(argin)
        return [[return_code], [message]]

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
