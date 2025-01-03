# pylint: disable=invalid-name
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKAObsDevice."""
from __future__ import annotations

import re
from typing import Any

import pytest
import tango
from ska_control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    ObsMode,
    ObsState,
    SimulationMode,
    TestMode,
)
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup
from tango import DevState
from tango.test_context import MultiDeviceTestContext

from ska_tango_base import SKABaseDevice, SKAObsDevice
from ska_tango_base.obs import ObsDeviceComponentManager
from ska_tango_base.testing.reference import ReferenceBaseComponentManager


# pylint: disable=abstract-method
class SimpleComponentManager(ObsDeviceComponentManager):
    """Simple Component Manager for test purposes.

    We need this so that the component manager exposes the
    Long Running Command properties from the base class.
    """


class SimpleSKAObsDevice(SKAObsDevice[ObsDeviceComponentManager]):
    """Simple concrete class for test purposes."""

    def create_component_manager(
        self: SKAObsDevice[ObsDeviceComponentManager],
    ) -> ObsDeviceComponentManager:
        """Create and return the component manager for this device.

        :returns: a reference component manager.
        """
        return SimpleComponentManager(
            self.logger,
            self._communication_state_changed,
            self._component_state_changed,
        )


class SimpleSKABaseDevice(SKABaseDevice[SimpleComponentManager]):
    """Simple concrete class for test purposes."""

    def create_component_manager(
        self: SKABaseDevice[SimpleComponentManager],
    ) -> SimpleComponentManager:
        """Create and return the component manager for this device.

        :returns: a reference component manager.
        """
        return SimpleComponentManager(
            self.logger,
            self._communication_state_changed,
            self._component_state_changed,
        )


class TestSKAObsDevice:
    """Test class for tests of the SKAObsDevice device class."""

    @pytest.fixture(scope="class")
    def device_test_config(
        self: TestSKAObsDevice, device_properties: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Specify device configuration, including properties and memorized attributes.

        This implementation provides a concrete subclass of the device
        class under test, some properties, and a memorized value for
        adminMode.

        :param device_properties: fixture that returns device properties
            of the device under test

        :return: specification of how the device under test should be
            configured
        """
        return {
            "device": SKAObsDevice,
            "component_manager_patch": lambda self: ReferenceBaseComponentManager(
                self.logger,
                self._communication_state_changed,
                self._component_state_changed,
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip("Not implemented")
    def test_properties(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test device properties.

        :param device_under_test: a proxy to the device under test
        """

    def test_State(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.state() == DevState.OFF

    def test_Status(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.Status() == "The device is in OFF state."

    def test_GetVersionInfo(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for GetVersionInfo.

        :param device_under_test: a proxy to the device under test
        """
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+(rc[0-9]+)?, A set of generic base devices for SKA "
            "Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])

    def test_obsState(
        self: TestSKAObsDevice,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for obsState.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        assert device_under_test.obsState == ObsState.EMPTY

        # Check that events are working by subscribing and checking for that
        # initial event
        device_under_test.subscribe_event(
            "obsState",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["obsState"],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.EMPTY)

    def test_commandedObsState(
        self: TestSKAObsDevice,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for commandedObsState.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        assert device_under_test.commandedObsState == ObsState.EMPTY

        # Check that events are working by subscribing and checking for that
        device_under_test.subscribe_event(
            "commandedObsState",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["commandedObsState"],
        )
        change_event_callbacks.assert_change_event("commandedObsState", ObsState.EMPTY)

    def test_obsMode(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for obsMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.obsMode == ObsMode.IDLE

    def test_configurationProgress(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for configurationProgress.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.configurationProgress == 0

    def test_configurationDelayExpected(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for configurationDelayExpected.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.configurationDelayExpected == 0

    def test_buildState(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for buildState.

        :param device_under_test: a proxy to the device under test
        """
        build_pattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+(rc[0-9]+)?, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(build_pattern, device_under_test.buildState)) is not None

    def test_versionId(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        version_id_pattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+(rc[0-9]+)?")
        assert (re.match(version_id_pattern, device_under_test.versionId)) is not None

    def test_healthState(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.healthState == HealthState.UNKNOWN

    def test_adminMode(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for adminMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.adminMode == AdminMode.ONLINE

    def test_controlMode(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.controlMode == ControlMode.REMOTE

    def test_simulationMode(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.simulationMode == SimulationMode.FALSE

    def test_testMode(
        self: TestSKAObsDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.testMode == TestMode.NONE


@pytest.mark.forked
def test_multiple_devices_in_same_process() -> None:
    """Test that we can run this device with other devices in a single process."""
    # The order here is important - base class last, so that we can
    # test that the subclass isn't breaking anything.
    devices_info = (
        {"class": SimpleSKAObsDevice, "devices": [{"name": "test/obs/1"}]},
        {"class": SimpleSKABaseDevice, "devices": [{"name": "test/base/1"}]},
    )

    with MultiDeviceTestContext(devices_info, process=False) as context:
        proxy1 = context.get_device("test/obs/1")
        proxy2 = context.get_device("test/base/1")
        assert proxy1.state() == tango.DevState.DISABLE
        assert proxy2.state() == tango.DevState.DISABLE
