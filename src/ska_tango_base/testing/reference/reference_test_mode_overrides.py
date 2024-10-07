# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
A reference implementation of an SKA base device using Test Mode Overrides.

It inherits from ReferenceSkaBaseDevice so we can run the same tests, ensuring that
adding TestModeOverrideMixin doesn't break anything too badly.
"""
from __future__ import annotations

from typing import cast

from ska_control_model import HealthState
from tango.server import attribute

from ...base import TestModeOverrideMixin, overridable
from .reference_base_device import ReferenceSkaBaseDevice

__all__ = ["TestModeOverrideMixin", "main"]


class ReferenceTestModeOverrides(
    ReferenceSkaBaseDevice,
    TestModeOverrideMixin,
):
    """Implements a reference SKA base device with Test Mode Overrides."""

    @attribute(dtype=HealthState)  # type: ignore[misc]
    @overridable
    def health_hardware(self: ReferenceTestModeOverrides) -> HealthState:
        """
        Read the Health State of the device hardware.

        :return: Health State of the device hardware
        """
        return HealthState.OK


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
    return cast(int, ReferenceTestModeOverrides.run_server(args=args or None, **kwargs))


if __name__ == "__main__":
    main()
