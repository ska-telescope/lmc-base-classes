# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKACapability."""
from __future__ import annotations

import re
from typing import Any

import pytest
import tango
from ska_control_model import AdminMode

from ska_tango_base import SKACapability
from ska_tango_base.testing.reference import ReferenceBaseComponentManager


class TestSKACapability:
    """Test case for packet generation."""

    @pytest.fixture(scope="class")
    def device_test_config(
        self: TestSKACapability, device_properties: dict[str, Any]
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
            "device": SKACapability,
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
        self: TestSKACapability, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test device properties.

        :param device_under_test: a proxy to the device under test
        """

    def test_ConfigureInstances(
        self: TestSKACapability, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for ConfigureInstances.

        :param device_under_test: a proxy to the device under test
        """
        device_under_test.ConfigureInstances(1)
        assert device_under_test.configuredInstances == 1

    def test_activationTime(
        self: TestSKACapability, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for activationTime.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.activationTime == 0.0

    def test_buildState(
        self: TestSKACapability, device_under_test: tango.DeviceProxy
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
        self: TestSKACapability, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        version_id_pattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(version_id_pattern, device_under_test.versionId)) is not None

    def test_configuredInstances(
        self: TestSKACapability, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for configuredInstances.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.configuredInstances == 0

    def test_usedComponents(
        self: TestSKACapability, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for usedComponents.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.usedComponents == ("",)
