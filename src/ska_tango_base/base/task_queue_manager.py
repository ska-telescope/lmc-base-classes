"""
This module provides a QueueManager, TaskResult and QueueTask classes.

* **TaskUniqueId**: is a convenience class for parsing and generating the IDs used
  to identify the tasks.

* **TaskResult**: is a convenience class for parsing and formatting the
  results of a task.

* **QueueTask**: is a class that instances of which can be added to the queue for execution
  by background threads.

* **QueueManager**: that implements the queue and thread worker functionality.

************
TaskUniqueId
************

This is a simple convenience class for generating and parsing the IDs that identify tasks.

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
from uuid import uuid4
from queue import Empty, Queue
from datetime import datetime
from threading import Event
from inspect import signature
from typing import Any, Callable, Dict, Optional, Tuple, Union

import tango

from ska_tango_base.commands import BaseCommand, ResultCode

MAX_QUEUE_SIZE = 100  # Maximum supported size of the queue
MAX_WORKER_COUNT = 50  # Maximum number of workers supported


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


class TaskUniqueId:
    """Convenience class for the unique ID of a task."""

    def __init__(self, id_uuid: str, id_datetime: datetime, id_task_name: str) -> None:
        """Create a TaskUniqueId instance.

        :param id_uuid: The uuid portion of the task identifier
        :type id_uuid: str
        :param id_datetime: The datetime portion of the task identifier
        :type id_datetime: datetime
        :param id_task_name: The task name portion of the task identifier
        :type id_task_name: str
        """
        self.id_uuid = id_uuid
        self.id_datetime = id_datetime
        self.id_task_name = id_task_name

    @classmethod
    def generate_unique_id(cls, task_name: str) -> str:
        """Return a new unique ID."""
        return f"{time.time()}_{uuid4().fields[-1]}_{task_name}"

    @classmethod
    def from_unique_id(cls, unique_id: str):
        """Parse a unique ID."""
        parts = unique_id.split("_")
        id_uuid = parts[1]
        id_datetime = datetime.fromtimestamp(float(parts[0]))
        id_task_name = "_".join(parts[2:])
        return TaskUniqueId(
            id_uuid=id_uuid, id_datetime=id_datetime, id_task_name=id_task_name
        )


class TaskResult:
    """Convenience class for results."""

    result_code: ResultCode
    task_result: str
    unique_id: str

    def __init__(
        self, result_code: ResultCode, task_result: str, unique_id: str
    ) -> None:
        """Create the TaskResult.

        :param result_code: The ResultCode of the task result
        :type result_code: ResultCode
        :param task_result: The string of the task result
        :type task_result: str
        :param unique_id: The unique identifier of a task.
        :type unique_id: str
        """
        self.result_code = result_code
        self.task_result = task_result
        self.unique_id = unique_id

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

    @classmethod
    def from_response_command(cls, command_result: Tuple[str, str]) -> TaskResult:
        """Convert from ResponseCommand to TaskResult.

        :param command_result: The task_result (unique_id, result_code)
        :type command_result: tuple
        :return: The task result
        :rtype: TaskResult
        :raises: ValueError
        """
        if not command_result or len(command_result) != 2:
            raise ValueError(f"Cannot parse task_result {command_result}")

        return TaskResult(
            result_code=ResultCode(int(command_result[1])),
            task_result="",
            unique_id=command_result[0],
        )

    def get_task_unique_id(self) -> TaskUniqueId:
        """Convert from the unique_id string to TaskUniqueId."""
        return TaskUniqueId.from_unique_id(self.unique_id)


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
            update_progress_callback: Callable,
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
            self._update_progress_callback = update_progress_callback
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
                            unique_id, _, _ = self._work_queue.get()
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
                        (unique_id, task, argin) = self._work_queue.get(
                            block=True, timeout=self._queue_fetch_timeout
                        )

                        self._update_command_state_callback(unique_id, "IN_PROGRESS")
                        self.current_task_id = unique_id
                        setattr(task, "update_progress", self._update_task_progress)
                        result = self.execute_task(task, argin, unique_id)
                        self._result_callback(result)
                        self._work_queue.task_done()
                    except Empty:
                        continue
                return

        def _update_task_progress(self, progress: str) -> None:
            """Update the current task progress.

            :param progress: An indication of progress
            :type progress: str
            """
            self.current_task_progress = progress
            self._update_progress_callback()

        @classmethod
        def execute_task(
            cls, task: BaseCommand, argin: Any, unique_id: str
        ) -> TaskResult:
            """Execute a task, return results in a standardised format.

            :param task: Task to execute
            :type task: BaseCommand
            :param argin: The argument for the command
            :type argin: Any
            :param unique_id: The task unique ID
            :type unique_id: str
            :return: The result of the task
            :rtype: TaskResult
            """
            try:
                if hasattr(task, "is_allowed"):
                    is_allowed_signature = signature(task.is_allowed)
                    if "raise_if_disallowed" in is_allowed_signature.parameters:
                        is_task_allowed = task.is_allowed(raise_if_disallowed=True)
                    else:
                        is_task_allowed = task.is_allowed()
                    if not is_task_allowed:
                        return TaskResult(
                            ResultCode.NOT_ALLOWED, "Command not allowed", unique_id
                        )
                if argin:
                    result = task(argin)
                else:
                    result = task()
                # If the response is (ResultCode, Any)
                if (
                    isinstance(result, tuple)
                    and len(result) == 2
                    and isinstance(result[0], ResultCode)
                ):
                    return TaskResult(result[0], f"{result[1]}", unique_id)
                # else set as OK and return the string of whatever the result was
                result = TaskResult(ResultCode.OK, f"{result}", unique_id)
            except Exception as err:
                result = TaskResult(
                    ResultCode.FAILED,
                    f"Error: {err} {traceback.format_exc()}",
                    unique_id,
                )
            return result

    def __init__(
        self: QueueManager,
        max_queue_size: int = 0,
        queue_fetch_timeout: float = 0.1,
        num_workers: int = 0,
        logger: Optional[logging.Logger] = None,
        push_change_event: Optional[Callable] = None,
    ):
        """Init QueryManager.

        Creates the queue and starts the thread that will execute tasks
        from it.

        :param max_queue_size: The maximum size of the queue
        :type max_queue_size: int
        :param max_queue_size: The time to wait for items in the queue
        :type max_queue_size: float
        :param num_workers: The number of worker threads to start
        :type num_workers: float
        :param logger: Python logger
        :type logger: logging.Logger
        """
        if max_queue_size > MAX_QUEUE_SIZE:
            raise ValueError(f"A maximum queue size of {MAX_QUEUE_SIZE} is supported")
        if num_workers > MAX_WORKER_COUNT:
            raise ValueError(
                f"A maximum number of {MAX_WORKER_COUNT} workers is supported"
            )
        self._max_queue_size = max_queue_size
        self._work_queue = Queue(self._max_queue_size)
        self._queue_fetch_timeout = queue_fetch_timeout
        self._push_change_event = push_change_event
        self.stopping_event = threading.Event()
        self.aborting_event = threading.Event()
        self._property_update_lock = threading.Lock()
        self._logger = logger if logger else logging.getLogger(__name__)

        self._task_result: Union[Tuple[str, str, str], Tuple[()]] = ()
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
                self.update_progress_callback,
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
    def task_result(self) -> Union[Tuple[str, str, str], Tuple[()]]:
        """Return the last task result.

        :return: Last task result
        :rtype: Tuple
        """
        return self._task_result

    @property
    def task_ids_in_queue(
        self,
    ) -> Tuple[str,]:  # noqa: E231
        """Task IDs in the queue.

        :return: The task IDs in the queue
        :rtype: tuple
        """
        return tuple(self._tasks_in_queue.keys())

    @property
    def tasks_in_queue(
        self,
    ) -> Tuple[str,]:  # noqa: E231
        """Task names in the queue.

        :return: The list of task names in the queue
        :rtype: tuple
        """
        return tuple(self._tasks_in_queue.values())

    @property
    def task_status(
        self,
    ) -> Tuple[str,]:  # noqa: E231
        """Return task status.

        :return: The task status pairs (id, status)
        :rtype: tuple(str,)
        """
        statuses = []
        for u_id, status in self._task_status.copy().items():
            statuses.append(u_id)
            statuses.append(status)
        return tuple(statuses)

    @property
    def task_progress(
        self,
    ) -> Tuple[Optional[str],]:  # noqa: E231
        """Return the task progress.

        :return: The task progress pairs (id, progress)
        :rtype: tuple(str,)
        """
        progress = []
        for worker in self._threads:
            if worker.current_task_id:
                progress.append(worker.current_task_id)
                progress.append(worker.current_task_progress)
        return tuple(progress)

    def enqueue_task(
        self, task: BaseCommand, argin: Optional[Any] = None
    ) -> Tuple[str, ResultCode]:
        """Add the task to be done onto the queue.

        :param task: The task to execute in a thread
        :type task: BaseCommand
        :param argin: The parameter for the command
        :type argin: Any
        :return: The unique ID of the command
        :rtype: string
        """
        unique_id = self.generate_unique_id(task.__class__.__name__)

        # Inject the events into the task
        setattr(task, "aborting_event", self.aborting_event)
        setattr(task, "stopping_event", self.stopping_event)

        # If there is no queue, just execute the command and return
        if self._max_queue_size == 0:
            self.update_task_state_callback(unique_id, "IN_PROGRESS")

            # This task blocks, so no need to update progress
            setattr(task, "update_progress", lambda x: None)

            result = self.Worker.execute_task(task, argin, unique_id)
            self.result_callback(result)
            return unique_id, result.result_code

        if self.queue_full:
            self.result_callback(
                TaskResult(ResultCode.REJECTED, "Queue is full", unique_id)
            )
            return unique_id, ResultCode.REJECTED

        self._work_queue.put([unique_id, task, argin])
        with self._property_update_lock:
            self._tasks_in_queue[unique_id] = task.__class__.__name__
        self._on_property_change("longRunningCommandsInQueue", self.tasks_in_queue)
        self._on_property_change("longRunningCommandIDsInQueue", self.task_ids_in_queue)
        return unique_id, ResultCode.QUEUED

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

        self._on_property_change("longRunningCommandResult", self.task_result)

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
            self._on_property_change("longRunningCommandsInQueue", self.tasks_in_queue)
            self._on_property_change(
                "longRunningCommandIDsInQueue", self.task_ids_in_queue
            )

        with self._property_update_lock:
            self._task_status[unique_id] = status
        self._on_property_change("longRunningCommandStatus", self.task_status)

    def update_progress_callback(self):
        """Trigger the property change callback back to the device."""
        self._on_property_change("longRunningCommandProgress", self.task_progress)

    def _on_property_change(self, property_name: str, property_value: Any):
        """Trigger when a property changes value.

        :param property_name: The property name
        :type property_name: str
        :param property_name: The property value
        :type property_name: Any
        """
        if self._push_change_event:
            self._push_change_event(property_name, property_value)

    def abort_tasks(self):
        """Start aborting tasks."""
        self.aborting_event.set()

    def resume_tasks(self):
        """Unsets aborting so tasks can be picked up again."""
        self.aborting_event.clear()

    def stop_tasks(self):
        """Set stopping_event on each thread so it exists out. Killing the thread."""
        self.stopping_event.set()

    @property
    def is_aborting(self) -> bool:
        """Return whether we are in aborting state."""
        return self.aborting_event.is_set()

    @classmethod
    def generate_unique_id(cls, task_name) -> str:
        """Generate a unique ID for the task.

        :param task_name: The name of the task
        :type task_name: string
        :return: The unique ID of the task
        :rtype: string
        """
        return TaskUniqueId.generate_unique_id(task_name)

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

        if unique_id in self.task_status:
            return TaskState.IN_PROGRESS

        return TaskState.NOT_FOUND

    def __len__(self) -> int:
        """Approximate length of the queue.

        :return: The approximate length of the queue
        :rtype: int
        """
        return self._work_queue.qsize()

    def __bool__(self):
        """Ensure `if QueueManager()` works as expected with `__len__` being overridden.

        :return: True
        :rtype: bool
        """
        return True
