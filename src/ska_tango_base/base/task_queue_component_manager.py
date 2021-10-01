"""
This module provides a QueueManager, TaskResult and QueueTask classes.

* **TaskResult**: is a convenience `dataclass` for parsing and formatting the
  results of a task.

* **QueueTask**: is a class that instances of which can be added to the queue for execution
  by background threads.

* **QueueManager**: that implements the queue and thread worker functionality.

**********
TaskResult
**********

This is a simple convenience class to parse or format the task result. The result of a task will
be made available as a Tango device attribute named `command_result`. It will be a tuple of 3 strings.

1. The unique ID
    Every command/task put on the queue for execution by background threads will have a unique ID.
2. The Result Code
    This is the result of the task executed by a worker from the queue.
3. The task result
    The string representation of the returned result for the task on the queue.

.. code-block:: py

    from ska_tango_base.base.task_queue_component_manager import TaskResult
    tr = TaskResult.from_task_result(("UniqueID", "0", "The task result"))
    tr
    TaskResult(result_code=<ResultCode.OK: 0>, task_result='The task result', unique_id='UniqueID')
    tr.to_task_result()
    ('UniqueID', '0', 'The task result')

*********
QueueTask
*********

This class should be subclassed and the `do` method implemented with the required functionality.
The `do` method will be executed by the background worker in a thread.

`get_task_name` can be overridden if you want to change the name of the task as it would appear in
the `tasks_in_queue` property.

Simple example:

.. code-block:: py

    class SimpleTask(QueueTask):
        def do(self):
            num_one = self.args[0]
            num_two = self.kwargs.get("num_two")
            return num_one + num_two

    return SimpleTask(2, num_two=3)

3 items are added dynamically by the worker thread and is available for use in the class instance.

* **aborting_event**: can be check periodically to determine whether
  the queue tasks have been aborted to gracefully complete the task in progress.
  The thread will stay active and once `aborting_event` has been unset,
  new tasks will be fetched from the queue for execution.

.. code-block:: py

    class AbortTask(QueueTask):
        def do(self):
            sleep_time = self.args[0]
            while not self.aborting_event.is_set():
                time.sleep(sleep_time)

    return AbortTask(0.2)

* **stopping_event**: can be check periodically to determine whether
  the queue tasks have been stopped. In this case the thread will complete.

.. code-block:: py

    class StopTask(QueueTask):
        def do(self):
            assert not self.stopping_event.is_set()
            while not self.stopping_event.is_set():
                pass

    return StopTask()

* **update_progress**: a callback that can be called wth the current progress
  of the task in progress

.. code-block:: py

    class ProgressTask(QueueTask):
        def do(self):
            for i in range(100):
                self.update_progress(str(i))
                time.sleep(0.5)

    return ProgressTask()

************
QueueManager
************

The queue manager class manages the queue, workers and the update of properties.
The number of worker threads can be specified.

When `num_workers` is 0, tasks that are enqueued will *not* be put on the queue,
but will simply be executed and thus block until done. No worker threads are started in this case.

As tasks are taken off the queue and completes, the properties below will be updated. An optional callback
`on_property_update_callback` can be specified that will be executed for every property change. This callback
will be called with the name of the property and its current value.

* **tasks_in_queue**: A list of names for the tasks in the queue.
  Changes when a queue item is added or removed.

* **task_ids_in_queue**: A list of unique IDs for the tasks in the queue.
  Changes when a queue item is added or removed.

* **task_result**: The result of the latest completed task. Changes when task completes.

* **task_status**: A list of unique IDs and the their status.
  Currently indicates when a task is in progress and changes when a task is started or completed.

Other properties of note:

* **queue_full**: Indicates whether the queue is full or not.
  If the queue is full, the result of any enqueued task will immediately be set to REJECTED.

* **task_progress**: When reading this property the progress of the tasks are fetched from the worker threads.

Aborting tasks
--------------

When `abort_tasks` is called on the queue manager the following will happen.

* Any tasks in progress will complete. Tasks that check `aborting_event` periodically will know to complete
  otherwise it will complete as per normal.

* Any tasks on the queue will be removed and their result set to ABORTED. They will not be executed.

* Any tasks enqueued while in aborted state will immediately be removed from the queue and marked as ABORTED.

* The thread stays alive.

When `resume_tasks` is then called, tasks are again put on the queue, retrieved and executed as per normal.

Stopping tasks
--------------

Once `stop_tasks` is called the worker threads completes as soon as possible.

* Any tasks in progress will complete. Tasks that check `stopping_event` will know to exit gracefully.

* The thread will cease.

Getting the state of a task
---------------------------

Calling `get_task_state` with the task ID will check the state of the task. A history of completed tasks
are not kept, so it may not be found.

"""
from __future__ import annotations
import enum
import logging
import threading
import time
import traceback
from queue import Empty, Queue
from threading import Event
from typing import Any, Callable, Dict, Optional, Tuple
from dataclasses import dataclass

