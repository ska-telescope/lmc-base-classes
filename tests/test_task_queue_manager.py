"""Tests for QueueManager and its component manager."""
import logging
import time
import pytest
from unittest.mock import MagicMock, patch

from ska_tango_base.commands import ResultCode
from ska_tango_base.base.task_queue_manager import (
    QueueManager,
    TaskResult,
    QueueTask,
    TaskState,
)
from ska_tango_base.base.component_manager import BaseComponentManager

logger = logging.getLogger(__name__)


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


@pytest.fixture
def progress_task():
    """Fixture for a test that throws an exception."""

    def get_task():
        class ProgressTask(QueueTask):
            def do(self):
                for i in range(100):
                    self.update_progress(str(i))
                    time.sleep(0.5)

        return ProgressTask()

    return get_task


@pytest.fixture
def exc_task():
    """Fixture for a test that throws an exception."""

    def get_task():
        class ExcTask(QueueTask):
            def do(self):
                raise Exception("An error occurred")

        return ExcTask()

    return get_task


@pytest.fixture
def slow_task():
    """Fixture for a test that takes long."""

    def get_task():
        class SlowTask(QueueTask):
            def do(self):
                time.sleep(2)

        return SlowTask()

    return get_task


@pytest.fixture
def simple_task():
    """Fixture for a very simple task."""

    def get_task():
        class SimpleTask(QueueTask):
            def do(self):
                num_one = self.args[0]
                num_two = self.kwargs.get("num_two")
                return num_one + num_two

        return SimpleTask(2, num_two=3)

    return get_task


@pytest.fixture
def abort_task():
    """Fixture for a task that aborts."""

    def get_task():
        class AbortTask(QueueTask):
            def do(self):
                sleep_time = self.args[0]
                while not self.aborting_event.is_set():
                    time.sleep(sleep_time)

        return AbortTask(0.2)

    return get_task


@pytest.fixture
def stop_task():
    """Fixture for a task that stops."""

    def get_task():
        class StopTask(QueueTask):
            def do(self):
                assert not self.stopping_event.is_set()
                while not self.stopping_event.is_set():
                    pass

        return StopTask()

    return get_task


class TestQueueTask:
    """Test QueueTask."""

    def test_simple(self, simple_task):
        """Test simple task."""
        assert simple_task().do() == 5

    def test_exception(self, exc_task):
        """Test that exception is thrown."""
        with pytest.raises(Exception):
            exc_task().do()


class TestQueueManager:
    """General QueueManager checks."""

    def test_threads_start(self):
        """Test that threads start up. Set stop and exit."""
        qm = QueueManager(max_queue_size=2, num_workers=2, logger=logger)
        assert len(qm._threads) == 2
        for worker in qm._threads:
            assert worker.is_alive()
            assert worker.daemon

        for worker in qm._threads:
            worker.stopping_event.set()


