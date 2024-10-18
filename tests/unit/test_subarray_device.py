# pylint: disable=invalid-name, too-many-arguments, too-many-lines
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKASubarray."""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Callable

import pytest
import tango
from ska_control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    ObsMode,
    ObsState,
    SimulationMode,
    TaskStatus,
    TestMode,
)
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup
from tango import DevError, DevFailed, DevState

from ska_tango_base.base import JSONData
from ska_tango_base.long_running_commands_api import (
    LrcCallback,
    LrcSubscriptions,
    invoke_lrc,
)
from ska_tango_base.testing.reference import ReferenceSkaSubarray
from tests.conftest import Helpers

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
        successful_lrc_callback: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> Callable[[], None]:
        """
        Turn on the device and clear the queue attributes.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks
        :param successful_lrc_callback: callback fixture to use with invoke_lrc
        :param caplog: pytest LogCaptureFixture
        :return: Callable helper function
        """

        def _turn_on_device() -> None:
            assert device_under_test.state() == DevState.OFF
            for attribute in [
                "state",
                "status",
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
            change_event_callbacks.assert_change_event("obsState", ObsState.EMPTY)
            change_event_callbacks.assert_change_event(
                "commandedObsState", ObsState.EMPTY
            )
            # Call command
            _ = invoke_lrc(successful_lrc_callback, device_under_test, "On")
            Helpers.assert_expected_logs(
                caplog,
                [  # Log messages must be in this exact order
                    "lrc_callback(status=STAGING)",
                    "lrc_callback(status=QUEUED)",
                    "lrc_callback(status=IN_PROGRESS)",
                    "lrc_callback(progress=33)",
                    "lrc_callback(progress=66)",
                    "lrc_callback(result=[0, 'On command completed OK'])",
                    "lrc_callback(status=COMPLETED)",
                ],
            )
            # Command is completed
            change_event_callbacks.assert_change_event("state", tango.DevState.ON)
            change_event_callbacks.assert_change_event(
                "status", "The device is in ON state."
            )
            assert device_under_test.state() == tango.DevState.ON

        return _turn_on_device

    @pytest.fixture()
    def assign_resources_to_empty_subarray(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        successful_lrc_callback: LrcCallback,
        aborted_lrc_callback: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> Callable[[list[str], bool], LrcSubscriptions]:
        """
        Assign resources to the device and clear the queue attributes.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks
        :param successful_lrc_callback: callback fixture to use with invoke_lrc
        :param aborted_lrc_callback: callback fixture to use with invoke_lrc
        :param caplog: pytest LogCaptureFixture
        :return: Callable helper function
        """

        def _assign_resources_to_empty_subarray(
            resources_list: list[str], to_be_aborted: bool
        ) -> Any:
            """
            Assign resources to the device and clear the queue attributes.

            :param resources_list: list of resources to assign
            :param to_be_aborted: if command will be aborted while in progress
            :return: the executed AssignResources() command's unique ID
            """
            # Call command
            resources_to_assign = json.dumps({"resources": resources_list})
            assign_command = invoke_lrc(
                aborted_lrc_callback if to_be_aborted else successful_lrc_callback,
                device_under_test,
                "AssignResources",
                (resources_to_assign,),
            )
            Helpers.assert_expected_logs(
                caplog,
                [  # Log messages must be in this exact order
                    "lrc_callback(status=STAGING)",
                    "lrc_callback(status=QUEUED)",
                    "lrc_callback(status=IN_PROGRESS)",
                ],
            )
            change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
            change_event_callbacks.assert_change_event(
                "commandedObsState", ObsState.IDLE
            )
            if to_be_aborted:
                return assign_command
            Helpers.assert_expected_logs(
                caplog,
                [  # Log messages must be in this exact order
                    "lrc_callback(progress=33)",
                    "lrc_callback(progress=66)",
                    "lrc_callback(result=[0, 'Resource assignment completed OK'])",
                    "lrc_callback(status=COMPLETED)",
                ],
            )
            change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)
            assert device_under_test.obsState == device_under_test.commandedObsState
            assert list(device_under_test.assignedResources) == resources_list
            return assign_command

        return _assign_resources_to_empty_subarray

    @pytest.fixture()
    def configure_subarray(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        successful_lrc_callback: LrcCallback,
        aborted_lrc_callback: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> Callable[[dict[str, int], bool], LrcSubscriptions]:
        """
        Configure the device and clear the queue attributes.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks
        :param successful_lrc_callback: callback fixture to use with invoke_lrc
        :param aborted_lrc_callback: callback fixture to use with invoke_lrc
        :param caplog: pytest LogCaptureFixture
        :return: Callable helper function
        """

        def _configure_subarray(
            configuration_to_apply: dict[str, int], to_be_aborted: bool
        ) -> Any:
            """
            Configure the device and clear the queue attributes.

            :param configuration_to_apply: dict
            :param to_be_aborted: if command will be aborted while in progress
            :return: the executed Configure() command's unique ID
            """
            assert list(device_under_test.configuredCapabilities) == [
                "blocks:0",
                "channels:0",
            ]
            # Call command
            configure_command = invoke_lrc(
                aborted_lrc_callback if to_be_aborted else successful_lrc_callback,
                device_under_test,
                "Configure",
                (json.dumps(configuration_to_apply),),
            )
            Helpers.assert_expected_logs(
                caplog,
                [  # Log messages must be in this exact order
                    "lrc_callback(status=STAGING)",
                    "lrc_callback(status=QUEUED)",
                    "lrc_callback(status=IN_PROGRESS)",
                ],
            )
            change_event_callbacks.assert_change_event("obsState", ObsState.CONFIGURING)
            change_event_callbacks.assert_change_event(
                "commandedObsState", ObsState.READY
            )
            if to_be_aborted:
                return configure_command
            Helpers.assert_expected_logs(
                caplog,
                [  # Log messages must be in this exact order
                    "lrc_callback(progress=33)",
                    "lrc_callback(progress=66)",
                    "lrc_callback(result=[0, 'Configure completed OK'])",
                    "lrc_callback(status=COMPLETED)",
                ],
            )
            # Command is completed
            change_event_callbacks.assert_change_event("obsState", ObsState.READY)
            assert device_under_test.obsState == device_under_test.commandedObsState
            return configure_command

        return _configure_subarray

    @pytest.fixture()
    def reset_subarray(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        successful_lrc_callback: LrcCallback,
        aborted_lrc_callback: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> Callable[[ObsState, bool], LrcSubscriptions]:
        """
        Reset the device and clear the queue attributes.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks
        :param successful_lrc_callback: callback fixture to use with invoke_lrc
        :param aborted_lrc_callback: callback fixture to use with invoke_lrc
        :param caplog: pytest LogCaptureFixture
        :return: Callable helper function
        """

        def _reset_subarray(
            expected_obs_state: ObsState, to_be_aborted: bool
        ) -> LrcSubscriptions:
            """
            Reset the device and clear the queue attributes.

            :param expected_obs_state: the expected obsState after ObsReset completed
            :param to_be_aborted: if command will be aborted while in progress
            :return: the executed ObsReset() command's unique ID
            """
            # Call command
            reset_command = invoke_lrc(
                aborted_lrc_callback if to_be_aborted else successful_lrc_callback,
                device_under_test,
                "ObsReset",
            )
            Helpers.assert_expected_logs(
                caplog,
                [  # Log messages must be in this exact order
                    "lrc_callback(status=STAGING)",
                    "lrc_callback(status=QUEUED)",
                    "lrc_callback(status=IN_PROGRESS)",
                ],
            )
            change_event_callbacks.assert_change_event("obsState", ObsState.RESETTING)
            change_event_callbacks.assert_change_event(
                "commandedObsState", expected_obs_state
            )
            if to_be_aborted:
                return reset_command
            Helpers.assert_expected_logs(
                caplog,
                [  # Log messages must be in this exact order
                    "lrc_callback(progress=33)",
                    "lrc_callback(progress=66)",
                    "lrc_callback(result=[0, 'Obs reset completed OK'])",
                    "lrc_callback(status=COMPLETED)",
                ],
            )
            # Command is completed
            change_event_callbacks.assert_change_event("obsState", expected_obs_state)
            assert device_under_test.obsState == device_under_test.commandedObsState
            return reset_command

        return _reset_subarray

    @pytest.fixture()
    def abort_subarray_command(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        logger: logging.Logger,
        caplog: pytest.LogCaptureFixture,
    ) -> Callable[[LrcSubscriptions], None]:
        """
        Abort the given command in progress and clear the queue attributes.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks
        :param logger: test logger
        :param caplog: pytest LogCaptureFixture
        :return: Callable helper function
        """

        def abort_callback(
            status: TaskStatus | None = None,
            progress: int | None = None,
            result: JSONData | None = None,
            error: tuple[DevError] | None = None,
            **kwargs: Any,
        ) -> None:
            if progress is not None:
                logger.info(f"abort_callback(progress={progress})")
            if result is not None:
                logger.info(f"abort_callback(result={result})")
            if status is not None:
                logger.info(f"abort_callback(status={status.name})")
            if error is not None:
                logger.error(f"abort_callback(error={error})")
            if kwargs:
                logger.error(f"abort_callback(kwargs={kwargs})")

        def _abort_subarray_command(lrc: LrcSubscriptions) -> None:
            """
            Abort the given command in progress and clear the queue attributes.

            :param lrc: of command in progress to abort
            """
            _ = invoke_lrc(abort_callback, device_under_test, "Abort")
            change_event_callbacks.assert_change_event("obsState", ObsState.ABORTING)
            change_event_callbacks.assert_change_event(
                "commandedObsState", ObsState.ABORTED
            )
            Helpers.assert_expected_logs(
                caplog,
                [  # Log messages must be in this exact order
                    # "lrc_callback(status=IN_PROGRESS)",
                    "abort_callback(status=STAGING)",
                    # "lrc_callback(status=IN_PROGRESS)",
                    "abort_callback(status=IN_PROGRESS)",
                    "lrc_callback(result=[7, 'Command has been aborted'])",
                    "lrc_callback(status=ABORTED)",
                    # "abort_callback(status=IN_PROGRESS)",
                    "abort_callback(result=[0, 'Abort completed OK'])",
                    "abort_callback(status=COMPLETED)",
                ],
            )
            change_event_callbacks.assert_change_event("obsState", ObsState.ABORTED)
            assert device_under_test.obsState == device_under_test.commandedObsState
            change_event_callbacks.assert_not_called()
            del lrc

        return _abort_subarray_command

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
        assign_resources_to_empty_subarray: Callable[
            [list[str], bool], LrcSubscriptions
        ],
        successful_lrc_callback: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test for AssignResources, ReleaseResources and ReleaseAllResources.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks
        :param turn_on_device: helper function
        :param assign_resources_to_empty_subarray: helper function
        :param successful_lrc_callback: callback fixture to use with invoke_lrc
        :param caplog: pytest LogCaptureFixture
        """
        turn_on_device()
        assign_resources_to_empty_subarray(["BAND1", "BAND2"], False)

        # Test partial release of resources
        resources_to_release = json.dumps({"resources": ["BAND1"]})
        _ = invoke_lrc(
            successful_lrc_callback,
            device_under_test,
            "ReleaseResources",
            (resources_to_release,),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                "lrc_callback(status=STAGING)",
                "lrc_callback(status=QUEUED)",
                "lrc_callback(status=IN_PROGRESS)",
                "lrc_callback(progress=33)",
                "lrc_callback(progress=66)",
                "lrc_callback(result=[0, 'Resource release completed OK'])",
                "lrc_callback(status=COMPLETED)",
            ],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)
        assert list(device_under_test.assignedResources) == ["BAND2"]
        assert device_under_test.obsState == ObsState.IDLE

        # Test release all
        _ = invoke_lrc(
            successful_lrc_callback, device_under_test, "ReleaseAllResources"
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        change_event_callbacks.assert_change_event("commandedObsState", ObsState.EMPTY)
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                "lrc_callback(status=STAGING)",
                "lrc_callback(status=QUEUED)",
                "lrc_callback(status=IN_PROGRESS)",
                "lrc_callback(progress=33)",
                "lrc_callback(progress=66)",
                "lrc_callback(result=[0, 'Resource release completed OK'])",
                "lrc_callback(status=COMPLETED)",
            ],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.EMPTY)
        assert device_under_test.obsState == device_under_test.commandedObsState
        assert not device_under_test.assignedResources

    def test_configure_and_end(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        turn_on_device: Callable[[], None],
        assign_resources_to_empty_subarray: Callable[
            [list[str], bool], LrcSubscriptions
        ],
        configure_subarray: Callable[[dict[str, int], bool], LrcSubscriptions],
        successful_lrc_callback: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test for Configure and End.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks.
        :param turn_on_device: helper function
        :param assign_resources_to_empty_subarray: helper function
        :param configure_subarray: helper function
        :param successful_lrc_callback: callback fixture to use with invoke_lrc
        :param caplog: pytest LogCaptureFixture
        """
        turn_on_device()
        assign_resources_to_empty_subarray(["BAND1"], False)
        configure_subarray({"blocks": 1, "channels": 2}, False)
        assert list(device_under_test.configuredCapabilities) == [
            "blocks:1",
            "channels:2",
        ]

        # Deconfigure (End)
        _ = invoke_lrc(successful_lrc_callback, device_under_test, "End")
        change_event_callbacks.assert_change_event("commandedObsState", ObsState.IDLE)
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                "lrc_callback(status=STAGING)",
                "lrc_callback(status=QUEUED)",
                "lrc_callback(status=IN_PROGRESS)",
                "lrc_callback(progress=33)",
                "lrc_callback(progress=66)",
                "lrc_callback(result=[0, 'Deconfigure completed OK'])",
                "lrc_callback(status=COMPLETED)",
            ],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)
        assert device_under_test.obsState == device_under_test.commandedObsState
        assert list(device_under_test.configuredCapabilities) == [
            "blocks:0",
            "channels:0",
        ]

    def test_scan_and_end_scan(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        turn_on_device: Callable[[], None],
        assign_resources_to_empty_subarray: Callable[
            [list[str], bool], LrcSubscriptions
        ],
        configure_subarray: Callable[[dict[str, int], bool], LrcSubscriptions],
        successful_lrc_callback: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test for Scan and EndScan.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks.
        :param turn_on_device: helper function
        :param assign_resources_to_empty_subarray: helper function
        :param configure_subarray: helper function
        :param successful_lrc_callback: callback fixture to use with invoke_lrc
        :param caplog: pytest LogCaptureFixture
        """
        turn_on_device()
        assign_resources_to_empty_subarray(["BAND1"], False)
        configure_subarray({"blocks": 2}, False)
        assert list(device_under_test.configuredCapabilities) == [
            "blocks:2",
            "channels:0",
        ]

        # Scan
        dummy_scan_arg = {"scan_id": "scan_25"}
        _ = invoke_lrc(
            successful_lrc_callback,
            device_under_test,
            "Scan",
            (json.dumps(dummy_scan_arg),),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.SCANNING)
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                "lrc_callback(status=STAGING)",
                "lrc_callback(status=QUEUED)",
                "lrc_callback(status=IN_PROGRESS)",
                "lrc_callback(progress=33)",
                "lrc_callback(progress=66)",
                "lrc_callback(result="
                f"[0, 'Scan {dummy_scan_arg['scan_id']} commencement completed OK'])",
                "lrc_callback(status=COMPLETED)",
            ],
        )

        # End scan
        _ = invoke_lrc(successful_lrc_callback, device_under_test, "EndScan")
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                "lrc_callback(status=STAGING)",
                "lrc_callback(status=QUEUED)",
                "lrc_callback(status=IN_PROGRESS)",
                "lrc_callback(progress=33)",
                "lrc_callback(progress=66)",
                "lrc_callback(result=[0, 'End scan completed OK'])",
                "lrc_callback(status=COMPLETED)",
            ],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.READY)
        assert device_under_test.obsState == device_under_test.commandedObsState

    def test_abort_and_obsreset_from_resourcing(
        self: TestSKASubarray,
        turn_on_device: Callable[[], None],
        assign_resources_to_empty_subarray: Callable[
            [list[str], bool], LrcSubscriptions
        ],
        abort_subarray_command: Callable[[LrcSubscriptions], None],
        reset_subarray: Callable[[ObsState, bool], LrcSubscriptions],
    ) -> None:
        """
        Test for Abort and Reset from AssignResources from EMPTY state.

        :param turn_on_device: helper function
        :param assign_resources_to_empty_subarray: helper function
        :param abort_subarray_command: helper function
        :param reset_subarray: helper function
        """
        turn_on_device()
        assign_command = assign_resources_to_empty_subarray(["BAND1"], True)
        # Abort assign command
        abort_subarray_command(assign_command)
        # Reset from aborted state to empty
        reset_subarray(ObsState.EMPTY, False)

    def test_abort_and_obsreset_from_configuring(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        turn_on_device: Callable[[], None],
        assign_resources_to_empty_subarray: Callable[
            [list[str], bool], LrcSubscriptions
        ],
        configure_subarray: Callable[[dict[str, int], bool], LrcSubscriptions],
        abort_subarray_command: Callable[[LrcSubscriptions], None],
        reset_subarray: Callable[[ObsState, bool], LrcSubscriptions],
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
        configure_command = configure_subarray({"blocks": 2}, True)
        # Abort configure command
        abort_subarray_command(configure_command)
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
        assign_resources_to_empty_subarray: Callable[
            [list[str], bool], LrcSubscriptions
        ],
        abort_subarray_command: Callable[[LrcSubscriptions], None],
        reset_subarray: Callable[[ObsState, bool], LrcSubscriptions],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test for Reset after fault of AssignResources.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks.
        :param turn_on_device: helper function
        :param assign_resources_to_empty_subarray: helper function
        :param abort_subarray_command: helper function
        :param reset_subarray: helper function
        :param caplog: pytest LogCaptureFixture
        """
        turn_on_device()
        assign_command = assign_resources_to_empty_subarray(["BAND1"], True)
        # Simulate observation fault
        device_under_test.SimulateObsFault()
        change_event_callbacks.assert_change_event("obsState", ObsState.FAULT)
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                "lrc_callback(result=[7, 'Command has been aborted'])",
                "lrc_callback(status=ABORTED)",
            ],
        )
        del assign_command
        # Reset from fault state then abort reset
        reset_command = reset_subarray(ObsState.EMPTY, True)
        abort_subarray_command(reset_command)
        # Reset again from abort to empty state
        reset_subarray(ObsState.EMPTY, False)

    def test_obsreset_from_resourcing_after_idle(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        turn_on_device: Callable[[], None],
        assign_resources_to_empty_subarray: Callable[
            [list[str], bool], LrcSubscriptions
        ],
        abort_subarray_command: Callable[[LrcSubscriptions], None],
        reset_subarray: Callable[[ObsState, bool], LrcSubscriptions],
        aborted_lrc_callback: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test for Abort and Reset from AssignResources from IDLE state.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event callbacks.
        :param turn_on_device: helper function
        :param assign_resources_to_empty_subarray: helper function
        :param abort_subarray_command: helper function
        :param reset_subarray: helper function
        :param aborted_lrc_callback: callback fixture to use with invoke_lrc
        :param caplog: pytest LogCaptureFixture
        """
        turn_on_device()
        assign_resources_to_empty_subarray(["BAND1"], False)
        # Assign more resources
        assign_command = invoke_lrc(
            aborted_lrc_callback,
            device_under_test,
            "AssignResources",
            (json.dumps({"resources": ["BAND2"]}),),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                "lrc_callback(status=STAGING)",
                "lrc_callback(status=QUEUED)",
                "lrc_callback(status=IN_PROGRESS)",
            ],
        )
        # Abort 2nd assign command
        abort_subarray_command(assign_command)
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

    def test_is_cmd_allowed_exceptions(
        self: TestSKASubarray,
        device_under_test: tango.DeviceProxy,
    ) -> None:
        """
        Test the 'is_cmd_allowed' methods' raised exception messages.

        :param device_under_test: a proxy to the device under test
        """
        with pytest.raises(DevFailed) as exc:
            device_under_test.Configure(json.dumps({"blocks": 2}))
        assert (
            "ska_tango_base.faults.StateModelError: Configure command "
            "not permitted in observation state EMPTY" in str(exc.value)
        )
        with pytest.raises(DevFailed) as exc:
            device_under_test.Scan(json.dumps({"scan_id": "scan_1"}))
        assert (
            "ska_tango_base.faults.StateModelError: Scan command "
            "not permitted in observation state EMPTY" in str(exc.value)
        )
        with pytest.raises(DevFailed) as exc:
            device_under_test.EndScan()
        assert (
            "ska_tango_base.faults.StateModelError: EndScan command "
            "not permitted in observation state EMPTY" in str(exc.value)
        )
        with pytest.raises(DevFailed) as exc:
            device_under_test.End()
        assert (
            "ska_tango_base.faults.StateModelError: End command "
            "not permitted in observation state EMPTY" in str(exc.value)
        )
        with pytest.raises(DevFailed) as exc:
            device_under_test.Abort()
        assert (
            "ska_tango_base.faults.StateModelError: Abort command "
            "not permitted in observation state EMPTY" in str(exc.value)
        )
        with pytest.raises(DevFailed) as exc:
            device_under_test.ObsReset()
        assert (
            "ska_tango_base.faults.StateModelError: ObsReset command "
            "not permitted in observation state EMPTY" in str(exc.value)
        )
        with pytest.raises(DevFailed) as exc:
            device_under_test.Restart()
        assert (
            "ska_tango_base.faults.StateModelError: Restart command "
            "not permitted in observation state EMPTY" in str(exc.value)
        )
        device_under_test.AssignResources(json.dumps({"resources": ["BAND1"]}))
        with pytest.raises(DevFailed) as exc:
            device_under_test.AssignResources(json.dumps({"resources": ["BAND2"]}))
        assert (
            "ska_tango_base.faults.StateModelError: AssignResources command "
            "not permitted in observation state RESOURCING" in str(exc.value)
        )
        with pytest.raises(DevFailed) as exc:
            device_under_test.ReleaseResources(json.dumps({"resources": ["BAND1"]}))
        assert (
            "ska_tango_base.faults.StateModelError: ReleaseResources command "
            "not permitted in observation state RESOURCING" in str(exc.value)
        )
        with pytest.raises(DevFailed) as exc:
            device_under_test.ReleaseAllResources()
        assert (
            "ska_tango_base.faults.StateModelError: ReleaseAllResources command "
            "not permitted in observation state RESOURCING" in str(exc.value)
        )
