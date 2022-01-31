"""This module provides for asynchronous execution of tasks."""
import concurrent.futures
from enum import IntEnum
import threading
import traceback
from typing import Callable, Optional


class TaskStatus(IntEnum):
    """The status of the QueueTask in the QueueManager."""

    STAGING = 0
    """
    The request to execute the task has been received but not yet acted
    upon.
    """

    QUEUED = 1
    """
    The task has been accepted and will be executed at a future time
    """

    IN_PROGRESS = 2
    """
    The task in progress
    """

    ABORTED = 3
    """
    The task in progress has been aborted
    """

    NOT_FOUND = 4
    """
    The task is not found
    """

    COMPLETED = 5
    """
    The task was completed.
    """

    REJECTED = 6
    """
    The task was rejected.
    """


class TaskExecutor:
    """An asynchronous executor of tasks."""

    def __init__(self, max_workers: Optional[int]):
        """
        Initialise a new instance.

        :param max_workers: the maximum number of worker threads
        """
        self._max_workers = max_workers

        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
        )
        self._abort_event = threading.Event()
        self._submit_lock = threading.Lock()

    def submit(
        self,
        func: Callable,
        args=None,
        kwargs=None,
        task_callback: Optional[Callable] = None,
    ) -> bool:
        """
        Submit a new task.

        :param func: the function to be executed.
        :param args: positional arguments to the function
        :param task_callback: the callback to be called when the status
            or progress of the task execution changes
        :param kwargs: keyword arguments to the function
        """
        with self._submit_lock:
            try:
                self._executor.submit(
                    self._run,
                    func,
                    args,
                    kwargs,
                    task_callback,
                    self._abort_event,
                )
            except RuntimeError:
                if task_callback is not None:
                    message = "Queue is aborting"
                    task_callback(status=TaskStatus.REJECTED, message=message)
                    return TaskStatus.REJECTED, message
            else:
                if task_callback is not None:
                    task_callback(status=TaskStatus.QUEUED)
                return TaskStatus.QUEUED, "Task queued"

    def abort(self, task_callback: Optional[Callable] = None):
        """
        Tell this executor to abort execution.

        New submissions will be rejected until the queue is empty and no
        tasks are still running. Tasks on the queue will be marked as
        aborted and not run. Tasks already running will be allowed to
        continue running
        """
        if task_callback is not None:
            task_callback(status=TaskStatus.IN_PROGRESS)
        self._abort_event.set()

        def _shutdown_and_relaunch(max_workers):
            self._executor.shutdown(wait=True)

            # Create a new Event rather than just clearing the old one, in case a
            # running thread is yet to check.
            self._abort_event = threading.Event()
            self._executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            )
            if task_callback is not None:
                task_callback(status=TaskStatus.COMPLETED)

        threading.Thread(
            target=_shutdown_and_relaunch, args=(self._max_workers,)
        ).start()
        return TaskStatus.IN_PROGRESS, "Aborting tasks"

    def _run(self, func, args, kwargs, task_callback, abort_event):
        # Let the submit method finish before we start. This prevents this thread from
        # calling back with "IN PROGRESS" before the submit method has called back with
        # "QUEUED".
        with self._submit_lock:
            pass

        if abort_event.is_set():
            if task_callback is not None:
                task_callback(status=TaskStatus.ABORTED)
        else:
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
                    **kwargs
                )
            except Exception:
                traceback.print_exc()
