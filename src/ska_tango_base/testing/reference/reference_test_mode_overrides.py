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
# pylint: disable=invalid-name
from __future__ import annotations

from src.ska_tango_base.testing.reference import ReferenceSkaBaseDevice
from ...base import TestModeOverrideMixin


__all__ = ["SKABaseDevice", "main"]


class ReferenceTestModeOverrides(ReferenceSkaBaseDevice, TestModeOverrideMixin):
    """Implements a reference SKA base device with Test Mode Overrides."""

    # TODO


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
