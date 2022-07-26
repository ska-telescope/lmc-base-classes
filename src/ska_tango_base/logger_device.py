# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
This module implements SKALogger device, a generic base device for logging for SKA.

It enables to view on-line logs through the Tango Logging Services and
to store logs using Python logging. It configures the log levels of
remote logging for selected devices.
"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple, cast

from tango import DebugIt, DevFailed, DeviceProxy
from tango.server import command

from ska_tango_base import SKABaseDevice

# from ska_tango_base.base import BaseComponentManager
from ska_tango_base.commands import FastCommand, ResultCode
from ska_tango_base.control_model import LoggingLevel

DevVarLongStringArrayType = Tuple[List[ResultCode], List[Optional[str]]]

__all__ = ["SKALogger", "main"]


class SKALogger(SKABaseDevice):
    """A generic base device for Logging for SKA."""

    # -----------------
    # Device Properties
    # -----------------

    # ---------------
    # General methods
    # ---------------
    def init_command_objects(self: SKALogger) -> None:
        """Set up the command objects."""
        super().init_command_objects()
        self.register_command_object(
            "SetLoggingLevel",
            self.SetLoggingLevelCommand(self.logger),
        )

    def create_component_manager(self: SKALogger) -> None:
        """
        Create and return the component manager for this device.

        :return: None, this device doesn't have a component manager
        """
        return None  # This device doesn't have a component manager yet

    def always_executed_hook(self: SKALogger) -> None:
        """
        Perform actions that are executed before every device command.

        This is a Tango hook.
        """
        pass

    def delete_device(self: SKALogger) -> None:
        """
        Clean up any resources prior to device deletion.

        This method is a Tango hook that is called by the device
        destructor and by the device Init command. It allows for any
        memory or other resources allocated in the init_device method to
        be released prior to device deletion.
        """
        pass

    # ----------
    # Attributes
    # ----------

    # --------
    # Commands
    # --------
    class SetLoggingLevelCommand(FastCommand):
        """A class for the SKALoggerDevice's SetLoggingLevel() command."""

        def do(  # type: ignore[override]
            self: SKALogger.SetLoggingLevelCommand, argin: Tuple[List[str], List[Any]]
        ) -> tuple[ResultCode, str]:
            """
            Stateless hook for SetLoggingLevel() command functionality.

            :param argin: tuple consisting of list of logging levels
                and list of tango devices

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            logging_levels = argin[0][:]
            logging_devices = argin[1][:]
            for level, device in zip(logging_levels, logging_devices):
                try:
                    new_level = LoggingLevel(cast(int, level))
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
        doc_out="(ResultCode, 'informational message')",
    )
    @DebugIt()
    def SetLoggingLevel(
        self: SKALogger, argin: DevVarLongStringArrayType
    ) -> DevVarLongStringArrayType:
        """
        Set the logging level of the specified devices.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: Array consisting of

            * argin[0]: list of DevLong. Desired logging level.
            * argin[1]: list of DevString. Desired tango device.

        :returns: ResultCode & message.
        """
        handler = self.get_command_object("SetLoggingLevel")
        (result_code, message) = handler(argin)
        return ([result_code], [message])


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
    return SKALogger.run_server(args=args or None, **kwargs)


if __name__ == "__main__":
    main()
