# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
SKATelState.

A generic base device for Telescope State for SKA.
"""
from __future__ import annotations

from tango.server import device_property

from .base import SKABaseDevice

__all__ = ["SKATelState", "main"]


# TODO: This rather pointless class has no commands or attributes, so we
# haven't provided it with a component manager either; hence its
# `create_component_manager` is still the abstract one inherited from the base
# device.
# pylint: disable-next=abstract-method
class SKATelState(SKABaseDevice):
    """A generic base device for Telescope State for SKA."""

    # -----------------
    # Device Properties
    # -----------------

    TelStateConfigFile = device_property(
        dtype="str",
    )

    # ----------
    # Attributes
    # ----------

    # --------
    # Commands
    # --------


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
    return SKATelState.run_server(args=args or None, **kwargs)


if __name__ == "__main__":
    main()
