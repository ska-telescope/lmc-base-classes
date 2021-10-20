"""Tests for the reference base device that uses queue manager."""

from io import StringIO

import pytest
import time

from unittest import mock
from tango import EventType
from tango.test_context import DeviceTestContext
from tango.utils import EventCallback
from reference_base_device import (
    BlockingBaseDevice,
    AsyncBaseDevice,
    AsyncClientDevice,
)
from ska_tango_base.base.task_queue_manager import TaskResult
from ska_tango_base.commands import ResultCode


class TestCommands:
    """Check that blocking and async commands behave the same way.

    BlockingBaseDevice - QueueManager has no threads and blocks tasks
    AsyncBaseDevice - QueueManager has multiple threads, tasks run from queue
    """

    @pytest.mark.forked
    @pytest.mark.timeout(5)
    def test_short_command(self):
        """Test a simple command."""
        for class_name in [BlockingBaseDevice, AsyncBaseDevice]:
            with DeviceTestContext(class_name, process=True) as proxy:
                proxy.Short(1)
                # Wait for a result, if the task does not abort, we'll time out here
                while not proxy.longRunningCommandResult:
                    time.sleep(0.1)

                result = TaskResult.from_task_result(proxy.longRunningCommandResult)
                assert result.result_code == ResultCode.OK
                assert result.get_task_unique_id().id_task_name == "ShortCommand"

    @pytest.mark.forked
    @pytest.mark.timeout(5)
    def test_non_aborting_command(self):
        """Test tasks that does not abort."""
        for class_name in [BlockingBaseDevice, AsyncBaseDevice]:
            with DeviceTestContext(class_name, process=True) as proxy:
                proxy.NonAbortingLongRunning(0.01)
                # Wait for a result, if the task does not abort, we'll time out here
                while not proxy.longRunningCommandResult:
                    time.sleep(0.1)
                result = TaskResult.from_task_result(proxy.longRunningCommandResult)
                assert result.result_code == ResultCode.OK
                assert (
                    result.get_task_unique_id().id_task_name
                    == "NonAbortingLongRunningCommand"
                )

    @pytest.mark.forked
    @pytest.mark.timeout(5)
    def test_aborting_command(self):
        """Test Abort.

        BlockingBaseDevice will block on `AbortingLongRunning` so calling
        AbortCommands after that makes no sense.
        """
        with DeviceTestContext(AsyncBaseDevice, process=True) as proxy:
            unique_id, _ = proxy.AbortingLongRunning(0.5)
            # Wait for the task to be in progress
            while not proxy.longRunningCommandStatus:
                time.sleep(0.1)
            # Abort the tasks
            proxy.AbortCommands()
            # Wait for a result, if the task does not abort, we'll time out here
            while not proxy.longRunningCommandResult:
                time.sleep(0.1)
            result = TaskResult.from_task_result(proxy.longRunningCommandResult)
            assert result.unique_id == unique_id
            assert result.result_code == ResultCode.ABORTED
            assert "Aborted" in result.task_result

    @pytest.mark.forked
    @pytest.mark.timeout(5)
    def test_exception_command(self):
        """Test the task that throws an error."""
        for class_name in [BlockingBaseDevice, AsyncBaseDevice]:
            with DeviceTestContext(class_name, process=True) as proxy:
                unique_id, _ = proxy.LongRunningException()
                while not proxy.longRunningCommandResult:
                    time.sleep(0.1)
                result = TaskResult.from_task_result(proxy.longRunningCommandResult)
                assert result.unique_id == unique_id
                assert result.result_code == ResultCode.FAILED
                assert (
                    "An error occurred Traceback (most recent call last)"
                    in result.task_result
                )


