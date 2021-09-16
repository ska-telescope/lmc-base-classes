"""This module implements a component manager that has the ability to queue tasks for execution by background threads"""
import functools
import logging
import threading
import time
import traceback
from queue import Empty, Queue
from threading import Event
from typing import Any, Callable

import tango

from ska_tango_base.base.component_manager import BaseComponentManager
from ska_tango_base.commands import ResultCode


class QueueManager:
    """Manages the worker thread and the attributes that will communicate the
    state of the queue.
    """

    class _Worker(threading.Thread):
        """A worker thread that takes tasks from the queue and performs them."""

        def __init__(
            self,
            queue: Queue,
            logger: logging.Logger,
            stopping_event: Event,
            aborting_event: Event,
            result_callback: Callable,
            queue_fetch_timeout: int = 0.1,
        ) -> None:
            """Initiate a worker

            :param self: Worker class
            :type self: QueueManager._Worker
            :param queue: The queue from which tasks are pulled
            :type queue: Queue
            :param logger: Logger to log to
            :type logger: logging.Logger
            :param stopping_event: Indicates whether to get more tasks off the queue
            :type stopping_event: Event
            :param aborting_event: Indicates whther to get more tasks off the queue
            :type aborting_event: Event
            :param result_callback: [description]
            :type result_callback: Callable
            """
            super().__init__()
            self._work_queue = queue
            self._logger = logger
            self._is_stopping = stopping_event
            self._is_aborting = aborting_event
            self._result_callback = result_callback
            self._queue_fetch_timeout = queue_fetch_timeout
            self.setDaemon(True)

        def run(self) -> None:
            with tango.EnsureOmniThread():
                while not self._is_stopping.is_set():
                    if self._is_aborting.is_set():
                        # Drain the Queue since self.is_aborting is set
                        while not self._work_queue.empty():
                            unique_id, _ = self._work_queue.get()
                            self._logger.warning("Aborting task ID [%s]", unique_id)
                            result = (
                                ResultCode.ABORTED,
                                f"{unique_id} Aborted",
                            )
                            self._result_callback(unique_id, result)
                            self._work_queue.task_done()
                        self._is_aborting.clear()
                    try:
                        (unique_id, task) = self._work_queue.get(
                            block=True, timeout=self._queue_fetch_timeout
                        )
                        self._currently_executing_id = unique_id
                        self.command_status = [f"{unique_id}", "IN PROGRESS"]

                        try:
                            result = (ResultCode.OK, task())
                        except Exception as err:
                            result = (
                                ResultCode.FAILED,
                                f"Error: {err} {traceback.format_exc()}",
                            )
                        self._work_queue.task_done()
                        self._result_callback(unique_id, result)
                    except Empty:
                        continue

    def __init__(
        self,
        logger: logging.Logger,
        max_queue_size: int = 0,
        queue_fetch_timeout: float = 0.1,
        num_workers: int = 0,
    ):
        """QueryManager init

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

        self._threads = [
            self._Worker(
                self._work_queue,
                self._logger,
                self.is_stopping,
                self.is_aborting,
                self.result_callback,
            )
            for i in range(num_workers)
        ]
        for thread in self._threads:
            thread.start()

    @property
    def queue_full(self):
        return self._work_queue.full()

    @property
    def command_result(self):
        return self._command_result

    @command_result.setter
    def command_result(self, value):
        self._command_result = value
        # self._tango_device.push_change_event(
        #     "longRunningCommandResult",
        #     self._command_result,
        # )

    @property
    def command_ids_in_queue(self):
        return self._command_ids_in_queue

    @command_ids_in_queue.setter
    def command_ids_in_queue(self, value):
        self._command_ids_in_queue = value
        # self._tango_device.push_change_event(
        #     "longRunningCommandIDsInQueue",
        #     self._command_ids_in_queue,
        # )

    @property
    def commands_in_queue(self):
        return self._commands_in_queue

    @commands_in_queue.setter
    def commands_in_queue(self, value):
        self._commands_in_queue = value
        # self._tango_device.push_change_event(
        #     "longRunningCommandsInQueue",
        #     self._commands_in_queue,
        # )

    @property
    def command_status(self):
        return self._command_status

    @command_status.setter
    def command_status(self, value):
        self._command_status = value
        # self._tango_device.push_change_event(
        #     "longRunningCommandStatus",
        #     self._command_status,
        # )

    @property
    def command_progress(self):
        return self._command_progress

    @command_progress.setter
    def command_progress(self, value):
        if self._currently_executing_id and value:
            self._command_progress = [
                f"{self._currently_executing_id}",
                f"{value}",
            ]
        else:
            self._command_progress = []
        # self._tango_device.push_change_event(
        #     "longRunningCommandProgress",
        #     self._command_progress,
        # )

    def enqueue_command(self, task: functools.partial):
        """Add the task to be done onto the queue

        :param task: The task to execute in a thread
        :type task: functools.partial
        :return: The unique ID of the command
        :rtype: string
        """
        unique_id = self.get_unique_id(task.func.__name__)

        if self.queue_full:
            self.result_callback(unique_id, (ResultCode.REJECTED, "Queue is full"))
            return unique_id

        self._work_queue.put([unique_id, task])

        with self.command_queue_lock:
            self._command_ids_in_queue.append(unique_id)
            self.command_ids_in_queue = self._command_ids_in_queue
            self._commands_in_queue.append(task.func.__name__)
            self.commands_in_queue = self._commands_in_queue
        return unique_id

    def result_callback(self, unique_id, result):
        """Called when the command, taken from the queue have completed to
        update the appropriate attributes

        :param result: The result of the command
        :type result: tuple, (result_code, result_string)
        :param: The unique ID of the command
        :type: string
        """
        self.command_progress = None
        self.command_result = [f"{unique_id}", f"{int(result[0])}", f"{result[1]}"]

        if self.commands_in_queue:
            with self.command_queue_lock:
                self.command_ids_in_queue.pop(0)
                self.commands_in_queue.pop(0)
        self.command_status = []

    def abort_commands(self):
        """Start aborting commands"""
        self.is_aborting.set()

    def exit_worker(self):
        """Exit the worker thread
        NOTE: Long running commands in progress should complete
        """
        self.is_stopping.set()

    def get_unique_id(self, command_name):
        """Generate a unique ID for the command

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

        for worker in self._threads:
            worker._is_aborting.set()

        thread_aborting_state = [worker._is_aborting for worker in self._threads]
        while not any(thread_aborting_state):
            thread_aborting_state = [worker._is_aborting for worker in self._threads]

        for worker in self._threads:
            worker._is_stopping.set()


class TaskQueueComponentManager(BaseComponentManager):
    """A component manager that provides message queue functionality."""

    def __init__(
        self,
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
