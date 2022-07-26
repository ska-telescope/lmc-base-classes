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

from ska_tango_base import SKABaseDevice

__all__ = ["SKATelState", "main"]


class SKATelState(SKABaseDevice):
    """A generic base device for Telescope State for SKA."""

    # -----------------
    # Device Properties
    # -----------------

    TelStateConfigFile = device_property(
        dtype="str",
    )

    # ---------------
    # General methods
    # ---------------
    def always_executed_hook(self: SKATelState) -> None:
        """
        Perform actions that are executed before every device command.

        This is a Tango hook.
        """
        pass

    def delete_device(self: SKATelState) -> None:
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
