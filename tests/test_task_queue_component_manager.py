"""Tests for QueueManager and its component manager."""
import functools
import logging
import time
import pytest
from functools import partial
from unittest.mock import MagicMock, patch

from ska_tango_base.commands import ResultCode
from ska_tango_base.base.task_queue_component_manager import (
    QueueManager,
    TaskResult,
    TaskQueueComponentManager,
)

logger = logging.getLogger(__name__)


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


def check_matching_pattern(list_to_check=()):
    """Check that lengths go 1,2,3,2,1 for example."""
    list_to_check = list(list_to_check)
    if not list_to_check[-1]:
        list_to_check.pop()
    assert len(list_to_check) > 2
    while len(list_to_check) > 2:
        last_e = list_to_check.pop()
        first_e = list_to_check.pop(0)
        assert len(last_e) == len(first_e)


class TestQueueManagerTasks:
    """QueueManager checks for tasks executed."""

    @pytest.mark.timeout(5)
    def test_task_ids(self):
        """Check ids."""
        qm = QueueManager(logger, max_queue_size=5, num_workers=2)
        add_task_one = partial(add_five, 0)
        add_task_two = partial(add_five, 1)
        unique_id_one = qm.enqueue_command(add_task_one)
        unique_id_two = qm.enqueue_command(add_task_two)
        assert unique_id_one.endswith("add_five")
        assert unique_id_one != unique_id_two

    @pytest.mark.timeout(5)
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

    @pytest.mark.timeout(5)
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

    @pytest.mark.timeout(5)
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

    @pytest.mark.timeout(5)
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

    @pytest.mark.timeout(5)
    def test_multi_jobs(self):
        """Test that multiple threads are working. Test that attribute updates fires."""
        num_of_workers = 3

        call_back_func = MagicMock()
        qm = QueueManager(
            logger,
            max_queue_size=5,
            num_workers=num_of_workers,
            on_property_update_callback=call_back_func,
        )
        unique_ids = []
        for _ in range(4):
            unique_id = qm.enqueue_command(functools.partial(slow_function, 2))
            unique_ids.append(unique_id)

        # Wait for a item on the queue
        while not qm.command_ids_in_queue:
            pass
        # Wait for commands to finish
        while qm.command_ids_in_queue:
            pass

        all_passed_params = [a_call[0] for a_call in call_back_func.call_args_list]
        commands_in_queue = [
            a_call[1]
            for a_call in all_passed_params
            if a_call[0] == "commands_in_queue"
        ]
        command_ids_in_queue = [
            a_call[1]
            for a_call in all_passed_params
            if a_call[0] == "command_ids_in_queue"
        ]
        command_status = [
            a_call[1] for a_call in all_passed_params if a_call[0] == "command_status"
        ]
        command_result = [
            a_call[1] for a_call in all_passed_params if a_call[0] == "command_result"
        ]
        command_result_ids = [res[0] for res in command_result]

        check_matching_pattern(tuple(commands_in_queue))
        check_matching_pattern(tuple(command_ids_in_queue))

        # Since there's 3 workers there should at least once be 3 in progress
        for status in command_status:
            if len(status) == num_of_workers:
                break
        else:
            assert 0, f"Length of {num_of_workers} in command_status not found"

        assert len(command_result) == 4
        for unique_id in unique_ids:
            assert unique_id in command_result_ids


class TestComponentManager:
    """Tests for the component manager."""

    def test_init(self):
        """Test that we can init the component manager."""
        qm = QueueManager(logger, max_queue_size=0, num_workers=1)
        cm = TaskQueueComponentManager(
            message_queue=qm, op_state_model=None, logger=logger
        )
        assert cm.message_queue.command_ids_in_queue == []
