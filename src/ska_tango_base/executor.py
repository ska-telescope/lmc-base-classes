"""This module provides for asynchronous execution of tasks."""
from enum import IntEnum
import queue
import threading
from typing import Optional

from tango import EnsureOmniThread


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

    FAILED = 7
    """
    The task failed to complete.

    Note that this should not be used for a task that executes to
    completion, but does not achieve its goal. This kind of
    domain-specific notion of "succeeded" versus "failed" should be
    passed as a task result. Here, FAILED means that the task executor
    has detected a failure of the task to run to completion. For
    example, execution of the task might have resulted in the raising of
    an uncaught exception.
    """


class _MessageQueueExecutor:
    """
    This class implements an executor with a pool of worker threads that
    pull tasks from a queue. This is essentially what a
    :py:class:`concurrent.futures.ThreadPoolExecutor` does, and this
    class has much-the-same interface. Ideally, we could simply replace
    this with a ThreadPoolExecutor. However for now we have to
    re-implement this so that we can wrap each thread in a
    :py:class:`tango.EnsureOmniThread()` context.
    """

    def __init__(self, max_workers):
        self._queue = queue.SimpleQueue()
        self._accepting = threading.Event()
        self._accepting.set()

        self._workers = [
            threading.Thread(target=self._work) for _ in range(max_workers)
        ]
        self._stop = False
        for worker in self._workers:
            worker.start()

    def _work(self):
        with EnsureOmniThread():
            while not self._stop:
                while self._accepting.is_set() and not self._stop:
                    try:
                        (fn, args, kwargs) = self._queue.get(timeout=1.0)
                    except queue.Empty:
                        continue
                    fn(*args, **kwargs)

                # We still need to run what's already on the queue,
                # but abort is set so these will be aborted.
                while not self._queue.empty() and not self._stop:
                    try:
                        (fn, args, kwargs) = self._queue.get_nowait()
                    except queue.Empty:
                        break
                    else:
                        fn(*args, **kwargs)
                self._accepting.set()

    def submit(self, fn, *args, **kwargs):
        if not self._accepting.is_set():
            raise RuntimeError("Executor is aborting.")
        self._queue.put((fn, args, kwargs))

    def clear(self, wait=True):
        self._accepting.clear()
        if wait:
            self._accepting.wait()

    def terminate(self):
        self._stop = True
        for worker in self._workers:
            worker.join()


class TaskExecutor:
    """An asynchronous executor of tasks."""

    def __init__(self, max_workers: Optional[int]):
        """
        Initialise a new instance.

        :param max_workers: the maximum number of worker threads
        """
        self._submit_lock = threading.Lock()

        self._max_workers = max_workers or 3

        self._executor = _MessageQueueExecutor(
            max_workers=self._max_workers,
        )

        self._abort_event = threading.Event()
        self._abort_queue = queue.SimpleQueue()
        self._aborter = threading.Thread(target=self._wait_to_abort)
        self._stop = False
        self._aborter.start()

    def submit(self, func, args=None, kwargs=None, task_callback=None):
        """
        Submit a new task.

        :param func: the function to be executed.
        :param args: positional arguments to the function
        :param task_callback: the callback to be called when the status
            or progress of the task execution changes
        :param kwargs: keyword arguments to the function
        """
        with self._submit_lock:
            if self._abort_event.is_set() and task_callback is not None:
                message = "Queue is aborting"
                task_callback(status=TaskStatus.REJECTED, message=message)
                return TaskStatus.REJECTED, message

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

    def abort(self, task_callback):
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

        self._abort_queue.put(task_callback)
        return TaskStatus.IN_PROGRESS, "Aborting tasks"

    def _wait_to_abort(self):
        with EnsureOmniThread():
            while not self._stop:
                try:
                    task_callback = self._abort_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                self._executor.clear(wait=True)

                # Create a new Event rather than just clearing the old one, in case a
                # running thread is yet to check.
                self._abort_event = threading.Event()
                if task_callback is not None:
                    task_callback(status=TaskStatus.COMPLETED)

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
            except Exception as exc:
                if task_callback is not None:
                    task_callback(status=TaskStatus.FAILED, exception=exc)

    def terminate(self):
        self._stop = True
        self._executor.terminate()
        self._aborter.join()