class TestQueueManagerTasks:
    """QueueManager checks for tasks executed."""

    @pytest.mark.timeout(5)
    def test_task_ids(self, simple_task):
        """Check ids."""
        qm = QueueManager(max_queue_size=5, num_workers=2, logger=logger)
        unique_id_one = qm.enqueue_task(simple_task())
        unique_id_two = qm.enqueue_task(simple_task())
        assert unique_id_one.endswith("SimpleTask")
        assert unique_id_one != unique_id_two

    @pytest.mark.timeout(5)
    def test_task_is_executed(self, simple_task):
        """Check that tasks are executed."""
        with patch.object(QueueManager, "result_callback") as my_cb:
            qm = QueueManager(max_queue_size=5, num_workers=2, logger=logger)
            unique_id_one = qm.enqueue_task(simple_task())
            unique_id_two = qm.enqueue_task(simple_task())

            while my_cb.call_count != 2:
                time.sleep(0.5)
            result_one = my_cb.call_args_list[0][0][0]
            result_two = my_cb.call_args_list[1][0][0]

            assert result_one.unique_id.endswith("SimpleTask")
            assert result_one.unique_id == unique_id_one
            assert result_two.unique_id.endswith("SimpleTask")
            assert result_two.unique_id == unique_id_two

            assert result_one.result_code == ResultCode.OK
            assert result_two.result_code == ResultCode.OK

            assert result_one.task_result == "5"
            assert result_two.task_result == "5"

    @pytest.mark.timeout(5)
    def test_task_result(self, simple_task, exc_task):
        """Check task results are what's expected."""
        qm = QueueManager(max_queue_size=5, num_workers=2, logger=logger)
        add_task_one = simple_task()
        exc_task = exc_task()

        qm.enqueue_task(add_task_one)
        while not qm.task_result:
            time.sleep(0.5)
        task_result = TaskResult.from_task_result(qm.task_result)
        assert task_result.unique_id.endswith("SimpleTask")
        assert task_result.result_code == ResultCode.OK
        assert task_result.task_result == "5"

        qm.enqueue_task(exc_task)
        while qm.task_result[0].endswith("SimpleTask"):
            time.sleep(0.5)
        task_result = TaskResult.from_task_result(qm.task_result)
        assert task_result.unique_id.endswith("ExcTask")
        assert task_result.result_code == ResultCode.FAILED
        assert task_result.task_result.startswith(
            "Error: An error occurred Traceback ("
        )

    @pytest.mark.timeout(10)
    def test_full_queue(self, slow_task):
        """Check full queues rejects new commands."""
        with patch.object(QueueManager, "result_callback") as my_cb:
            qm = QueueManager(max_queue_size=1, num_workers=1, logger=logger)
            for i in range(10):
                qm.enqueue_task(slow_task())

            while len(my_cb.call_args_list) != 10:
                time.sleep(0.5)

            results = [i[0][0].result_code for i in my_cb.call_args_list]
            # 9/10 should be rejected since the first is busy and the queue length is 1
            assert results[-1] == ResultCode.OK
            for res in results[:-1]:
                assert res == ResultCode.REJECTED

        with patch.object(QueueManager, "result_callback") as my_cb:
            qm = QueueManager(max_queue_size=2, num_workers=2, logger=logger)
            for i in range(10):
                qm.enqueue_task(slow_task())

            while len(my_cb.call_args_list) != 10:
                time.sleep(0.5)
            results = [i[0][0].result_code for i in my_cb.call_args_list]
            # 8/10 should be rejected since two are taken to be processed.
            assert results[-1] == ResultCode.OK
            assert results[-2] == ResultCode.OK
            for res in results[:-2]:
                assert res == ResultCode.REJECTED

    @pytest.mark.timeout(5)
    def test_zero_queue(self, simple_task):
        """Check task_result is the same between queue and non queue."""
        expected_name = "SimpleTask"
        expected_result_code = ResultCode.OK
        expected_result = "5"

        # No Queue
        qm = QueueManager(max_queue_size=0, num_workers=1, logger=logger)
        assert len(qm._threads) == 0
        res = qm.enqueue_task(simple_task())
        assert res.endswith(expected_name)
        assert qm.task_result[0].endswith(expected_name)
        assert int(qm.task_result[1]) == expected_result_code
        assert qm.task_result[2] == expected_result

        # Queue
        qm = QueueManager(max_queue_size=2, num_workers=1, logger=logger)
        res = qm.enqueue_task(simple_task())
        assert res.endswith(expected_name)

        # Wait for the task to be picked up
        while not qm.task_result:
            time.sleep(0.5)
        assert qm.task_result[0].endswith(expected_name)
        assert int(qm.task_result[1]) == expected_result_code
        assert qm.task_result[2] == expected_result

    @pytest.mark.timeout(5)
    def test_multi_jobs(self, slow_task):
        """Test that multiple threads are working. Test that attribute updates fires."""
        num_of_workers = 3

        call_back_func = MagicMock()
        qm = QueueManager(
            max_queue_size=5,
            num_workers=num_of_workers,
            on_property_update_callback=call_back_func,
            logger=logger,
        )
        unique_ids = []
        for _ in range(4):
            unique_id = qm.enqueue_task(slow_task())
            unique_ids.append(unique_id)

        # Wait for a item on the queue
        while not qm.task_ids_in_queue:
            pass

        while not qm.task_result:
            pass

        # Wait for last task to finish
        while unique_ids[-1] != TaskResult.from_task_result(qm.task_result).unique_id:
            pass

        all_passed_params = [a_call[0] for a_call in call_back_func.call_args_list]
        tasks_in_queue = [
            a_call[1] for a_call in all_passed_params if a_call[0] == "tasks_in_queue"
        ]
        task_ids_in_queue = [
            a_call[1]
            for a_call in all_passed_params
            if a_call[0] == "task_ids_in_queue"
        ]
        task_status = [
            a_call[1] for a_call in all_passed_params if a_call[0] == "task_status"
        ]
        task_result = [
            a_call[1] for a_call in all_passed_params if a_call[0] == "task_result"
        ]
        task_result_ids = [res[0] for res in task_result]

        check_matching_pattern(tuple(tasks_in_queue))
        check_matching_pattern(tuple(task_ids_in_queue))

        # Since there's 3 workers there should at least once be 3 in progress
        for status in task_status:
            if len(status) == num_of_workers:
                break
        else:
            assert 0, f"Length of {num_of_workers} in task_status not found"
        assert len(task_result) == 4
        for unique_id in unique_ids:
            assert unique_id in task_result_ids

    def test_task_progress(self, progress_task):
        """Test the progress updates."""
        qm = QueueManager(max_queue_size=8, num_workers=2, logger=logger)
        unique_id_one = qm.enqueue_task(progress_task())
        unique_id_two = qm.enqueue_task(progress_task())

        time.sleep(0.5)
        assert unique_id_one in qm.task_progress
        assert unique_id_two in qm.task_progress
        progress_one_before = qm.task_progress[unique_id_one]
        progress_two_before = qm.task_progress[unique_id_two]
        time.sleep(1.0)
        progress_one_after = qm.task_progress[unique_id_one]
        progress_two_after = qm.task_progress[unique_id_two]

        assert int(progress_one_after) > int(progress_one_before)
        assert int(progress_two_after) > int(progress_two_before)

    def test_task_get_state_completed(self, simple_task):
        """Test the QueueTask get state is completed."""
        qm = QueueManager(max_queue_size=8, num_workers=2, logger=logger)
        unique_id_one = qm.enqueue_task(simple_task())
        while not qm.task_result:
            pass
        assert qm.get_task_state(unique_id=unique_id_one) == TaskState.COMPLETED

    def test_task_get_state_in_queued(self, slow_task):
        """Test the QueueTask get state is queued."""
        qm = QueueManager(max_queue_size=8, num_workers=1, logger=logger)
        qm.enqueue_task(slow_task())
        qm.enqueue_task(slow_task())
        unique_id_last = qm.enqueue_task(slow_task())

        assert qm.get_task_state(unique_id=unique_id_last) == TaskState.QUEUED

    def test_task_get_state_in_progress(self, progress_task):
        """Test the QueueTask get state is in progress."""
        qm = QueueManager(max_queue_size=8, num_workers=2, logger=logger)
        unique_id_one = qm.enqueue_task(progress_task())
        while not qm.task_progress:
            pass

        assert qm.get_task_state(unique_id=unique_id_one) == TaskState.IN_PROGRESS

    def test_task_get_state_in_not_found(self):
        """Test the QueueTask get state not found."""
        qm = QueueManager(max_queue_size=8, num_workers=2, logger=logger)
        assert qm.get_task_state(unique_id="non_existing_id") == TaskState.NOT_FOUND


