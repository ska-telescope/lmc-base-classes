# pylint: disable=invalid-name
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
SKAController.

Controller device
"""
from __future__ import annotations

import logging
from typing import Any, Generic, List, Optional, Tuple, TypeVar, cast

from ska_control_model import ResultCode
from tango import DebugIt
from tango.server import attribute, command, device_property

from .base import BaseComponentManager, SKABaseDevice
from .commands import DeviceInitCommand, FastCommand
from .utils import convert_dict_to_list, validate_capability_types, validate_input_sizes

__all__ = ["ControllerComponentManager", "SKAController", "main"]


# pylint: disable-next=abstract-method
class ControllerComponentManager(BaseComponentManager):
    """A stub for an controller component manager."""

    # TODO


ComponentManagerT = TypeVar("ComponentManagerT", bound=ControllerComponentManager)


class SKAController(SKABaseDevice, Generic[ComponentManagerT]):
    """Controller device."""

    # -----------------
    # Device Properties
    # -----------------

    # List of maximum number of instances per capability type provided by this Element;
    # CORRELATOR=512, PSS-BEAMS=4, PST-BEAMS=6, VLBI-BEAMS=4  or for DSH it can be:
    # BAND-1=1, BAND-2=1, BAND3=0, BAND-4=0, BAND-5=0 (if only bands 1&amp;2 is
    # installed).
    MaxCapabilities = device_property(
        dtype=("str",),
    )

    def init_command_objects(self: SKAController) -> None:
        """Set up the command objects."""
        super().init_command_objects()
        self.register_command_object(
            "IsCapabilityAchievable",
            self.IsCapabilityAchievableCommand(self, self.logger),
        )

    class InitCommand(DeviceInitCommand):
        # pylint: disable=protected-access  # command classes are friend classes
        """A class for the SKAController's init_device() "command"."""

        def do(
            self: SKAController.InitCommand,
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
            self._device._element_logger_address = ""
            self._device._element_alarm_address = ""
            self._device._element_tel_state_address = ""
            self._device._element_database_address = ""
            self._device._element_alarm_device = ""
            self._device._element_tel_state_device = ""
            self._device._element_database_device = ""

            self._device._max_capabilities = {}
            if self._device.MaxCapabilities:
                for max_capability in self._device.MaxCapabilities:
                    (
                        capability_type,
                        max_capability_instances,
                    ) = max_capability.split(":")
                    self._device._max_capabilities[capability_type] = int(
                        max_capability_instances
                    )

            self._device._available_capabilities = self._device._max_capabilities.copy()

            message = "SKAController Init command completed OK"
            self.logger.info(message)
            self._completed()
            return (ResultCode.OK, message)

    def create_component_manager(self: SKAController) -> ComponentManagerT:
        """
        Create and return a component manager for this device.

        :raises NotImplementedError: because it is not implemented.
        """
        raise NotImplementedError("SKAController is incomplete.")

    # ----------
    # Attributes
    # ----------

    @attribute(dtype="str", doc="FQDN of Element Logger")
    def elementLoggerAddress(self: SKAController) -> str:
        """
        Read FQDN of Element Logger device.

        :return: FQDN of Element Logger device
        """
        return self._element_logger_address

    @attribute(dtype="str", doc="FQDN of Element Alarm Handlers")
    def elementAlarmAddress(self: SKAController) -> str:
        """
        Read FQDN of Element Alarm device.

        :return: FQDN of Element Alarm device
        """
        return self._element_alarm_address

    @attribute(dtype="str", doc="FQDN of Element TelState device")
    def elementTelStateAddress(self: SKAController) -> str:
        """
        Read FQDN of Element TelState device.

        :return: FQDN of Element TelState device
        """
        return self._element_tel_state_address

    @attribute(dtype="str", doc="FQDN of Element Database device")
    def elementDatabaseAddress(self: SKAController) -> str:
        """
        Read FQDN of Element Database device.

        :return: FQDN of Element Database device
        """
        return self._element_database_address

    @attribute(
        dtype=("str",),
        max_dim_x=20,
        doc=(
            "Maximum number of instances of each capability type,"
            " e.g. 'CORRELATOR:512', 'PSS-BEAMS:4'."
        ),
    )
    def maxCapabilities(self: SKAController) -> list[str]:
        """
        Read maximum number of instances of each capability type.

        :return: list of maximum number of instances of each capability
            type
        """
        return convert_dict_to_list(self._max_capabilities)

    @attribute(
        dtype=("str",),
        max_dim_x=20,
        doc=(
            "A list of available number of instances of each capability type, "
            "e.g. 'CORRELATOR:512', 'PSS-BEAMS:4'."
        ),
    )
    def availableCapabilities(self: SKAController) -> list[str]:
        """
        Read list of available number of instances of each capability type.

        :return: list of available number of instances of each
            capability type
        """
        return convert_dict_to_list(self._available_capabilities)

    # --------
    # Commands
    # --------

    class IsCapabilityAchievableCommand(FastCommand):
        # pylint: disable=protected-access  # command classes are friend classes
        """A class for the SKAController's IsCapabilityAchievable() command."""

        def __init__(
            self: SKAController.IsCapabilityAchievableCommand,
            device: SKAController,
            logger: Optional[logging.Logger] = None,
        ):
            """
            Initialise a new instance.

            :param device: the device that this command acts upon.
            :param logger: a logger for this command to log with.
            """
            self._device = device
            super().__init__(logger=logger)

        def do(
            self: SKAController.IsCapabilityAchievableCommand,
            *args: Any,
            **kwargs: Any,
        ) -> bool:
            """
            Stateless hook for device IsCapabilityAchievable() command.

            :param args: positional arguments to the command. There is a single
                positional argument: an array consisting of pairs of
                * [nrInstances]: DevLong. Number of instances of the capability.
                * [Capability types]: DevString. Type of capability.
            :param kwargs: keyword arguments to the command. This command does
                not take any, so this should be empty.

            :return: Whether the capability is achievable
            """
            argin = cast(Tuple[List[int], List[str]], args[0])
            command_name = "IsCapabilityAchievable"
            capabilities_instances, capability_types = argin
            validate_input_sizes(command_name, argin)
            validate_capability_types(
                command_name,
                capability_types,
                list(self._device._max_capabilities.keys()),
            )

            for capability_type, capability_instances in zip(
                capability_types, capabilities_instances
            ):
                if (
                    not self._device._available_capabilities[capability_type]
                    >= capability_instances
                ):
                    return False
            return True

    @command(
        dtype_in="DevVarLongStringArray",
        doc_in="[nrInstances][Capability types]",
        dtype_out=bool,
        doc_out="(ResultCode, 'Command unique ID')",
    )
    @DebugIt()
    def IsCapabilityAchievable(
        self: SKAController, argin: tuple[list[int], list[str]]
    ) -> bool:
        """
        Check if provided capabilities can be achieved by the resource(s).

        To modify behaviour for this command, modify the do() method of
        the command class.

        :param argin: An array consisting pair of

            * [nrInstances]: DevLong. Number of instances of the capability.
            * [Capability types]: DevString. Type of capability.

        :return: True or False
        """
        handler = self.get_command_object("IsCapabilityAchievable")
        return handler(argin)


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
    return SKAController.run_server(args=args or None, **kwargs)


if __name__ == "__main__":
    main()