import tango

from ska_tango_base.base.component_manager import BaseComponentManager
from ska_tango_base.commands import ResultCode


class TaskState(enum.IntEnum):
    """The state of the QueueTask in the QueueManager."""

    QUEUED = 0
    """
    The task has been accepted and will be executed at a future time
    """

    IN_PROGRESS = 1
    """
    The task in progress
    """

    ABORTED = 2
    """
    The task in progress has been aborted
    """

    NOT_FOUND = 3
    """
    The task is not found
    """

    COMPLETED = 4
    """
    The task was completed.
    """

    NOT_ALLOWED = 5
    """
    The task is not allowed to be executed
    """


@dataclass
class TaskResult:
    """Convenience class for results."""

    result_code: ResultCode
    task_result: str
    unique_id: str

    def to_task_result(self) -> Tuple[str, str, str]:
        """Convert TaskResult to task_result.

        :return: The task result
        :rtype: tuple[str, str, str]
        """
        return f"{self.unique_id}", f"{int(self.result_code)}", f"{self.task_result}"

    @classmethod
    def from_task_result(cls, task_result: Tuple[str, str, str]) -> TaskResult:
        """Convert task_result tuple to TaskResult.

        :param task_result: The task_result (unique_id, result_code, task_result)
        :type task_result: tuple
        :return: The task result
        :rtype: TaskResult
        :raises: ValueError
        """
        if not task_result or len(task_result) != 3:
            raise ValueError(f"Cannot parse task_result {task_result}")

        return TaskResult(
            result_code=ResultCode(int(task_result[1])),
            task_result=task_result[2],
            unique_id=task_result[0],
        )


