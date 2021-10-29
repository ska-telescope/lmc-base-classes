"""Test various Tango devices with long running commmands working together."""
import time
import pytest

from io import StringIO
from unittest.mock import MagicMock

from tango.utils import EventCallback
from tango import EventType

from reference_base_device import AsyncBaseDevice
from ska_tango_base.base.task_queue_manager import TaskResult, TaskState
from ska_tango_base.commands import ResultCode
from ska_tango_base.utils import LongRunningDeviceInterface

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
        "class": AsyncBaseDevice,
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


class TestMultiDevice:
    """Multi-device tests."""

    @pytest.mark.forked
    @pytest.mark.timeout(6)
    def test_chain(self, multi_device_tango_context):
        """Test that commands flow from top to middle to low level."""
        # Top level
        top_device = multi_device_tango_context.get_device("test/toplevel/1")
        top_device_result_events = EventCallback(fd=StringIO())
        top_device.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            top_device_result_events,
            wait=True,
        )
        top_device_queue_events = EventCallback(fd=StringIO())
        top_device.subscribe_event(
            "longRunningCommandsInQueue",
            EventType.CHANGE_EVENT,
            top_device_queue_events,
            wait=True,
        )

        # Mid level
        mid_device = multi_device_tango_context.get_device("test/midlevel/3")
        mid_device_result_events = EventCallback(fd=StringIO())
        mid_device.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            mid_device_result_events,
            wait=True,
        )
        mid_device_queue_events = EventCallback(fd=StringIO())
        mid_device.subscribe_event(
            "longRunningCommandsInQueue",
            EventType.CHANGE_EVENT,
            mid_device_queue_events,
            wait=True,
        )

        # Low level
        low_device = multi_device_tango_context.get_device("test/lowlevel/6")
        low_device_result_events = EventCallback(fd=StringIO())
        low_device.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            low_device_result_events,
            wait=True,
        )
        low_device_queue_events = EventCallback(fd=StringIO())
        low_device.subscribe_event(
            "longRunningCommandsInQueue",
            EventType.CHANGE_EVENT,
            low_device_queue_events,
            wait=True,
        )

        # Call the toplevel command
        # Sleep for 4 so that if a task is not queued the Tango command will time out
        tr = TaskResult.from_response_command(top_device.CallChildren(4))
        assert tr.result_code == ResultCode.QUEUED

        # Get all the events
        top_result_events = self.get_events(top_device_result_events, 1)
        top_queue_events = self.get_events(top_device_queue_events, 1)
        mid_result_events = self.get_events(mid_device_result_events, 1)
        mid_queue_events = self.get_events(mid_device_queue_events, 1)
        low_result_events = self.get_events(low_device_result_events, 1)
        low_queue_events = self.get_events(low_device_queue_events, 1)

        # Make sure every level device command gets queued
        top_queue_events[0] == ("CallChildrenCommand",)
        mid_queue_events[0] == ("CallChildrenCommand",)
        low_queue_events[0] == ("CallChildrenCommand",)

        top_level_taskresult = TaskResult.from_task_result(top_result_events[0])
        mid_level_taskresult = TaskResult.from_task_result(mid_result_events[0])
        low_level_taskresult = TaskResult.from_task_result(low_result_events[0])

        # Make sure the command moved from top level to lowest level
        assert (
            top_level_taskresult.task_result
            == "Called children: ['test/midlevel/1', 'test/midlevel/2', 'test/midlevel/3']"
        )
        assert (
            mid_level_taskresult.task_result
            == "Called children: ['test/lowlevel/5', 'test/lowlevel/6']"
        )
        assert low_level_taskresult.task_result == "Slept 4.0"

    @pytest.mark.forked
    @pytest.mark.timeout(8)
    def test_util_interface(self, multi_device_tango_context):
        """Test LongRunningDeviceInterface."""
        devices = []
        for i in range(1, 5):
            devices.append(f"test/lowlevel/{i}")

        mock_dunc = MagicMock()

        dev_interface = LongRunningDeviceInterface(devices, logger=None)
        dev_interface.execute_long_running_command(
            "CallChildren", 1.0, on_completion_callback=mock_dunc
        )
        time.sleep(2)
        assert mock_dunc.called
        assert mock_dunc.call_args[0][0] == "CallChildren"

        task_ids = mock_dunc.call_args[0][1]

        low_device = multi_device_tango_context.get_device("test/lowlevel/1")
        for id in task_ids:
            res = low_device.CheckLongRunningCommandStatus(id)
            if int(res[1][0]) == TaskState.COMPLETED:
                break
        else:
            assert 0, "At least one task should be completed on device test/lowlevel/1"

    def get_events(self, event_callback: EventCallback, min_required: int):
        """Keep reading events until the required count is found."""
        events = []
        while len(events) < min_required:
            events = [
                i.attr_value.value
                for i in event_callback.get_events()
                if i.attr_value
                and i.attr_value.value
                and i.attr_value.value != ("", "", "")
            ]
            time.sleep(0.2)
        return events
