# pylint: disable=too-many-lines  # TODO: pylint is right, this is too long
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKASubarray."""
from __future__ import annotations

import json
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

from ska_tango_base import SKASubarray
from ska_tango_base.commands import ResultCode
from ska_tango_base.testing.reference import ReferenceSubarrayComponentManager


class TestSKASubarray:  # pylint: disable=too-many-public-methods
    """Test cases for SKASubarray device."""

    @pytest.fixture(scope="class")
    def device_properties(self: TestSKASubarray) -> dict[str, Any]:
        """
        Fixture that returns properties of the device under test.

        :return: properties of the device under test
        """
        return {
            "CapabilityTypes": ["BAND1", "BAND2"],
            "LoggingTargetsDefault": "",
            "GroupDefinitions": "",
            "SkaLevel": "4",
            "SubID": "1",
        }

    @pytest.fixture(scope="class")
    def device_test_config(
        self: TestSKASubarray, device_properties: dict[str, Any]
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
            "device": SKASubarray,
            "component_manager_patch": lambda self: ReferenceSubarrayComponentManager(
                self.CapabilityTypes,
                self.logger,
                self._communication_state_changed,
                self._component_state_changed,
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip(reason="Not implemented")
    def test_properties(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test device properties.

        :param device_under_test: a proxy to the device under test
        """

    def test_GetVersionInfo(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
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

    def test_Status(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.Status() == "The device is in OFF state."

    def test_State(self: TestSKASubarray, device_under_test: tango.DeviceProxy) -> None:
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.state() == DevState.OFF

    # TODO: pylint is right that this is too long and complex
    def test_assign_and_release_resources(  # pylint: disable=too-many-statements
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for AssignResources.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "status",
            "longRunningCommandProgress",
            "longRunningCommandStatus",
            "longRunningCommandResult",
        ]:
            device_under_test.subscribe_event(
                attribute,
                tango.EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(tango.DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandProgress"].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(None)
        change_event_callbacks["longRunningCommandResult"].assert_change_event(("", ""))

        [[result_code], [on_command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "QUEUED")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "IN_PROGRESS")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "66")
        )

        change_event_callbacks.assert_change_event("state", tango.DevState.ON)
        change_event_callbacks.assert_change_event(
            "status", "The device is in ON state."
        )

        assert device_under_test.state() == tango.DevState.ON

        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                on_command_id,
                json.dumps([int(ResultCode.OK), "On command completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "COMPLETED")
        )

        # TODO: Everything above here is just to turn on the device and clear the queue
        # attributes. We need a better way to handle this.

        # Test assignment of resources
        device_under_test.subscribe_event(
            "obsState",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["obsState"],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.EMPTY)

        resources_to_assign = ["BAND1", "BAND2"]
        [
            [result_code],
            [assign_command_id],
        ] = device_under_test.AssignResources(json.dumps(resources_to_assign))
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "QUEUED"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "IN_PROGRESS"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "66")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                assign_command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "COMPLETED"),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        assert list(device_under_test.assignedResources) == resources_to_assign

        # Test partial release of resources
        resources_to_release = ["BAND1"]
        [
            [result_code],
            [release_command_id],
        ] = device_under_test.ReleaseResources(json.dumps(resources_to_release))
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                release_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                release_command_id,
                "IN_PROGRESS",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (release_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (release_command_id, "66")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                release_command_id,
                json.dumps([int(ResultCode.OK), "Resource release completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                release_command_id,
                "COMPLETED",
            ),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        assert list(device_under_test.assignedResources) == ["BAND2"]
        assert device_under_test.obsState == ObsState.IDLE

        # Test release all
        [
            [result_code],
            [releaseall_command_id],
        ] = device_under_test.ReleaseAllResources()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                release_command_id,
                "COMPLETED",
                releaseall_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                release_command_id,
                "COMPLETED",
                releaseall_command_id,
                "IN_PROGRESS",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (releaseall_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (releaseall_command_id, "66")
        )

        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                releaseall_command_id,
                json.dumps([int(ResultCode.OK), "Resource release completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                release_command_id,
                "COMPLETED",
                releaseall_command_id,
                "COMPLETED",
            ),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.EMPTY)

        assert not device_under_test.assignedResources

    # TODO: pylint is right that this is too long and complex
    def test_configure_and_end(  # pylint: disable=too-many-statements
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for Configure.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "status",
            "longRunningCommandProgress",
            "longRunningCommandStatus",
            "longRunningCommandResult",
        ]:
            device_under_test.subscribe_event(
                attribute,
                tango.EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(tango.DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandProgress"].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(None)
        change_event_callbacks["longRunningCommandResult"].assert_change_event(("", ""))

        [[result_code], [on_command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "QUEUED")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "IN_PROGRESS")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "66")
        )

        change_event_callbacks.assert_change_event("state", tango.DevState.ON)
        change_event_callbacks.assert_change_event(
            "status", "The device is in ON state."
        )

        assert device_under_test.state() == tango.DevState.ON

        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                on_command_id,
                json.dumps([int(ResultCode.OK), "On command completed OK"]),
            ),
        )

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "COMPLETED")
        )

        # assignment of resources
        device_under_test.subscribe_event(
            "obsState",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["obsState"],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.EMPTY)

        resources_to_assign = ["BAND1"]
        [
            [result_code],
            [assign_command_id],
        ] = device_under_test.AssignResources(json.dumps(resources_to_assign))
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "QUEUED"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "IN_PROGRESS"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "66")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                assign_command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "COMPLETED"),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        assert list(device_under_test.assignedResources) == resources_to_assign

        # TODO: Everything above here is just to turn on the device, assign it some
        # resources, and clear the queue attributes. We need a better way to handle
        # this.
        assert list(device_under_test.configuredCapabilities) == [
            "BAND1:0",
            "BAND2:0",
        ]

        configuration_to_apply = {"BAND1": 2}
        [[result_code], [config_command_id]] = device_under_test.Configure(
            json.dumps(configuration_to_apply)
        )
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.CONFIGURING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "IN_PROGRESS",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (config_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (config_command_id, "66")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                config_command_id,
                json.dumps([int(ResultCode.OK), "Configure completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
            ),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.READY)

        assert list(device_under_test.configuredCapabilities) == [
            "BAND1:2",
            "BAND2:0",
        ]

        # test deconfigure
        [[result_code], [end_command_id]] = device_under_test.End()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                end_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                end_command_id,
                "IN_PROGRESS",
            ),
        )

        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (end_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (end_command_id, "66")
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                end_command_id,
                json.dumps([int(ResultCode.OK), "Deconfigure completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                end_command_id,
                "COMPLETED",
            ),
        )

        assert list(device_under_test.configuredCapabilities) == [
            "BAND1:0",
            "BAND2:0",
        ]

    # TODO: pylint is right that this is too long and complex
    def test_scan_and_end_scan(  # pylint: disable=too-many-statements
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for Scan.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "status",
            "longRunningCommandProgress",
            "longRunningCommandStatus",
            "longRunningCommandResult",
        ]:
            device_under_test.subscribe_event(
                attribute,
                tango.EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(tango.DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandProgress"].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(None)
        change_event_callbacks["longRunningCommandResult"].assert_change_event(("", ""))

        [[result_code], [on_command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "QUEUED")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "IN_PROGRESS")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "66")
        )

        change_event_callbacks.assert_change_event("state", tango.DevState.ON)
        change_event_callbacks.assert_change_event(
            "status", "The device is in ON state."
        )

        assert device_under_test.state() == tango.DevState.ON

        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                on_command_id,
                json.dumps([int(ResultCode.OK), "On command completed OK"]),
            ),
        )

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "COMPLETED")
        )

        # assignment of resources
        device_under_test.subscribe_event(
            "obsState",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["obsState"],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.EMPTY)

        resources_to_assign = ["BAND1"]
        [
            [result_code],
            [assign_command_id],
        ] = device_under_test.AssignResources(json.dumps(resources_to_assign))
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "QUEUED"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "IN_PROGRESS"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "66")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                assign_command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "COMPLETED"),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        assert list(device_under_test.assignedResources) == resources_to_assign

        # configuration
        assert list(device_under_test.configuredCapabilities) == [
            "BAND1:0",
            "BAND2:0",
        ]

        configuration_to_apply = {"BAND1": 2}
        [[result_code], [config_command_id]] = device_under_test.Configure(
            json.dumps(configuration_to_apply)
        )
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.CONFIGURING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "IN_PROGRESS",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (config_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (config_command_id, "66")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                config_command_id,
                json.dumps([int(ResultCode.OK), "Configure completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
            ),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.READY)

        assert list(device_under_test.configuredCapabilities) == [
            "BAND1:2",
            "BAND2:0",
        ]

        # TODO: Everything above here is just to turn on the device, assign it some
        # resources, configure it, and clear the queue attributes. We need a better way
        # to handle this.

        dummy_scan_arg = 5
        [[result_code], [scan_command_id]] = device_under_test.Scan(
            json.dumps(dummy_scan_arg)
        )
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                scan_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                scan_command_id,
                "IN_PROGRESS",
            ),
        )

        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (scan_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (scan_command_id, "66")
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.SCANNING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                scan_command_id,
                json.dumps([int(ResultCode.OK), "Scan commencement completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                scan_command_id,
                "COMPLETED",
            ),
        )

        # test end scan
        [[result_code], [endscan_command_id]] = device_under_test.EndScan()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                scan_command_id,
                "COMPLETED",
                endscan_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                scan_command_id,
                "COMPLETED",
                endscan_command_id,
                "IN_PROGRESS",
            ),
        )

        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (endscan_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (endscan_command_id, "66")
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.READY)
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                endscan_command_id,
                json.dumps([int(ResultCode.OK), "End scan completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                scan_command_id,
                "COMPLETED",
                endscan_command_id,
                "COMPLETED",
            ),
        )

    # TODO: pylint is right that this is too long and complex
    def test_abort_and_obsreset(  # pylint: disable=too-many-statements
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for Reset.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "status",
            "longRunningCommandProgress",
            "longRunningCommandStatus",
            "longRunningCommandResult",
        ]:
            device_under_test.subscribe_event(
                attribute,
                tango.EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(tango.DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandProgress"].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(None)
        change_event_callbacks["longRunningCommandResult"].assert_change_event(("", ""))

        [[result_code], [on_command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "QUEUED")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "IN_PROGRESS")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "66")
        )

        change_event_callbacks.assert_change_event("state", tango.DevState.ON)
        change_event_callbacks.assert_change_event(
            "status", "The device is in ON state."
        )

        assert device_under_test.state() == tango.DevState.ON

        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                on_command_id,
                json.dumps([int(ResultCode.OK), "On command completed OK"]),
            ),
        )

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "COMPLETED")
        )

        # assignment of resources
        device_under_test.subscribe_event(
            "obsState",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["obsState"],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.EMPTY)

        resources_to_assign = ["BAND1"]
        [
            [result_code],
            [assign_command_id],
        ] = device_under_test.AssignResources(json.dumps(resources_to_assign))
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "QUEUED"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "IN_PROGRESS"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "66")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                assign_command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "COMPLETED"),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        assert list(device_under_test.assignedResources) == resources_to_assign

        # TODO: Everything above here is just to turn on the device, assign it some
        # resources, and clear the queue attributes. We need a better way to handle
        # this.

        # Start configuring but then abort
        assert list(device_under_test.configuredCapabilities) == [
            "BAND1:0",
            "BAND2:0",
        ]

        configuration_to_apply = {"BAND1": 2}
        [[result_code], [configure_command_id]] = device_under_test.Configure(
            json.dumps(configuration_to_apply)
        )
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.CONFIGURING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                configure_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                configure_command_id,
                "IN_PROGRESS",
            ),
        )
        [[result_code], [abort_command_id]] = device_under_test.Abort()
        assert result_code == ResultCode.STARTED

        change_event_callbacks.assert_change_event("obsState", ObsState.ABORTING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                configure_command_id,
                "IN_PROGRESS",
                abort_command_id,
                "IN_PROGRESS",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                configure_command_id,
                "IN_PROGRESS",
                abort_command_id,
                "COMPLETED",
            ),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.ABORTED)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                configure_command_id,
                "ABORTED",
                abort_command_id,
                "COMPLETED",
            ),
        )

        change_event_callbacks.assert_not_called()

        # Reset from aborted state
        [[result_code], [reset_command_id]] = device_under_test.ObsReset()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.RESETTING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                configure_command_id,
                "ABORTED",
                abort_command_id,
                "COMPLETED",
                reset_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                configure_command_id,
                "ABORTED",
                abort_command_id,
                "COMPLETED",
                reset_command_id,
                "IN_PROGRESS",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (reset_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (reset_command_id, "66")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                reset_command_id,
                json.dumps([int(ResultCode.OK), "Obs reset completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                configure_command_id,
                "ABORTED",
                abort_command_id,
                "COMPLETED",
                reset_command_id,
                "COMPLETED",
            ),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        assert list(device_under_test.configuredCapabilities) == [
            "BAND1:0",
            "BAND2:0",
        ]
        assert device_under_test.obsState == ObsState.IDLE

    def test_activationTime(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for activationTime.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.activationTime == 0.0

    def test_adminMode(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for adminMode.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        assert device_under_test.state() == DevState.OFF
        assert device_under_test.adminMode == AdminMode.ONLINE

        device_under_test.subscribe_event(
            "adminMode",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["adminMode"],
        )
        device_under_test.subscribe_event(
            "state",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["state"],
        )
        change_event_callbacks["adminMode"].assert_change_event(AdminMode.ONLINE)
        change_event_callbacks["state"].assert_change_event(tango.DevState.OFF)

        device_under_test.adminMode = AdminMode.OFFLINE
        change_event_callbacks.assert_change_event("adminMode", AdminMode.OFFLINE)
        change_event_callbacks.assert_change_event("state", tango.DevState.DISABLE)
        assert device_under_test.state() == tango.DevState.DISABLE
        assert device_under_test.adminMode == AdminMode.OFFLINE

        device_under_test.adminMode = AdminMode.MAINTENANCE
        change_event_callbacks.assert_change_event("adminMode", AdminMode.MAINTENANCE)
        change_event_callbacks.assert_change_event("state", tango.DevState.UNKNOWN)
        change_event_callbacks.assert_change_event("state", tango.DevState.OFF)
        assert device_under_test.state() == tango.DevState.OFF
        assert device_under_test.adminMode == AdminMode.MAINTENANCE

    def test_buildState(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
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

    def test_configurationDelayExpected(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for configurationDelayExpected.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.configurationDelayExpected == 0

    def test_configurationProgress(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for configurationProgress.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.configurationProgress == 0

    def test_controlMode(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.controlMode == ControlMode.REMOTE

    def test_healthState(self, device_under_test: tango.DeviceProxy) -> None:
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.healthState == HealthState.UNKNOWN

    def test_obsMode(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for obsMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.obsMode == ObsMode.IDLE

    def test_obsState(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for obsState.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.obsState == ObsState.EMPTY

    def test_simulationMode(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.simulationMode == SimulationMode.FALSE

    def test_testMode(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.testMode == TestMode.NONE

    def test_versionId(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        version_id_pattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(version_id_pattern, device_under_test.versionId)) is not None
