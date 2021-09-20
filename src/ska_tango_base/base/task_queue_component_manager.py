"""This module implements a component manager that can queue tasks for execution by background threads."""
from __future__ import annotations
import functools
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

    def to_command_result(self) -> List[str]:
        """Convert TaskResult to command_result.

        :return: The command result
        :rtype: list[str]
        """
        return [f"{self.unique_id}", f"{int(self.result_code)}", f"{self.task_result}"]

    @classmethod
    def from_command_result(cls, command_result: list) -> TaskResult:
        """Convert command_result to TaskResult.

        :param command_result: The command_result [unique_id, result_code, task_result]
        :type command_result: list
        :return: The task result
        :rtype: TaskResult
        """
        return TaskResult(
            result_code=ResultCode(int(command_result[1])),
            task_result=command_result[2],
            unique_id=command_result[0],
        )


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
            :param aborting_event: Indicates whether to get more tasks off the queue
            :type aborting_event: Event
            :param result_callback: The callback to run to pass back results
            :type result_callback: Callable
            :param update_command_state_callback: Callback to update command state
            :type update_command_state_callback: Callable
            """
            super().__init__()
            self._work_queue = queue
            self._logger = logger
            self.is_stopping = stopping_event
            self.is_aborting = aborting_event
            self._result_callback = result_callback
            self._update_command_state_callback = update_command_state_callback
            self._queue_fetch_timeout = queue_fetch_timeout
            self.setDaemon(True)

        def run(self) -> None:
            """Run in the thread.

            Tasks are fetched off the queue and executed.
            if _is_stopping is set the thread wil exit.
            If _is_aborting is set the queue will be emptied. Once emptied it will reset.
            """
            with tango.EnsureOmniThread():
                while not self.is_stopping.is_set():
                    if self.is_aborting.is_set():
                        # Drain the Queue since self.is_aborting is set
                        while not self._work_queue.empty():
                            unique_id, _ = self._work_queue.get()
                            self._logger.warning("Aborting task ID [%s]", unique_id)
                            result = TaskResult(
                                ResultCode.ABORTED, f"{unique_id} Aborted", unique_id
                            )
                            self._result_callback(result)
                            self._work_queue.task_done()
                        self.is_aborting.clear()
                    try:
                        (unique_id, task) = self._work_queue.get(
                            block=True, timeout=self._queue_fetch_timeout
                        )

                        self._update_command_state_callback(unique_id, "IN_PROGRESS")

                        task_result = self.execute_task(task)
                        result = TaskResult(
                            task_result[0], f"{task_result[1]}", unique_id
                        )
                        self._work_queue.task_done()
                        self._result_callback(result)
                    except Empty:
                        continue

        @classmethod
        def execute_task(cls, task: Callable):
            """Execute a task, return results in a standardised format.

            :param task: Callable to execute
            :type task: Callable
            :return: (ResultCode, result)
            :rtype: tuple
            """
            try:
                result = (ResultCode.OK, task())
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
        self.is_aborting = threading.Event()
        self.is_stopping = threading.Event()
        self.command_queue_lock = threading.Lock()
        self.command_status_lock = threading.Lock()

        self._command_result = []
        self._command_ids_in_queue = []
        self._commands_in_queue: Dict[str, str] = {}  # unique_id, command_name
        self._command_status: Dict[str, str] = {}  # unique_id, status
        self._command_progress = {}
        self._threads = []

        # If there's no queue, don't start threads
        if not self._max_queue_size:
            return

        self._threads = [
            self.Worker(
                self._work_queue,
                self._logger,
                self.is_stopping,
                self.is_aborting,
                self.result_callback,
                self.update_command_state_callback,
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
    def command_result(self) -> list:
        """Return the last command result.

        :return: Last command result
        :rtype: list
        """
        return self._command_result

    @command_result.setter
    def command_result(self, value):
        """Set the command_result.

        :param value: the command result
        :type value: list
        """
        self._command_result = value
        if self._on_property_update_callback:
            self._on_property_update_callback("command_result", self.command_result)

    @property
    def command_ids_in_queue(self) -> list:
        """Command IDs in the queue.

        :return: The command IDs in the queue
        :rtype: list
        """
        return self._command_ids_in_queue

    @command_ids_in_queue.setter
    def command_ids_in_queue(self, value):
        """Set command IDs in the queue."""
        self._command_ids_in_queue = value
        if self._on_property_update_callback:
            self._on_property_update_callback(
                "command_ids_in_queue", self.command_ids_in_queue
            )

    @property
    def commands_in_queue(self) -> list:
        """Command names in the queue.

        :return: The list of command names in the queue
        :rtype: list
        """
        return list(self._commands_in_queue.values())

    @commands_in_queue.setter
    def commands_in_queue(self, value):
        """Set command names in the queue.

        :return: The list of command names in the queue
        :rtype: list
        """
        self._commands_in_queue = value
        if self._on_property_update_callback:
            self._on_property_update_callback(
                "commands_in_queue", self.commands_in_queue
            )

    @property
    def command_status(self) -> list:
        """Return command status.

        :return: The command status
        :rtype: list
        """
        result = []
        for unique_id, status in self._command_status.items():
            result.append(unique_id)
            result.append(status)
        return result

    @command_status.setter
    def command_status(self, value: dict):
        """Set the command status.

        :param value: command status dict
        :type value: dict
        """
        self._command_status = value
        if self._on_property_update_callback:
            self._on_property_update_callback("command_status", self.command_status)

    @property
    def command_progress(self) -> list:
        """Return the command progress.

        :return: The command progress
        :rtype: list
        """
        result = []
        for unique_id, progress in self._command_progress.items():
            result.append(unique_id)
            result.append(progress)
        return result

    @command_progress.setter
    def command_progress(self, value: dict):
        """Set the command progress.

        :param value: The command progress dictionary
        :type value: dict
        """
        self._command_progress = value
        if self._on_property_update_callback:
            self._on_property_update_callback("command_progress", self.command_progress)

    def enqueue_command(self, task: functools.partial) -> str:
        """Add the task to be done onto the queue.

        :param task: The task to execute in a thread
        :type task: functools.partial
        :return: The unique ID of the command
        :rtype: string
        """
        unique_id = self.get_unique_id(task.func.__name__)

        # If there is no queue, just execute the command and return
        if self._max_queue_size == 0:
            self.update_command_state_callback(unique_id, "IN_PROGRESS")
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

        with self.command_queue_lock:
            self._command_ids_in_queue.append(unique_id)
            self.command_ids_in_queue = self._command_ids_in_queue
            self._commands_in_queue[unique_id] = task.func.__name__
            self.commands_in_queue = self._commands_in_queue
        return unique_id

    def result_callback(self, task_result: TaskResult):
        """Run when the command, taken from the queue have completed to update the appropriate attributes.

        :param task_result: The result of the command
        :type task_result: TaskResult
        """
        with self.command_status_lock:
            if task_result.unique_id in self._command_status:
                del self._command_status[task_result.unique_id]
            self.command_status = self._command_status
            self._command_result = task_result.to_command_result()
            self.command_result = self._command_result

        with self.command_queue_lock:
            if self.commands_in_queue:
                if task_result.unique_id in self._commands_in_queue:
                    del self._commands_in_queue[task_result.unique_id]
                    self.commands_in_queue = self._commands_in_queue

                if task_result.unique_id in self._command_ids_in_queue:
                    self._command_ids_in_queue.remove(task_result.unique_id)
                    self.command_ids_in_queue = self._command_ids_in_queue

    def update_command_state_callback(self, unique_id: str, status: str):
        """Update the executing command state.

        :param unique_id: The command unique ID
        :type unique_id: str
        :param status: The state of the command
        :type status: str
        """
        self._command_status[unique_id] = status
        self.command_status = self._command_status

    def abort_commands(self):
        """Start aborting commands."""
        self.is_aborting.set()

    def exit_worker(self):
        """Exit the worker thread.

        NOTE: Long running commands in progress should complete
        """
        self.is_stopping.set()

    @classmethod
    def get_unique_id(cls, command_name):
        """Generate a unique ID for the command.

        :param command_name: The name of the command
        :type command_name: string
        :return: The unique ID of the command
        :rtype: string
        """
        return f"{time.time()}_{command_name}"

    def __del__(self) -> None:
        """Release resources prior to instance deletion.

        - Set the workers to aborting, this will empty out the queue and set the result code
          for each task to `Aborted`.
          It will also block any new tasks fo coming in.
        - Wait for the queues to empty out.
        - Set the workers to stopping, this will exit out the running thread.
        """
        if not self._threads:
            return

        for worker in self._threads:
            worker.is_aborting.set()

        thread_aborting_state = [worker.is_aborting for worker in self._threads]
        while not any(thread_aborting_state):
            thread_aborting_state = [worker.is_aborting for worker in self._threads]

        for worker in self._threads:
            worker.is_stopping.set()


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
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Put `func` on the queue. The unique ID for it is returned.

        :param func: The method to call
        :type func: Callable
        :param args: The method arguments
        :type args: Any
        :param kwargs: The method keyword arguments
        :type kwargs: Any
        :return: The unique ID of the queued command
        :rtype: str
        """
        return self.message_queue.enqueue_command(functools.partial(func, args, kwargs))
