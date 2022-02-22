"""Test various Tango devices with long running commmands working together."""
import pytest
from tango import EventType
from tango.test_context import DeviceTestContext

from ska_tango_base.commands import ResultCode

from .multidevice import ExampleMultiDevice
from .utils import LRCAttributesStore

# Testing a chain of calls
# On command `CallChildren`
#   If the device has children:
#       Call `CallChildren` on each child
#   If no children:
#       Sleep the time specified, simulating blocking work
#
# test/toplevel/1
#   test/midlevel/1
#       test/lowlevel/1
#       test/lowlevel/2
#   test/midlevel/2
#       test/lowlevel/3
#       test/lowlevel/4
#   test/midlevel/3
#       test/lowlevel/5
#       test/lowlevel/6


devices_to_test = [
    {
        "class": ExampleMultiDevice,
        "devices": [
            {
                "name": "test/toplevel/1",
                "properties": {
                    "client_devices": [
                        "test/midlevel/1",
                        "test/midlevel/2",
                        "test/midlevel/3",
                    ],
                },
            },
            {
                "name": "test/midlevel/1",
                "properties": {
                    "client_devices": [
                        "test/lowlevel/1",
                        "test/lowlevel/2",
                    ],
                },
            },
            {
                "name": "test/midlevel/2",
                "properties": {
                    "client_devices": [
                        "test/lowlevel/3",
                        "test/lowlevel/4",
                    ],
                },
            },
            {
                "name": "test/midlevel/3",
                "properties": {
                    "client_devices": [
                        "test/lowlevel/5",
                        "test/lowlevel/6",
                    ],
                },
            },
            {"name": "test/lowlevel/1"},
            {"name": "test/lowlevel/2"},
            {"name": "test/lowlevel/3"},
            {"name": "test/lowlevel/4"},
            {"name": "test/lowlevel/5"},
            {"name": "test/lowlevel/6"},
        ],
    },
]


@pytest.mark.forked
def test_device():
    """Test our Multidevice."""
    with DeviceTestContext(ExampleMultiDevice, process=True) as top_device:

        top_device_event_store = LRCAttributesStore()
        top_device.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            top_device_event_store,
            wait=True,
        )

        top_device.subscribe_event(
            "longRunningCommandProgress",
            EventType.CHANGE_EVENT,
            top_device_event_store,
            wait=True,
        )

        # Get the empty initial value
        top_device_event_store.get_attribute_value("longRunningCommandResult")

        # Short
        result_code, result = top_device.Short(5)
        assert ResultCode(int(result_code)) == ResultCode.OK
        assert result == "7"

        # NonAbortingLongRunning
        result_code, command_id = top_device.NonAbortingLongRunning(0.1)
        assert ResultCode(int(result_code)) == ResultCode.QUEUED
        assert command_id.endswith("NonAbortingLongRunning")

        next_result = top_device_event_store.get_attribute_value(
            "longRunningCommandResult", fetch_timeout=10
        )
        assert next_result[0].endswith("NonAbortingLongRunning")
        assert next_result[1] == '"non_aborting_lrc OK"'

        # AbortingLongRunning
        result_code, command_id = top_device.AbortingLongRunning(0.1)
        assert ResultCode(int(result_code)) == ResultCode.QUEUED
        assert command_id.endswith("AbortingLongRunning")

        top_device.AbortCommands()

        next_result = top_device_event_store.get_attribute_value(
            "longRunningCommandResult", fetch_timeout=10
        )
        assert next_result[0].endswith("AbortingLongRunning")
        assert next_result[1] == '"AbortingTask Aborted 0.1"'

        # LongRunningException
        result_code, command_id = top_device.LongRunningException()
        assert ResultCode(int(result_code)) == ResultCode.QUEUED
        assert command_id.endswith("LongRunningException")

        next_result = top_device_event_store.get_attribute_value(
            "longRunningCommandResult", fetch_timeout=10
        )
        assert next_result[0].endswith("LongRunningException")
        assert next_result[1] == '"Something went wrong"'


@pytest.mark.forked
def test_progress():
    """Test the progress."""
    with DeviceTestContext(ExampleMultiDevice, process=True) as top_device:

        top_device_event_store = LRCAttributesStore()

        top_device.subscribe_event(
            "longRunningCommandProgress",
            EventType.CHANGE_EVENT,
            top_device_event_store,
            wait=True,
        )

        # Progress
        result_code, command_id = top_device.TestProgress(0.3)
        assert ResultCode(int(result_code)) == ResultCode.QUEUED
        assert command_id.endswith("TestProgress")

        for i in [1, 25, 50, 74, 100]:
            next_result = list(
                top_device_event_store.get_attribute_value(
                    "longRunningCommandProgress", fetch_timeout=10
                )
            )
            assert command_id in next_result
            assert next_result[next_result.index(command_id) + 1] == f"{i}"


@pytest.mark.forked
def test_multi_layer(multi_device_tango_context):
    """Test the long running commands between devices."""
    top_device = multi_device_tango_context.get_device("test/toplevel/1")
    mid_device = multi_device_tango_context.get_device("test/midlevel/3")
    low_device = multi_device_tango_context.get_device("test/lowlevel/6")

    top_device_event_store = LRCAttributesStore()
    top_device.subscribe_event(
        "longRunningCommandResult",
        EventType.CHANGE_EVENT,
        top_device_event_store,
        wait=True,
    )

    mid_device_event_store = LRCAttributesStore()
    mid_device.subscribe_event(
        "longRunningCommandResult",
        EventType.CHANGE_EVENT,
        mid_device_event_store,
        wait=True,
    )

    low_device_event_store = LRCAttributesStore()
    low_device.subscribe_event(
        "longRunningCommandResult",
        EventType.CHANGE_EVENT,
        low_device_event_store,
        wait=True,
    )

    # remove initial empty values
    low_device_event_store.get_attribute_value("longRunningCommandResult")
    mid_device_event_store.get_attribute_value("longRunningCommandResult")
    top_device_event_store.get_attribute_value("longRunningCommandResult")

    # Start toplevel
    top_device.CallChildren(2)

    # Make sure nobody finishes too quick
    assert top_device.longRunningCommandResult == ("", "")
    assert mid_device.longRunningCommandResult == ("", "")
    assert low_device.longRunningCommandResult == ("", "")

    # Wait for lowest level device to finish
    command_id, message = low_device_event_store.get_attribute_value(
        "longRunningCommandResult", fetch_timeout=10
    )
    assert command_id.endswith("CallChildren")
    assert message == '"Finished leaf node"'

    # Wait for mid level device to finish
    command_id, message = mid_device_event_store.get_attribute_value(
        "longRunningCommandResult", fetch_timeout=10
    )
    assert command_id.endswith("CallChildren")
    assert (
        message == "\"All children completed ['test/lowlevel/5', 'test/lowlevel/6']\""
    )

    # Wait for top level device to finish
    command_id, message = top_device_event_store.get_attribute_value(
        "longRunningCommandResult", fetch_timeout=10
    )
    assert command_id.endswith("CallChildren")
    assert (
        message
        == "\"All children completed ['test/midlevel/1', 'test/midlevel/2', 'test/midlevel/3']\""
    )
