# pylint: disable=invalid-name
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

from typing import Any, TypeVar, cast

from ska_control_model import LoggingLevel, ResultCode
from tango import DebugIt, DevFailed, DeviceProxy
from tango.server import command

from .base import BaseComponentManager, SKABaseDevice
from .commands import FastCommand

DevVarLongStringArrayType = tuple[list[ResultCode], list[str]]

__all__ = ["LoggerComponentManager", "SKALogger", "main"]


# pylint: disable-next=abstract-method
class LoggerComponentManager(BaseComponentManager):
    """A stub for an logger component manager."""

    # TODO


ComponentManagerT = TypeVar("ComponentManagerT", bound=LoggerComponentManager)


class SKALogger(SKABaseDevice[ComponentManagerT]):
    """A generic base device for Logging for SKA."""

    # -----------------
    # Device Properties
    # -----------------

    # ---------------
    # General methods
    # ---------------
    def init_command_objects(self: SKALogger[ComponentManagerT]) -> None:
        """Set up the command objects."""
        super().init_command_objects()
        self.register_command_object(
            "SetLoggingLevel",
            self.SetLoggingLevelCommand(self.logger),
        )

    def create_component_manager(
        self: SKALogger[ComponentManagerT],
    ) -> ComponentManagerT:
        """
        Create and return the component manager for this device.

        :return: None, this device doesn't have a component manager
        """
        # TODO: This should raise NotImplementedError, but that would break some tests.
        return None  # type: ignore[return-value]

    # ----------
    # Attributes
    # ----------

    # --------
    # Commands
    # --------
    class SetLoggingLevelCommand(FastCommand[tuple[ResultCode, str]]):
        """A class for the SKALoggerDevice's SetLoggingLevel() command."""

        def do(
            self: SKALogger.SetLoggingLevelCommand,
            *args: Any,
            **kwargs: Any,
        ) -> tuple[ResultCode, str]:
            """
            Stateless hook for SetLoggingLevel() command functionality.

            :param args: positional arguments to the command. This
                command takes a single positional argument, which is a
                tuple consisting of list of logging levels and list of
                tango devices.
            :param kwargs: keyword arguments to the command. This command does
                not take any, so this should be empty.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            argin = cast(tuple[list[str], list[Any]], args[0])
            logging_levels = argin[0][:]
            logging_devices = argin[1][:]
            for level, device in zip(logging_levels, logging_devices):
                try:
                    new_level = LoggingLevel(int(level))
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

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in="DevVarLongStringArray",
        doc_in="Logging level for selected devices:"
        "(0=OFF, 1=FATAL, 2=ERROR, 3=WARNING, 4=INFO, 5=DEBUG)."
        "Example: [[4, 5], ['my/dev/1', 'my/dev/2']].",
        dtype_out="DevVarLongStringArray",
        doc_out="(ResultCode, 'informational message')",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def SetLoggingLevel(
        self: SKALogger[ComponentManagerT], argin: DevVarLongStringArrayType
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
    return cast(int, SKALogger.run_server(args=args or None, **kwargs))


if __name__ == "__main__":
    main()
