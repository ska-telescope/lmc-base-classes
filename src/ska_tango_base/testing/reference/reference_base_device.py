# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
A reference implementation of an SKA base device for tests.

It inherits from SKABaseDevice.
"""
# pylint: disable=invalid-name
from __future__ import annotations

from typing import cast

from ska_control_model import ResultCode
from tango.server import command

from ...base import SKABaseDevice
from ...commands import SubmittedSlowCommand
from .reference_base_component_manager import (
    FakeBaseComponent,
    ReferenceBaseComponentManager,
)

__all__ = ["SKABaseDevice", "main"]


class ReferenceSkaBaseDevice(SKABaseDevice[ReferenceBaseComponentManager]):
    """Implements a reference SKA base device."""

    def create_component_manager(
        self: ReferenceSkaBaseDevice,
    ) -> ReferenceBaseComponentManager:
        """
        Create and return a component manager for this device.

        :returns: a reference subarray component manager.
        """
        return ReferenceBaseComponentManager(
            self.logger,
            self._communication_state_changed,
            self._component_state_changed,
            _component=FakeBaseComponent(),
        )

    def init_command_objects(self: ReferenceSkaBaseDevice) -> None:
        """Initialise the command handlers for commands supported by this device."""
        super().init_command_objects()
        for command_name, method_name in [
            ("SimulateCommandError", "simulate_command_error"),
            ("SimulateIsCmdAllowedError", "simulate_is_cmd_allowed_error"),
        ]:
            self.register_command_object(
                command_name,
                SubmittedSlowCommand(
                    command_name,
                    self._command_tracker,
                    self.component_manager,
                    method_name,
                    logger=None,
                ),
            )

    @command(dtype_out="DevVarLongStringArray")  # type: ignore[misc]
    def SimulateCommandError(
        self: ReferenceSkaBaseDevice,
    ) -> tuple[list[ResultCode], list[str]]:
        """
        Simulate a command that raises a CommandError during execution.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        """
        handler = self.get_command_object("SimulateCommandError")
        result_code, message = handler()
        return ([result_code], [message])

    @command(dtype_out="DevVarLongStringArray")  # type: ignore[misc]
    def SimulateIsCmdAllowedError(
        self: ReferenceSkaBaseDevice,
    ) -> tuple[list[ResultCode], list[str]]:
        """
        Simulate a command with a is_cmd_allowed method that raises an Exception.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        """
        handler = self.get_command_object("SimulateIsCmdAllowedError")
        result_code, message = handler()
        return ([result_code], [message])

    @command()  # type: ignore[misc]
    def SimulateFault(self: ReferenceSkaBaseDevice) -> None:
        """Simulate a fault state."""
        # pylint: disable=protected-access
        self.component_manager._component.simulate_fault(True)

    @command(dtype_in=float)  # type: ignore[misc]
    def SetCommandTrackerRemovalTime(
        self: ReferenceSkaBaseDevice, seconds: float
    ) -> None:
        """Set the CommandTracker's removal time.

        Setting the command removal time lower than the default 10s simplifies tests'
        assertions of some LRC attributes.

        :param seconds: of removal timer.
        """
        # pylint: disable=protected-access
        self._command_tracker._removal_time = seconds


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
    return cast(int, ReferenceSkaBaseDevice.run_server(args=args or None, **kwargs))


if __name__ == "__main__":
    main()
