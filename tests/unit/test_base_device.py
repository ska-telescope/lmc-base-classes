# pylint: disable=invalid-name, too-many-lines
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
from typing import Any

import pytest
from ska_control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    LoggingLevel,
    ResultCode,
    SimulationMode,
    TestMode,
)
from ska_tango_testing.mock.placeholders import Anything
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup
from tango import DevFailed, DeviceProxy, DevState, EventType

from ska_tango_base import SKABaseDevice
from ska_tango_base.base.base_device import _DEBUGGER_PORT
from ska_tango_base.faults import CommandError
from ska_tango_base.long_running_commands_api import LrcCallback, invoke_lrc
from ska_tango_base.testing.reference import (
    ReferenceBaseComponentManager,
    ReferenceSkaBaseDevice,
)
from tests.conftest import Helpers


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
            "device": ReferenceSkaBaseDevice,
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
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test device properties.

        :param device_under_test: a DeviceProxy to the device under
            test, running in a DeviceTestContext
        """

    def test_State(self: TestSKABaseDevice, device_under_test: DeviceProxy) -> None:
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.state() == DevState.OFF

    def test_commandedState(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for commandedState.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        device_under_test.SetCommandTrackerRemovalTime(0)
        assert device_under_test.adminMode == AdminMode.ONLINE
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "commandedState",
            "longRunningCommandStatus",
        ]:
            device_under_test.subscribe_event(
                attribute,
                EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )
        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["commandedState"].assert_change_event("None")
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(())

        # ON command
        [[result_code], [on_command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED
        Helpers.assert_lrcstatus_change_event_staging_queued_in_progress(
            change_event_callbacks, on_command_id
        )
        change_event_callbacks["commandedState"].assert_change_event("ON")
        change_event_callbacks["state"].assert_change_event(DevState.ON)
        assert device_under_test.commandedState == device_under_test.state().name
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "COMPLETED")
        )

        # Simulate fault
        device_under_test.SimulateFault()
        change_event_callbacks["state"].assert_change_event(DevState.FAULT)
        with pytest.raises(
            DevFailed,
            match="Command On not allowed when the device is in FAULT state",
        ):
            device_under_test.On()
        with pytest.raises(
            DevFailed,
            match="Command Standby not allowed when the device is in FAULT state",
        ):
            device_under_test.Standby()
        assert device_under_test.commandedState == "ON"

        # RESET command
        [[result_code], [reset_command_id]] = device_under_test.Reset()
        assert result_code == ResultCode.QUEUED
        Helpers.assert_lrcstatus_change_event_staging_queued_in_progress(
            change_event_callbacks, reset_command_id
        )
        change_event_callbacks["state"].assert_change_event(DevState.ON)
        assert device_under_test.commandedState == device_under_test.state().name
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (reset_command_id, "COMPLETED")
        )

        # STANDBY command
        [[result_code], [standby_command_id]] = device_under_test.Standby()
        assert result_code == ResultCode.QUEUED
        Helpers.assert_lrcstatus_change_event_staging_queued_in_progress(
            change_event_callbacks, standby_command_id
        )
        change_event_callbacks["commandedState"].assert_change_event("STANDBY")
        change_event_callbacks["state"].assert_change_event(DevState.STANDBY)
        assert device_under_test.commandedState == device_under_test.state().name
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (standby_command_id, "COMPLETED")
        )

        # OFF command
        [[result_code], [off_command_id]] = device_under_test.Off()
        assert result_code == ResultCode.QUEUED
        Helpers.assert_lrcstatus_change_event_staging_queued_in_progress(
            change_event_callbacks, off_command_id
        )
        change_event_callbacks["commandedState"].assert_change_event("OFF")
        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        assert device_under_test.commandedState == device_under_test.state().name
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (off_command_id, "COMPLETED")
        )
        with pytest.raises(
            DevFailed,
            match="Command Reset not allowed when the device is in OFF state",
        ):
            device_under_test.Reset()

    def test_Status(self: TestSKABaseDevice, device_under_test: DeviceProxy) -> None:
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.Status() == "The device is in OFF state."

    def test_GetVersionInfo(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
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
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        successful_lrc_callback: LrcCallback,
    ) -> None:
        """
        Test for Reset.

        :param device_under_test: a proxy to the device under test
        :param successful_lrc_callback: callback fixture to use with invoke_lrc.
        """
        # The main test of this command is
        # TestSKABaseDevice_commands::test_ResetCommand
        assert device_under_test.state() == DevState.OFF

        with pytest.raises(
            DevFailed,
            match="Command Reset not allowed when the device is in OFF state",
        ):
            _ = invoke_lrc(successful_lrc_callback, device_under_test, "Reset")

    def test_deprecated_LRC_attributes(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for deprecated long running command attributes.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support.
        """
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "longRunningCommandStatus",
            "longRunningCommandProgress",
            "longRunningCommandInProgress",
            "longRunningCommandsInQueue",
            "longRunningCommandIDsInQueue",
            "longRunningCommandResult",
        ]:
            device_under_test.subscribe_event(
                attribute,
                EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks.assert_change_event("state", DevState.OFF)
        change_event_callbacks.assert_change_event("longRunningCommandStatus", ())
        change_event_callbacks.assert_change_event("longRunningCommandProgress", ())
        change_event_callbacks.assert_change_event("longRunningCommandInProgress", ())
        change_event_callbacks.assert_change_event("longRunningCommandsInQueue", ())
        change_event_callbacks.assert_change_event("longRunningCommandIDsInQueue", ())
        change_event_callbacks.assert_change_event("longRunningCommandResult", ("", ""))

        # ON command
        [[result_code], [on_command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED
        on_command = on_command_id.split("_", 2)[2]
        change_event_callbacks.assert_change_event(
            "longRunningCommandsInQueue", (on_command,)
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandIDsInQueue", (on_command_id,)
        )
        Helpers.assert_lrcstatus_change_event_staging_queued_in_progress(
            change_event_callbacks, on_command_id
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandInProgress", (on_command,)
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "66")
        )
        change_event_callbacks.assert_change_event("state", DevState.ON)
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
        change_event_callbacks.assert_change_event("longRunningCommandInProgress", ())
        assert device_under_test.longRunningCommandsInQueue == (on_command,)
        assert device_under_test.longRunningCommandIDsInQueue == (on_command_id,)

    def test_new_user_facing_LRC_attributes(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for the new user (human) facing LRC attributes.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support.
        """
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "lrcQueue",
            "lrcExecuting",
            "lrcFinished",
        ]:
            device_under_test.subscribe_event(
                attribute,
                EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["lrcQueue"].assert_change_event(())
        change_event_callbacks["lrcExecuting"].assert_change_event(())
        change_event_callbacks["lrcFinished"].assert_change_event(())

        [[result_code], [_]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        Helpers.print_change_event_queue(change_event_callbacks, "lrcQueue")
        change_event_callbacks["lrcExecuting"].assert_change_event(())  # TODO: ??
        change_event_callbacks["lrcFinished"].assert_change_event(())  # TODO: ??
        change_event_callbacks["lrcQueue"].assert_change_event(Anything)
        change_event_callbacks["lrcQueue"].assert_change_event(Anything)

        Helpers.print_change_event_queue(change_event_callbacks, "lrcExecuting")
        change_event_callbacks["lrcExecuting"].assert_change_event(Anything)
        change_event_callbacks["lrcExecuting"].assert_change_event(Anything)
        change_event_callbacks["lrcExecuting"].assert_change_event(Anything)

        change_event_callbacks.assert_change_event("state", DevState.ON)
        assert device_under_test.state() == DevState.ON

        Helpers.print_change_event_queue(change_event_callbacks, "lrcFinished")
        change_event_callbacks["lrcExecuting"].assert_change_event(Anything)
        change_event_callbacks["lrcFinished"].assert_change_event(Anything)

    def test_On(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        successful_lrc_callback: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test for On command.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support.
        :param successful_lrc_callback: callback fixture to use with invoke_lrc.
        :param caplog: pytest LogCaptureFixture
        """
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "status",
            "longRunningCommandInProgress",
        ]:
            device_under_test.subscribe_event(
                attribute,
                EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandInProgress"].assert_change_event(())

        lrc = invoke_lrc(successful_lrc_callback, device_under_test, "On")
        on_command = lrc.command_id.split("_", 2)[2]
        change_event_callbacks.assert_change_event(
            "longRunningCommandInProgress", (on_command,)
        )
        change_event_callbacks.assert_change_event("state", DevState.ON)
        change_event_callbacks.assert_change_event(
            "status", "The device is in ON state."
        )
        assert device_under_test.state() == DevState.ON
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
        change_event_callbacks["longRunningCommandInProgress"].assert_change_event(())

        # Check what happens if we call On() when the device is already ON.
        with pytest.raises(
            CommandError, match="On command rejected: Device is already in ON state."
        ):
            _ = invoke_lrc(successful_lrc_callback, device_under_test, "On")
        Helpers.assert_expected_logs(
            caplog, ["On command rejected: Device is already in ON state."]
        )
        change_event_callbacks.assert_not_called()

    def test_Standby(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        successful_lrc_callback: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test for Standby command.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support.
        :param successful_lrc_callback: callback fixture to use with invoke_lrc.
        :param caplog: pytest LogCaptureFixture
        """
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "status",
            "longRunningCommandInProgress",
        ]:
            device_under_test.subscribe_event(
                attribute,
                EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandInProgress"].assert_change_event(())

        lrc = invoke_lrc(successful_lrc_callback, device_under_test, "Standby")
        standby_command = lrc.command_id.split("_", 2)[2]
        change_event_callbacks.assert_change_event(
            "longRunningCommandInProgress", (standby_command,)
        )
        change_event_callbacks.assert_change_event("state", DevState.STANDBY)
        change_event_callbacks.assert_change_event(
            "status", "The device is in STANDBY state."
        )
        assert device_under_test.state() == DevState.STANDBY
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                "lrc_callback(status=STAGING)",
                "lrc_callback(status=QUEUED)",
                "lrc_callback(status=IN_PROGRESS)",
                "lrc_callback(progress=33)",
                "lrc_callback(progress=66)",
                "lrc_callback(result=[0, 'Standby command completed OK'])",
                "lrc_callback(status=COMPLETED)",
            ],
        )
        change_event_callbacks.assert_change_event("longRunningCommandInProgress", ())
        assert (
            device_under_test.CheckLongRunningCommandStatus(lrc.command_id)
            == "COMPLETED"
        )

        # Check what happens if we call Standby() when the device is already STANDBY.
        with pytest.raises(
            CommandError,
            match="Standby command rejected: Device is already in STANDBY state.",
        ):
            _ = invoke_lrc(successful_lrc_callback, device_under_test, "Standby")
        Helpers.assert_expected_logs(
            caplog, ["Standby command rejected: Device is already in STANDBY state."]
        )
        change_event_callbacks.assert_not_called()

    def test_Off(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        successful_lrc_callback: LrcCallback,
    ) -> None:
        """
        Test for Off command.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        :param successful_lrc_callback: callback fixture to use with invoke_lrc.
        """
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "status",
        ]:
            device_under_test.subscribe_event(
                attribute,
                EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )

        # Check what happens if we call Off() when the device is already OFF.
        with pytest.raises(
            CommandError,
            match="Off command rejected: Device is already in OFF state.",
        ):
            _ = invoke_lrc(successful_lrc_callback, device_under_test, "Off")
        change_event_callbacks.assert_not_called()

    def test_Abort(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        lrc_callback_log_only: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test for Abort command.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support.
        :param lrc_callback_log_only: callback fixture to use with invoke_lrc.
        :param caplog: pytest LogCaptureFixture
        """
        assert device_under_test.state() == DevState.OFF

        device_under_test.subscribe_event(
            "longRunningCommandInProgress",
            EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandInProgress"],
        )
        change_event_callbacks["longRunningCommandInProgress"].assert_change_event(())

        on_subs = invoke_lrc(lrc_callback_log_only, device_under_test, "On")
        on_command = on_subs.command_id.split("_", 2)[2]
        change_event_callbacks.assert_change_event(
            "longRunningCommandInProgress", (on_command,)
        )
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                "lrc_callback(status=STAGING)",
                "lrc_callback(status=QUEUED)",
                "lrc_callback(status=IN_PROGRESS)",
            ],
        )

        abort_subs = invoke_lrc(lrc_callback_log_only, device_under_test, "Abort")
        abort_command = abort_subs.command_id.split("_", 2)[2]
        change_event_callbacks["longRunningCommandInProgress"].assert_change_event(
            (on_command, abort_command)
        )
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                # "lrc_callback(status=IN_PROGRESS)",  # On
                "lrc_callback(status=STAGING)",  # Abort
                # "lrc_callback(status=IN_PROGRESS)",  # On
                "lrc_callback(status=IN_PROGRESS)",  # Abort
                "lrc_callback(result=[7, 'Command has been aborted'])",  # On
                "lrc_callback(status=ABORTED)",  # On
                # "lrc_callback(status=IN_PROGRESS)",  # Abort
                "lrc_callback(result=[0, 'Abort completed OK'])",  # Abort
                "lrc_callback(status=COMPLETED)",  # Abort
            ],
        )
        change_event_callbacks["longRunningCommandInProgress"].assert_change_event(
            (abort_command,)
        )
        change_event_callbacks["longRunningCommandInProgress"].assert_change_event(())

    def test_command_exception(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        lrc_callback_log_only: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test for when a command encounters an Exception.

        :param device_under_test: a proxy to the device under test
        :param lrc_callback_log_only: callback fixture to use with invoke_lrc.
        :param caplog: pytest LogCaptureFixture
        """
        cmd_subs = invoke_lrc(lrc_callback_log_only, device_under_test, "On")
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
        cmd_subs = invoke_lrc(
            lrc_callback_log_only, device_under_test, "SimulateCommandError"
        )
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                "lrc_callback(status=STAGING)",
                "lrc_callback(status=QUEUED)",
                "lrc_callback(result=[3, 'Unhandled exception during execution: "
                "Command encountered unexpected error'])",
                "lrc_callback(status=FAILED)",
            ],
        )
        cmd_subs = invoke_lrc(
            lrc_callback_log_only,
            device_under_test,
            "SimulateIsCmdAllowedError",
        )
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                "lrc_callback(status=STAGING)",
                "lrc_callback(status=QUEUED)",
                "lrc_callback(result=[5, \"Exception from 'is_cmd_allowed' method: "
                "'is_cmd_allowed' method encountered unexpected error\"])",
                "lrc_callback(status=REJECTED)",
            ],
        )
        del cmd_subs

    def test_lrc_api_exception(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        lrc_callback_log_only: LrcCallback,
    ) -> None:
        """
        Test for when invoke_lrc encounters a Tango exception.

        :param device_under_test: a proxy to the device under test
        :param lrc_callback_log_only: callback fixture to use with invoke_lrc.
        """
        with pytest.raises(DevFailed) as exc_info:
            invoke_lrc(lrc_callback_log_only, device_under_test, "DummyCmd", (1,))
            assert (
                "Invocation of command 'DummyCmd' failed with args: (1,)"
                in exc_info.value
            )

    def test_lrcStatusQueue(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test the LRC status queue is pruned when there are too many commands to report.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        # Set the removal time long enough to cover the execution time of the test
        device_under_test.SetCommandTrackerRemovalTime(1000)
        max_queued_tasks = 32  # Set in TaskExecutorComponentManager
        assert device_under_test.state() == DevState.OFF

        device_under_test.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )

        # Queue enough commands to fill the buffer
        command_ids = []
        for _ in range(max_queued_tasks):
            result_code, cmd_id = device_under_test.STANDBY()
            assert ResultCode(int(result_code)) == ResultCode.QUEUED
            command_ids.append(cmd_id[0])

        # Wait for them all to complete and queue another batch:
        for cmd_id in command_ids:
            change_event_callbacks.assert_change_event(
                "longRunningCommandResult",
                (
                    cmd_id,
                    json.dumps([int(ResultCode.OK), "Standby command completed OK"]),
                ),
                lookahead=max_queued_tasks,
                consume_nonmatches=True,
            )
        for _ in range(max_queued_tasks):
            result_code, cmd_id = device_under_test.ON()
            assert ResultCode(int(result_code)) == ResultCode.QUEUED
            command_ids.append(cmd_id[0])

        # Verify all commands reported in the Status attribute at this stage
        status_attribute = device_under_test.read_attribute("longRunningCommandStatus")
        for cmd_id in command_ids:
            assert cmd_id in status_attribute.value

        # Queue another ten to push the number over the array bounds
        for cmd_id in command_ids[32:42]:
            change_event_callbacks.assert_change_event(
                "longRunningCommandResult",
                (
                    cmd_id,
                    json.dumps([int(ResultCode.OK), "On command completed OK"]),
                ),
                lookahead=max_queued_tasks,
            )
        for _ in range(10):
            result_code, cmd_id = device_under_test.OFF()
            assert ResultCode(int(result_code)) == ResultCode.QUEUED
            command_ids.append(cmd_id[0])

        # max_queued_tasks = 32 and max_executing_tasks = 2,
        # so the attribute bounds are 32*2 + 2 = 66
        # Since we have submitted 74 commands, the first eight
        # completed commands should have been removed
        expected_removed_items = command_ids[:8]
        expected_present_items = command_ids[8:]
        status_attribute = device_under_test.read_attribute("longRunningCommandStatus")

        for cmd_id in expected_removed_items:
            assert cmd_id not in status_attribute.value
        for cmd_id in expected_present_items:
            assert cmd_id in status_attribute.value

    def test_buildState(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
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

    def test_versionId(self: TestSKABaseDevice, device_under_test: DeviceProxy) -> None:
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        version_id_pattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(version_id_pattern, device_under_test.versionId)) is not None

    def test_loggingLevel(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
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
        self: TestSKABaseDevice, device_under_test: DeviceProxy
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
        assert device_under_test.loggingTargets == ()
        with pytest.raises(DevFailed):
            device_under_test.loggingTargets = ("invalid::type",)

    def test_healthState(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.healthState == HealthState.UNKNOWN

    def test_adminMode(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
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
                EventType.CHANGE_EVENT,
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

        device_under_test.adminMode = AdminMode.ENGINEERING
        change_event_callbacks.assert_change_event("adminMode", AdminMode.ENGINEERING)
        assert device_under_test.adminMode == AdminMode.ENGINEERING

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
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.controlMode == ControlMode.REMOTE

    def test_simulationMode(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.simulationMode == SimulationMode.FALSE

    def test_testMode(self: TestSKABaseDevice, device_under_test: DeviceProxy) -> None:
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.testMode == TestMode.NONE

    def test_debugger_not_listening_by_default(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,  # pylint: disable=unused-argument
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
        self: TestSKABaseDevice, device_under_test: DeviceProxy
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
        self: TestSKABaseDevice, device_under_test: DeviceProxy
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
        device_under_test: DeviceProxy,
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
            EventType.CHANGE_EVENT,
            change_event_callbacks["state"],
        )
        change_event_callbacks.assert_change_event("state", DevState.OFF)

        device_under_test.On()

        change_event_callbacks.assert_change_event("state", DevState.ON)

        assert device_under_test.state() == DevState.ON
