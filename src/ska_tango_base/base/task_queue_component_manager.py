"""This module implements a component manager that can queue tasks for execution by background threads."""
from __future__ import annotations
import functools
import logging
import threading
import time
import traceback
from queue import Empty, Queue
from threading import Event
from typing import Any, Callable, List
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
            self._currently_executing_id = ""
            self._command_status = []
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
                        # self._currently_executing_id = unique_id
                        # self._command_status = [f"{unique_id}", "IN PROGRESS"]

                        task_result = self.execute_task(task)
                        result = TaskResult(
                            task_result[0], f"{task_result[1]}", unique_id
                        )
                        self._work_queue.task_done()
                        self._update_command_state_callback("", "")
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
        self.is_aborting = threading.Event()
        self.is_stopping = threading.Event()
        self.command_queue_lock = threading.Lock()

        self._command_result = []
        self._command_ids_in_queue = []
        self._commands_in_queue = []
        self._command_status = []
        self._command_progress = []
        self._currently_executing_id = None
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
    def command_result(self, value: list):
        """Set the command result.

        :param value: The command result
        :type value: list
        """
        self._command_result = value

    @property
    def command_ids_in_queue(self) -> list:
        """Command IDs in the queue.

        :return: The command IDs in the queue
        :rtype: list
        """
        return self._command_ids_in_queue

    @command_ids_in_queue.setter
    def command_ids_in_queue(self, value: list):
        """Set the command IDs in the queue.

        :param value: The list of command IDs in the queue
        :type value: list
        """
        self._command_ids_in_queue = value

    @property
    def commands_in_queue(self) -> list:
        """Command names in the queue.

        :return: The list of command names in the queue
        :rtype: list
        """
        return self._commands_in_queue

    @commands_in_queue.setter
    def commands_in_queue(self, value: list):
        """Set the commands in queue.

        :param value: The commands in the queue
        :type value: list
        """
        self._commands_in_queue = value

    @property
    def command_status(self) -> list:
        """Return command status.

        :return: The command status
        :rtype: list
        """
        return self._command_status

    @command_status.setter
    def command_status(self, value: list):
        """Set the command status.

        :param value: The command status
        :type value: list
        """
        self._command_status = value

    @property
    def command_progress(self) -> list:
        """Return the command progress.

        :return: The command progress
        :rtype: list
        """
        return self._command_progress

    @command_progress.setter
    def command_progress(self, value: list):
        """Set the command progress.

        :param value: The command progress.
        :type value: list
        """
        if self._currently_executing_id and value:
            self._command_progress = [
                f"{self._currently_executing_id}",
                f"{value}",
            ]
        else:
            self._command_progress = []

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
            self.update_command_state_callback("", "")
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
            self._commands_in_queue.append(task.func.__name__)
            self.commands_in_queue = self._commands_in_queue
        return unique_id

    def result_callback(self, task_result: TaskResult):
        """Run when the command, taken from the queue have completed to update the appropriate attributes.

        :param task_result: The result of the command
        :type task_result: TaskResult
        """
        self.command_progress = None
        self.command_result = task_result.to_command_result()

        if self.commands_in_queue:
            with self.command_queue_lock:
                self.command_ids_in_queue.pop(0)
                self.commands_in_queue.pop(0)
        self.command_status = []

    def update_command_state_callback(self, unique_id: str, progress_state: str):
        """Update the executing command state.

        :param unique_id: The command unique ID
        :type unique_id: str
        :param progress_state: The state of the command progress
        :type progress_state: str
        """
        self._currently_executing_id = unique_id
        self._command_progress = [unique_id, progress_state]

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
        logger: logging.Logger,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialise a new instance.

        :param message_queue: a message queue for this component manager to use
        :param logger: a logger for this component manager to use
        :param args: positional arguments to pass to the parent class
        :param kwargs: keyword arguments to pass to the parent class.
        """
        self._message_queue = message_queue
        super().__init__(logger, *args, **kwargs)

    def enqueue(
        self,
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> ResultCode:
        """
        Put a method call onto the queue.

        :param func: the method to be called.
        :param args: positional arguments to the method
        :param kwargs: keyword arguments to the method

        :return: a result code
        """
        return self._message_queue.enqueue(func, *args, **kwargs)
