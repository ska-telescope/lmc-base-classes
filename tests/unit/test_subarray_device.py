# pylint: disable=invalid-name, too-many-arguments
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
import time
from typing import Any, Callable

import pytest
import tango
from ska_control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    ObsMode,
    ObsState,
    ResultCode,
    SimulationMode,
    TestMode,
)
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup
from tango import DevState

from ska_tango_base.testing.reference import FakeSubarrayComponent, ReferenceSkaSubarray

CallableAnyNone = Callable[[Any], None]


class TestSKASubarray:  # pylint: disable=too-many-public-methods
    """Test cases for SKASubarray device."""

    @pytest.fixture(scope="class")
    def device_properties(self: TestSKASubarray) -> dict[str, Any]:
        """
        Fixture that returns properties of the device under test.

        :return: properties of the device under test
        """
        return {
            "CapabilityTypes": ["blocks", "channels"],
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
            "device": ReferenceSkaSubarray,
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.fixture()
    def turn_on_device(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        assert_lrcstatus_change_event_staging_queued_in_progress: CallableAnyNone,
    ) -> Callable[[], None]:
        """
        Turn on the device and clear the queue attributes.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks
        :param assert_lrcstatus_change_event_staging_queued_in_progress: helper function
        :return: Callable helper function
        """

        def inner_helper() -> None:
            device_under_test.SetCommandTrackerRemovalTime(0)
            assert device_under_test.state() == DevState.OFF
            for attribute in [
                "state",
                "status",
                "longRunningCommandProgress",
                "longRunningCommandStatus",
                "longRunningCommandResult",
                "obsState",
                "commandedObsState",
            ]:
                device_under_test.subscribe_event(
                    attribute,
                    tango.EventType.CHANGE_EVENT,
                    change_event_callbacks[attribute],
                )
            change_event_callbacks.assert_change_event("state", tango.DevState.OFF)
            change_event_callbacks.assert_change_event(
                "status", "The device is in OFF state."
            )
            change_event_callbacks.assert_change_event("longRunningCommandProgress", ())
            change_event_callbacks.assert_change_event("longRunningCommandStatus", ())
            change_event_callbacks.assert_change_event(
                "longRunningCommandResult", ("", "")
            )
            change_event_callbacks.assert_change_event("obsState", ObsState.EMPTY)
            change_event_callbacks.assert_change_event(
                "commandedObsState", ObsState.EMPTY
            )
            # Call command
            [[result_code], [on_command_id]] = device_under_test.On()
            assert result_code == ResultCode.QUEUED
            assert_lrcstatus_change_event_staging_queued_in_progress(on_command_id)
            for progress_point in FakeSubarrayComponent.PROGRESS_REPORTING_POINTS:
                change_event_callbacks.assert_change_event(
                    "longRunningCommandProgress", (on_command_id, progress_point)
                )
            # Command is completed
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

        return inner_helper

    @pytest.fixture()
    def assign_resources_to_empty_subarray(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        assert_lrcstatus_change_event_staging_queued_in_progress: CallableAnyNone,
    ) -> Callable[[list[str], bool], Any]:
        """
        Assign resources to the device and clear the queue attributes.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks
        :param assert_lrcstatus_change_event_staging_queued_in_progress: helper function
        :return: Callable helper function
        """

        def inner_helper(
            resources_list: list[str], return_before_completed: bool
        ) -> Any:
            """
            Assign resources to the device and clear the queue attributes.

            :param resources_list: list of resources to assign
            :param return_before_completed: return while command is in progress
            :return: the executed AssignResources() command's unique ID
            """
            # Call command
            resources_to_assign = {"resources": resources_list}
            [
                [result_code],
                [assign_command_id],
            ] = device_under_test.AssignResources(json.dumps(resources_to_assign))
            assert result_code == ResultCode.QUEUED
            change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
            assert_lrcstatus_change_event_staging_queued_in_progress(assign_command_id)
            change_event_callbacks.assert_change_event(
                "commandedObsState", ObsState.IDLE
            )
            if return_before_completed:
                return assign_command_id
            for progress_point in FakeSubarrayComponent.PROGRESS_REPORTING_POINTS:
                change_event_callbacks.assert_change_event(
                    "longRunningCommandProgress", (assign_command_id, progress_point)
                )
            # Command is completed
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
                (assign_command_id, "COMPLETED"),
            )
            change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)
            assert device_under_test.obsState == device_under_test.commandedObsState
            assert (
                list(device_under_test.assignedResources)
                == resources_to_assign["resources"]
            )
            return assign_command_id

        return inner_helper

    @pytest.fixture()
    def configure_subarray(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        assert_lrcstatus_change_event_staging_queued_in_progress: CallableAnyNone,
    ) -> Callable[[dict[str, int], bool], Any]:
        """
        Configure the device and clear the queue attributes.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks
        :param assert_lrcstatus_change_event_staging_queued_in_progress: helper function
        :return: Callable helper function
        """

        def inner_helper(
            configuration_to_apply: dict[str, int], return_before_completed: bool
        ) -> Any:
            """
            Configure the device and clear the queue attributes.

            :param configuration_to_apply: dict
            :param return_before_completed: return while command is in progress
            :return: the executed Configure() command's unique ID
            """
            assert list(device_under_test.configuredCapabilities) == [
                "blocks:0",
                "channels:0",
            ]
            # Call command
            [[result_code], [configure_command_id]] = device_under_test.Configure(
                json.dumps(configuration_to_apply)
            )
            assert result_code == ResultCode.QUEUED
            change_event_callbacks.assert_change_event("obsState", ObsState.CONFIGURING)
            assert_lrcstatus_change_event_staging_queued_in_progress(
                configure_command_id
            )
            change_event_callbacks.assert_change_event(
                "commandedObsState", ObsState.READY
            )
            if return_before_completed:
                return configure_command_id
            for progress_point in FakeSubarrayComponent.PROGRESS_REPORTING_POINTS:
                change_event_callbacks.assert_change_event(
                    "longRunningCommandProgress", (configure_command_id, progress_point)
                )
            # Command is completed
            change_event_callbacks.assert_change_event(
                "longRunningCommandResult",
                (
                    configure_command_id,
                    json.dumps([int(ResultCode.OK), "Configure completed OK"]),
                ),
            )
            change_event_callbacks.assert_change_event(
                "longRunningCommandStatus", (configure_command_id, "COMPLETED")
            )
            change_event_callbacks.assert_change_event("obsState", ObsState.READY)
            assert device_under_test.obsState == device_under_test.commandedObsState
            return configure_command_id

        return inner_helper

    @pytest.fixture()
    def reset_subarray(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        assert_lrcstatus_change_event_staging_queued_in_progress: CallableAnyNone,
    ) -> Callable[[ObsState, bool], Any]:
        """
        Reset the device and clear the queue attributes.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks
        :param assert_lrcstatus_change_event_staging_queued_in_progress: helper function
        :return: Callable helper function
        """

        def inner_helper(
            expected_obs_state: ObsState, return_before_completed: bool
        ) -> Any:
            """
            Reset the device and clear the queue attributes.

            :param expected_obs_state: the expected obsState after ObsReset completed
            :param return_before_completed: return while command is in progress
            :return: the executed ObsReset() command's unique ID
            """
            # Call command
            [[result_code], [reset_command_id]] = device_under_test.ObsReset()
            assert result_code == ResultCode.QUEUED
            change_event_callbacks.assert_change_event("obsState", ObsState.RESETTING)
            assert_lrcstatus_change_event_staging_queued_in_progress(reset_command_id)
            change_event_callbacks.assert_change_event(
                "commandedObsState", expected_obs_state
            )
            if return_before_completed:
                return reset_command_id
            for progress_point in FakeSubarrayComponent.PROGRESS_REPORTING_POINTS:
                change_event_callbacks.assert_change_event(
                    "longRunningCommandProgress", (reset_command_id, progress_point)
                )
            # Command is completed
            change_event_callbacks.assert_change_event(
                "longRunningCommandResult",
                (
                    reset_command_id,
                    json.dumps([int(ResultCode.OK), "Obs reset completed OK"]),
                ),
            )
            change_event_callbacks.assert_change_event(
                "longRunningCommandStatus", (reset_command_id, "COMPLETED")
            )
            change_event_callbacks.assert_change_event("obsState", expected_obs_state)
            assert device_under_test.obsState == device_under_test.commandedObsState
            return reset_command_id

        return inner_helper

    @pytest.fixture()
    def abort_subarray_command(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> Callable[[str], None]:
        """
        Abort the given command in progress and clear the queue attributes.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks
        :return: Callable helper function
        """

        def inner_helper(command_id: str) -> None:
            """
            Abort the given command in progress and clear the queue attributes.

            :param command_id: of command in progress to abort
            """
            delay = 0.2
            device_under_test.SetCommandTrackerRemovalTime(delay)
            event_id = device_under_test.subscribe_event(
                "longRunningCommandInProgress",
                tango.EventType.CHANGE_EVENT,
                change_event_callbacks["longRunningCommandInProgress"],
            )
            command_name = command_id.split("_", 2)[2]
            change_event_callbacks.assert_change_event(
                "longRunningCommandInProgress", (command_name,)
            )
            [[result_code], [abort_command_id]] = device_under_test.Abort()
            assert result_code == ResultCode.STARTED
            change_event_callbacks.assert_change_event("obsState", ObsState.ABORTING)
            change_event_callbacks.assert_change_event(
                "longRunningCommandStatus",
                (command_id, "IN_PROGRESS", abort_command_id, "STAGING"),
            )
            change_event_callbacks.assert_change_event(
                "longRunningCommandStatus",
                (command_id, "IN_PROGRESS", abort_command_id, "IN_PROGRESS"),
            )
            abort_name = abort_command_id.split("_", 2)[2]
            change_event_callbacks.assert_change_event(
                "longRunningCommandInProgress", (command_name, abort_name)
            )
            change_event_callbacks.assert_change_event(
                "commandedObsState", ObsState.ABORTED
            )
            change_event_callbacks.assert_change_event(
                "longRunningCommandStatus",
                (command_id, "ABORTED", abort_command_id, "IN_PROGRESS"),
            )
            change_event_callbacks.assert_change_event(
                "longRunningCommandInProgress", (abort_name,)
            )
            # Abort is completed
            change_event_callbacks.assert_change_event(
                "longRunningCommandResult",
                (
                    abort_command_id,
                    json.dumps([int(ResultCode.OK), "Abort completed OK"]),
                ),
            )
            change_event_callbacks.assert_change_event(
                "longRunningCommandStatus",
                (command_id, "ABORTED", abort_command_id, "COMPLETED"),
            )
            change_event_callbacks.assert_change_event(
                "longRunningCommandInProgress", ()
            )
            change_event_callbacks.assert_change_event("obsState", ObsState.ABORTED)
            assert device_under_test.obsState == device_under_test.commandedObsState
            change_event_callbacks.assert_not_called()
            device_under_test.unsubscribe_event(event_id)
            device_under_test.SetCommandTrackerRemovalTime(0)
            time.sleep(delay)

        return inner_helper

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

    def test_assign_and_release_resources(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        turn_on_device: Callable[[], None],
        assign_resources_to_empty_subarray: Callable[[list[str], bool], Any],
        assert_lrcstatus_change_event_staging_queued_in_progress: CallableAnyNone,
    ) -> None:
        """
        Test for AssignResources, ReleaseResources and ReleaseAllResources.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks
        :param turn_on_device: helper function
        :param assign_resources_to_empty_subarray: helper function
        :param assert_lrcstatus_change_event_staging_queued_in_progress: helper function
        """
        turn_on_device()
        assign_resources_to_empty_subarray(["BAND1", "BAND2"], False)
        # Test partial release of resources
        resources_to_release = {"resources": ["BAND1"]}
        [
            [result_code],
            [release_command_id],
        ] = device_under_test.ReleaseResources(json.dumps(resources_to_release))
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        assert_lrcstatus_change_event_staging_queued_in_progress(release_command_id)
        for progress_point in FakeSubarrayComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (release_command_id, progress_point)
            )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                release_command_id,
                json.dumps([int(ResultCode.OK), "Resource release completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (release_command_id, "COMPLETED")
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
        assert_lrcstatus_change_event_staging_queued_in_progress(releaseall_command_id)
        change_event_callbacks.assert_change_event("commandedObsState", ObsState.EMPTY)
        for progress_point in FakeSubarrayComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (releaseall_command_id, progress_point)
            )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                releaseall_command_id,
                json.dumps([int(ResultCode.OK), "Resource release completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (releaseall_command_id, "COMPLETED")
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.EMPTY)
        assert device_under_test.obsState == device_under_test.commandedObsState
        assert not device_under_test.assignedResources

    def test_configure_and_end(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        turn_on_device: Callable[[], None],
        assign_resources_to_empty_subarray: Callable[[list[str], bool], Any],
        configure_subarray: Callable[[dict[str, int], bool], Any],
        assert_lrcstatus_change_event_staging_queued_in_progress: CallableAnyNone,
    ) -> None:
        """
        Test for Configure and End.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks.
        :param turn_on_device: helper function
        :param assign_resources_to_empty_subarray: helper function
        :param configure_subarray: helper function
        :param assert_lrcstatus_change_event_staging_queued_in_progress: helper function
        """
        turn_on_device()
        assign_resources_to_empty_subarray(["BAND1"], False)
        configure_subarray({"blocks": 1, "channels": 2}, False)
        assert list(device_under_test.configuredCapabilities) == [
            "blocks:1",
            "channels:2",
        ]
        # test deconfigure
        [[result_code], [end_command_id]] = device_under_test.End()
        assert result_code == ResultCode.QUEUED
        assert_lrcstatus_change_event_staging_queued_in_progress(end_command_id)
        change_event_callbacks.assert_change_event("commandedObsState", ObsState.IDLE)

        for progress_point in FakeSubarrayComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (end_command_id, progress_point)
            )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)
        assert device_under_test.obsState == device_under_test.commandedObsState
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                end_command_id,
                json.dumps([int(ResultCode.OK), "Deconfigure completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (end_command_id, "COMPLETED")
        )
        assert list(device_under_test.configuredCapabilities) == [
            "blocks:0",
            "channels:0",
        ]

    def test_scan_and_end_scan(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        turn_on_device: Callable[[], None],
        assign_resources_to_empty_subarray: Callable[[list[str], bool], Any],
        configure_subarray: Callable[[dict[str, int], bool], Any],
        assert_lrcstatus_change_event_staging_queued_in_progress: CallableAnyNone,
    ) -> None:
        """
        Test for Scan and EndScan.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks.
        :param turn_on_device: helper function
        :param assign_resources_to_empty_subarray: helper function
        :param configure_subarray: helper function
        :param assert_lrcstatus_change_event_staging_queued_in_progress: helper function
        """
        turn_on_device()
        assign_resources_to_empty_subarray(["BAND1"], False)
        configure_subarray({"blocks": 2}, False)
        assert list(device_under_test.configuredCapabilities) == [
            "blocks:2",
            "channels:0",
        ]
        dummy_scan_arg = {"scan_id": "scan_25"}
        [[result_code], [scan_command_id]] = device_under_test.Scan(
            json.dumps(dummy_scan_arg)
        )
        assert result_code == ResultCode.QUEUED
        assert_lrcstatus_change_event_staging_queued_in_progress(scan_command_id)
        for progress_point in FakeSubarrayComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (scan_command_id, progress_point)
            )
        change_event_callbacks.assert_change_event("obsState", ObsState.SCANNING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                scan_command_id,
                json.dumps(
                    [int(ResultCode.OK), "Scan scan_25 commencement completed OK"]
                ),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (scan_command_id, "COMPLETED")
        )
        # test end scan
        [[result_code], [endscan_command_id]] = device_under_test.EndScan()
        assert result_code == ResultCode.QUEUED
        assert_lrcstatus_change_event_staging_queued_in_progress(endscan_command_id)
        for progress_point in FakeSubarrayComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (endscan_command_id, progress_point)
            )
        change_event_callbacks.assert_change_event("obsState", ObsState.READY)
        assert device_under_test.obsState == device_under_test.commandedObsState
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                endscan_command_id,
                json.dumps([int(ResultCode.OK), "End scan completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (endscan_command_id, "COMPLETED")
        )

    def test_abort_and_obsreset_from_resourcing(
        self: TestSKASubarray,
        turn_on_device: Callable[[], None],
        assign_resources_to_empty_subarray: Callable[[list[str], bool], Any],
        abort_subarray_command: Callable[[str], None],
        reset_subarray: Callable[[ObsState, bool], Any],
    ) -> None:
        """
        Test for Abort and Reset from AssignResources from EMPTY state.

        :param turn_on_device: helper function
        :param assign_resources_to_empty_subarray: helper function
        :param abort_subarray_command: helper function
        :param reset_subarray: helper function
        """
        turn_on_device()
        assign_command_id = assign_resources_to_empty_subarray(["BAND1"], True)
        # Abort assign command
        abort_subarray_command(assign_command_id)
        # Reset from aborted state to empty
        reset_subarray(ObsState.EMPTY, False)

    def test_abort_and_obsreset_from_configuring(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        turn_on_device: Callable[[], None],
        assign_resources_to_empty_subarray: Callable[[list[str], bool], Any],
        configure_subarray: Callable[[dict[str, int], bool], Any],
        abort_subarray_command: Callable[[str], None],
        reset_subarray: Callable[[ObsState, bool], Any],
    ) -> None:
        """
        Test for Abort and Reset from Configure.

        :param device_under_test: a proxy to the device under test
        :param turn_on_device: helper function
        :param assign_resources_to_empty_subarray: helper function
        :param configure_subarray: helper function
        :param abort_subarray_command: helper function
        :param reset_subarray: helper function
        """
        turn_on_device()
        assign_resources_to_empty_subarray(["BAND1"], False)
        configure_command_id = configure_subarray({"blocks": 2}, True)
        # Abort configure command
        abort_subarray_command(configure_command_id)
        # Reset from aborted state to idle
        reset_subarray(ObsState.IDLE, False)
        assert list(device_under_test.configuredCapabilities) == [
            "blocks:0",
            "channels:0",
        ]

    def test_fault_obsreset_abort_from_resourcing(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        turn_on_device: Callable[[], None],
        assign_resources_to_empty_subarray: Callable[[list[str], bool], Any],
        abort_subarray_command: Callable[[str], None],
        reset_subarray: Callable[[ObsState, bool], Any],
    ) -> None:
        """
        Test for Reset after fault of AssignResources.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks.
        :param turn_on_device: helper function
        :param assign_resources_to_empty_subarray: helper function
        :param abort_subarray_command: helper function
        :param reset_subarray: helper function
        """
        turn_on_device()
        assign_command_id = assign_resources_to_empty_subarray(["BAND1"], True)
        # Simulate observation fault
        device_under_test.SimulateObsFault()
        change_event_callbacks.assert_change_event("obsState", ObsState.FAULT)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (assign_command_id, "ABORTED")
        )
        # Reset from fault state then abort reset
        reset_command_id = reset_subarray(ObsState.EMPTY, True)
        abort_subarray_command(reset_command_id)
        # Reset again from abort to empty state
        reset_subarray(ObsState.EMPTY, False)

    def test_obsreset_from_resourcing_after_idle(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        turn_on_device: Callable[[], None],
        assign_resources_to_empty_subarray: Callable[[list[str], bool], Any],
        abort_subarray_command: Callable[[str], None],
        reset_subarray: Callable[[ObsState, bool], Any],
        assert_lrcstatus_change_event_staging_queued_in_progress: CallableAnyNone,
    ) -> None:
        """
        Test for Abort and Reset from AssignResources from IDLE state.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks.
        :param turn_on_device: helper function
        :param assign_resources_to_empty_subarray: helper function
        :param abort_subarray_command: helper function
        :param reset_subarray: helper function
        :param assert_lrcstatus_change_event_staging_queued_in_progress: helper function
        """
        turn_on_device()
        assign_resources_to_empty_subarray(["BAND1"], False)
        # Assign more resources
        [result_code], [assign_command_id] = device_under_test.AssignResources(
            json.dumps({"resources": ["BAND2"]})
        )
        assert result_code == ResultCode.QUEUED
        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        assert_lrcstatus_change_event_staging_queued_in_progress(assign_command_id)
        # Abort 2nd assign command
        abort_subarray_command(assign_command_id)
        # Reset from aborted state to idle state
        reset_subarray(ObsState.IDLE, False)

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
        :param change_event_callbacks: dictionary of mock change event callbacks
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

        device_under_test.adminMode = AdminMode.ENGINEERING
        change_event_callbacks.assert_change_event("adminMode", AdminMode.ENGINEERING)
        change_event_callbacks.assert_change_event("state", tango.DevState.UNKNOWN)
        change_event_callbacks.assert_change_event("state", tango.DevState.OFF)
        assert device_under_test.state() == tango.DevState.OFF
        assert device_under_test.adminMode == AdminMode.ENGINEERING

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

    def test_healthState(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
    ) -> None:
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

    def test_commandedObsState(
        self: TestSKASubarray, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for commandedObsState.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.commandedObsState == ObsState.EMPTY

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
