# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module contains the tests for the TestModeOverrideMixin class."""
from __future__ import annotations

from typing import Any

import pytest
from ska_control_model import AdminMode, HealthState, TestMode
from tango import DevFailed, DeviceProxy, DevState

from ska_tango_base.testing.reference import ReferenceBaseComponentManager
from ska_tango_base.testing.reference.reference_test_mode_overrides import (
    ReferenceTestModeOverrides,
)

# from tests.conftest import Helpers


class TestTestModeOverrides:
    """Test cases for TestModeOverrideMixin class."""

    @pytest.fixture(scope="class")
    def device_test_config(
        self: TestTestModeOverrides, device_properties: dict[str, str]
    ) -> dict[str, Any]:
        """
        Specify device configuration, including properties and memorized attributes.

        This implementation provides a concrete subclass of
        SKABaseDevice with the TestModeOverrideMixin.

        :param device_properties: fixture that returns device properties
            of the device under test
        :return: specification of how the device under test should be
            configured
        """
        return {
            "device": ReferenceTestModeOverrides,
            "component_manager_patch": lambda self: ReferenceBaseComponentManager(
                self.logger,
                self._communication_state_changed,
                self._component_state_changed,
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    def test_test_mode_overrides(
        self: TestTestModeOverrides, device_under_test: DeviceProxy
    ) -> None:
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.state() == DevState.OFF
        assert device_under_test.testMode == TestMode.NONE
        assert device_under_test.health_hardware == HealthState.OK
        with pytest.raises(
            DevFailed,
            match="It is currently not allowed to write attribute test_mode_overrides",
        ):
            device_under_test.test_mode_overrides = '{"health_hardware": 1}'
        device_under_test.testMode = TestMode.TEST
        assert device_under_test.testMode == TestMode.TEST
        assert device_under_test.health_hardware == HealthState.OK
        device_under_test.test_mode_overrides = '{"health_hardware": 1}'
        assert device_under_test.health_hardware == HealthState.DEGRADED
        device_under_test.test_mode_overrides = '{"health_hardware": 2}'
        assert device_under_test.health_hardware == HealthState.FAILED
        device_under_test.testMode = TestMode.NONE
        assert device_under_test.testMode == TestMode.NONE
        assert device_under_test.health_hardware == HealthState.OK
