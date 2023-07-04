# pylint: disable=invalid-name
# TODO: Split logging service out from base_device module, then split these
# tests the same way.

# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module contains the tests for the SKABaseDevice."""
from __future__ import annotations

import json
import re
import socket
import time
import unittest
from typing import Any

import pytest
import tango
from ska_control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    LoggingLevel,
    ResultCode,
    SimulationMode,
    TaskStatus,
    TestMode,
)
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup
from tango import DevFailed, DevState

import ska_tango_base.base.base_device
from ska_tango_base import SKABaseDevice
from ska_tango_base.base import CommandTracker
from ska_tango_base.base.base_device import _DEBUGGER_PORT
from ska_tango_base.testing.reference import (
    FakeBaseComponent,
    ReferenceBaseComponentManager,
)


class TestCommandTracker:
    """Tests of the CommandTracker class."""

    @pytest.fixture
    def callbacks(
        self: TestCommandTracker, mocker: unittest.mock.Mock
    ) -> dict[str, unittest.mock.Mock]:
        """
        Return a dictionary of mocks for use as callbacks.

        These callbacks will be passed to the command tracker under
        test, and can then be used in testing to check that callbacks
        are called as expected.

        :param mocker: pytest fixture that wraps
            :py:mod:`unittest.mock`.

        :return: a dictionary of mocks for use as callbacks
        """
        return {
            "queue": mocker.Mock(),
            "status": mocker.Mock(),
            "progress": mocker.Mock(),
            "result": mocker.Mock(),
            "exception": mocker.Mock(),
        }

    @pytest.fixture
    def removal_time(self: TestCommandTracker) -> float:
        """
        Return how long the command tracker should retain memory of a completed command.

        :return: amount of time, in seconds.
        """
        return 0.1

    @pytest.fixture
    def command_tracker(
        self: TestCommandTracker,
        callbacks: dict[str, unittest.mock.Mock],
        removal_time: float,
    ) -> CommandTracker:
        """
        Return the command tracker under test.

        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        :param removal_time: how long completed command is retained

        :return: the command tracker under test
        """
        return CommandTracker(
            queue_changed_callback=callbacks["queue"],
            status_changed_callback=callbacks["status"],
            progress_changed_callback=callbacks["progress"],
            result_callback=callbacks["result"],
            exception_callback=callbacks["exception"],
            removal_time=removal_time,
        )

    # TODO: pylint is right that this test is way too long.
    def test_command_tracker(  # pylint: disable=too-many-statements
        self: TestCommandTracker,
        command_tracker: CommandTracker,
        removal_time: float,
        callbacks: dict[str, unittest.mock.Mock],
    ) -> None:
        """
        Test that the command tracker correctly tracks commands.

        :param command_tracker: the command tracker under test
        :param removal_time: how long completed command is retained
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """
        assert command_tracker.commands_in_queue == []
        assert command_tracker.command_statuses == []
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result is None
        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_not_called()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        first_command_id = command_tracker.new_command("first_command")
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command")
        ]
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.STAGING)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result is None
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_called_once_with(
            [(first_command_id, "first_command")]
        )
        callbacks["queue"].reset_mock()
        callbacks["status"].assert_not_called()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        command_tracker.update_command_info(
            first_command_id, status=TaskStatus.IN_PROGRESS
        )
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command")
        ]
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.IN_PROGRESS)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result is None
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_called_once_with(
            [(first_command_id, TaskStatus.IN_PROGRESS)]
        )
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        second_command_id = command_tracker.new_command("second_command")
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command"),
            (second_command_id, "second_command"),
        ]
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.IN_PROGRESS),
            (second_command_id, TaskStatus.STAGING),
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result is None
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_called_once_with(
            [
                (first_command_id, "first_command"),
                (second_command_id, "second_command"),
            ]
        )
        callbacks["queue"].reset_mock()
        callbacks["status"].assert_not_called()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        command_tracker.update_command_info(first_command_id, progress=50)
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command"),
            (second_command_id, "second_command"),
        ]
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.IN_PROGRESS),
            (second_command_id, TaskStatus.STAGING),
        ]
        assert command_tracker.command_progresses == [(first_command_id, 50)]
        assert command_tracker.command_result is None
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_not_called()
        callbacks["progress"].assert_called_once_with([(first_command_id, 50)])
        callbacks["progress"].reset_mock()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        command_tracker.update_command_info(
            first_command_id, result=(ResultCode.OK, "a message string")
        )
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.IN_PROGRESS),
            (second_command_id, TaskStatus.STAGING),
        ]
        assert command_tracker.command_progresses == [(first_command_id, 50)]
        assert command_tracker.command_result == (
            first_command_id,
            (ResultCode.OK, "a message string"),
        )
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_not_called()
        callbacks["progress"].assert_not_called()
        callbacks["progress"].reset_mock()
        callbacks["result"].assert_called_once_with(
            first_command_id, (ResultCode.OK, "a message string")
        )
        callbacks["result"].reset_mock()
        callbacks["exception"].assert_not_called()

        command_tracker.update_command_info(
            first_command_id, status=TaskStatus.COMPLETED
        )
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command"),
            (second_command_id, "second_command"),
        ]
        time.sleep(removal_time + 0.1)
        assert command_tracker.commands_in_queue == [
            (second_command_id, "second_command")
        ]
        assert command_tracker.command_statuses == [
            (second_command_id, TaskStatus.STAGING)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result == (
            first_command_id,
            (ResultCode.OK, "a message string"),
        )
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_called_once_with(
            [(second_command_id, "second_command")]
        )
        callbacks["queue"].reset_mock()
        callbacks["status"].assert_called_once_with(
            [
                (first_command_id, TaskStatus.COMPLETED),
                (second_command_id, TaskStatus.STAGING),
            ]
        )
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        command_tracker.update_command_info(
            second_command_id, status=TaskStatus.IN_PROGRESS
        )
        assert command_tracker.commands_in_queue == [
            (second_command_id, "second_command")
        ]
        assert command_tracker.command_statuses == [
            (second_command_id, TaskStatus.IN_PROGRESS)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result == (
            first_command_id,
            (ResultCode.OK, "a message string"),
        )
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_called_once_with(
            [
                (second_command_id, TaskStatus.IN_PROGRESS),
            ]
        )
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        exception_to_raise = ValueError("Exception under test")

        command_tracker.update_command_info(
            second_command_id,
            status=TaskStatus.FAILED,
            exception=exception_to_raise,
        )
        assert command_tracker.commands_in_queue == [
            (second_command_id, "second_command")
        ]
        assert command_tracker.command_statuses == [
            (second_command_id, TaskStatus.FAILED)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result == (
            first_command_id,
            (ResultCode.OK, "a message string"),
        )
        assert command_tracker.command_exception == (
            second_command_id,
            exception_to_raise,
        )

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_called_once_with(
            [
                (second_command_id, TaskStatus.FAILED),
            ]
        )
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_called_once_with(
            second_command_id, exception_to_raise
        )


class TestSKABaseDevice:  # pylint: disable=too-many-public-methods
    """Test cases for SKABaseDevice."""

    @pytest.fixture(scope="class")
    def device_test_config(
        self: TestSKABaseDevice, device_properties: dict[str, str]
    ) -> dict[str, Any]:
        """
        Specify device configuration, including properties and memorized attributes.

        This implementation provides a concrete subclass of
        SKABaseDevice, and a memorized value for adminMode.

        :param device_properties: fixture that returns device properties
            of the device under test

        :return: specification of how the device under test should be
            configured
        """
        return {
            "device": SKABaseDevice,
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
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test device properties.

        :param device_under_test: a DeviceProxy to the device under
            test, running in a tango.DeviceTestContext
        """

    def test_State(
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.state() == DevState.OFF

    def test_Status(
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.Status() == "The device is in OFF state."

    def test_GetVersionInfo(
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
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

    def test_Reset(
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for Reset.

        :param device_under_test: a proxy to the device under test
        """
        # The main test of this command is
        # TestSKABaseDevice_commands::test_ResetCommand
        assert device_under_test.state() == DevState.OFF

        with pytest.raises(
            DevFailed,
            match="Command Reset not allowed when the device is in OFF state",
        ):
            _ = device_under_test.Reset()

    def test_On(
        self: TestSKABaseDevice,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for On command.

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

        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandProgress"].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(None)
        change_event_callbacks["longRunningCommandResult"].assert_change_event(("", ""))

        [[result_code], [command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (command_id, "QUEUED")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (command_id, "IN_PROGRESS")
        )
        for progress_point in FakeBaseComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (command_id, progress_point)
            )

        change_event_callbacks.assert_change_event("state", DevState.ON)
        change_event_callbacks.assert_change_event(
            "status", "The device is in ON state."
        )

        assert device_under_test.state() == DevState.ON

        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                command_id,
                json.dumps([int(ResultCode.OK), "On command completed OK"]),
            ),
        )

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (command_id, "COMPLETED")
        )

        # Check what happens if we call On() when the device is already ON.
        [[result_code], [message]] = device_under_test.On()
        assert result_code == ResultCode.REJECTED
        assert message == "Device is already in ON state."

        change_event_callbacks.assert_not_called()

    def test_Standby(
        self: TestSKABaseDevice,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for Standby command.

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

        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandProgress"].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(None)
        change_event_callbacks["longRunningCommandResult"].assert_change_event(("", ""))

        [[result_code], [command_id]] = device_under_test.Standby()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (command_id, "QUEUED")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (command_id, "IN_PROGRESS")
        )
        for progress_point in FakeBaseComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (command_id, progress_point)
            )

        change_event_callbacks.assert_change_event("state", DevState.STANDBY)
        change_event_callbacks.assert_change_event(
            "status", "The device is in STANDBY state."
        )

        assert device_under_test.state() == DevState.STANDBY

        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                command_id,
                json.dumps([int(ResultCode.OK), "Standby command completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (command_id, "COMPLETED")
        )

        assert (
            device_under_test.CheckLongRunningCommandStatus(command_id) == "COMPLETED"
        )

        # Check what happens if we call Standby() when the device is already STANDBY.
        [[result_code], [message]] = device_under_test.Standby()
        assert result_code == ResultCode.REJECTED
        assert message == "Device is already in STANDBY state."

        change_event_callbacks.assert_not_called()

    def test_Off(
        self: TestSKABaseDevice,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for Off command.

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

        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandProgress"].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(None)
        change_event_callbacks["longRunningCommandResult"].assert_change_event(("", ""))

        # Check what happens if we call Off() when the device is already OFF.
        [[result_code], [message]] = device_under_test.Off()
        assert result_code == ResultCode.REJECTED
        assert message == "Device is already in OFF state."

        change_event_callbacks.assert_not_called()

    def test_buildState(
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
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
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        version_id_pattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(version_id_pattern, device_under_test.versionId)) is not None

    def test_loggingLevel(
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for loggingLevel.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.loggingLevel == LoggingLevel.INFO

        for level in LoggingLevel:
            device_under_test.loggingLevel = level
            assert device_under_test.loggingLevel == level
            assert device_under_test.get_logging_level() == level

        with pytest.raises(DevFailed):
            device_under_test.loggingLevel = LoggingLevel.FATAL + 100

    def test_loggingTargets(
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for loggingTargets.

        :param device_under_test: a proxy to the device under test
        """
        # tango logging target must be enabled by default
        assert device_under_test.loggingTargets == ("tango::logger",)

        # test console target
        device_under_test.loggingTargets = ("console::cout",)
        assert device_under_test.loggingTargets == ("console::cout",)
        device_under_test.loggingTargets = (
            "console::cout",
            "file::/tmp/dummy",
            "syslog::udp://localhost:514",
        )
        assert device_under_test.loggingTargets == (
            "console::cout",
            "file::/tmp/dummy",
            "syslog::udp://localhost:514",
        )
        device_under_test.loggingTargets = ("tango::logger",)
        assert device_under_test.loggingTargets == ("tango::logger",)
        device_under_test.loggingTargets = tuple()
        assert device_under_test.loggingTargets is None
        with pytest.raises(DevFailed):
            device_under_test.loggingTargets = ("invalid::type",)

    def test_healthState(
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.healthState == HealthState.UNKNOWN

    def test_adminMode(
        self: TestSKABaseDevice,
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

        for attribute in ["state", "status", "adminMode"]:
            device_under_test.subscribe_event(
                attribute,
                tango.EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["adminMode"].assert_change_event(AdminMode.ONLINE)

        assert device_under_test.adminMode == AdminMode.ONLINE
        assert device_under_test.state() == DevState.OFF

        device_under_test.adminMode = AdminMode.OFFLINE

        change_event_callbacks.assert_change_event("adminMode", AdminMode.OFFLINE)
        assert device_under_test.adminMode == AdminMode.OFFLINE

        change_event_callbacks.assert_change_event("state", DevState.DISABLE)
        change_event_callbacks.assert_change_event(
            "status", "The device is in DISABLE state."
        )
        assert device_under_test.state() == DevState.DISABLE

        device_under_test.adminMode = AdminMode.MAINTENANCE
        change_event_callbacks.assert_change_event("adminMode", AdminMode.MAINTENANCE)
        assert device_under_test.adminMode == AdminMode.MAINTENANCE

        change_event_callbacks.assert_change_event("state", DevState.UNKNOWN)
        change_event_callbacks.assert_change_event(
            "status", "The device is in UNKNOWN state."
        )

        change_event_callbacks.assert_change_event("state", DevState.OFF)
        change_event_callbacks.assert_change_event(
            "status", "The device is in OFF state."
        )
        assert device_under_test.state() == DevState.OFF

        device_under_test.adminMode = AdminMode.ONLINE
        change_event_callbacks.assert_change_event("adminMode", AdminMode.ONLINE)
        assert device_under_test.adminMode == AdminMode.ONLINE

        change_event_callbacks.assert_not_called()

        assert device_under_test.state() == DevState.OFF

    def test_controlMode(
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.controlMode == ControlMode.REMOTE

    def test_simulationMode(
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.simulationMode == SimulationMode.FALSE

    def test_testMode(
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.testMode == TestMode.NONE

    def test_debugger_not_listening_by_default(
        self: TestSKABaseDevice,
        device_under_test: tango.DeviceProxy,  # pylint: disable=unused-argument
    ) -> None:
        """
        Test that DebugDevice is not active until enabled.

        :param device_under_test: a proxy to the device under test. This
            is not actually used, but the inclusion of the fixture
            ensures the device is running, which is a pre-condition of
            the test.
        """
        # pylint: disable-next=protected-access
        assert not SKABaseDevice._global_debugger_listening
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            with pytest.raises(ConnectionRefusedError):
                s.connect(("localhost", _DEBUGGER_PORT))

    def test_DebugDevice_starts_listening_on_default_port(
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test that enabling DebugDevice makes it listen on its default port.

        :param device_under_test: a proxy to the device under test
        """
        port = device_under_test.DebugDevice()
        assert port == _DEBUGGER_PORT
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", _DEBUGGER_PORT))
        assert device_under_test.state

    @pytest.mark.usefixtures("patch_debugger_to_start_on_ephemeral_port")
    def test_DebugDevice_twice_does_not_raise(
        self: TestSKABaseDevice, device_under_test: tango.DeviceProxy
    ) -> None:
        """
        Test that it is safe to enable the DebugDevice when it is already enabled.

        :param device_under_test: a proxy to the device under test
        """
        device_under_test.DebugDevice()
        port = device_under_test.DebugDevice()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", port))

    @pytest.mark.usefixtures("patch_debugger_to_start_on_ephemeral_port")
    def test_DebugDevice_does_not_break_a_command(
        self: TestSKABaseDevice,
        device_under_test: tango.DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test that enabling the DebugDevice feature does not break device commands.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        device_under_test.DebugDevice()
        assert device_under_test.state() == DevState.OFF

        device_under_test.subscribe_event(
            "state",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["state"],
        )
        change_event_callbacks.assert_change_event("state", DevState.OFF)

        device_under_test.On()

        change_event_callbacks.assert_change_event("state", DevState.ON)

        assert device_under_test.state() == DevState.ON


@pytest.fixture()
def patch_debugger_to_start_on_ephemeral_port() -> None:
    """
    Patch the debugger so that it starts on an ephemeral port.

    This is necessary because of intermittent debugger test failures: if
    the previous test has used the debugger port, then when the test
    tries to bind to that port, it may find that the OS has not made it
    available for use yet.
    """
    # pylint: disable-next=protected-access
    ska_tango_base.base.base_device._DEBUGGER_PORT = 0
