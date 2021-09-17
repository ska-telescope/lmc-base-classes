"""Tests for QueueManager and its component manager."""
import logging
import time
import pytest
from functools import partial
from unittest.mock import patch

from ska_tango_base.commands import ResultCode
from ska_tango_base.base.task_queue_component_manager import QueueManager, TaskResult

logger = logging.getLogger(__name__)


@pytest.mark.timeout(5)
class TestQueueManager:
    """General QueueManager checks."""

    def test_threads_start(self):
        """Test that threads start up. Set stop and exit."""
        qm = QueueManager(logger, max_queue_size=2, num_workers=2)
        assert len(qm._threads) == 2
        for worker in qm._threads:
            assert worker.is_alive()
            assert worker.daemon

        for worker in qm._threads:
            worker.is_stopping.set()

    def test_qm_del(self):
        """Check delete."""
        qm = QueueManager(logger, max_queue_size=2, num_workers=2)
        assert len(qm._threads) == 2
        for worker in qm._threads:
            assert worker.is_alive()
            assert worker.daemon
        del qm


def add_five(num: int) -> int:
    """Add 5 to number passed in.

    :param num: Number to add 5 to
    :type num: int
    """
    return 5 + num


def add_ten(num: int) -> int:
    """Add 10 to number passed in.

    :param num: Number to add 5 to
    :type num: int
    """
    return 10 + num


def slow_function(num: float):
    """Sleep num seconds.

    :param num: seconds to sleep
    :type num: int
    """
    time.sleep(num)


def raise_an_exc():
    """Raise an Exception."""
    raise Exception("An Error occurred")


