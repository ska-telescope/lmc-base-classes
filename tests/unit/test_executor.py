"""Tests of the ska_tango_base.executor module."""
from threading import Lock
from time import sleep

import pytest

from ska_tango_base.executor import TaskExecutor, TaskStatus


class TestTaskExecutor:
    """Tests of the TaskExecutor class."""

    @pytest.fixture()
    def max_workers(self):
        """
        Return the maximum number of worker threads.

        :return: the maximum number of worker threads
        """
        return 3

    @pytest.fixture()
    def executor(self, max_workers):
        """
        Return the TaskExecutor under test.

        :param max_workers: maximum number of worker threads.
        """
        return TaskExecutor(max_workers)

    def test_task_execution(self, executor, max_workers, callbacks):
        """
        Test that we can execute tasks.

        :param executor: the task executor under test
        :param max_workers: the maximum number of worker threads in the
            task executor
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """

        def _claim_lock(lock, task_callback, task_abort_event):
            if task_callback is not None:
                task_callback(status=TaskStatus.IN_PROGRESS)
            with lock:
                if task_abort_event.is_set():
                    task_callback(status=TaskStatus.ABORTED)
                    return
            if task_callback is not None:
                task_callback(status=TaskStatus.COMPLETED)

        locks = [Lock() for _ in range(max_workers + 1)]

        for i in range(max_workers + 1):
            locks[i].acquire()

        for i in range(max_workers + 1):
            executor.submit(_claim_lock, args=[locks[i]], task_callback=callbacks[i])

        for i in range(max_workers + 1):
            callbacks[i].assert_next_call(status=TaskStatus.QUEUED)

        for i in range(max_workers):
            callbacks[i].assert_next_call(status=TaskStatus.IN_PROGRESS)
        callbacks[max_workers].assert_not_called()

        locks[0].release()

        callbacks[0].assert_next_call(status=TaskStatus.COMPLETED)
        callbacks[max_workers].assert_next_call(status=TaskStatus.IN_PROGRESS)

        for i in range(1, max_workers + 1):
            locks[i].release()

        for i in range(1, max_workers + 1):
            callbacks[i].assert_next_call(status=TaskStatus.COMPLETED)

    def test_abort(self, executor, max_workers, callbacks):
        """
        Test that we can abort execution.

        Specifically, test that:

        * tasks already started continue to run

        * tasks on the queue get to run but only so that the worker
          thread can set them to aborted

        * newly submitted tasks are rejected

        * but once the queue is empty then the abortion state completes,
          and tasks can once again be submitted.

        :param executor: the task executor under test
        :param max_workers: the maximum number of worker threads in the
            task executor
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """

        def _claim_lock(lock, task_callback, task_abort_event):
            if task_callback is not None:
                task_callback(status=TaskStatus.IN_PROGRESS)
            with lock:
                if task_abort_event.is_set():
                    task_callback(status=TaskStatus.ABORTED)
                    return
            if task_callback is not None:
                task_callback(status=TaskStatus.COMPLETED)

        locks = [Lock() for _ in range(max_workers + 2)]

        for i in range(max_workers + 2):
            locks[i].acquire()

        for i in range(max_workers + 1):
            executor.submit(_claim_lock, args=[locks[i]], task_callback=callbacks[i])

        for i in range(max_workers + 1):
            callbacks[i].assert_next_call(status=TaskStatus.QUEUED)

        for i in range(max_workers):
            callbacks[i].assert_next_call(status=TaskStatus.IN_PROGRESS)
        callbacks[max_workers].assert_not_called()

        executor.abort(task_callback=callbacks["abort"])
        callbacks["abort"].assert_next_call(status=TaskStatus.IN_PROGRESS)

        executor.submit(
            _claim_lock,
            args=[locks[max_workers + 1]],
            task_callback=callbacks[max_workers + 1],
        )
        callbacks[max_workers + 1].assert_next_call(
            status=TaskStatus.REJECTED, message="Queue is aborting"
        )

        for i in range(max_workers + 1):
            locks[i].release()

        for i in range(max_workers):
            callbacks[i].assert_next_call(status=TaskStatus.ABORTED)
        callbacks[max_workers].assert_next_call(status=TaskStatus.ABORTED)

        sleep(0.1)  # TODO: Abort command needs to signal completion too

        executor.submit(
            _claim_lock,
            args=[locks[max_workers + 1]],
            task_callback=callbacks[max_workers + 1],
        )
        callbacks[max_workers + 1].assert_next_call(status=TaskStatus.QUEUED)
        callbacks[max_workers + 1].assert_next_call(status=TaskStatus.IN_PROGRESS)

        locks[max_workers + 1].release()

        callbacks[max_workers + 1].assert_next_call(status=TaskStatus.COMPLETED)

    def test_exception(self, executor, callbacks):
        """
        Test that the executor handles an uncaught exception correctly.

        :param executor: the task executor under test
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """
        exception_to_raise = ValueError("Exception under test")

        def _raise_exception(task_callback, task_abort_event):
            if task_callback is not None:
                task_callback(status=TaskStatus.IN_PROGRESS)
            raise exception_to_raise

        executor.submit(_raise_exception, task_callback=callbacks[0])

        callbacks[0].assert_next_call(status=TaskStatus.QUEUED)
        callbacks[0].assert_next_call(status=TaskStatus.IN_PROGRESS)
        callbacks[0].assert_next_call(
            status=TaskStatus.FAILED, exception=exception_to_raise
        )
