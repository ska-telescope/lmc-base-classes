# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""Tests of the ska_tango_base.executor module."""
from __future__ import annotations

from threading import Event, Lock
from time import sleep

import pytest
from ska_control_model import TaskStatus
from ska_tango_testing.mock import MockCallableGroup

from ska_tango_base.base import TaskCallbackType
from ska_tango_base.executor import TaskExecutor


class TestTaskExecutor:
    """Tests of the TaskExecutor class."""

    @pytest.fixture()
    def max_workers(self: TestTaskExecutor) -> int:
        """
        Return the maximum number of worker threads.

        :return: the maximum number of worker threads
        """
        return 3

    @pytest.fixture()
    def executor(self: TestTaskExecutor, max_workers: int) -> TaskExecutor:
        """
        Return the TaskExecutor under test.

        :param max_workers: maximum number of worker threads.

        :return: a TaskExecutor
        """
        return TaskExecutor(max_workers)

    @pytest.fixture()
    def callbacks(self: TestTaskExecutor, max_workers: int) -> MockCallableGroup:
        """
        Return a dictionary of callbacks with asynchrony support.

        :param max_workers: maximum number of worker threads.

        :return: a collections.defaultdict that returns callbacks by name.
        """
        job_callbacks = [f"job_{i}" for i in range(max_workers + 2)]
        return MockCallableGroup(*job_callbacks, "abort")

    def test_task_execution(
        self: TestTaskExecutor,
        executor: TaskExecutor,
        max_workers: int,
        callbacks: MockCallableGroup,
    ) -> None:
        """
        Test that we can execute tasks.

        :param executor: the task executor under test
        :param max_workers: the maximum number of worker threads in the
            task executor
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """

        def _claim_lock(
            lock: Lock,
            *,
            task_callback: TaskCallbackType | None,
            task_abort_event: Event,
        ) -> None:
            if task_callback is not None:
                task_callback(status=TaskStatus.IN_PROGRESS)
            with lock:
                if task_abort_event.is_set() and task_callback is not None:
                    task_callback(status=TaskStatus.ABORTED)
                    return
            if task_callback is not None:
                task_callback(status=TaskStatus.COMPLETED)

        locks = [Lock() for _ in range(max_workers + 1)]

        for i in range(max_workers + 1):
            locks[i].acquire()

        for i in range(max_workers + 1):
            executor.submit(
                _claim_lock,
                args=[locks[i]],
                task_callback=callbacks[f"job_{i}"],
            )

        # the workers will immediately pull off tasks to execute
        # so check fo a non-empty queue (at least) since we expect
        # one command to be left waiting while the three workers are busy
        commands_in_queue = executor.get_input_queue_size()
        assert commands_in_queue > 0

        for i in range(max_workers + 1):
            callbacks[f"job_{i}"].assert_call(status=TaskStatus.QUEUED)

        for i in range(max_workers):
            callbacks[f"job_{i}"].assert_call(status=TaskStatus.IN_PROGRESS)
        callbacks[f"job_{max_workers}"].assert_not_called()

        locks[0].release()

        callbacks["job_0"].assert_call(status=TaskStatus.COMPLETED)
        callbacks[f"job_{max_workers}"].assert_call(status=TaskStatus.IN_PROGRESS)

        for i in range(1, max_workers + 1):
            locks[i].release()

        for i in range(1, max_workers + 1):
            callbacks[f"job_{i}"].assert_call(status=TaskStatus.COMPLETED)

    def test_abort(
        self: TestTaskExecutor,
        executor: TaskExecutor,
        max_workers: int,
        callbacks: MockCallableGroup,
    ) -> None:
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

        def _claim_lock(
            lock: Lock,
            *,
            task_callback: TaskCallbackType,
            task_abort_event: Event,
        ) -> None:
            if task_callback is not None:
                task_callback(status=TaskStatus.IN_PROGRESS)
            with lock:
                if task_abort_event.is_set() and task_callback is not None:
                    task_callback(status=TaskStatus.ABORTED)
                    return
            if task_callback is not None:
                task_callback(status=TaskStatus.COMPLETED)

        locks = [Lock() for _ in range(max_workers + 2)]

        for i in range(max_workers + 2):
            locks[i].acquire()

        for i in range(max_workers + 1):
            executor.submit(
                _claim_lock,
                args=[locks[i]],
                task_callback=callbacks[f"job_{i}"],
            )

        for i in range(max_workers + 1):
            callbacks[f"job_{i}"].assert_call(status=TaskStatus.QUEUED)

        for i in range(max_workers):
            callbacks[f"job_{i}"].assert_call(status=TaskStatus.IN_PROGRESS)
        callbacks[f"job_{max_workers}"].assert_not_called()

        executor.abort(task_callback=callbacks["abort"])
        callbacks["abort"].assert_call(status=TaskStatus.IN_PROGRESS)

        executor.submit(
            _claim_lock,
            args=[locks[max_workers + 1]],
            task_callback=callbacks[f"job_{max_workers + 1}"],
        )
        callbacks[f"job_{max_workers + 1}"].assert_call(status=TaskStatus.REJECTED)

        for i in range(max_workers + 1):
            locks[i].release()

        for i in range(max_workers):
            callbacks[f"job_{i}"].assert_call(status=TaskStatus.ABORTED)
        callbacks[f"job_{max_workers}"].assert_call(status=TaskStatus.ABORTED)

        sleep(0.1)  # TODO: Abort command needs to signal completion too

        executor.submit(
            _claim_lock,
            args=[locks[max_workers + 1]],
            task_callback=callbacks[f"job_{max_workers + 1}"],
        )
        callbacks[f"job_{max_workers + 1}"].assert_call(status=TaskStatus.QUEUED)
        callbacks[f"job_{max_workers + 1}"].assert_call(status=TaskStatus.IN_PROGRESS)

        locks[max_workers + 1].release()

        callbacks[f"job_{max_workers + 1}"].assert_call(status=TaskStatus.COMPLETED)

    def test_exception(
        self: TestTaskExecutor,
        executor: TaskExecutor,
        callbacks: MockCallableGroup,
    ) -> None:
        """
        Test that the executor handles an uncaught exception correctly.

        :param executor: the task executor under test
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """
        exception_to_raise = ValueError("Exception under test")

        def _raise_exception(
            *,
            task_callback: TaskCallbackType,
            task_abort_event: Event,  # pylint: disable=unused-argument
        ) -> None:
            task_callback(status=TaskStatus.IN_PROGRESS)
            raise exception_to_raise

        executor.submit(_raise_exception, task_callback=callbacks["job_0"])

        callbacks.assert_call("job_0", status=TaskStatus.QUEUED)
        callbacks.assert_call("job_0", status=TaskStatus.IN_PROGRESS)
        callbacks.assert_call(
            "job_0", status=TaskStatus.FAILED, exception=exception_to_raise
        )