@pytest.mark.forked
def test_callbacks():
    """Check that the callback is firing that sends the push change event."""
    with mock.patch.object(AsyncBaseDevice, "push_change_event") as my_cb:
        with DeviceTestContext(AsyncBaseDevice, process=False) as proxy:
            # Execute some commands
            proxy.TestProgress(0.5)
            while not proxy.longRunningCommandResult:
                time.sleep(0.1)
            assert my_cb.called

            called_args = [
                (_call[0][0], _call[0][1]) for _call in my_cb.call_args_list[5:]
            ]

            attribute_names = [arg[0] for arg in called_args]
            assert attribute_names == [
                "longRunningCommandsInQueue",
                "longRunningCommandIDsInQueue",
                "longRunningCommandsInQueue",
                "longRunningCommandIDsInQueue",
                "longRunningCommandStatus",
                "longRunningCommandProgress",
                "longRunningCommandProgress",
                "longRunningCommandProgress",
                "longRunningCommandProgress",
                "longRunningCommandProgress",
                "longRunningCommandResult",
            ]

            # longRunningCommandsInQueue
            attribute_values = [arg[1] for arg in called_args]
            assert len(attribute_values[0]) == 1
            assert attribute_values[0] == ("TestProgressCommand",)

            # longRunningCommandIDsInQueue
            assert len(attribute_values[1]) == 1
            assert attribute_values[1][0].endswith("TestProgressCommand")

            # longRunningCommandsInQueue
            assert not attribute_values[2]

            # longRunningCommandIDsInQueue
            assert not attribute_values[3]

            # longRunningCommandStatus
            assert len(attribute_values[4]) == 2
            assert attribute_values[4][0].endswith("TestProgressCommand")
            assert attribute_values[4][1] == "IN_PROGRESS"

            # longRunningCommandProgress
            for (index, progress) in zip(range(5, 9), ["1", "25", "50", "74", "100"]):
                assert len(attribute_values[index]) == 2
                assert attribute_values[index][0].endswith("TestProgressCommand")
                assert attribute_values[index][1] == progress

            # longRunningCommandResult
            assert len(attribute_values[10]) == 3
            tr = TaskResult.from_task_result(attribute_values[10])
            assert tr.get_task_unique_id().id_task_name == "TestProgressCommand"
            assert tr.result_code == ResultCode.OK
            assert tr.task_result == "OK"


@pytest.mark.forked
@pytest.mark.timeout(10)
def test_events():
    """Testing the events.

    NOTE: Adding more than 1 event subscriptions leads to inconsistent results.
          Sometimes misses events.

          Full callback tests (where the push events are triggered) are covered
          in `test_callbacks`
    """
    with DeviceTestContext(AsyncBaseDevice, process=True) as proxy:
        progress_events = EventCallback(fd=StringIO())

        proxy.subscribe_event(
            "longRunningCommandProgress",
            EventType.CHANGE_EVENT,
            progress_events,
            wait=True,
        )

        proxy.TestProgress(0.2)

        # Wait for task to finish
        while not proxy.longRunningCommandResult:
            time.sleep(0.1)

        # Wait for progress events
        while not progress_events.get_events():
            time.sleep(0.5)

        progress_event_values = [
            event.attr_value.value
            for event in progress_events.get_events()
            if event.attr_value and event.attr_value.value
        ]
        for index, progress in enumerate(["1", "25", "50", "74", "100"]):
            assert progress_event_values[index][1] == progress


devices_to_test = [
    {
        "class": AsyncBaseDevice,
        "devices": [
            {"name": "test/asyncdevice/1"},
            {"name": "test/asyncdevice/2"},
        ],
    },
    {
        "class": AsyncClientDevice,
        "devices": [
            {
                "name": "test/asyncclientdevice/1",
                "properties": {
                    "client_devices": [
                        "test/asyncdevice/1",
                    ],
                },
            },
            {
                "name": "test/asyncclientdevice/2",
                "properties": {
                    "client_devices": [
                        "test/asyncdevice/1",
                        "test/asyncdevice/2",
                    ],
                },
            },
        ],
    },
]


