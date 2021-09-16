import logging
import time
import pytest
from functools import partial
from unittest.mock import patch

from ska_tango_base.commands import ResultCode
from ska_tango_base.base.task_queue_component_manager import QueueManager

logger = logging.getLogger(__name__)

@pytest.mark.timeout(5)
class TestQueueManager:
    """General QueueManager checks"""

    def test_threads_start(self):
        qm = QueueManager(logger, num_workers=2)
        assert len(qm._threads) == 2
        for worker in qm._threads:
            assert worker.is_alive()
            assert worker.daemon

        for worker in qm._threads:
            worker._is_stopping.set()

    def test_qm_del(self):
        qm = QueueManager(logger, num_workers=2)
        assert len(qm._threads) == 2
        for worker in qm._threads:
            assert worker.is_alive()
            assert worker.daemon
        del qm


def add_five(num: int) -> int:
    """Add 5 to number passed in

    :param num: Number to add 5 to
    :type num: int
    """
    return 5 + num


def add_ten(num: int) -> int:
    """Add 10 to number passed in

    :param num: Number to add 5 to
    :type num: int
    """
    return 10 + num


def slow_function(num: float):
    """Sleep num seconds

    :param num: seconds to sleep
    :type num: int
    """
    time.sleep(num)


def raise_an_exc():
    """Add 10 to number passed in

    :param num: Number to add 5 to
    :type num: int
    """
    raise Exception("An Error occured")

@pytest.mark.timeout(5)
class TestQueueManagerTasks:
    """QueueManager checks for tasks executed"""

    def test_task_ids(self):
        qm = QueueManager(logger, max_queue_size=5, num_workers=2)
        add_task_one = partial(add_five, 0)
        add_task_two = partial(add_five, 1)
        unique_id_one = qm.enqueue_command(add_task_one)
        unique_id_two = qm.enqueue_command(add_task_two)
        assert unique_id_one.endswith("add_five")
        assert unique_id_one != unique_id_two

    def test_task_is_executed(self):
        with patch.object(QueueManager, "result_callback") as my_cb:
            qm = QueueManager(logger, max_queue_size=5, num_workers=2)
            add_task_one = partial(add_five, 0)
            add_task_two = partial(add_ten, 1)
            unique_id_one = qm.enqueue_command(add_task_one)
            unique_id_two = qm.enqueue_command(add_task_two)

            while my_cb.call_count != 2:
                time.sleep(0.5)
            call_one = my_cb.call_args_list[0][0]
            call_two = my_cb.call_args_list[1][0]

            assert call_one[0].endswith("add_five")
            assert call_one[0] == unique_id_one
            assert call_two[0].endswith("add_ten")
            assert call_two[0] == unique_id_two

            assert call_one[1][0] == ResultCode.OK
            assert call_two[1][0] == ResultCode.OK

            assert call_one[1][1] == 5
            assert call_two[1][1] == 11

    def test_command_result(self):
        qm = QueueManager(logger, max_queue_size=5, num_workers=2)
        add_task_one = partial(add_five, 0)
        exc_task = partial(raise_an_exc)

        qm.enqueue_command(add_task_one)
        while qm.command_result == []:
            time.sleep(0.5)
        assert qm.command_result[0].endswith("add_five")
        assert int(qm.command_result[1]) == ResultCode.OK
        assert qm.command_result[2] == "5"

        qm.enqueue_command(exc_task)
        while qm.command_result[0].endswith("add_five"):
            time.sleep(0.5)
        assert qm.command_result[0].endswith("raise_an_exc")
        assert int(qm.command_result[1]) == ResultCode.FAILED
        assert qm.command_result[2].startswith(
            "Error: An Error occured Traceback (most"
        )

    def test_full_queue(self):
        with patch.object(QueueManager, "result_callback") as my_cb:
            qm = QueueManager(logger, max_queue_size=1, num_workers=1)
            for i in range(10):
                slow_task = partial(slow_function, 0.5)
                qm.enqueue_command(slow_task)

        while len(my_cb.call_args_list) != 10:
            time.sleep(0.5)
        results = [call_list[0][1][0] for call_list in my_cb.call_args_list]
        # 9/10 should be rejected since the first is busy and the queue length is 1
        assert results[-1] == ResultCode.OK
        for res in results[:-1]:
            res == ResultCode.REJECTED

        with patch.object(QueueManager, "result_callback") as my_cb:
            qm = QueueManager(logger, max_queue_size=2, num_workers=2)
            for i in range(10):
                slow_task = partial(slow_function, 0.5)
                qm.enqueue_command(slow_task)

        while len(my_cb.call_args_list) != 10:
            time.sleep(0.5)
        results = [call_list[0][1][0] for call_list in my_cb.call_args_list]
        # 8/10 should be rejected since two are taken to be processed.
        assert results[-1] == ResultCode.OK
        assert results[-2] == ResultCode.OK
        for res in results[:-2]:
            res == ResultCode.REJECTED
