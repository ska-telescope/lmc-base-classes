"""Tests for the reference base device that uses queue manager."""

from io import StringIO
import time
from unittest import mock
import pytest

from tango.test_context import DeviceTestContext
from tango.utils import EventCallback
from tango import EventType
from ska_tango_base.base.reference_base_device import (
    BlockingBaseDevice,
    AsyncBaseDevice,
)
from ska_tango_base.base.task_queue_manager import TaskResult
from ska_tango_base.commands import ResultCode


class TestCommands:
    """Check that blocking and async commands behave the same way.

    BlockingBaseDevice - QueueManager has no threads and blocks tasks
    AsyncBaseDevice - QueueManager has multiple threads, tasks run from queue
    """

    def test_short_command(self):
        """Test a simple command."""
        for class_name in [BlockingBaseDevice, AsyncBaseDevice]:
            with DeviceTestContext(class_name, process=True) as proxy:
                result = TaskResult.from_response_command(proxy.Short(1))
                assert result.result_code == ResultCode.OK
                assert result.unique_id.endswith("SimpleTask")

    def test_non_aborting_command(self):
        """Test tasks that does not abort."""
        for class_name in [BlockingBaseDevice, AsyncBaseDevice]:
            with DeviceTestContext(class_name, process=True) as proxy:
                result = TaskResult.from_response_command(
                    proxy.NonAbortingLongRunning(0.01)
                )
                assert result.result_code == ResultCode.OK
                assert result.unique_id.endswith("NonAbortingTask")

    @pytest.mark.timeout(5)
    def test_aborting_command(self):
        """Test Abort.

        BlockingBaseDevice will block on `AbortingLongRunning` so calling
        AbortCommands after that makes no sense.
        """
        with DeviceTestContext(AsyncBaseDevice, process=True) as proxy:
            _, unique_id = proxy.AbortingLongRunning(0.5)
            # Wait for the task to be in progress
            while not proxy.longRunningCommandStatus:
                pass
            # Abort the tasks
            proxy.AbortCommands()
            # Wait for a result, if the task does not abort, we'll time out here
            while not proxy.longRunningCommandResult:
                pass
            result = TaskResult.from_task_result(proxy.longRunningCommandResult)
            assert result.unique_id == unique_id
            assert result.result_code == ResultCode.ABORTED
            assert "Aborted" in result.task_result

    @pytest.mark.timeout(5)
    def test_exception_command(self):
        """Test the task that throws an error."""
        for class_name in [BlockingBaseDevice, AsyncBaseDevice]:
            with DeviceTestContext(class_name, process=True) as proxy:
                _, unique_id = proxy.LongRunningException()
                while not proxy.longRunningCommandResult:
                    pass
                result = TaskResult.from_task_result(proxy.longRunningCommandResult)
                assert result.unique_id == unique_id
                assert result.result_code == ResultCode.FAILED
                assert (
                    "An error occurred Traceback (most recent call last)"
                    in result.task_result
                )


def test_callbacks():
    """Check that the callback is firing that sends the push change event."""
    with mock.patch.object(AsyncBaseDevice, "_push_change_event_callback") as my_cb:
        with DeviceTestContext(AsyncBaseDevice, process=False) as proxy:
            # Execute some commands
            proxy.TestProgress(0.5)
            while not proxy.longRunningCommandResult:
                time.sleep(0.1)
            assert my_cb.called
            called_args = [(_call[0][0], _call[0][1]) for _call in my_cb.call_args_list]

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
            assert attribute_values[0] == ["ProgressTask"]

            # longRunningCommandIDsInQueue
            assert len(attribute_values[1]) == 1
            assert attribute_values[1][0].endswith("ProgressTask")

            # longRunningCommandsInQueue
            assert not attribute_values[2]

            # longRunningCommandIDsInQueue
            assert not attribute_values[3]

            # longRunningCommandStatus
            assert len(attribute_values[4]) == 2
            assert attribute_values[4][0].endswith("ProgressTask")
            assert attribute_values[4][1] == "IN_PROGRESS"

            # longRunningCommandProgress
            for (index, progress) in zip(range(5, 9), ["1", "25", "50", "74", "100"]):
                assert len(attribute_values[index]) == 2
                assert attribute_values[index][0].endswith("ProgressTask")
                assert attribute_values[index][1] == progress

            # longRunningCommandResult
            assert len(attribute_values[10]) == 3
            tr = TaskResult.from_task_result(attribute_values[10])
            tr.unique_id.endswith("ProgressTask")
            tr.result_code == ResultCode.OK
            tr.task_result == "None"


@pytest.mark.skip(
    "Run this test alone and it will pass. Run in this suite and it will Segfault"
)
def test_events():
    """Testing the events.

    NOTE: Adding more than 2 event subscriptions leads to inconsistent results.
          Sometimes misses events.

          Full callback tests (where the push events are triggered) are covered
          in `test_callbacks`
    """
    with DeviceTestContext(AsyncBaseDevice, process=True) as proxy:
        progress_events = EventCallback(fd=StringIO())
        ids_in_queue_events = EventCallback(fd=StringIO())

        progress_id = proxy.subscribe_event(
            "longRunningCommandProgress",
            EventType.CHANGE_EVENT,
            progress_events,
            wait=True,
        )
        ids_id = proxy.subscribe_event(
            "longRunningCommandIDsInQueue",
            EventType.CHANGE_EVENT,
            ids_in_queue_events,
            wait=True,
        )

        proxy.TestProgress(0.5)

        # Wait for task to finish
        while not proxy.longRunningCommandResult:
            time.sleep(0.1)

        progress_event_values = [
            event.attr_value.value
            for event in progress_events.get_events()
            if event.attr_value and event.attr_value.value
        ]
        for index, progress in enumerate(["1", "25", "50", "74", "100"]):
            assert progress_event_values[index][1] == progress

        ids_in_queue_events_values = [
            event.attr_value.value
            for event in ids_in_queue_events.get_events()
            if event.attr_value and event.attr_value.value
        ]
        assert len(ids_in_queue_events_values) == 1
        assert ids_in_queue_events_values[0][0].endswith("ProgressTask")
        proxy.unsubscribe_event(progress_id)
        proxy.unsubscribe_event(ids_id)