@pytest.mark.timeout(5)
class TestQueueManagerTasks:
    """QueueManager checks for tasks executed."""

    def test_task_ids(self):
        """Check ids."""
        qm = QueueManager(logger, max_queue_size=5, num_workers=2)
        add_task_one = partial(add_five, 0)
        add_task_two = partial(add_five, 1)
        unique_id_one = qm.enqueue_command(add_task_one)
        unique_id_two = qm.enqueue_command(add_task_two)
        assert unique_id_one.endswith("add_five")
        assert unique_id_one != unique_id_two

    def test_task_is_executed(self):
        """Check that tasks are executed."""
        with patch.object(QueueManager, "result_callback") as my_cb:
            qm = QueueManager(logger, max_queue_size=5, num_workers=2)
            add_task_one = partial(add_five, 0)
            add_task_two = partial(add_ten, 1)
            unique_id_one = qm.enqueue_command(add_task_one)
            unique_id_two = qm.enqueue_command(add_task_two)

            while my_cb.call_count != 2:
                time.sleep(0.5)
            result_one = my_cb.call_args_list[0][0][0]
            result_two = my_cb.call_args_list[1][0][0]

            assert result_one.unique_id.endswith("add_five")
            assert result_one.unique_id == unique_id_one
            assert result_two.unique_id.endswith("add_ten")
            assert result_two.unique_id == unique_id_two

            assert result_one.result_code == ResultCode.OK
            assert result_two.result_code == ResultCode.OK

            assert result_one.task_result == "5"
            assert result_two.task_result == "11"

    def test_command_result(self):
        """Check task results are what's expected."""
        qm = QueueManager(logger, max_queue_size=5, num_workers=2)
        add_task_one = partial(add_five, 0)
        exc_task = partial(raise_an_exc)

        qm.enqueue_command(add_task_one)
        while not qm.command_result:
            time.sleep(0.5)
        task_result = TaskResult.from_command_result(qm.command_result)
        assert task_result.unique_id.endswith("add_five")
        assert task_result.result_code == ResultCode.OK
        assert task_result.task_result == "5"

        qm.enqueue_command(exc_task)
        while qm.command_result[0].endswith("add_five"):
            time.sleep(0.5)
        task_result = TaskResult.from_command_result(qm.command_result)
        assert task_result.unique_id.endswith("raise_an_exc")
        assert task_result.result_code == ResultCode.FAILED
        assert task_result.task_result.startswith(
            "Error: An Error occurred Traceback (most"
        )

    def test_full_queue(self):
        """Check full queues rejects new commands."""
        with patch.object(QueueManager, "result_callback") as my_cb:
            qm = QueueManager(logger, max_queue_size=1, num_workers=1)
            for i in range(10):
                slow_task = partial(slow_function, 0.5)
                qm.enqueue_command(slow_task)

            while len(my_cb.call_args_list) != 10:
                time.sleep(0.5)

            results = [i[0][0].result_code for i in my_cb.call_args_list]
            # 9/10 should be rejected since the first is busy and the queue length is 1
            assert results[-1] == ResultCode.OK
            for res in results[:-1]:
                assert res == ResultCode.REJECTED

        with patch.object(QueueManager, "result_callback") as my_cb:
            qm = QueueManager(logger, max_queue_size=2, num_workers=2)
            for i in range(10):
                slow_task = partial(slow_function, 0.5)
                qm.enqueue_command(slow_task)

            while len(my_cb.call_args_list) != 10:
                time.sleep(0.5)
            results = [i[0][0].result_code for i in my_cb.call_args_list]
            # 8/10 should be rejected since two are taken to be processed.
            assert results[-1] == ResultCode.OK
            assert results[-2] == ResultCode.OK
            for res in results[:-2]:
                assert res == ResultCode.REJECTED

    def test_zero_queue(self):
        """Check command_result is the same between queue and non queue."""
        expected_name = "add_five"
        expected_result_code = ResultCode.OK
        expected_result = "6"

        # No Queue
        qm = QueueManager(logger, max_queue_size=0, num_workers=1)
        assert len(qm._threads) == 0
        add_task_one = partial(add_five, 1)
        res = qm.enqueue_command(add_task_one)
        assert res.endswith(expected_name)
        assert qm.command_result[0].endswith(expected_name)
        assert int(qm.command_result[1]) == expected_result_code
        assert qm.command_result[2] == expected_result

        # Queue
        qm = QueueManager(logger, max_queue_size=2, num_workers=1)
        add_task_one = partial(add_five, 1)
        res = qm.enqueue_command(add_task_one)
        assert res.endswith(expected_name)

        # Wait for the task to be picked up
        while not qm.command_result:
            time.sleep(0.5)
        assert qm.command_result[0].endswith(expected_name)
        assert int(qm.command_result[1]) == expected_result_code
        assert qm.command_result[2] == expected_result

    def test_currently_executing(self):
        """Check that currently executing and progress state is updated."""
        # Queue
        with patch.object(QueueManager, "update_command_state_callback") as my_cb:
            qm = QueueManager(logger, max_queue_size=1, num_workers=1)
            add_task_one = partial(add_five, 1)
            unique_id = qm.enqueue_command(add_task_one)
            while not qm.command_result:
                time.sleep(0.5)
            assert my_cb.call_count == 2
            assert my_cb.call_args_list[0][0][0] == unique_id
            assert my_cb.call_args_list[0][0][1] == "IN_PROGRESS"
            assert not my_cb.call_args_list[1][0][0]
            assert not my_cb.call_args_list[1][0][1]

        # No Queue
        with patch.object(QueueManager, "update_command_state_callback") as my_cb:
            qm = QueueManager(logger, max_queue_size=0, num_workers=1)
            add_task_one = partial(add_five, 1)
            unique_id = qm.enqueue_command(add_task_one)
            while not qm.command_result:
                time.sleep(0.5)
            assert my_cb.call_count == 2
            assert my_cb.call_args_list[0][0][0] == unique_id
            assert my_cb.call_args_list[0][0][1] == "IN_PROGRESS"
            assert not my_cb.call_args_list[1][0][0]
            assert not my_cb.call_args_list[1][0][1]
