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

from typing import Any

from tango import DebugIt
from tango.server import attribute, command, device_property

from ska_tango_base.base import SKABaseDevice
from ska_tango_base.commands import FastCommand

__all__ = ["SKAAlarmHandler", "main"]


# TODO: This under-developed device class does not yet have a component
# manager; hence it still inherits the abstract `create_component_manager`
# method from the base device.
class SKAAlarmHandler(SKABaseDevice):  # pylint: disable=abstract-method
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

    def init_command_objects(self: SKAAlarmHandler) -> None:
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

    # ----------
    # Attributes
    # ----------

    @attribute(dtype="int", doc="Number of active Alerts")
    def statsNrAlerts(self: SKAAlarmHandler) -> int:
        """
        Read number of active alerts.

        :return: Number of active alerts
        """
        return 0

    @attribute(dtype="int", doc="Number of active Alarms")
    def statsNrAlarms(self: SKAAlarmHandler) -> int:
        """
        Read number of active alarms.

        :return: Number of active alarms
        """
        return 0

    @attribute(dtype="int", doc="Number of New active alarms")
    def statsNrNewAlarms(self: SKAAlarmHandler) -> int:
        """
        Read number of new active alarms.

        :return: Number of new active alarms
        """
        return 0

    @attribute(dtype="double", doc="Number of unacknowledged alarms")
    def statsNrUnackAlarms(self: SKAAlarmHandler) -> float:
        """
        Read number of unacknowledged alarms.

        :return: Number of unacknowledged alarms.
        """
        return 0.0

    @attribute(dtype="double", doc="Number of returned alarms")
    def statsNrRtnAlarms(self: SKAAlarmHandler) -> float:
        """
        Read number of returned alarms.

        :return: Number of returned alarms
        """
        return 0.0

    @attribute(dtype=("str",), max_dim_x=10000, doc="List of active alerts")
    def activeAlerts(self: SKAAlarmHandler) -> list[str]:
        """
        Read list of active alerts.

        :return: List of active alerts
        """
        return [""]

    @attribute(dtype=("str",), max_dim_x=10000, doc="List of active alarms")
    def activeAlarms(self: SKAAlarmHandler) -> list[str]:
        """
        Read list of active alarms.

        :return: List of active alarms
        """
        return [""]

    # --------
    # Commands
    # --------

    # pylint: disable-next=too-few-public-methods
    class GetAlarmRuleCommand(FastCommand):
        """A class for the SKAAlarmHandler's GetAlarmRule() command."""

        def do(  # type: ignore[override]
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

    # pylint: disable-next=too-few-public-methods
    class GetAlarmDataCommand(FastCommand):
        """A class for the SKAAlarmHandler's GetAlarmData() command."""

        def do(  # type: ignore[override]
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

    # pylint: disable-next=too-few-public-methods
    class GetAlarmAdditionalInfoCommand(FastCommand):
        """A class for the SKAAlarmHandler's GetAlarmAdditionalInfo() command."""

        def do(  # type: ignore[override]
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

    # pylint: disable-next=too-few-public-methods
    class GetAlarmStatsCommand(FastCommand):
        """A class for the SKAAlarmHandler's GetAlarmStats() command."""

        def do(  # type: ignore[override]
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

    # pylint: disable-next=too-few-public-methods
    class GetAlertStatsCommand(FastCommand):
        """A class for the SKAAlarmHandler's GetAlertStats() command."""

        def do(  # type: ignore[override]
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

    @command(
        dtype_in="str",
        doc_in="Alarm name",
        dtype_out="str",
        doc_out="JSON string",
    )
    @DebugIt()
    def GetAlarmRule(self: SKAAlarmHandler, argin: str) -> str:
        """
        Get all configuration info of the alarm, e.g. rule, defined action, etc.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: Name of the alarm

        :return: JSON string containing configuration information of the alarm
        """
        handler = self.get_command_object("GetAlarmRule")
        return handler(argin)

    @command(
        dtype_in="str",
        doc_in="Alarm name",
        dtype_out="str",
        doc_out="JSON string",
    )
    @DebugIt()
    def GetAlarmData(self: SKAAlarmHandler, argin: str) -> str:
        """
        Get data on all attributes participating in the alarm rule.

        The data includes current value, quality factor and status.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: Name of the alarm

        :return: JSON string containing alarm data
        """
        handler = self.get_command_object("GetAlarmData")
        return handler(argin)

    @command(
        dtype_in="str",
        doc_in="Alarm name",
        dtype_out="str",
        doc_out="JSON string",
    )
    @DebugIt()
    def GetAlarmAdditionalInfo(self: SKAAlarmHandler, argin: str) -> str:
        """
        Get additional alarm information.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: Name of the alarm

        :return: JSON string containing additional alarm information
        """
        handler = self.get_command_object("GetAlarmAdditionalInfo")
        return handler(argin)

    @command(
        dtype_out="str",
        doc_out="JSON string",
    )
    @DebugIt()
    def GetAlarmStats(self: SKAAlarmHandler) -> str:
        """
        Get current alarm stats.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: JSON string containing alarm statistics
        """
        handler = self.get_command_object("GetAlarmStats")
        return handler()

    @command(
        dtype_out="str",
        doc_out="JSON string",
    )
    @DebugIt()
    def GetAlertStats(self: SKAAlarmHandler) -> str:
        """
        Get current alert stats.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: JSON string containing alert statistics
        """
        handler = self.get_command_object("GetAlertStats")
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
    return SKAAlarmHandler.run_server(args=args or None, **kwargs)


if __name__ == "__main__":
    main()
