"""Test various Tango devices with long running commmands working together."""
import pytest

from tango import EventType
from tango.test_context import DeviceTestContext

from .multidevice import LongRunningCommandBaseTestDevice
from .utils import LRCAttributesStore
from ska_tango_base.commands import ResultCode

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
        "class": LongRunningCommandBaseTestDevice,
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
    with DeviceTestContext(
        LongRunningCommandBaseTestDevice, process=True
    ) as top_device:

        top_device_attr_store = LRCAttributesStore()
        top_device.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            top_device_attr_store,
            wait=True,
        )

        top_device.subscribe_event(
            "longRunningCommandProgress",
            EventType.CHANGE_EVENT,
            top_device_attr_store,
            wait=True,
        )

        # Get the empty initial value
        top_device_attr_store.get_attribute_value("longRunningCommandResult")

        # Short
        result_code, result = top_device.Short(5)
        assert ResultCode(int(result_code)) == ResultCode.OK
        assert result == "7"

        # NonAbortingLongRunning
        result_code, command_id = top_device.NonAbortingLongRunning(0.1)
        assert ResultCode(int(result_code)) == ResultCode.QUEUED
        assert command_id.endswith("NonAbortingLongRunning")

        next_result = top_device_attr_store.get_attribute_value(
            "longRunningCommandResult", fetch_timeout=10
        )
        assert next_result[0].endswith("NonAbortingLongRunning")
        assert next_result[1] == '"non_aborting_lrc OK"'

        # AbortingLongRunning
        result_code, command_id = top_device.AbortingLongRunning(0.1)
        assert ResultCode(int(result_code)) == ResultCode.QUEUED
        assert command_id.endswith("AbortingLongRunning")

        top_device.AbortCommands()

        next_result = top_device_attr_store.get_attribute_value(
            "longRunningCommandResult", fetch_timeout=10
        )
        assert next_result[0].endswith("AbortingLongRunning")
        assert next_result[1] == '"NonAbortingTask Aborted 0.1"'

        # LongRunningException
        result_code, command_id = top_device.LongRunningException()
        assert ResultCode(int(result_code)) == ResultCode.QUEUED
        assert command_id.endswith("LongRunningException")

        next_result = top_device_attr_store.get_attribute_value(
            "longRunningCommandResult", fetch_timeout=10
        )
        assert next_result[0].endswith("LongRunningException")
        assert next_result[1] == '"Something went wrong"'

        # Progress
        result_code, command_id = top_device.TestProgress(0.1)
        assert ResultCode(int(result_code)) == ResultCode.QUEUED
        assert command_id.endswith("TestProgress")

        for i in [1, 25, 50, 74, 100]:
            next_result = list(
                top_device_attr_store.get_attribute_value(
                    "longRunningCommandProgress", fetch_timeout=10
                )
            )
            assert command_id in next_result
            assert next_result[next_result.index(command_id) + 1] == f"{i}"


@pytest.mark.skip("WIP")
@pytest.mark.forked
def test_multi_layer(multi_device_tango_context):
    """Test the long running commands between devices."""
    top_device = multi_device_tango_context.get_device("test/toplevel/1")
    top_device.CallChildren(0.5)

    lowest_device = multi_device_tango_context.get_device("test/lowlevel/6")

    low_device_attr_store = LRCAttributesStore()
    lowest_device.subscribe_event(
        "longRunningCommandResult",
        EventType.CHANGE_EVENT,
        low_device_attr_store,
        wait=True,
    )
