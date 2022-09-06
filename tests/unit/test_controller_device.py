# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKAController."""
from __future__ import annotations

import re
from typing import Any

import pytest
import tango
from ska_control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    SimulationMode,
    TestMode,
)
from tango import DevState

from ska_tango_base import SKAController
from ska_tango_base.testing.reference import ReferenceBaseComponentManager


class TestSKAController(object):
    """Test class for tests of the SKAController device class."""

    # capabilities = ['BAND1:1', 'BAND2:1', 'BAND3:0', 'BAND4:0', 'BAND5:0']

    @pytest.fixture(scope="class")
    def device_properties(self: TestSKAController) -> dict[str, Any]:
        """
        Fixture that returns properties of the device under test.

        :return: properties of the device under test
        """
        return {
            "SkaLevel": "4",
            "LoggingTargetsDefault": "",
            "GroupDefinitions": "",
            "NrSubarrays": "16",
            "CapabilityTypes": "",
            "MaxCapabilities": ["BAND1:1", "BAND2:1"],
        }

    @pytest.fixture(scope="class")
    def device_test_config(
        self: TestSKAController, device_properties: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Specification of the device under test.

        The specification includes the device's properties and
        memorized attributes.

        This implementation provides a concrete subclass of the device
        class under test, some properties, and a memorized value for
        adminMode.

        :param device_properties: fixture that returns device properties
            of the device under test

        :return: specification of how the device under test should be
            configured
        """
        return {
            "device": SKAController,
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
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test device properties.

        :param device_under_test: a proxy to the device under test
        """
        pass

    def test_State(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.state() == DevState.OFF

    def test_Status(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.Status() == "The device is in OFF state."

    def test_GetVersionInfo(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for GetVersionInfo.

        :param device_under_test: a proxy to the device under test
        """
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])

    @pytest.mark.parametrize(
        ("capability", "success"),
        [([[2], ["BAND1"]], False), ([[1], ["BAND1"]], True)],
    )
    def test_isCapabilityAchievable(
        self,
        device_under_test: tango.DeviceProxy,
        capability: tuple[list[int], list[str]],
        success: bool,
    ) -> None:
        """
        Test for isCapabilityAchievable to test failure condition.

        :param device_under_test: a proxy to the device under test
        :param capability: the capability
        :param success: True for test success else False
        """
        assert success == device_under_test.isCapabilityAchievable(capability)

    def test_elementLoggerAddress(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for elementLoggerAddress.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.elementLoggerAddress == ""

    def test_elementAlarmAddress(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for elementAlarmAddress.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.elementAlarmAddress == ""

    def test_elementTelStateAddress(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for elementTelStateAddress.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.elementTelStateAddress == ""

    def test_elementDatabaseAddress(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for elementDatabaseAddress.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.elementDatabaseAddress == ""

    def test_buildState(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for buildState.

        :param device_under_test: a proxy to the device under test
        """
        build_pattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(build_pattern, device_under_test.buildState)) is not None

    def test_versionId(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        version_id_pattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(version_id_pattern, device_under_test.versionId)) is not None

    def test_healthState(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.healthState == HealthState.UNKNOWN

    def test_adminMode(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for adminMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.adminMode == AdminMode.ONLINE

    def test_controlMode(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.controlMode == ControlMode.REMOTE

    def test_simulationMode(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.simulationMode == SimulationMode.FALSE

    def test_testMode(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.testMode == TestMode.NONE

    def test_maxCapabilities(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for maxCapabilities.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.maxCapabilities == ("BAND1:1", "BAND2:1")

    def test_availableCapabilities(
        self: TestSKAController, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for availableCapabilities.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.availableCapabilities == (
            "BAND1:1",
            "BAND2:1",
        )
