# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""Tests of the ska_tango_base.executor module."""
from __future__ import annotations

from threading import Event, Lock

import pytest
from ska_control_model import TaskStatus
from ska_tango_testing.mock import MockCallableGroup

from ska_tango_base.base import TaskCallbackType
from ska_tango_base.executor import TaskExecutor


class TestTaskExecutor:
    """Tests of the TaskExecutor class."""

    @pytest.fixture()
    def executor(self: TestTaskExecutor) -> TaskExecutor:
        """
        Return the TaskExecutor under test.

        :return: a TaskExecutor
        """
        return TaskExecutor()

    @pytest.fixture()
    def callbacks(self: TestTaskExecutor) -> MockCallableGroup:
        """
        Return a dictionary of callbacks with asynchrony support.

        :return: a collections.defaultdict that returns callbacks by name.
        """
        job_callbacks = [f"job_{i}" for i in range(3)]
        return MockCallableGroup(*job_callbacks, "abort")

    # pylint: disable=consider-using-with
    def test_task_execution(
        self: TestTaskExecutor,
        executor: TaskExecutor,
        callbacks: MockCallableGroup,
    ) -> None:
        """
        Test that we can execute tasks.

        :param executor: the task executor under test
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

        locks = [Lock(), Lock()]
        locks[0].acquire()
        locks[1].acquire()

        executor.submit(_claim_lock, args=[locks[0]], task_callback=callbacks["job_0"])
        executor.submit(_claim_lock, args=[locks[1]], task_callback=callbacks["job_1"])

        # The queue size should equal the calls to executor.submit
        # But since the worker thread could dequeue commands before
        # fetching the queue size, it is safer to check for a non-empty
        # queue to have a stable test
        commands_in_queue = executor.get_input_queue_size()
        assert commands_in_queue > 0

        callbacks["job_0"].assert_call(status=TaskStatus.QUEUED)
        callbacks["job_1"].assert_call(status=TaskStatus.QUEUED)

        callbacks["job_0"].assert_call(status=TaskStatus.IN_PROGRESS)
        callbacks["job_1"].assert_not_called()

        locks[0].release()
        callbacks["job_0"].assert_call(status=TaskStatus.COMPLETED)
        callbacks["job_1"].assert_call(status=TaskStatus.IN_PROGRESS)

        locks[1].release()
        callbacks["job_1"].assert_call(status=TaskStatus.COMPLETED)

    # pylint: disable=consider-using-with
    def test_abort(
        self: TestTaskExecutor,
        executor: TaskExecutor,
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

        locks = [Lock(), Lock(), Lock()]
        locks[0].acquire()
        locks[1].acquire()
        locks[2].acquire()

        executor.submit(_claim_lock, args=[locks[0]], task_callback=callbacks["job_0"])
        executor.submit(_claim_lock, args=[locks[1]], task_callback=callbacks["job_1"])

        callbacks["job_0"].assert_call(status=TaskStatus.QUEUED)
        callbacks["job_1"].assert_call(status=TaskStatus.QUEUED)
        callbacks["job_0"].assert_call(status=TaskStatus.IN_PROGRESS)
        callbacks["job_1"].assert_not_called()

        executor.abort(task_callback=callbacks["abort"])
        callbacks["abort"].assert_call(status=TaskStatus.IN_PROGRESS)

        # TODO: Abort can finish before this job is submitted, causing this test to fail
        executor.submit(_claim_lock, [locks[2]], task_callback=callbacks["job_2"])
        callbacks["job_2"].assert_call(status=TaskStatus.REJECTED)

        locks[0].release()
        locks[1].release()
        callbacks["job_0"].assert_call(status=TaskStatus.ABORTED)
        callbacks["job_1"].assert_call(status=TaskStatus.ABORTED)
        callbacks["abort"].assert_call(status=TaskStatus.COMPLETED)

        executor.submit(_claim_lock, args=[locks[2]], task_callback=callbacks["job_2"])
        callbacks["job_2"].assert_call(status=TaskStatus.QUEUED)
        callbacks["job_2"].assert_call(status=TaskStatus.IN_PROGRESS)

        locks[2].release()
        callbacks["job_2"].assert_call(status=TaskStatus.COMPLETED)

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
