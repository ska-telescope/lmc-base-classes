# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
SKACapability.

Capability handling device
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional, Tuple

from tango import DebugIt
from tango.server import attribute, command, device_property

from ska_tango_base.commands import DeviceInitCommand, FastCommand, ResultCode
from ska_tango_base.obs import SKAObsDevice

DevVarLongStringArrayType = Tuple[List[ResultCode], List[Optional[str]]]

__all__ = ["SKACapability", "main"]


# TODO: This under-developed device class does not yet have a component
# manager, so its `create_component_manager` method is still the abstract
# method inherited from the base device.
class SKACapability(SKAObsDevice):  # pylint: disable=abstract-method
    """
    A Subarray handling device.

    It exposes the instances of configured capabilities.
    """

    def init_command_objects(self: SKACapability) -> None:
        """Set up the command objects."""
        super().init_command_objects()
        self.register_command_object(
            "ConfigureInstances",
            self.ConfigureInstancesCommand(self, self.logger),
        )

    # pylint: disable-next=too-few-public-methods
    class InitCommand(DeviceInitCommand):
        """A class for the CapabilityDevice's init_device() "command"."""

        def do(  # type: ignore[override]
            self: SKACapability.InitCommand,
            *args: Any,
            **kwargs: Any,
        ) -> tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.

            :param args: positional arguments to the command. This command does
                not take any, so this should be empty.
            :param kwargs: keyword arguments to the command. This command does
                not take any, so this should be empty.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            # pylint: disable-next=protected-access
            self._device._activation_time = 0.0

            # pylint: disable-next=protected-access
            self._device._configured_instances = 0

            # pylint: disable-next=protected-access
            self._device._used_components = [""]

            message = "SKACapability Init command completed OK"
            self.logger.info(message)
            self._completed()
            return (ResultCode.OK, message)

    # -----------------
    # Device Properties
    # -----------------

    CapType = device_property(
        dtype="str",
    )

    CapID = device_property(
        dtype="str",
    )

    SubID = device_property(
        dtype="str",
    )

    # ----------
    # Attributes
    # ----------
    @attribute(
        dtype="double",
        unit="s",
        standard_unit="s",
        display_unit="s",
        doc="Time of activation in seconds since Unix epoch.",
    )
    def activationTime(self: SKACapability) -> float:
        """
        Read time of activation since Unix epoch.

        :return: Activation time in seconds
        """
        return self._activation_time

    @attribute(
        dtype="uint16",
        doc=(
            "Number of instances of this Capability Type currently in use on this "
            "subarray."
        ),
    )
    def configuredInstances(self: SKACapability) -> int:
        """
        Read the number of instances of a capability in the subarray.

        :return: The number of configured instances of a capability in a subarray
        """
        return self._configured_instances

    @attribute(
        dtype=("str",),
        max_dim_x=100,
        doc="A list of components with no. of instances in use on this Capability.",
    )
    def usedComponents(self: SKACapability) -> list[str]:
        """
        Read the list of components with no.

        of instances in use on this Capability

        :return: The number of components currently in use.
        """
        return self._used_components

    # --------
    # Commands
    # --------

    # pylint: disable-next=too-few-public-methods
    class ConfigureInstancesCommand(FastCommand):
        """A class for the SKALoggerDevice's SetLoggingLevel() command."""

        def __init__(
            self: SKACapability.ConfigureInstancesCommand,
            device: SKACapability,
            logger: Optional[logging.Logger] = None,
        ) -> None:
            """
            Initialise a new instance.

            :param device: the device to which this command belongs.
            :param logger: a logger for the command to log with
            """
            self._device = device
            super().__init__(logger=logger)

        def do(  # type: ignore[override]
            self: SKACapability.ConfigureInstancesCommand,
            *args: Any,
            **kwargs: Any,
        ) -> tuple[ResultCode, str]:
            """
            Stateless hook for ConfigureInstances()) command functionality.

            :param args: positional arguments to the command. This command takes
                a single integer number of instances.
            :param kwargs: keyword arguments to the command. This command does
                not take any, so this should be empty.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            # pylint: disable-next=protected-access
            self._device._configured_instances = int(args[0])

            message = "ConfigureInstances command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    @command(
        dtype_in="uint16",
        doc_in="The number of instances to configure for this Capability.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def ConfigureInstances(
        self: SKACapability, argin: int
    ) -> DevVarLongStringArrayType:
        """
        Specify the number of instances of the current capacity to be configured.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: Number of instances to configure

        :return: ResultCode and string message
        """
        handler = self.get_command_object("ConfigureInstances")
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
    return SKACapability.run_server(args=args or None, **kwargs)


if __name__ == "__main__":
    main()
