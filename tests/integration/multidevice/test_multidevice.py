# type: ignore
"""Test various Tango devices with long running commmands working together."""
import pytest
import tango
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup

from ska_tango_base.commands import ResultCode

from .multidevice import ExampleMultiDevice


@pytest.fixture(scope="function")
def device_test_config(device_properties):
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


@pytest.fixture()
def change_event_callbacks() -> MockTangoEventCallbackGroup:
    """
    Return a dictionary of Tango device change event callbacks with asynchrony support.

    :return: a collections.defaultdict that returns change event
        callbacks by name.
    """
    return MockTangoEventCallbackGroup(
        "longRunningCommandProgress",
        "longRunningCommandResult",
        timeout=5.0,
    )


@pytest.mark.forked
def test_device_init(device_under_test):
    """
    Test device initialisation.

    :param device_under_test: a proxy to the device under test
    """
    state = device_under_test.State()
    assert state == tango.DevState.DISABLE


@pytest.mark.forked
def test_device(device_under_test, change_event_callbacks):
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
def test_non_abort(device_under_test, change_event_callbacks):
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
def test_abort(device_under_test, change_event_callbacks):
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
def test_exception(device_under_test, change_event_callbacks):
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
def test_progress(device_under_test, change_event_callbacks):
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
