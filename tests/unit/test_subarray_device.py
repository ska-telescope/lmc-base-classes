# pylint: skip-file  # TODO: Incrementally lint this repo
#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKASubarray project
#
#
#
#########################################################################################
"""Contain the tests for the SKASubarray."""

import json
import re

import pytest
import tango

# PROTECTED REGION ID(SKASubarray.test_additional_imports) ENABLED START #
from ska_tango_base import SKASubarray
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    ObsMode,
    ObsState,
    SimulationMode,
    TestMode,
)
from ska_tango_base.testing.reference import ReferenceSubarrayComponentManager

# PROTECTED REGION END #    //  SKASubarray.test_additional_imports


class TestSKASubarray:
    """Test cases for SKASubarray device."""

    @pytest.fixture(scope="class")
    def device_properties(self):
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
    def device_test_config(self, device_properties):
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
    def test_properties(self, device_under_test):
        """
        Test device properties.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKASubarray.test_properties
        """Test the Tango device properties of this subarray device."""

    # PROTECTED REGION ID(SKASubarray.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test):
        """
        Test for GetVersionInfo.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_GetVersionInfo) ENABLED START #
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])
        # PROTECTED REGION END #    //  SKASubarray.test_GetVersionInfo

    # PROTECTED REGION ID(SKASubarray.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Status_decorators
    def test_Status(self, device_under_test):
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_Status) ENABLED START #
        assert device_under_test.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKASubarray.test_Status

    # PROTECTED REGION ID(SKASubarray.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_State_decorators
    def test_State(self, device_under_test):
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_State) ENABLED START #
        assert device_under_test.state() == tango.DevState.OFF
        # PROTECTED REGION END #    //  SKASubarray.test_State

    # PROTECTED REGION ID(SKASubarray.test_AssignResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_AssignResources_decorators
    def test_assign_and_release_resources(
        self, device_under_test, change_event_callbacks
    ):
        """
        Test for AssignResources.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        # PROTECTED REGION ID(SKASubarray.test_AssignResources) ENABLED START #
        assert device_under_test.state() == tango.DevState.OFF

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
        change_event_callbacks[
            "longRunningCommandProgress"
        ].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(
            None
        )
        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            ("", "")
        )

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

        change_event_callbacks.assert_change_event(
            "obsState", ObsState.RESOURCING
        )
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
                json.dumps(
                    [int(ResultCode.OK), "Resource assignment completed OK"]
                ),
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
        ] = device_under_test.ReleaseResources(
            json.dumps(resources_to_release)
        )
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "obsState", ObsState.RESOURCING
        )
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
                json.dumps(
                    [int(ResultCode.OK), "Resource release completed OK"]
                ),
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

        change_event_callbacks.assert_change_event(
            "obsState", ObsState.RESOURCING
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
                json.dumps(
                    [int(ResultCode.OK), "Resource release completed OK"]
                ),
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
        # PROTECTED REGION END #    //  SKASubarray.test_AssignResources

    # PROTECTED REGION ID(SKASubarray.test_Configure_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Configure_decorators
    def test_configure_and_end(
        self, device_under_test, change_event_callbacks
    ):
        """
        Test for Configure.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        # PROTECTED REGION ID(SKASubarray.test_Configure) ENABLED START #
        assert device_under_test.state() == tango.DevState.OFF

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
        change_event_callbacks[
            "longRunningCommandProgress"
        ].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(
            None
        )
        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            ("", "")
        )

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

        change_event_callbacks.assert_change_event(
            "obsState", ObsState.RESOURCING
        )
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
                json.dumps(
                    [int(ResultCode.OK), "Resource assignment completed OK"]
                ),
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

        change_event_callbacks.assert_change_event(
            "obsState", ObsState.CONFIGURING
        )
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
        # PROTECTED REGION END #    //  SKASubarray.test_Configure

    # PROTECTED REGION ID(SKASubarray.test_Scan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Scan_decorators
    def test_scan_and_end_scan(
        self, device_under_test, change_event_callbacks
    ):
        """
        Test for Scan.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        # PROTECTED REGION ID(SKASubarray.test_Scan) ENABLED START #
        assert device_under_test.state() == tango.DevState.OFF

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
        change_event_callbacks[
            "longRunningCommandProgress"
        ].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(
            None
        )
        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            ("", "")
        )

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

        change_event_callbacks.assert_change_event(
            "obsState", ObsState.RESOURCING
        )
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
                json.dumps(
                    [int(ResultCode.OK), "Resource assignment completed OK"]
                ),
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

        change_event_callbacks.assert_change_event(
            "obsState", ObsState.CONFIGURING
        )
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
        change_event_callbacks.assert_change_event(
            "obsState", ObsState.SCANNING
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                scan_command_id,
                json.dumps(
                    [int(ResultCode.OK), "Scan commencement completed OK"]
                ),
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

    # PROTECTED REGION ID(SKASubarray.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Reset_decorators
    def test_abort_and_obsreset(
        self, device_under_test, change_event_callbacks
    ):
        """
        Test for Reset.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        # PROTECTED REGION ID(SKASubarray.test_Reset) ENABLED START #

        assert device_under_test.state() == tango.DevState.OFF

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
        change_event_callbacks[
            "longRunningCommandProgress"
        ].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(
            None
        )
        change_event_callbacks["longRunningCommandResult"].assert_change_event(
            ("", "")
        )

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

        change_event_callbacks.assert_change_event(
            "obsState", ObsState.RESOURCING
        )
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
                json.dumps(
                    [int(ResultCode.OK), "Resource assignment completed OK"]
                ),
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

        change_event_callbacks.assert_change_event(
            "obsState", ObsState.CONFIGURING
        )
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

        change_event_callbacks.assert_change_event(
            "obsState", ObsState.ABORTING
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
        change_event_callbacks.assert_change_event(
            "obsState", ObsState.ABORTED
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
            ),
        )

        change_event_callbacks.assert_not_called()

        # Reset from aborted state
        [[result_code], [reset_command_id]] = device_under_test.ObsReset()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "obsState", ObsState.RESETTING
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
        # PROTECTED REGION END #    //  SKASubarray.test_Reset

    # PROTECTED REGION ID(SKASubarray.test_activationTime_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_activationTime_decorators
    def test_activationTime(self, device_under_test):
        """
        Test for activationTime.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_activationTime) ENABLED START #
        assert device_under_test.activationTime == 0.0
        # PROTECTED REGION END #    //  SKASubarray.test_activationTime

    # PROTECTED REGION ID(SKASubarray.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_adminMode_decorators
    def test_adminMode(self, device_under_test, change_event_callbacks):
        """
        Test for adminMode.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        # PROTECTED REGION ID(SKASubarray.test_adminMode) ENABLED START #
        assert device_under_test.state() == tango.DevState.OFF
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
        change_event_callbacks["adminMode"].assert_change_event(
            AdminMode.ONLINE
        )
        change_event_callbacks["state"].assert_change_event(tango.DevState.OFF)

        device_under_test.adminMode = AdminMode.OFFLINE
        change_event_callbacks.assert_change_event(
            "adminMode", AdminMode.OFFLINE
        )
        change_event_callbacks.assert_change_event(
            "state", tango.DevState.DISABLE
        )
        assert device_under_test.state() == tango.DevState.DISABLE
        assert device_under_test.adminMode == AdminMode.OFFLINE

        device_under_test.adminMode = AdminMode.MAINTENANCE
        change_event_callbacks.assert_change_event(
            "adminMode", AdminMode.MAINTENANCE
        )
        change_event_callbacks.assert_change_event(
            "state", tango.DevState.UNKNOWN
        )
        change_event_callbacks.assert_change_event("state", tango.DevState.OFF)
        assert device_under_test.state() == tango.DevState.OFF
        assert device_under_test.adminMode == AdminMode.MAINTENANCE
        # PROTECTED REGION END #    //  SKASubarray.test_adminMode

    # PROTECTED REGION ID(SKASubarray.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_buildState_decorators
    def test_buildState(self, device_under_test):
        """
        Test for buildState.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (
            re.match(buildPattern, device_under_test.buildState)
        ) is not None
        # PROTECTED REGION END #    //  SKASubarray.test_buildState

    # PROTECTED REGION ID(SKASubarray.test_configurationDelayExpected_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_configurationDelayExpected_decorators
    def test_configurationDelayExpected(self, device_under_test):
        """
        Test for configurationDelayExpected.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_configurationDelayExpected) ENABLED START #
        assert device_under_test.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SKASubarray.test_configurationDelayExpected

    # PROTECTED REGION ID(SKASubarray.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_configurationProgress_decorators
    def test_configurationProgress(self, device_under_test):
        """
        Test for configurationProgress.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_configurationProgress) ENABLED START #
        assert device_under_test.configurationProgress == 0
        # PROTECTED REGION END #    //  SKASubarray.test_configurationProgress

    # PROTECTED REGION ID(SKASubarray.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_controlMode_decorators
    def test_controlMode(self, device_under_test):
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_controlMode) ENABLED START #
        assert device_under_test.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKASubarray.test_controlMode

    # PROTECTED REGION ID(SKASubarray.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_healthState_decorators
    def test_healthState(self, device_under_test):
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_healthState) ENABLED START #
        assert device_under_test.healthState == HealthState.UNKNOWN
        # PROTECTED REGION END #    //  SKASubarray.test_healthState

    # PROTECTED REGION ID(SKASubarray.test_obsMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_obsMode_decorators
    def test_obsMode(self, device_under_test):
        """
        Test for obsMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_obsMode) ENABLED START #
        assert device_under_test.obsMode == ObsMode.IDLE
        # PROTECTED REGION END #    //  SKASubarray.test_obsMode

    # PROTECTED REGION ID(SKASubarray.test_obsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_obsState_decorators
    def test_obsState(self, device_under_test):
        """
        Test for obsState.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_obsState) ENABLED START #
        assert device_under_test.obsState == ObsState.EMPTY
        # PROTECTED REGION END #    //  SKASubarray.test_obsState

    # PROTECTED REGION ID(SKASubarray.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_simulationMode_decorators
    def test_simulationMode(self, device_under_test):
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_simulationMode) ENABLED START #
        assert device_under_test.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKASubarray.test_simulationMode

    # PROTECTED REGION ID(SKASubarray.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_testMode_decorators
    def test_testMode(self, device_under_test):
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_testMode) ENABLED START #
        assert device_under_test.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKASubarray.test_testMode

    # PROTECTED REGION ID(SKASubarray.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_versionId_decorators
    def test_versionId(self, device_under_test):
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (
            re.match(versionIdPattern, device_under_test.versionId)
        ) is not None
        # PROTECTED REGION END #    //  SKASubarray.test_versionId
