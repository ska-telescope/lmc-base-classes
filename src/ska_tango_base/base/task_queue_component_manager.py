"""This module implements a component manager that can queue tasks for execution by background threads."""
from __future__ import annotations
import logging
import threading
import time
import traceback
from queue import Empty, Queue
from threading import Event
from typing import Any, Callable, Dict, List, Optional
from attr import dataclass

import tango

from ska_tango_base.base.component_manager import BaseComponentManager
from ska_tango_base.commands import ResultCode


@dataclass
class TaskResult:
    """Convenience class for results."""

    result_code: ResultCode
    task_result: str
    unique_id: str

    def to_task_result(self) -> List[str]:
        """Convert TaskResult to task_result.

        :return: The task result
        :rtype: list[str]
        """
        return [f"{self.unique_id}", f"{int(self.result_code)}", f"{self.task_result}"]

    @classmethod
    def from_task_result(cls, task_result: list) -> TaskResult:
        """Convert task_result list to TaskResult.

        :param task_result: The task_result [unique_id, result_code, task_result]
        :type task_result: list
        :return: The task result
        :rtype: TaskResult
        """
        return TaskResult(
            result_code=ResultCode(int(task_result[1])),
            task_result=task_result[2],
            unique_id=task_result[0],
        )


class QueueTask:
    """A task that can be put on the queue."""

    def __init__(self: QueueTask, *args, **kwargs) -> None:
        """Create the task. args and kwargs are stored and should be referenced in the `do` method.

        :param self: [description]
        :type self: QueueTask
        """
        self.args = args
        self.kwargs = kwargs

    def update_progress(self, progress: str):
        """Private method to call the callback to update the progress.

        :param progress: [description]
        :type progress: str
        """
        self._update_progress_callback = self.kwargs.get("update_progress_callback")
        if self._update_progress_callback:
            self._update_progress_callback(progress)

    def get_task_name(self) -> str:
        """Return a custom task name.

        :return: The name of the task
        :rtype: str
        """
        return self.__class__.__name__

    def do(self: QueueTask) -> Any:
        """Implement this method with your functionality."""
        raise NotImplementedError


