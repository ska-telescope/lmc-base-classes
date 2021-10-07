"""Tests for the reference base device that uses queue manager."""

import pytest

from tango.test_context import DeviceTestContext
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
