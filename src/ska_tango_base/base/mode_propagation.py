# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module implements mode propagation."""

import logging
import threading
from typing import Any, Callable, Final, cast

import tango
from ska_control_model import AdminMode, ControlMode, SimulationMode, TestMode


class ModeReckoner:
    def __init__(
        self,
        **callbacks: Callable[[Any], None],
    ) -> None:
        self._lock = threading.Lock()

        self._propagating = False
        self._propagated: dict[str, Any] = {}
        self._values: dict[str, Any] = {}

        self._callbacks = callbacks

    @property
    def propagating(self) -> bool:
        return self._propagating

    @propagating.setter
    def propagating(self, propagating: bool) -> None:
        with self._lock:
            if self._propagating == propagating:
                return
            self._propagating = propagating
            if propagating:
                for name, value in self._propagated.items():
                    self._set(name, value)

    def propagate(self, name: str, value: Any) -> None:
        with self._lock:
            self._propagated[name] = value
            if self._propagating:
                self._set(name, value)

    def __getitem__(self, name: str) -> Any:
        return self._values.get(name)

    def __setitem__(self, name: str, value: Any) -> None:
        with self._lock:
            self._propagating = False
            self._set(name, value)

    def _set(self, name: str, value: Any) -> None:
        if self._values.get(name) != value:
            self._values[name] = value
            self._callbacks[name](value)


class ModePropagator:
    INITIAL_VALUE_TIMEOUT: Final = 5.0

    def __init__(
        self,
        parent_trl: str | None,
        logger: logging.Logger,
        admin_mode_callback: Callable[[AdminMode], None],
        control_mode_callback: Callable[[ControlMode], None],
        simulation_mode_callback: Callable[[SimulationMode], None],
        test_mode_callback: Callable[[TestMode], None],
    ) -> None:
        self._logger = logger
        self._initial_value_event = threading.Event()

        self._reckoner = ModeReckoner(
            admin_mode=admin_mode_callback,
            control_mode=control_mode_callback,
            simulation_mode=simulation_mode_callback,
            test_mode=test_mode_callback,
        )

        self._parent: tango.DeviceProxy | None = None
        self._subscription_ids: list[str] = []
        if parent_trl:
            self._parent = tango.DeviceProxy(parent_trl)
            for mode in ["admin_mode", "control_mode", "simulation_mode", "test_mode"]:
                subscription_id = self._parent.subscribe_event(
                    mode,
                    tango.EventType.CHANGE_EVENT,
                    self.parent_mode_changed,
                )
                self._subscription_ids.append(subscription_id)

        def _set_initial_propagation(timeout: float) -> None:
            self._initial_value_event.wait(timeout)
            if not self._initial_value_event.is_set():
                self._reckoner.propagating = True

        threading.Thread(
            target=_set_initial_propagation, args=[self.INITIAL_VALUE_TIMEOUT]
        ).start()

    def __del__(self) -> None:
        if self._parent is not None:
            for subscription_ids in self._subscription_ids:
                self._parent.unsubscribe_event(subscription_ids)

    @property
    def propagating(self) -> bool:
        return self._reckoner.propagating

    @propagating.setter
    def propagating(self, propagating: bool) -> None:
        self._reckoner.propagating = propagating
        self._initial_value_event.set()

    @property
    def admin_mode(self) -> AdminMode:
        return cast(AdminMode, self._reckoner["admin_mode"])

    @admin_mode.setter
    def admin_mode(self, admin_mode: AdminMode) -> None:
        self._reckoner["admin_mode"] = admin_mode

    @property
    def control_mode(self) -> ControlMode:
        return cast(ControlMode, self._reckoner["control_mode"])

    @control_mode.setter
    def control_mode(self, control_mode: ControlMode) -> None:
        self._reckoner["control_mode"] = control_mode

    @property
    def simulation_mode(self) -> SimulationMode:
        return cast(SimulationMode, self._reckoner["simulation_mode"])

    @simulation_mode.setter
    def simulation_mode(self, simulation_mode: SimulationMode) -> None:
        self._reckoner["simulation_mode"] = simulation_mode

    @property
    def test_mode(self) -> TestMode:
        return cast(TestMode, self._reckoner["test_mode"])

    @test_mode.setter
    def test_mode(self, test_mode: TestMode) -> None:
        self._reckoner["test_mode"] = test_mode

    def parent_mode_changed(self, event: tango.EventData) -> None:
        if event.err:
            self._logger.info(
                f"Received error change event: error stack is {event.errors}."
            )
            return

        attribute_data = event.attr_value
        self._reckoner.propagate(attribute_data.name, attribute_data.value)
