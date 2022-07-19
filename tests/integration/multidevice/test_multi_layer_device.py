"""Test various Tango devices with long running commmands working together."""
import pytest

from .multidevice import ExampleMultiDevice

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


@pytest.fixture(scope="module")
def devices_to_test(request):
    """Fixture for devices to test."""
    return [
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
def test_multi_layer(
    multi_device_tango_context, multi_tango_change_event_helper
):
    """Test the long running commands between devices."""
    top_device = multi_device_tango_context.get_device("test/toplevel/1")

    top_device_lrc_result_cb = multi_tango_change_event_helper.subscribe(
        "test/toplevel/1", "longRunningCommandResult"
    )
    mid_device_lrc_result_cb = multi_tango_change_event_helper.subscribe(
        "test/midlevel/3", "longRunningCommandResult"
    )
    low_device_lrc_result_cb = multi_tango_change_event_helper.subscribe(
        "test/lowlevel/6", "longRunningCommandResult"
    )

    top_device_lrc_result_cb.get_next_change_event()
    mid_device_lrc_result_cb.get_next_change_event()
    low_device_lrc_result_cb.get_next_change_event()

    top_device.CallChildren(2)

    command_id, message = low_device_lrc_result_cb.get_next_change_event()
    assert command_id.endswith("CallChildren")
    assert message == '"Finished leaf node"'

    # Wait for mid level device to finish
    command_id, message = mid_device_lrc_result_cb.get_next_change_event()
    assert command_id.endswith("CallChildren")
    assert (
        message
        == "\"All children completed ['test/lowlevel/5', 'test/lowlevel/6']\""
    )

    # Wait for top level device to finish
    command_id, message = top_device_lrc_result_cb.get_next_change_event()
    assert command_id.endswith("CallChildren")
    assert (
        message
        == "\"All children completed ['test/midlevel/1', 'test/midlevel/2', 'test/midlevel/3']\""
    )
