# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
A reference implementation of an SKA subarray device.

It inherits from SKASubarray but provides schemas for some commands.
"""
# pylint: disable=invalid-name
from __future__ import annotations

import logging
from typing import Callable, Final, cast

from ska_control_model import ResultCode, TaskStatus
from tango.server import command

from ...base import CommandTracker
from ...subarray.subarray_device import SKASubarray
from .reference_subarray_component_manager import (
    FakeSubarrayComponent,
    ReferenceSubarrayComponentManager,
)

DevVarLongStringArrayType = tuple[list[ResultCode], list[str]]

__all__ = ["SKASubarray", "main"]


class ReferenceSkaSubarray(SKASubarray[ReferenceSubarrayComponentManager]):
    """Implements a reference SKA Subarray device."""

    def create_component_manager(
        self: ReferenceSkaSubarray,
    ) -> ReferenceSubarrayComponentManager:
        """
        Create and return a component manager for this device.

        :returns: a reference subarray component manager.
        """
        return ReferenceSubarrayComponentManager(
            self.CapabilityTypes,
            self.logger,
            self._communication_state_changed,
            self._component_state_changed,
            _component=FakeSubarrayComponent(self.CapabilityTypes),
        )

    class AssignResourcesCommand(SKASubarray.AssignResourcesCommand):
        """A class for SKASubarray's AssignResources() command."""

        SCHEMA: Final = {
            # pylint: disable=line-too-long
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://skao.int/ska-tango-base/ReferenceSkaSubarray_AssignResources.json",  # noqa: E501
            "title": "ska-tango-base ReferenceSkaSubarray AssignResources schema",
            "description": "Schema for ska-tango-base ReferenceSkaSubarray AssignResources command",  # noqa: E501
            "type": "object",
            "properties": {
                "resources": {
                    "description": "Resources to assign",
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["resources"],
        }

        def __init__(
            self: ReferenceSkaSubarray.AssignResourcesCommand,
            command_tracker: CommandTracker,
            component_manager: ReferenceSubarrayComponentManager,
            callback: Callable[[bool], None] | None = None,
            logger: logging.Logger | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: an optional callback to be called when this
                command starts and finishes.
            :param logger: a logger for this command to log with.
            """
            super().__init__(
                command_tracker,
                component_manager,
                callback=callback,
                logger=logger,
                schema=self.SCHEMA,
            )

    class ReleaseResourcesCommand(SKASubarray.ReleaseResourcesCommand):
        """A class for SKASubarray's ReleaseResources() command."""

        SCHEMA: Final = {
            # pylint: disable=line-too-long
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://skao.int/ska-tango-base/ReferenceSkaSubarray_ReleaseResources.json",  # noqa: E501
            "title": "ska-tango-base ReferenceSkaSubarray ReleaseResources schema",
            "description": "Schema for ska-tango-base ReferenceSkaSubarray ReleaseResources command",  # noqa: E501
            "type": "object",
            "properties": {
                "resources": {
                    "description": "Resources to release",
                    "type": "array",
                    "items": {"type": "string"},
                }
            },
            "required": ["resources"],
        }

        def __init__(
            self: ReferenceSkaSubarray.ReleaseResourcesCommand,
            command_tracker: CommandTracker,
            component_manager: ReferenceSubarrayComponentManager,
            callback: Callable[[bool], None] | None = None,
            logger: logging.Logger | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: an optional callback to be called when this
                command starts and finishes.
            :param logger: a logger for this command to log with.
            """
            super().__init__(
                command_tracker,
                component_manager,
                callback=callback,
                logger=logger,
                schema=self.SCHEMA,
            )

    class ConfigureCommand(SKASubarray.ConfigureCommand):
        """A class for SKASubarray's Configure() command."""

        SCHEMA: Final = {
            # pylint: disable=line-too-long
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://skao.int/ska-tango-base/ReferenceSkaSubarray_Configure.json",  # noqa: E501
            "title": "ska-tango-base ReferenceSkaSubarray Configure schema",
            "description": "Schema for ska-tango-base ReferenceSkaSubarray Configure command",  # noqa: E501
            "type": "object",
            "properties": {
                "blocks": {
                    "description": "Number of blocks in this scan",
                    "type": "integer",
                    "minimum": 0,
                },
                "channels": {
                    "description": "Number of channels in this scan",
                    "type": "integer",
                    "minimum": 0,
                },
            },
        }

        def __init__(
            self: ReferenceSkaSubarray.ConfigureCommand,
            command_tracker: CommandTracker,
            component_manager: ReferenceSubarrayComponentManager,
            callback: Callable[[bool], None] | None = None,
            logger: logging.Logger | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: an optional callback to be called when this
                command starts and finishes.
            :param logger: a logger for this command to log with.
            """
            super().__init__(
                command_tracker,
                component_manager,
                callback=callback,
                logger=logger,
                schema=self.SCHEMA,
            )

    class ScanCommand(SKASubarray.ScanCommand):
        """A class for SKASubarray's Scan() command."""

        SCHEMA: Final = {
            # pylint: disable=line-too-long
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://skao.int/ska-tango-base/ReferenceSkaSubarray_Scan.json",
            "title": "ska-tango-base ReferenceSkaSubarray Scan schema",
            "description": "Schema for ska-tango-base ReferenceSkaSubarray Scan command",  # noqa: E501
            "type": "object",
            "properties": {
                "scan_id": {
                    "description": "Scan ID",
                    "type": "string",
                },
            },
            "required": ["scan_id"],
        }

        def __init__(
            self: ReferenceSkaSubarray.ScanCommand,
            command_tracker: CommandTracker,
            component_manager: ReferenceSubarrayComponentManager,
            callback: Callable[[bool], None] | None = None,
            logger: logging.Logger | None = None,
        ) -> None:
            """
            Initialise a new instance.

            :param command_tracker: the device's command tracker
            :param component_manager: the device's component manager
            :param callback: an optional callback to be called when this
                command starts and finishes.
            :param logger: a logger for this command to log with.
            """
            super().__init__(
                command_tracker,
                component_manager,
                callback=callback,
                logger=logger,
                schema=self.SCHEMA,
            )

    @command()  # type: ignore[misc]
    def SimulateFault(self: ReferenceSkaSubarray) -> None:
        """Simulate a fault state."""
        # pylint: disable=protected-access
        self.component_manager._component.simulate_fault(True)

    @command()  # type: ignore[misc]
    def SimulateObsFault(self: ReferenceSkaSubarray) -> None:
        """Simulate an observation fault state."""
        # pylint: disable=protected-access
        self.component_manager._component.simulate_obsfault()
        for uid, status in self._command_tracker.command_statuses:
            if status == TaskStatus.IN_PROGRESS:
                self._command_tracker.update_command_info(uid, TaskStatus.FAILED)


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
    return cast(int, ReferenceSkaSubarray.run_server(args=args or None, **kwargs))


if __name__ == "__main__":
    main()
