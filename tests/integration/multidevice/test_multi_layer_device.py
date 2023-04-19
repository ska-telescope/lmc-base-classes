"""Test various Tango devices with long running commmands working together."""

import pytest
import tango
import tango.test_context
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup

from ...conftest import DeviceSpecType
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


@pytest.fixture(name="devices_to_test", scope="module")
def devices_to_test_fixture() -> list[DeviceSpecType]:
    """
    Fixture for devices to test.

    :return: a list of specifications of devices to be included in the
        test context.
    """
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


@pytest.fixture(name="change_event_callbacks")
def change_event_callbacks_fixture() -> MockTangoEventCallbackGroup:
    """
    Return a dictionary of Tango device change event callbacks with asynchrony support.

    :return: a collections.defaultdict that returns change event
        callbacks by name.
    """
    return MockTangoEventCallbackGroup(
        "top_result",
        "mid_result",
        "low_result",
        timeout=5.0,
    )


@pytest.mark.forked
def test_multi_layer(
    multi_device_tango_context: tango.test_context.MultiDeviceTestContext,
    change_event_callbacks: MockTangoEventCallbackGroup,
) -> None:
    """
    Test the long running commands between devices.

    :param multi_device_tango_context: a lightweight Tango test context
        containing multiple devices
    :param change_event_callbacks: a group of callbacks with asynchrony
        support, for use in receiving Tango change events.
    """
    top_device = multi_device_tango_context.get_device("test/toplevel/1")
    mid_device = multi_device_tango_context.get_device("test/midlevel/3")
    low_device = multi_device_tango_context.get_device("test/lowlevel/6")

    top_device.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["top_result"],
    )

    mid_device.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["mid_result"],
    )

    low_device.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks["low_result"],
    )

    change_event_callbacks["top_result"].assert_change_event(("", ""))
    change_event_callbacks["mid_result"].assert_change_event(("", ""))
    change_event_callbacks["low_result"].assert_change_event(("", ""))

    top_device.CallChildren(2)

    low_result = change_event_callbacks.assert_against_call("low_result")
    command_id, message = low_result["attribute_value"]
    assert command_id.endswith("CallChildren")
    assert message == '"Finished leaf node"'

    # Wait for mid level device to finish
    mid_result = change_event_callbacks.assert_against_call("mid_result")
    command_id, message = mid_result["attribute_value"]
    assert command_id.endswith("CallChildren")
    assert (
        message == "\"All children completed ['test/lowlevel/5', 'test/lowlevel/6']\""
    )

    # Wait for top level device to finish
    top_result = change_event_callbacks.assert_against_call("top_result")
    command_id, message = top_result["attribute_value"]
    assert command_id.endswith("CallChildren")
    assert message == (
        "\"All children completed ['test/midlevel/1', 'test/midlevel/2', "
        "'test/midlevel/3']\""
    )
