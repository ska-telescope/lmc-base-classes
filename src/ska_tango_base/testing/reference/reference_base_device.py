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

from tango.server import command

from ...base import SKABaseDevice
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
