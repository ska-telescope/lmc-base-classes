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

from typing import TypeVar, cast

from tango.server import device_property

from .base import BaseComponentManager, SKABaseDevice

__all__ = ["TelStateComponentManager", "SKATelState", "main"]


# pylint: disable-next=abstract-method
class TelStateComponentManager(BaseComponentManager):
    """A stub for a telescope state component manager."""

    # TODO


ComponentManagerT = TypeVar("ComponentManagerT", bound=TelStateComponentManager)


class SKATelState(SKABaseDevice[ComponentManagerT]):
    """A generic base device for Telescope State for SKA."""

    def create_component_manager(
        self: SKATelState[ComponentManagerT],
    ) -> ComponentManagerT:
        """
        Create and return a component manager for this device.

        :raises NotImplementedError: because it is not implemented.
        """
        raise NotImplementedError("SKATelState is incomplete.")

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
    return cast(int, SKATelState.run_server(args=args or None, **kwargs))


if __name__ == "__main__":
    main()
