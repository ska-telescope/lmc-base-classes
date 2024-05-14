# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module provides for asynchronous execution of tasks."""
from __future__ import annotations

import concurrent.futures
import threading
from typing import Any, Callable

from ska_control_model import ResultCode, TaskStatus

from ..base import TaskCallbackType

__all__ = ["TaskExecutor", "TaskStatus"]


# TODO: Placeholder for a future, better world in which we can typehint this
# as a callable that accepts arbitrary positional args, a task callback
# kwarg, an abort event kwargs, and arbitrary additional kwargs.
TaskFunctionType = Callable[..., None]


class TaskExecutor:
    """An asynchronous executor of tasks."""

    def __init__(self: TaskExecutor, max_workers: int | None = 1) -> None:
        """
        Initialise a new instance.

        :param max_workers: the maximum number of worker threads
            This is meant to be kept at the default value to allow
            the sequential execution of LRC except for special cases
        """
        self._max_workers = max_workers

        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
        )
        self._abort_event = threading.Event()
        self._submit_lock = threading.Lock()

    def get_input_queue_size(self: TaskExecutor) -> int:
        """
        Expose the number of queued items in the ThreadPoolExecutor.

        :return: Number of commands in the input queue
        """
        return self._executor._work_queue.qsize()  # pylint: disable=protected-access

    def submit(  # pylint: disable=too-many-arguments
        self: TaskExecutor,
        func: TaskFunctionType,
        args: Any = None,
        kwargs: Any = None,
        is_cmd_allowed: Callable[[], bool] | None = None,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Submit a new task.

        :param func: the function to be executed.
        :param args: positional arguments to the function
        :param kwargs: keyword arguments to the function
        :param is_cmd_allowed: sanity check for func
        :param task_callback: the callback to be called when the status
            or progress of the task execution changes

        :return: (TaskStatus, message)
        """
        with self._submit_lock:
            try:
                self._executor.submit(
                    self._run,
                    func,
                    args,
                    kwargs,
                    is_cmd_allowed,
                    task_callback,
                    self._abort_event,
                )
            except RuntimeError:
                self._call_task_callback(
                    task_callback,
                    status=TaskStatus.REJECTED,
                    result=(ResultCode.REJECTED, "Queue is being aborted"),
                )
                return TaskStatus.REJECTED, "Queue is being aborted"
            except Exception as exc:  # pylint: disable=broad-except
                self._call_task_callback(
                    task_callback,
                    status=TaskStatus.FAILED,
                    result=(
                        ResultCode.FAILED,
                        f"Unhandled exception submitting task: {str(exc)}",
                    ),
                    exception=exc,
                )
                return (
                    TaskStatus.FAILED,
                    f"Unhandled exception submitting task: {str(exc)}",
                )

            self._call_task_callback(task_callback, status=TaskStatus.QUEUED)
            return TaskStatus.QUEUED, "Task queued"

    def abort(
        self: TaskExecutor, task_callback: TaskCallbackType | None = None
    ) -> tuple[TaskStatus, str]:
        """
        Tell this executor to abort execution.

        New submissions will be rejected until the queue is empty and no
        tasks are still running. Tasks on the queue will be marked as
        aborted and not run. Tasks already running will be allowed to
        continue running

        :param task_callback: callback for abort complete

        :return: tuple of task status & message
        """
        self._call_task_callback(task_callback, status=TaskStatus.IN_PROGRESS)
        self._abort_event.set()

        def _shutdown_and_relaunch(max_workers: int) -> None:
            self._executor.shutdown(wait=True)

            # Create a new Event rather than just clearing the old one, in case a
            # running thread is yet to check.
            self._abort_event = threading.Event()
            self._executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            )
            self._call_task_callback(
                task_callback,
                status=TaskStatus.COMPLETED,
                result=(ResultCode.OK, "Abort completed OK"),
            )

        threading.Thread(
            target=_shutdown_and_relaunch, args=(self._max_workers,)
        ).start()
        return TaskStatus.IN_PROGRESS, "Aborting tasks"

    def _run(  # pylint: disable=too-many-arguments
        self: TaskExecutor,
        func: TaskFunctionType,
        args: Any,
        kwargs: Any,
        is_cmd_allowed: Callable[[], bool] | None,
        task_callback: TaskCallbackType | None,
        abort_event: threading.Event,
    ) -> None:
        # Let the submit method finish before we start. This prevents this thread from
        # calling back with "IN PROGRESS" before the submit method has called back with
        # "QUEUED".
        with self._submit_lock:
            pass

        if abort_event.is_set():
            self._call_task_callback(
                task_callback,
                status=TaskStatus.ABORTED,
                result=(ResultCode.ABORTED, "Command has been aborted"),
            )
            return

        if is_cmd_allowed is not None:
            try:
                if is_cmd_allowed() is False:
                    self._call_task_callback(
                        task_callback,
                        status=TaskStatus.REJECTED,
                        result=(ResultCode.NOT_ALLOWED, "Command is not allowed"),
                    )
                    return
            except Exception as exc:  # pylint: disable=broad-except
                # Catching all exceptions because we're on a thread. Any
                # uncaught exception will take down the thread without giving
                # us any useful diagnostics.
                self._call_task_callback(
                    task_callback,
                    status=TaskStatus.REJECTED,
                    result=(
                        ResultCode.REJECTED,
                        f"Exception from 'is_cmd_allowed' method: {str(exc)}",
                    ),
                    exception=exc,
                )
                return

        # Don't set the task to IN_PROGRESS yet, in case func is itself implemented
        # asynchronously. We leave it to func to set the task to IN_PROGRESS, and
        # eventually to set it to COMPLETE
        try:
            args = args or []
            kwargs = kwargs or {}
            func(
                *args,
                task_callback=task_callback,
                task_abort_event=abort_event,
                **kwargs,
            )
        except Exception as exc:  # pylint: disable=broad-except
            # Catching all exceptions because we're on a thread. Any
            # uncaught exception will take down the thread without giving
            # us any useful diagnostics.
            self._call_task_callback(
                task_callback,
                status=TaskStatus.FAILED,
                result=(
                    ResultCode.FAILED,
                    f"Unhandled exception during execution: {str(exc)}",
                ),
                exception=exc,
            )

    # This method is for linter to not complain about too many nested ifs
    def _call_task_callback(
        self: TaskExecutor,
        task_callback: TaskCallbackType | None,
        **kwargs: Any,
    ) -> None:
        if task_callback is not None:
            task_callback(**kwargs)