class TestQueueManagerExit:
    """Test the stopping and aborting."""

    @pytest.mark.timeout(15)
    def test_exit_abort(self, abort_task, slow_task):
        """Test aborting exit."""
        call_back_func = MagicMock()
        qm = QueueManager(
            max_queue_size=10,
            num_workers=2,
            on_property_update_callback=call_back_func,
            logger=logger,
        )
        cm = BaseComponentManager(op_state_model=None, queue_manager=qm, logger=None)

        cm.enqueue(abort_task())

        # Wait for the command to start
        while not qm.task_status:
            pass
        # Start aborting
        cm.queue_manager.abort_tasks()
        # Wait for the exit
        while not qm.task_result:
            pass
        # aborting state should be cleaned up since the queue is empty and
        # nothing is in progress
        while qm.is_aborting:
            pass

        # When aborting this should be rejected
        # Fill up the workers
        cm.enqueue(slow_task())
        cm.enqueue(slow_task())
        # Abort tasks
        cm.queue_manager.abort_tasks()

        # Load up some tasks that should be aborted
        cm.enqueue(slow_task())
        cm.enqueue(slow_task())
        unique_id = cm.enqueue(slow_task())

        while True:
            tr = TaskResult.from_task_result(qm.task_result)
            if tr.unique_id == unique_id and tr.result_code == ResultCode.ABORTED:
                break

        # Resume the commands
        qm.resume_tasks()
        assert not qm.is_aborting

        # Wait for my slow command to finish
        unique_id = cm.enqueue(slow_task())
        while True:
            tr = TaskResult.from_task_result(qm.task_result)
            if tr.unique_id == unique_id:
                break

    @pytest.mark.timeout(10)
    def test_exit_stop(self, stop_task):
        """Test stopping exit."""
        call_back_func = MagicMock()
        qm = QueueManager(
            max_queue_size=5,
            num_workers=2,
            on_property_update_callback=call_back_func,
            logger=logger,
        )
        cm = BaseComponentManager(op_state_model=None, queue_manager=qm, logger=None)
        cm.enqueue(stop_task())

        # Wait for the command to start
        while not qm.task_status:
            pass
        # Stop all threads
        cm.queue_manager.stop_tasks()
        # Wait for the exit
        while not qm.task_result:
            pass
        # Wait for all the workers to stop
        while not any([worker.is_alive() for worker in qm._threads]):
            pass

    @pytest.mark.timeout(5)
    def test_delete_queue(self, slow_task, stop_task, abort_task):
        """Test deleting the queue."""
        call_back_func = MagicMock()
        qm = QueueManager(
            max_queue_size=8,
            num_workers=2,
            on_property_update_callback=call_back_func,
            logger=logger,
        )
        cm = BaseComponentManager(op_state_model=None, queue_manager=qm, logger=None)
        cm.enqueue(slow_task())
        cm.enqueue(stop_task())
        cm.enqueue(abort_task())
        cm.enqueue(stop_task())
        cm.enqueue(abort_task())
        cm.enqueue(stop_task())
        cm.enqueue(abort_task())
        cm.enqueue(stop_task())
        cm.enqueue(abort_task())

        del cm.queue_manager
        del cm


class TestComponentManager:
    """Tests for the component manager."""

    def test_init(self):
        """Test that we can init the component manager."""
        qm = QueueManager(max_queue_size=0, num_workers=1, logger=logger)
        cm = BaseComponentManager(op_state_model=None, queue_manager=qm, logger=logger)
        assert cm.queue_manager.task_ids_in_queue == []
