"""Test various Tango devices with long running commmands working together."""
from typing import Any

import pytest
import tango
from ska_control_model import ResultCode
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup

from .multidevice import ExampleMultiDevice


@pytest.fixture(name="device_test_config", scope="function")
def device_test_config_fixture(device_properties: dict[str, str]) -> dict[str, Any]:
    """
    Return a specification of the device under test.

    The specification includes the device's properties and memorized
    attributes.

    :param device_properties: fixture that returns device properties
        of the device under test

    :return: specification of how the device under test should be
        configured
    """
    return {
        "device": ExampleMultiDevice,
        "component_manager_patch": None,
        "properties": device_properties,
        "memorized": None,
    }


@pytest.fixture(name="change_event_callbacks")
def change_event_callbacks_fixture() -> MockTangoEventCallbackGroup:
    """
    Return a dictionary of Tango device change event callbacks with asynchrony support.

    :return: a collections.defaultdict that returns change event
        callbacks by name.
    """
    return MockTangoEventCallbackGroup(
        "longRunningCommandProgress",
        "longRunningCommandResult",
        "longRunningCommandStatus",
        timeout=5.0,
    )


@pytest.mark.forked
def test_device_init(device_under_test: tango.DeviceProxy) -> None:
    """
    Test device initialisation.

    :param device_under_test: a proxy to the device under test
    """
    state = device_under_test.State()
    assert state == tango.DevState.DISABLE


@pytest.mark.forked
def test_device(
    device_under_test: tango.DeviceProxy,
    change_event_callbacks: MockTangoEventCallbackGroup,
) -> None:
    """
    Test our Multidevice.

    :param device_under_test: a proxy to the device under test
    :param change_event_callbacks: dictionary of mock change event
        callbacks with asynchrony support
    """
    device_under_test.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    change_event_callbacks.assert_change_event("longRunningCommandResult", ("", ""))

    # Short
    result_code, result = device_under_test.Short(5)
    assert ResultCode(int(result_code)) == ResultCode.OK
    assert result == "7"


@pytest.mark.forked
def test_non_abort(
    device_under_test: tango.DeviceProxy,
    change_event_callbacks: MockTangoEventCallbackGroup,
) -> None:
    """
    Test non abort.

    :param device_under_test: a proxy to the device under test
    :param change_event_callbacks: dictionary of mock change event
        callbacks with asynchrony support
    """
    device_under_test.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    change_event_callbacks.assert_change_event("longRunningCommandResult", ("", ""))

    # NonAbortingLongRunning
    result_code, command_id = device_under_test.NonAbortingLongRunning(0.1)
    assert ResultCode(int(result_code)) == ResultCode.QUEUED
    assert command_id.endswith("NonAbortingLongRunning")

    next_result = change_event_callbacks.assert_against_call("longRunningCommandResult")
    command_id, message = next_result["attribute_value"]
    assert command_id.endswith("NonAbortingLongRunning")
    assert message == '"non_aborting_lrc OK"'


@pytest.mark.forked
def test_abort(
    device_under_test: tango.DeviceProxy,
    change_event_callbacks: MockTangoEventCallbackGroup,
) -> None:
    """
    Test abort.

    :param device_under_test: a proxy to the device under test
    :param change_event_callbacks: dictionary of mock change event
        callbacks with asynchrony support
    """
    device_under_test.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    change_event_callbacks.assert_change_event("longRunningCommandResult", ("", ""))

    # AbortingLongRunning
    result_code, command_id = device_under_test.AbortingLongRunning(0.1)
    assert ResultCode(int(result_code)) == ResultCode.QUEUED
    assert command_id.endswith("AbortingLongRunning")

    device_under_test.AbortCommands()

    next_result = change_event_callbacks.assert_against_call("longRunningCommandResult")
    command_id, message = next_result["attribute_value"]
    assert command_id.endswith("AbortingLongRunning")
    assert message == '"AbortingTask Aborted 0.1"'


@pytest.mark.forked
def test_exception(
    device_under_test: tango.DeviceProxy,
    change_event_callbacks: MockTangoEventCallbackGroup,
) -> None:
    """
    Test exception.

    :param device_under_test: a proxy to the device under test
    :param change_event_callbacks: dictionary of mock change event
        callbacks with asynchrony support
    """
    device_under_test.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandResult"],
    )
    change_event_callbacks.assert_change_event("longRunningCommandResult", ("", ""))

    # LongRunningException
    result_code, command_id = device_under_test.LongRunningException()
    assert ResultCode(int(result_code)) == ResultCode.QUEUED
    assert command_id.endswith("LongRunningException")

    next_result = change_event_callbacks.assert_against_call("longRunningCommandResult")
    command_id, message = next_result["attribute_value"]
    assert command_id.endswith("LongRunningException")
    assert message == "Something went wrong"


@pytest.mark.forked
def test_progress(
    device_under_test: tango.DeviceProxy,
    change_event_callbacks: MockTangoEventCallbackGroup,
) -> None:
    """
    Test progress.

    :param device_under_test: a proxy to the device under test
    :param change_event_callbacks: dictionary of mock change event
        callbacks with asynchrony support
    """
    device_under_test.subscribe_event(
        "longRunningCommandProgress",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandProgress"],
    )
    change_event_callbacks.assert_change_event("longRunningCommandProgress", None)

    # Progress
    result_code, command_id = device_under_test.TestProgress(0.3)
    assert ResultCode(int(result_code)) == ResultCode.QUEUED
    assert command_id.endswith("TestProgress")

    for i in [1, 25, 50, 74, 100]:
        next_event = change_event_callbacks.assert_against_call(
            "longRunningCommandProgress"
        )
        progresses = list(next_event["attribute_value"])
        assert command_id in progresses
        assert progresses[progresses.index(command_id) + 1] == f"{i}"


@pytest.mark.forked
def test_device_allows_commands_to_be_queued(
    device_under_test: tango.DeviceProxy,
    change_event_callbacks: MockTangoEventCallbackGroup,
) -> None:
    """
    Test input queue accepts multiple commands.

    This test also checks that each command is checked
    against its is_cmd_allowed method before executing it

    :param device_under_test: a proxy to the device under test
    :param change_event_callbacks: dictionary of mock change event
        callbacks with asynchrony support
    """
    device_under_test.subscribe_event(
        "longRunningCommandStatus",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["longRunningCommandStatus"],
    )
    change_event_callbacks.assert_change_event("longRunningCommandStatus", None)

    # Command triggers: Transpose > Invert > Invert
    # The device will queue all these commands and 
    # inform later that 2nd Invert failed

    # check that all commands were queued
    command_ids = []
    for cmd in ("Transpose", "Invert", "Invert"):
        result_code, cmd_id = device_under_test.command_inout(cmd)
        command_ids.append(cmd_id)
        assert ResultCode(int(result_code)) == ResultCode.QUEUED

    # check that only the last command invokation failed
    # pylint: disable=unbalanced-tuple-unpacking
    transpose_id, invert_id1, invert_id2 = command_ids
    status_event = (
        transpose_id,
        "COMPLETED",
        invert_id1,
        "COMPLETED",
        invert_id2,
        "FAILED",
    )
    event_count = 6
    for _ in range(event_count):
        next_event = change_event_callbacks.assert_against_call(
            "longRunningCommandStatus"
        )
    status = next_event["attribute_value"]
    assert status == status_event
