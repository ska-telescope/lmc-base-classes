# pylint: disable=invalid-name
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKALogger."""
from __future__ import annotations

import re
from typing import Any

import pytest
import tango
from ska_control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    LoggingLevel,
    SimulationMode,
    TestMode,
)
from tango import DevState
from tango.test_context import MultiDeviceTestContext

from ska_tango_base.logger_device import SKALogger
from ska_tango_base.subarray import SKASubarray
from ska_tango_base.testing.reference import ReferenceBaseComponentManager


class TestSKALogger:
    """Test class for tests of the SKALogger device class."""

    @pytest.fixture(scope="class")
    def device_test_config(
        self: TestSKALogger, device_properties: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Specification of the device under test.

        The specification includes the device's properties and memorized
        attributes.

        :param device_properties: fixture that returns device properties
            of the device under test

        :return: specification of how the device under test should be
            configured
        """
        return {
            "device": SKALogger,
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
        self: TestSKALogger, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test device properties.

        :param device_under_test: a proxy to the device under test
        """

    def test_State(self: TestSKALogger, device_under_test: tango.DeviceProxy) -> None:
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.state() == DevState.OFF

    def test_Status(self: TestSKALogger, device_under_test: tango.DeviceProxy) -> None:
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.Status() == "The device is in OFF state."

    def test_GetVersionInfo(
        self: TestSKALogger, device_under_test: tango.DeviceProxy
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

    def test_buildState(
        self: TestSKALogger, device_under_test: tango.DeviceProxy
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
        self: TestSKALogger, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        version_id_pattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(version_id_pattern, device_under_test.versionId)) is not None

    def test_loggingLevel(
        self: TestSKALogger, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for loggingLevel.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.loggingLevel == LoggingLevel.INFO

    def test_healthState(
        self: TestSKALogger, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.healthState == HealthState.UNKNOWN

    def test_adminMode(
        self: TestSKALogger, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for adminMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.adminMode == AdminMode.ONLINE

    def test_controlMode(
        self: TestSKALogger, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.controlMode == ControlMode.REMOTE

    def test_simulationMode(
        self: TestSKALogger, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.simulationMode == SimulationMode.FALSE

    def test_testMode(
        self: TestSKALogger, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.testMode == TestMode.NONE


@pytest.mark.forked
def test_SetLoggingLevel() -> None:
    """Test for SetLoggingLevel."""
    logging_level = int(tango.LogLevel.LOG_ERROR)
    logging_target = "logger/target/1"
    logger_device = "logger/device/1"
    devices_info = (
        {"class": SKALogger, "devices": [{"name": logger_device}]},
        {"class": SKASubarray, "devices": [{"name": logging_target}]},
    )

    with MultiDeviceTestContext(devices_info, process=False) as multi_context:
        dev_proxy = multi_context.get_device(logging_target)
        dev_proxy.Init()
        dev_proxy.loggingLevel = int(tango.LogLevel.LOG_FATAL)
        assert dev_proxy.loggingLevel != logging_level

        levels = []
        levels.append(logging_level)
        targets = []
        targets.append(multi_context.get_device_access(logging_target))
        device_details = []
        device_details.append(levels)
        device_details.append(targets)
        multi_context.get_device(logger_device).SetLoggingLevel(device_details)
        assert dev_proxy.loggingLevel == logging_level
