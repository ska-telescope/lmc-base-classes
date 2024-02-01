# pylint: disable=invalid-name
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
SKAObsDevice.

A generic base device for Observations for SKA. It inherits
SKABaseDevice class. Any device implementing an obsMode will inherit
from SKAObsDevice instead of just SKABaseDevice.
"""
from __future__ import annotations

from typing import Any, TypeVar, cast

from ska_control_model import ObsMode, ObsState, ResultCode
from tango.server import attribute

from ..base import BaseComponentManager, SKABaseDevice
from ..commands import DeviceInitCommand

__all__ = ["ObsDeviceComponentManager", "SKAObsDevice", "main"]


# pylint: disable-next=abstract-method
class ObsDeviceComponentManager(BaseComponentManager):
    """A stub for an observing device component manager."""

    # TODO


ComponentManagerT = TypeVar("ComponentManagerT", bound=ObsDeviceComponentManager)


class SKAObsDevice(SKABaseDevice[ComponentManagerT]):
    """A generic base device for Observations for SKA."""

    def __init__(
        self: SKAObsDevice[ComponentManagerT],
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

        self._obs_state: ObsState
        self._commanded_obs_state: ObsState
        self._obs_mode: ObsMode
        self._config_progress: int
        self._config_delay_expected: int

        super().__init__(*args, **kwargs)

    class InitCommand(DeviceInitCommand):
        # pylint: disable=protected-access  # command classes are friend classes
        """A class for the SKAObsDevice's init_device() "command"."""

        def do(
            self: SKAObsDevice.InitCommand,
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
            for attribute_name in [
                "obsState",
                "commandedObsState",
                "obsMode",
                "configurationProgress",
                "configurationDelayExpected",
            ]:
                self._device.set_change_event(attribute_name, True)
                self._device.set_archive_event(attribute_name, True)

            self._device._obs_state = ObsState.EMPTY
            self._device._commanded_obs_state = ObsState.EMPTY
            self._device._obs_mode = ObsMode.IDLE
            self._device._config_progress = 0
            self._device._config_delay_expected = 0

            message = "SKAObsDevice Init command completed OK"
            self.logger.info(message)
            self._completed()
            return (ResultCode.OK, message)

    def create_component_manager(
        self: SKAObsDevice[ComponentManagerT],
    ) -> ComponentManagerT:
        """
        Create and return a component manager for this device.

        :raises NotImplementedError: because it is not implemented.
        """
        raise NotImplementedError("SKAObsDevice is abstract.")

    # -----------------
    # Device Properties
    # -----------------

    # ---------------
    # General methods
    # ---------------
    def _update_obs_state(
        self: SKAObsDevice[ComponentManagerT], obs_state: ObsState
    ) -> None:
        """
        Perform Tango operations in response to a change in obsState.

        This helper method is passed to the observation state model as a
        callback, so that the model can trigger actions in the Tango
        device.

        :param obs_state: the new obs_state value
        """
        self._obs_state = obs_state
        self.push_change_event("obsState", obs_state)
        self.push_archive_event("obsState", obs_state)

    def _update_commanded_obs_state(
        self: SKAObsDevice[ComponentManagerT], commanded_obs_state: ObsState
    ) -> None:
        self._commanded_obs_state = commanded_obs_state
        self.push_change_event("commandedObsState", commanded_obs_state)
        self.push_archive_event("commandedObsState", commanded_obs_state)

    # ----------
    # Attributes
    # ----------

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=ObsState
    )
    def obsState(self: SKAObsDevice[ComponentManagerT]) -> ObsState:
        """
        Read the Observation State of the device.

        :return: the current obs_state value
        """
        return self._obs_state

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=ObsState
    )
    def commandedObsState(self: SKAObsDevice[ComponentManagerT]) -> ObsState:
        """
        Read the last commanded Observation State of the device.

        :return: commanded Observation State string.
        """
        return self._commanded_obs_state

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype=ObsMode
    )
    def obsMode(self: SKAObsDevice[ComponentManagerT]) -> ObsMode:
        """
        Read the Observation Mode of the device.

        :return: the current obs_mode value
        """
        return self._obs_mode

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype="uint16",
        unit="%",
        max_value=100,
        min_value=0,
    )
    def configurationProgress(self: SKAObsDevice[ComponentManagerT]) -> int:
        """
        Read the percentage configuration progress of the device.

        :return: the percentage configuration progress
        """
        return self._config_progress

    @attribute(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype="uint16", unit="seconds"
    )
    def configurationDelayExpected(self: SKAObsDevice[ComponentManagerT]) -> int:
        """
        Read the expected Configuration Delay in seconds.

        :return: the expected configuration delay
        """
        return self._config_delay_expected

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
    return cast(int, SKAObsDevice.run_server(args=args or None, **kwargs))


if __name__ == "__main__":
    main()
