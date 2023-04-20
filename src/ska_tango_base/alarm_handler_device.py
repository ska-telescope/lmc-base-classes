# pylint: disable=invalid-name
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
This module implements SKAAlarmHandler, a generic base device for Alarms for SKA.

It exposes SKA alarms and SKA alerts as Tango attributes. SKA Alarms and
SKA/Element Alerts are rules-based configurable conditions that can be
defined over multiple attribute values and quality factors, and are
separate from the "built-in" Tango attribute alarms.
"""
from __future__ import annotations

from typing import Any, Callable, TypeVar, cast

from tango import DebugIt
from tango.server import attribute, command, device_property

from .base import BaseComponentManager, SKABaseDevice
from .commands import FastCommand

__all__ = ["AlarmHandlerComponentManager", "SKAAlarmHandler", "main"]


# pylint: disable-next=abstract-method
class AlarmHandlerComponentManager(BaseComponentManager):
    """A stub for an alarm handler component manager."""

    # TODO


ComponentManagerT = TypeVar("ComponentManagerT", bound=AlarmHandlerComponentManager)


class SKAAlarmHandler(SKABaseDevice[ComponentManagerT]):
    """A generic base device for Alarms for SKA."""

    # -----------------
    # Device Properties
    # -----------------

    SubAlarmHandlers = device_property(
        dtype=("str",),
    )

    AlarmConfigFile = device_property(
        dtype="str",
    )

    # ---------------
    # General methods
    # ---------------

    def init_command_objects(self: SKAAlarmHandler[ComponentManagerT]) -> None:
        """Set up the command objects."""
        super().init_command_objects()
        self.register_command_object(
            "GetAlarmRule",
            self.GetAlarmRuleCommand(self.logger),
        )
        self.register_command_object(
            "GetAlarmData",
            self.GetAlarmDataCommand(self.logger),
        )
        self.register_command_object(
            "GetAlarmAdditionalInfo",
            self.GetAlarmAdditionalInfoCommand(self.logger),
        )
        self.register_command_object(
            "GetAlarmStats",
            self.GetAlarmStatsCommand(self.logger),
        )
        self.register_command_object(
            "GetAlertStats",
            self.GetAlertStatsCommand(self.logger),
        )

    def create_component_manager(
        self: SKAAlarmHandler[ComponentManagerT],
    ) -> ComponentManagerT:
        """
        Create and return a component manager for this device.

        :raises NotImplementedError: because it is not implemented.
        """
        raise NotImplementedError("SKAAlarmHandler is incomplete.")

    # ----------
    # Attributes
    # ----------

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype="int", doc="Number of active Alerts"
    )
    def statsNrAlerts(self: SKAAlarmHandler[ComponentManagerT]) -> int:
        """
        Read number of active alerts.

        :return: Number of active alerts
        """
        return 0

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype="int", doc="Number of active Alarms"
    )
    def statsNrAlarms(self: SKAAlarmHandler[ComponentManagerT]) -> int:
        """
        Read number of active alarms.

        :return: Number of active alarms
        """
        return 0

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype="int", doc="Number of New active alarms"
    )
    def statsNrNewAlarms(self: SKAAlarmHandler[ComponentManagerT]) -> int:
        """
        Read number of new active alarms.

        :return: Number of new active alarms
        """
        return 0

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype="double", doc="Number of unacknowledged alarms"
    )
    def statsNrUnackAlarms(self: SKAAlarmHandler[ComponentManagerT]) -> float:
        """
        Read number of unacknowledged alarms.

        :return: Number of unacknowledged alarms.
        """
        return 0.0

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype="double", doc="Number of returned alarms"
    )
    def statsNrRtnAlarms(self: SKAAlarmHandler[ComponentManagerT]) -> float:
        """
        Read number of returned alarms.

        :return: Number of returned alarms
        """
        return 0.0

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=("str",), max_dim_x=10000, doc="List of active alerts"
    )
    def activeAlerts(self: SKAAlarmHandler[ComponentManagerT]) -> list[str]:
        """
        Read list of active alerts.

        :return: List of active alerts
        """
        return [""]

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=("str",), max_dim_x=10000, doc="List of active alarms"
    )
    def activeAlarms(self: SKAAlarmHandler[ComponentManagerT]) -> list[str]:
        """
        Read list of active alarms.

        :return: List of active alarms
        """
        return [""]

    # --------
    # Commands
    # --------
    class GetAlarmRuleCommand(FastCommand[str]):
        """A class for the SKAAlarmHandler's GetAlarmRule() command."""

        def do(
            self: SKAAlarmHandler.GetAlarmRuleCommand,
            *args: Any,
            **kwargs: Any,
        ) -> str:
            """
            Stateless hook for SKAAlarmHandler GetAlarmRule() command.

            :param args: positional arguments to the command. This
                command takes a single positional argument, which is the
                name of the alarm.
            :param kwargs: keyword arguments to the command. This command does
                not take any, so this should be empty.

            :return: JSON string containing alarm configuration info:
                rule, actions, etc.
            """
            return ""

    class GetAlarmDataCommand(FastCommand[str]):
        """A class for the SKAAlarmHandler's GetAlarmData() command."""

        def do(
            self: SKAAlarmHandler.GetAlarmDataCommand,
            *args: Any,
            **kwargs: Any,
        ) -> str:
            """
            Stateless hook for SKAAlarmHandler GetAlarmData() command.

            :param args: positional arguments to the command. This
                command takes a single positional argument, which is the
                name of the alarm.
            :param kwargs: keyword arguments to the command. This command does
                not take any, so this should be empty.

            :return: JSON string specifying alarm data
            """
            return ""

    class GetAlarmAdditionalInfoCommand(FastCommand[str]):
        """A class for the SKAAlarmHandler's GetAlarmAdditionalInfo() command."""

        def do(
            self: SKAAlarmHandler.GetAlarmAdditionalInfoCommand,
            *args: Any,
            **kwargs: Any,
        ) -> str:
            """
            Stateless hook for SKAAlarmHandler GetAlarmAdditionalInfo() command.

            :param args: positional arguments to the command. This
                command takes a single positional argument, which is the
                name of the alarm.
            :param kwargs: keyword arguments to the command. This command does
                not take any, so this should be empty.

            :return: JSON string specifying alarm additional info
            """
            return ""

    class GetAlarmStatsCommand(FastCommand[str]):
        """A class for the SKAAlarmHandler's GetAlarmStats() command."""

        def do(
            self: SKAAlarmHandler.GetAlarmStatsCommand,
            *args: Any,
            **kwargs: Any,
        ) -> str:
            """
            Stateless hook for SKAAlarmHandler GetAlarmStats() command.

            :param args: positional arguments to the command. This command does
                not take any, so this should be empty.
            :param kwargs: keyword arguments to the command. This command does
                not take any, so this should be empty.

            :return: JSON string specifying alarm stats
            """
            return ""

    class GetAlertStatsCommand(FastCommand[str]):
        """A class for the SKAAlarmHandler's GetAlertStats() command."""

        def do(
            self: SKAAlarmHandler.GetAlertStatsCommand,
            *args: Any,
            **kwargs: Any,
        ) -> str:
            """
            Stateless hook for SKAAlarmHandler GetAlertStats() command.

            :param args: positional arguments to the command. This command does
                not take any, so this should be empty.
            :param kwargs: keyword arguments to the command. This command does
                not take any, so this should be empty.

            :return: JSON string specifying alert stats
            """
            return ""

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in="str",
        doc_in="Alarm name",
        dtype_out="str",
        doc_out="JSON string",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def GetAlarmRule(self: SKAAlarmHandler[ComponentManagerT], argin: str) -> str:
        """
        Get all configuration info of the alarm, e.g. rule, defined action, etc.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: Name of the alarm

        :return: JSON string containing configuration information of the alarm
        """
        handler = cast(Callable[[str], str], self.get_command_object("GetAlarmRule"))
        return handler(argin)

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in="str",
        doc_in="Alarm name",
        dtype_out="str",
        doc_out="JSON string",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def GetAlarmData(self: SKAAlarmHandler[ComponentManagerT], argin: str) -> str:
        """
        Get data on all attributes participating in the alarm rule.

        The data includes current value, quality factor and status.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: Name of the alarm

        :return: JSON string containing alarm data
        """
        handler = cast(Callable[[str], str], self.get_command_object("GetAlarmData"))
        return handler(argin)

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in="str",
        doc_in="Alarm name",
        dtype_out="str",
        doc_out="JSON string",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def GetAlarmAdditionalInfo(
        self: SKAAlarmHandler[ComponentManagerT], argin: str
    ) -> str:
        """
        Get additional alarm information.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: Name of the alarm

        :return: JSON string containing additional alarm information
        """
        handler = cast(
            Callable[[str], str], self.get_command_object("GetAlarmAdditionalInfo")
        )
        return handler(argin)

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="str",
        doc_out="JSON string",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def GetAlarmStats(self: SKAAlarmHandler[ComponentManagerT]) -> str:
        """
        Get current alarm stats.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: JSON string containing alarm statistics
        """
        handler = cast(Callable[[], str], self.get_command_object("GetAlarmStats"))
        return handler()

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="str",
        doc_out="JSON string",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def GetAlertStats(self: SKAAlarmHandler[ComponentManagerT]) -> str:
        """
        Get current alert stats.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: JSON string containing alert statistics
        """
        handler = cast(Callable[[], str], self.get_command_object("GetAlertStats"))
        return handler()


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
    return cast(int, SKAAlarmHandler.run_server(args=args or None, **kwargs))


if __name__ == "__main__":
    main()
