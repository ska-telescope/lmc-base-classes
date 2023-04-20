# pylint: disable=invalid-name
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
from typing import Any, TypeVar, cast

from ska_control_model import ResultCode
from tango import DebugIt
from tango.server import attribute, command, device_property

from .commands import DeviceInitCommand, FastCommand
from .obs import ObsDeviceComponentManager, SKAObsDevice

DevVarLongStringArrayType = tuple[list[ResultCode], list[str]]

__all__ = ["CapabilityComponentManager", "SKACapability", "main"]


# pylint: disable-next=abstract-method
class CapabilityComponentManager(ObsDeviceComponentManager):
    """A stub for an SKA capability component manager."""

    # TODO


ComponentManagerT = TypeVar("ComponentManagerT", bound=CapabilityComponentManager)


class SKACapability(SKAObsDevice[ComponentManagerT]):
    """
    A Capability handling device.

    It exposes the instances of configured capabilities.
    """

    def __init__(
        self: SKACapability[ComponentManagerT],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialise a new instance.

        :param args: positional arguments.
        :param kwargs: keyword arguments.
        """
        # This __init__ method is created for type-hinting purposes only.
        # Tango devices are not supposed to have __init__ methods,
        # And they have a strange __new__ method,
        # that calls __init__ when you least expect it.
        # So don't put anything executable in here
        # (other than the super() call).

        self._used_components: list[str]
        self._activation_time: float
        self._configured_instances: int

        super().__init__(*args, **kwargs)

    def init_command_objects(self: SKACapability[ComponentManagerT]) -> None:
        """Set up the command objects."""
        super().init_command_objects()
        self.register_command_object(
            "ConfigureInstances",
            self.ConfigureInstancesCommand(self, self.logger),
        )

    class InitCommand(DeviceInitCommand):
        # pylint: disable=protected-access  # command classes are friend classes
        """A class for the CapabilityDevice's init_device() "command"."""

        def do(
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
            self._device._activation_time = 0.0

            self._device._configured_instances = 0

            self._device._used_components = [""]

            message = "SKACapability Init command completed OK"
            self.logger.info(message)
            self._completed()
            return (ResultCode.OK, message)

    def create_component_manager(
        self: SKACapability[ComponentManagerT],
    ) -> ComponentManagerT:
        """
        Create and return a component manager for this device.

        :raises NotImplementedError: because it is not implemented.
        """
        raise NotImplementedError("SKACapability is incomplete.")

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
    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype="double",
        unit="s",
        standard_unit="s",
        display_unit="s",
        doc="Time of activation in seconds since Unix epoch.",
    )
    def activationTime(self: SKACapability[ComponentManagerT]) -> float:
        """
        Read time of activation since Unix epoch.

        :return: Activation time in seconds
        """
        return self._activation_time

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype="uint16",
        doc=(
            "Number of instances of this Capability Type currently in use on this "
            "subarray."
        ),
    )
    def configuredInstances(self: SKACapability[ComponentManagerT]) -> int:
        """
        Read the number of instances of a capability in the subarray.

        :return: The number of configured instances of a capability in a subarray
        """
        return self._configured_instances

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=("str",),
        max_dim_x=100,
        doc="A list of components with no. of instances in use on this Capability.",
    )
    def usedComponents(self: SKACapability[ComponentManagerT]) -> list[str]:
        """
        Read the list of components with no.

        of instances in use on this Capability

        :return: The number of components currently in use.
        """
        return self._used_components

    # --------
    # Commands
    # --------

    class ConfigureInstancesCommand(FastCommand[tuple[ResultCode, str]]):
        # pylint: disable=protected-access  # command classes are friend classes
        """A class for the SKALoggerDevice's SetLoggingLevel() command."""

        def __init__(
            self: SKACapability.ConfigureInstancesCommand,
            device: SKACapability[ComponentManagerT],
            logger: logging.Logger | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param device: the device to which this command belongs.
            :param logger: a logger for the command to log with
            """
            self._device = device
            super().__init__(logger=logger)

        def do(
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
            self._device._configured_instances = int(args[0])

            message = "ConfigureInstances command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in="uint16",
        doc_in="The number of instances to configure for this Capability.",
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def ConfigureInstances(
        self: SKACapability[ComponentManagerT], argin: int
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
    return cast(int, SKACapability.run_server(args=args or None, **kwargs))


if __name__ == "__main__":
    main()