@pytest.mark.skip(
    "These tests should be made more robust. Getting inconsistent results"
)
class TestMultiDevice:
    """Multi-device tests."""

    # TODO track events from underlying device(s) instead

    @pytest.mark.forked
    def test_two_async_devices_communicating(self, multi_device_tango_context):
        """Test only two devices communication."""
        client = multi_device_tango_context.get_device("test/asyncclientdevice/1")

        commands_in_queue_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "longRunningCommandsInQueue",
            EventType.CHANGE_EVENT,
            commands_in_queue_events,
            wait=True,
        )

        command_ids_in_queue_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "longRunningCommandIDsInQueue",
            EventType.CHANGE_EVENT,
            command_ids_in_queue_events,
            wait=True,
        )

        client.TestProgressNoArgs()
        client.ping()
        time.sleep(2)

        commands_in_queue = [
            i.attr_value.value[0]
            for i in commands_in_queue_events.get_events()
            if i.attr_value.value
        ]
        # though two commands were triggered, only one is registered in the
        # event callback since ping is not registered as a long running command
        assert commands_in_queue == ["TestProgressNoArgsCommand"]

        command_ids_in_queue = [
            i.attr_value.value
            for i in command_ids_in_queue_events.get_events()
            if i.attr_value.value
        ]
        # there should be 1 ID since 1 command was triggered
        assert len(command_ids_in_queue) == 1

    @pytest.mark.forked
    def test_multiple_async_devices_communicating(self, multi_device_tango_context):
        """Test multiple devices."""
        client = multi_device_tango_context.get_device("test/asyncclientdevice/2")

        commands_in_queue_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "longRunningCommandsInQueue",
            EventType.CHANGE_EVENT,
            commands_in_queue_events,
            wait=True,
        )

        command_ids_in_queue_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "longRunningCommandIDsInQueue",
            EventType.CHANGE_EVENT,
            command_ids_in_queue_events,
            wait=True,
        )

        client.TestProgressNoArgs()
        client.ping()
        client.TestProgressWithArgs(0.5)
        time.sleep(3)

        commands_in_queue = [
            i.attr_value.value[0]
            for i in commands_in_queue_events.get_events()
            if i.attr_value.value
        ]
        assert commands_in_queue == [
            "TestProgressNoArgsCommand",
            "TestProgressWithArgsCommand",
        ]

        commands_ids_in_queue = [
            i.attr_value.value
            for i in command_ids_in_queue_events.get_events()
            if i.attr_value.value
        ]
        # should be checking for 4 since each comand triggers
        # two devices under the hood, see TODO in class
        assert len(commands_ids_in_queue) == 2

    @pytest.mark.forked
    def test_multiple_async_devices_communicating_with_duplicate_commands(
        self, multi_device_tango_context
    ):
        """Test multiple devices with duplicate commands."""
        client = multi_device_tango_context.get_device("test/asyncclientdevice/2")

        commands_in_queue_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "longRunningCommandsInQueue",
            EventType.CHANGE_EVENT,
            commands_in_queue_events,
            wait=True,
        )

        command_ids_in_queue_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "longRunningCommandIDsInQueue",
            EventType.CHANGE_EVENT,
            command_ids_in_queue_events,
            wait=True,
        )

        client.TestProgressNoArgs()
        client.TestProgressNoArgs()
        client.TestProgressNoArgs()
        client.TestProgressWithArgs(0.5)
        time.sleep(3)

        commands_in_queue = [
            i.attr_value.value
            for i in commands_in_queue_events.get_events()
            if i.attr_value.value
        ]
        assert commands_in_queue == [
            ("TestProgressNoArgsCommand",),
            ("TestProgressNoArgsCommand",),
            ("TestProgressNoArgsCommand",),
            ("TestProgressWithArgsCommand",),
        ]

        commands_ids_in_queue = [
            i.attr_value.value
            for i in command_ids_in_queue_events.get_events()
            if i.attr_value.value
        ]
        # should be checking for 8 since each comand triggers
        # two devices under the hood, see TODO in class
        assert len(commands_ids_in_queue) == 4