class QueueManager:
    """Manages the worker threads. Updates the properties as the tasks are completed."""

    class Worker(threading.Thread):
        """A worker thread that takes tasks from the queue and performs them."""

        def __init__(
            self: QueueManager.Worker,
            queue: Queue,
            logger: logging.Logger,
            stopping_event: Event,
            result_callback: Callable,
            update_command_state_callback: Callable,
            queue_fetch_timeout: int = 0.1,
        ) -> None:
            """Initiate a worker.

            :param self: Worker class
            :type self: QueueManager.Worker
            :param queue: The queue from which tasks are pulled
            :type queue: Queue
            :param logger: Logger to log to
            :type logger: logging.Logger
            :param stopping_event: Indicates whether to get more tasks off the queue
            :type stopping_event: Event
            :param update_command_state_callback: Callback to update command state
            :type update_command_state_callback: Callable
            """
            super().__init__()
            self._work_queue = queue
            self._logger = logger
            self.is_stopping = stopping_event
            self.is_aborting = threading.Event()
            self._result_callback = result_callback
            self._update_command_state_callback = update_command_state_callback
            self._queue_fetch_timeout = queue_fetch_timeout
            self.current_task_progress: Optional[str] = None
            self.current_task_id: Optional[str] = None
            self.setDaemon(True)

        def run(self) -> None:
            """Run in the thread.

            Tasks are fetched off the queue and executed.
            if _is_stopping is set the thread wil exit.
            If _is_aborting is set the queue will be emptied. All new commands will be aborted until
            is_aborting cleared.
            """
            with tango.EnsureOmniThread():
                while not self.is_stopping.is_set():
                    self.current_task_id = None
                    self.current_task_progress = ""

                    if self.is_aborting.is_set():
                        # Drain the Queue since self.is_aborting is set
                        while not self._work_queue.empty():
                            unique_id, _ = self._work_queue.get()
                            self.current_task_id = unique_id
                            self._logger.warning("Aborting task ID [%s]", unique_id)
                            result = TaskResult(
                                ResultCode.ABORTED, f"{unique_id} Aborted", unique_id
                            )
                            self._result_callback(result)
                            self._work_queue.task_done()
                        time.sleep(self._queue_fetch_timeout)
                        continue  # Don't try and get work off the queue below, continue next loop
                    try:
                        (unique_id, task) = self._work_queue.get(
                            block=True, timeout=self._queue_fetch_timeout
                        )
                        self.current_task_id = unique_id
                        self._update_command_state_callback(unique_id, "IN_PROGRESS")

                        # Inject is_aborting, is_stopping, progress_update into task
                        task.kwargs["is_aborting_event"] = self.is_aborting
                        task.kwargs["is_stopping_event"] = self.is_stopping
                        task.kwargs[
                            "update_progress_callback"
                        ] = self._update_progress_callback

                        task_result = self.execute_task(task)
                        result = TaskResult(
                            task_result[0], f"{task_result[1]}", unique_id
                        )
                        self._work_queue.task_done()
                        self._result_callback(result)
                    except Empty:
                        continue
                return

        def _update_progress_callback(self, progress: str) -> None:
            """Update the current task progress.

            :param progress: An indication of progress
            :type progress: str
            """
            self.current_task_progress = progress

        @classmethod
        def execute_task(cls, task: QueueTask):
            """Execute a task, return results in a standardised format.

            :param task: Task to execute
            :type task: QueueTask
            :return: (ResultCode, result)
            :rtype: tuple
            """
            try:
                result = (ResultCode.OK, task.do())
            except Exception as err:
                result = (
                    ResultCode.FAILED,
                    f"Error: {err} {traceback.format_exc()}",
                )
            return result

    def __init__(
        self: QueueManager,
        logger: logging.Logger,
        max_queue_size: int = 0,
        queue_fetch_timeout: float = 0.1,
        num_workers: int = 0,
        on_property_update_callback: Optional[Callable] = None,
    ):
        """Init QueryManager.

        Creates the queue and starts the thread that will execute commands
        from it.

        :param logger: Python logger
        :type logger: logging.Logger
        :param max_queue_size: The maximum size of the queue
        :type max_queue_size: int
        :param max_queue_size: The time to wait for items in the queue
        :type max_queue_size: float
        :param num_workers: The number of worker threads to start
        :type num_workers: float
        """
        self._logger = logger
        self._max_queue_size = max_queue_size
        self._work_queue = Queue(self._max_queue_size)
        self._queue_fetch_timeout = queue_fetch_timeout
        self._on_property_update_callback = on_property_update_callback
        self.is_stopping = threading.Event()
        self._property_update_lock = threading.Lock()

        self._task_result = []
        self._tasks_in_queue: Dict[str, str] = {}  # unique_id, task_name
        self._task_status: Dict[str, str] = {}  # unique_id, status
        self._threads = []

        # If there's no queue, don't start threads
        if not self._max_queue_size:
            return

        self._threads = [
            self.Worker(
                self._work_queue,
                self._logger,
                self.is_stopping,
                self.result_callback,
                self.update_task_state_callback,
            )
            for _ in range(num_workers)
        ]
        for thread in self._threads:
            thread.start()

    @property
    def queue_full(self) -> bool:
        """Check if the queue is full.

        :return: Whether or not the queue is full.
        :rtype: bool
        """
        return self._work_queue.full()

    @property
    def task_result(self) -> list:
        """Return the last task result.

        :return: Last task result
        :rtype: list
        """
        return self._task_result.copy()

    @property
    def task_ids_in_queue(self) -> list:
        """Task IDs in the queue.

        :return: The task IDs in the queue
        :rtype: list
        """
        return list(self._tasks_in_queue.keys())

    @property
    def tasks_in_queue(self) -> list:
        """Task names in the queue.

        :return: The list of task names in the queue
        :rtype: list
        """
        return list(self._tasks_in_queue.values())

    @property
    def task_status(self) -> Dict[str, str]:
        """Return task status.

        :return: The task status
        :rtype: Dict[str, str]
        """
        return self._task_status.copy()

    @property
    def task_progress(self) -> Dict[str, str]:
        """Return the task progress.

        :return: The task progress
        :rtype: Dict[str, str]
        """
        progress = {}
        for worker in self._threads:
            if worker.current_task_id:
                progress[worker.current_task_id] = worker.current_task_progress
        return progress

    def enqueue_task(self, task: QueueTask) -> str:
        """Add the task to be done onto the queue.

        :param task: The task to execute in a thread
        :type task: QueueTask
        :return: The unique ID of the command
        :rtype: string
        """
        unique_id = self.get_unique_id(task.get_task_name())

        # If there is no queue, just execute the command and return
        if self._max_queue_size == 0:
            self.update_task_state_callback(unique_id, "IN_PROGRESS")
            task_result = self.Worker.execute_task(task)
            result = TaskResult(task_result[0], f"{task_result[1]}", unique_id)
            self.result_callback(result)
            return unique_id

        if self.queue_full:
            self.result_callback(
                TaskResult(ResultCode.REJECTED, "Queue is full", unique_id)
            )
            return unique_id

        self._work_queue.put([unique_id, task])
        with self._property_update_lock:
            self._tasks_in_queue[unique_id] = task.get_task_name()
        self._on_property_change("tasks_in_queue")
        self._on_property_change("task_ids_in_queue")
        return unique_id

    def result_callback(self, task_result: TaskResult):
        """Run when the task, taken from the queue, have completed to update the appropriate attributes.

        :param task_result: The result of the task
        :type task_result: TaskResult
        """
        with self._property_update_lock:
            if task_result.unique_id in self._task_status:
                del self._task_status[task_result.unique_id]
            self._task_result = task_result.to_task_result()
        self._on_property_change("task_result")

        if task_result.unique_id in self._tasks_in_queue:
            with self._property_update_lock:
                del self._tasks_in_queue[task_result.unique_id]
            self._on_property_change("task_ids_in_queue")
            self._on_property_change("tasks_in_queue")

    def update_task_state_callback(self, unique_id: str, status: str):
        """Update the executing task state.

        :param unique_id: The task unique ID
        :type unique_id: str
        :param status: The state of the task
        :type status: str
        """
        with self._property_update_lock:
            self._task_status[unique_id] = status
        self._on_property_change("task_status")

    def _on_property_change(self, property_name: str):
        """Trigger when a property changes value.

        :param property_name: The property name
        :type property_name: str
        """
        if self._on_property_update_callback:
            self._on_property_update_callback(
                property_name, getattr(self, property_name)
            )

    def abort_commands(self):
        """Start aborting commands."""
        for worker in self._threads:
            worker.is_aborting.set()

    def resume_commands(self):
        """Unsets aborting so commands can be picked up again."""
        for worker in self._threads:
            worker.is_aborting.clear()

    def stop_commands(self):
        """Set is_stopping on each thread so it exists out. Killing the thread."""
        self.is_stopping.set()

    @property
    def is_aborting(self):
        """Return False if any of the threads are aborting."""
        return all([worker.is_aborting.is_set() for worker in self._threads])

    @classmethod
    def get_unique_id(cls, task_name):
        """Generate a unique ID for the task.

        :param task_name: The name of the task
        :type task_name: string
        :return: The unique ID of the task
        :rtype: string
        """
        return f"{time.time()}_{task_name}"

    def __del__(self) -> None:
        """Release resources prior to instance deletion.

        - Set the workers to aborting, this will empty out the queue and set the result code
          for each task to `Aborted`.
        - Wait for the queues to empty out.
        - Set the workers to stopping, this will exit out the running thread.
        """
        if not self._threads:
            return

        self.abort_commands()
        self._work_queue.join()
        for worker in self._threads:
            worker.is_stopping.set()
        while not any([worker.is_alive() for worker in self._threads]):
            pass

    def __len__(self) -> int:
        """Approximate length of the queue.

        :return: The approximate length of the queue
        :rtype: int
        """
        return self._work_queue.qsize()


class TaskQueueComponentManager(BaseComponentManager):
    """A component manager that provides message queue functionality."""

    def __init__(
        self: TaskQueueComponentManager,
        message_queue: QueueManager,
        op_state_model: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Create a new component manager that puts tasks on the queue.

        :param message_queue: The queue manager instance
        :type message_queue: QueueManager
        :param op_state_model: The ops state model
        :type op_state_model: Any
        """
        self.message_queue = message_queue

        super().__init__(op_state_model, *args, **kwargs)

    def enqueue(
        self,
        task: QueueTask,
    ) -> str:
        """Put `task` on the queue. The unique ID for it is returned.

        :param task: The task to execute in the thread
        :type task: QueueTask
        :return: The unique ID of the queued command
        :rtype: str
        """
        return self.message_queue.enqueue_task(task)
