# pylint: disable=invalid-name
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKAAlarmHandler."""
from __future__ import annotations

import re
from typing import Any

import pytest
import tango
from ska_control_model import AdminMode

from ska_tango_base import SKAAlarmHandler
from ska_tango_base.testing.reference import ReferenceBaseComponentManager


class TestSKAAlarmHandler:
    """Test class for tests of the SKAAlarmHander device class."""

    @pytest.fixture(scope="class")
    def device_test_config(
        self: TestSKAAlarmHandler, device_properties: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Fixture that specifies the device to be tested.

        The specification includes device properties and memorized
        attributes.

        :param device_properties: fixture that returns device properties
            of the device under test

        :return: specification of how the device under test should be
            configured
        """
        return {
            "device": SKAAlarmHandler,
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
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test the device properties.

        :param device_under_test: a proxy to the device under test
        """

    def test_GetAlarmRule(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for GetAlarmRule.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.GetAlarmRule("") == ""

    def test_GetAlarmData(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for GetAlarmData.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.GetAlarmData("") == ""

    def test_GetAlarmAdditionalInfo(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for GetAlarmAdditionalInfo.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.GetAlarmAdditionalInfo("") == ""

    def test_GetAlarmStats(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for GetAlarmStats.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.GetAlarmStats() == ""

    def test_GetAlertStats(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for GetAlertStats.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.GetAlertStats() == ""

    def test_GetVersionInfo(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
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

    def test_statsNrAlerts(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for statsNrAlerts.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.statsNrAlerts == 0

    def test_statsNrAlarms(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for statsNrAlarms.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.statsNrAlarms == 0

    def test_statsNrNewAlarms(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for statsNrNewAlarms.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.statsNrNewAlarms == 0

    def test_statsNrUnackAlarms(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for statsNrUnackAlarms.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.statsNrUnackAlarms == 0.0

    def test_statsNrRtnAlarms(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for statsNrRtnAlarms.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.statsNrRtnAlarms == 0.0

    def test_buildState(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
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
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        version_id_pattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+(rc[0-9]+)?")
        assert (re.match(version_id_pattern, device_under_test.versionId)) is not None

    def test_activeAlerts(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for activeAlerts.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.activeAlerts == ("",)

    def test_activeAlarms(
        self: TestSKAAlarmHandler, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for activeAlarms.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.activeAlarms == ("",)
