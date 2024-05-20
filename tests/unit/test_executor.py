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
from ska_control_model import ResultCode, TaskStatus
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

    def _claim_lock(
        self: TestTaskExecutor,
        lock: Lock,
        *,
        task_callback: TaskCallbackType | None,
        task_abort_event: Event,
    ) -> None:
        if task_callback is not None:
            task_callback(status=TaskStatus.IN_PROGRESS)
        with lock:
            if task_abort_event.is_set() and task_callback is not None:
                task_callback(
                    status=TaskStatus.ABORTED,
                    result=(ResultCode.ABORTED, "Command has been aborted"),
                )
                return
        if task_callback is not None:
            task_callback(status=TaskStatus.COMPLETED)

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
        locks = [Lock() for _ in range(max_workers + 1)]

        for i in range(max_workers + 1):
            locks[i].acquire()

        for i in range(max_workers + 1):
            executor.submit(
                self._claim_lock,
                args=[locks[i]],
                task_callback=callbacks[f"job_{i}"],
            )

        # The queue size should equal the calls to executor.submit (4 items)
        # But since the 3 worker threads could dequeue commands before
        # fetching the queue size, it is safer to check for a non-empty
        # queue to have a stable test
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
        locks = [Lock() for _ in range(max_workers + 2)]

        for i in range(max_workers + 2):
            locks[i].acquire()

        for i in range(max_workers + 1):
            executor.submit(
                self._claim_lock,
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

        status, message = executor.submit(
            self._claim_lock,
            args=[locks[max_workers + 1]],
            task_callback=callbacks[f"job_{max_workers + 1}"],
        )
        assert status is TaskStatus.REJECTED and message == "Queue is being aborted"
        callbacks[f"job_{max_workers + 1}"].assert_call(
            status=TaskStatus.REJECTED,
            result=(ResultCode.REJECTED, "Queue is being aborted"),
        )

        for i in range(max_workers + 1):
            locks[i].release()

        for i in range(max_workers):
            callbacks[f"job_{i}"].assert_call(
                status=TaskStatus.ABORTED,
                result=(ResultCode.ABORTED, "Command has been aborted"),
            )
        callbacks[f"job_{max_workers}"].assert_call(
            status=TaskStatus.ABORTED,
            result=(ResultCode.ABORTED, "Command has been aborted"),
        )

        sleep(0.1)  # TODO: Abort command needs to signal completion too

        executor.submit(
            self._claim_lock,
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
            "job_0",
            status=TaskStatus.FAILED,
            result=(
                ResultCode.FAILED,
                f"Unhandled exception during execution: {str(exception_to_raise)}",
            ),
            exception=exception_to_raise,
        )

    def test_is_cmd_allowed_false(
        self: TestTaskExecutor,
        executor: TaskExecutor,
        callbacks: MockCallableGroup,
    ) -> None:
        """
        Test the executor callback if the 'is_cmd_allowed' method returns False.

        :param executor: the task executor under test
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """

        def _is_cmd_allowed() -> bool:
            return False

        executor.submit(
            self._claim_lock,
            is_cmd_allowed=_is_cmd_allowed,
            task_callback=callbacks["job_0"],
        )
        callbacks.assert_call("job_0", status=TaskStatus.QUEUED)
        callbacks.assert_call(
            "job_0",
            status=TaskStatus.REJECTED,
            result=(ResultCode.NOT_ALLOWED, "Command is not allowed"),
        )

    def test_is_cmd_allowed_exception(
        self: TestTaskExecutor,
        executor: TaskExecutor,
        callbacks: MockCallableGroup,
    ) -> None:
        """
        Test the executor callback if the 'is_cmd_allowed' method raises an Exception.

        :param executor: the task executor under test
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """
        exception_to_raise = ValueError("Exception under test")

        def _is_cmd_allowed() -> bool:
            raise exception_to_raise

        executor.submit(
            self._claim_lock,
            is_cmd_allowed=_is_cmd_allowed,
            task_callback=callbacks["job_0"],
        )
        callbacks.assert_call("job_0", status=TaskStatus.QUEUED)
        callbacks.assert_call(
            "job_0",
            status=TaskStatus.REJECTED,
            result=(
                ResultCode.REJECTED,
                f"Exception from 'is_cmd_allowed' method: {str(exception_to_raise)}",
            ),
            exception=exception_to_raise,
        )