class QueueTask:
    """A task that can be put on the queue."""

    def __init__(self: QueueTask, *args, **kwargs) -> None:
        """Create the task. args and kwargs are stored and should be referenced in the `do` method."""
        self.args = args
        self.kwargs = kwargs
        self._update_progress_callback = None

    @property
    def aborting_event(self) -> threading.Event:
        """Worker adds aborting_event threading event.

        Indicates whether task execution have been aborted.

        :return: The aborting_event event.
        :rtype: threading.Event
        """
        return self.kwargs.get("aborting_event")

    @property
    def stopping_event(self) -> threading.Event:
        """Worker adds stopping_event threading event.

        Indicates whether task execution have been stopped.

        :return: The stopping_event.
        :rtype: threading.Event
        """
        return self.kwargs.get("stopping_event")

    def update_progress(self, progress: str):
        """Call the callback to update the progress.

        :param progress: String that to indicate progress of task
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
            aborting_event: Event,
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
            :param aborting_event: Indicates whether the queue is being aborted
            :type aborting_event: Event
            :param update_command_state_callback: Callback to update command state
            :type update_command_state_callback: Callable
            """
            super().__init__()
            self._work_queue = queue
            self._logger = logger
            self.stopping_event = stopping_event
            self.aborting_event = aborting_event
            self._result_callback = result_callback
            self._update_command_state_callback = update_command_state_callback
            self._queue_fetch_timeout = queue_fetch_timeout
            self.current_task_progress: Optional[str] = None
            self.current_task_id: Optional[str] = None
            self.setDaemon(True)

        def run(self) -> None:
            """Run in the thread.

            Tasks are fetched off the queue and executed.
            if stopping_event is set the thread will exit.
            If aborting_event is set the queue will be emptied. All new commands will be aborted until
            aborting_event cleared.
            """
            with tango.EnsureOmniThread():
                while not self.stopping_event.is_set():
                    self.current_task_id = None
                    self.current_task_progress = ""

                    if self.aborting_event.is_set():
                        # Drain the Queue since self.aborting_event is set
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

                        self._update_command_state_callback(unique_id, "IN_PROGRESS")
                        self.current_task_id = unique_id
                        # Inject aborting_event, stopping_event, progress_update into task
                        task.kwargs["aborting_event"] = self.aborting_event
                        task.kwargs["stopping_event"] = self.stopping_event
                        task.kwargs[
                            "update_progress_callback"
                        ] = self._update_progress_callback
                        result = self.execute_task(task, unique_id)
                        self._result_callback(result)
                        self._work_queue.task_done()
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
        def execute_task(cls, task: QueueTask, unique_id: str) -> TaskResult:
            """Execute a task, return results in a standardised format.

            :param task: Task to execute
            :type task: QueueTask
            :param unique_id: The task unique ID
            :type unique_id: str
            :return: The result of the task
            :rtype: TaskResult
            """
            try:
                result = TaskResult(ResultCode.OK, f"{task.do()}", unique_id)
            except Exception as err:
                result = TaskResult(
                    ResultCode.FAILED,
                    f"Error: {err} {traceback.format_exc()}",
                    unique_id,
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

        Creates the queue and starts the thread that will execute tasks
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
        self.stopping_event = threading.Event()
        self.aborting_event = threading.Event()
        self._property_update_lock = threading.Lock()

        self._task_result: Optional[Tuple[str, str, str]] = None
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
                self.stopping_event,
                self.aborting_event,
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
    def task_result(self) -> Tuple[str, str, str]:
        """Return the last task result.

        :return: Last task result
        :rtype: Tuple
        """
        return self._task_result

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
            result = self.Worker.execute_task(task, unique_id)
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

        # Once the queue is cleared and all the work in progress have completed, clear
        # the aborting state.
        if self.is_aborting and self._work_queue.empty() and (not self.task_status):
            self.resume_tasks()

        self._on_property_change("task_result")

    def update_task_state_callback(self, unique_id: str, status: str):
        """Update the executing task state.

        :param unique_id: The task unique ID
        :type unique_id: str
        :param status: The state of the task
        :type status: str
        """
        if unique_id in self._tasks_in_queue:
            with self._property_update_lock:
                del self._tasks_in_queue[unique_id]
            self._on_property_change("task_ids_in_queue")
            self._on_property_change("tasks_in_queue")

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

    def abort_tasks(self):
        """Start aborting tasks."""
        self.aborting_event.set()

    def resume_tasks(self):
        """Unsets aborting so tasks can be picked up again."""
        for worker in self._threads:
            worker.aborting_event.clear()

    def stop_tasks(self):
        """Set stopping_event on each thread so it exists out. Killing the thread."""
        self.stopping_event.set()

    @property
    def is_aborting(self) -> bool:
        """Return whether we are in aborting state."""
        return self.aborting_event.is_set()

    @classmethod
    def get_unique_id(cls, task_name) -> str:
        """Generate a unique ID for the task.

        :param task_name: The name of the task
        :type task_name: string
        :return: The unique ID of the task
        :rtype: string
        """
        return f"{time.time()}_{task_name}"

    def get_task_state(self, unique_id: str) -> TaskState:
        """Attempt to get state of QueueTask.

        :param unique_id: Unique ID of the QueueTask
        :type unique_id: str
        :return: State of the QueueTask
        :rtype: TaskState
        """
        if self._task_result:
            _task_result = TaskResult.from_task_result(self._task_result)
            if unique_id == _task_result.unique_id:
                return TaskState.COMPLETED

        if unique_id in self.task_ids_in_queue:
            return TaskState.QUEUED

        if unique_id in self.task_status.keys():
            return TaskState.IN_PROGRESS

        return TaskState.NOT_FOUND

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
