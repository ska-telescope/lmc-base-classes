"""Test various Tango devices with long running commmands working together."""
import pytest

import tango
from ska_tango_base.commands import ResultCode

from .multidevice import ExampleMultiDevice


@pytest.fixture(scope="function")
def device_test_config(device_properties):
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
        "device": ExampleMultiDevice,
        "component_manager_patch": None,
        "properties": device_properties,
        "memorized": None,
    }


@pytest.mark.forked
def test_device_init(device_under_test):
    """Test device initialisation."""
    state = device_under_test.State()
    assert state == tango.DevState.DISABLE


@pytest.mark.forked
def test_device(device_under_test, tango_change_event_helper):
    """Test our Multidevice."""
    lrc_result_cb = tango_change_event_helper.subscribe("longRunningCommandResult")
    lrc_result_cb.get_next_change_event()

    # Short
    result_code, result = device_under_test.Short(5)
    assert ResultCode(int(result_code)) == ResultCode.OK
    assert result == "7"


@pytest.mark.forked
def test_non_abort(device_under_test, tango_change_event_helper):
    """Test non abort."""
    lrc_result_cb = tango_change_event_helper.subscribe("longRunningCommandResult")
    lrc_result_cb.get_next_change_event()

    # NonAbortingLongRunning
    result_code, command_id = device_under_test.NonAbortingLongRunning(0.1)
    assert ResultCode(int(result_code)) == ResultCode.QUEUED
    assert command_id.endswith("NonAbortingLongRunning")

    next_result = lrc_result_cb.get_next_change_event()
    assert next_result[0].endswith("NonAbortingLongRunning")
    assert next_result[1] == '"non_aborting_lrc OK"'


@pytest.mark.forked
def test_abort(device_under_test, tango_change_event_helper):
    """Test abort."""
    lrc_result_cb = tango_change_event_helper.subscribe("longRunningCommandResult")
    lrc_result_cb.get_next_change_event()

    # AbortingLongRunning
    result_code, command_id = device_under_test.AbortingLongRunning(0.1)
    assert ResultCode(int(result_code)) == ResultCode.QUEUED
    assert command_id.endswith("AbortingLongRunning")

    device_under_test.AbortCommands()

    next_result = lrc_result_cb.get_next_change_event()
    assert next_result[0].endswith("AbortingLongRunning")
    assert next_result[1] == '"AbortingTask Aborted 0.1"'


@pytest.mark.forked
def test_exception(device_under_test, tango_change_event_helper):
    """Test exception."""
    lrc_result_cb = tango_change_event_helper.subscribe("longRunningCommandResult")
    lrc_result_cb.get_next_change_event()

    # LongRunningException
    result_code, command_id = device_under_test.LongRunningException()
    assert ResultCode(int(result_code)) == ResultCode.QUEUED
    assert command_id.endswith("LongRunningException")

    next_result = lrc_result_cb.get_next_change_event()
    assert next_result[0].endswith("LongRunningException")
    assert next_result[1] == '"Something went wrong"'


@pytest.mark.forked
def test_progress(device_under_test, tango_change_event_helper):
    """Test progress."""
    lrc_progress_cb = tango_change_event_helper.subscribe("longRunningCommandProgress")
    lrc_progress_cb.get_next_change_event()

    # Progress
    result_code, command_id = device_under_test.TestProgress(0.3)
    assert ResultCode(int(result_code)) == ResultCode.QUEUED
    assert command_id.endswith("TestProgress")

    for i in [1, 25, 50, 74, 100]:
        next_result = list(lrc_progress_cb.get_next_change_event())
        assert command_id in next_result
        assert next_result[next_result.index(command_id) + 1] == f"{i}"
