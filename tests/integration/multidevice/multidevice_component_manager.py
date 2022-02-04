"""Component Manager for Multi Device."""
import logging
import time
from functools import partial
from threading import Event
from typing import Callable, List, Optional

from ska_tango_base.base.component_manager import TaskExecutorComponentManager
from ska_tango_base.executor import TaskStatus

from .utils import LongRunningDeviceInterface


class MultiDeviceComponentManager(TaskExecutorComponentManager):
    """Component Manager for Multi Device."""

    def __init__(
        self,
        *args,
        client_devices: List,
        max_workers: Optional[int] = None,
        logger: logging.Logger = None,
        **kwargs,
    ):
        """Init MultiDeviceComponentManager.

        :param client_devices: The list of client devices.
        :type client_devices: List
        """
        self.client_devices = client_devices
        self.logger = logger

        self.clients_interface = None
        if self.client_devices:
            self.clients_interface = LongRunningDeviceInterface(
                self.client_devices, self.logger
            )

        super().__init__(*args, max_workers=max_workers, logger=logger, **kwargs)

    def _non_aborting_lrc(
        self,
        sleep_time: float,
        task_callback: Callable = None,
        task_abort_event: Event = None,
    ):
        """Take a long time to run.

        :param sleep_time: Time to sleep between iterations
        :type sleep_time: float
        :param task_callback: Update state, defaults to None
        :type task_callback: Callable, optional
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """
        retries = 45
        self.logger.info("NonAbortingTask started")
        while retries > 0:
            retries -= 1
            time.sleep(sleep_time)  # This command takes long
        self.logger.info("NonAbortingTask finished")
        task_callback(status=TaskStatus.COMPLETED, result="non_aborting_lrc OK")

    def non_aborting_lrc(self, sleep_time: float, task_callback: Callable = None):
        """Take a long time to complete.

        :param sleep_time: How long to sleep per iteration
        :type sleep_time: float
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
        """
        task_status, response = self.submit_task(
            self._non_aborting_lrc,
            args=[sleep_time],
            task_callback=task_callback,
        )
        return task_status, response

    def _aborting_lrc(
        self,
        sleep_time: float,
        task_callback: Callable = None,
        task_abort_event: Event = None,
    ):
        """Abort the task.

        :param sleep_time: Time to sleep between iterations
        :type sleep_time: float
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """
        retries = 45
        self.logger.info("NonAbortingTask started")
        while (not task_abort_event.is_set()) and retries > 0:
            retries -= 1
            time.sleep(sleep_time)  # This command takes long

        if retries == 0:  # Normal finish
            self.logger.info("NonAbortingTask finished normal")
            task_callback(
                status=TaskStatus.COMPLETED,
                result=f"NonAbortingTask completed {sleep_time}",
            )
        else:  # Aborted finish
            self.logger.info("NonAbortingTask finished aborted")
            task_callback(
                status=TaskStatus.ABORTED,
                result=f"NonAbortingTask Aborted {sleep_time}",
            )

    def aborting_lrc(self, sleep_time: float, task_callback: Callable = None):
        """Abort a task in progress.

        :param sleep_time: How long to sleep per iteration
        :type sleep_time: int
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
        """
        task_status, response = self.submit_task(
            self._aborting_lrc, args=[sleep_time], task_callback=task_callback
        )
        return task_status, response

    @staticmethod
    def _throw_exc(
        logger: logging.Logger,
        task_callback: Callable = None,
        task_abort_event: Event = None,
    ):
        """Throw an exception.

        :param logger: logger
        :type logger: logging.Logger
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        :raises RuntimeError: Just to indicate an issue
        """
        try:
            logger.info("About to raise an error")
            raise RuntimeError("Something went wrong")
        except RuntimeError as err:
            task_callback(status=TaskStatus.COMPLETED, result=f"{err}")

    def throw_exc(self, task_callback: Callable = None):
        """Illustrate exceptions.

        :param task_callback: Update task status
        :type task_callback: Callable
        """
        task_status, response = self.submit_task(
            self._throw_exc, args=[self.logger], task_callback=task_callback
        )
        return task_status, response

    @staticmethod
    def _show_progress(
        logger: logging.Logger,
        sleep_time: float,
        task_callback: Callable = None,
        task_abort_event: Event = None,
    ):
        """Illustrate progress.

        :param logger: logger
        :type logger: logging.Logger
        :param sleep_time: Time to sleep between progress
        :type sleep_time: float
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """
        task_callback(status=TaskStatus.IN_PROGRESS)
        for progress in [1, 25, 50, 74, 100]:
            task_callback(progress=progress)
            logger.info("Progress %s", progress)
            time.sleep(sleep_time)
        task_callback(status=TaskStatus.COMPLETED, result="Progress completed")

    def show_progress(self, sleep_time, task_callback=None):
        """Illustrate progress.

        :param sleep_time: Time to sleep between each progress update
        :type sleep_time: float
        :param task_callback: Update task status
        :type task_callback: Callable
        """
        task_status, response = self.submit_task(
            self._show_progress, args=[self.logger, sleep_time], task_callback=task_callback
        )
        return task_status, response

    @staticmethod
    def _simulate_work(
        logger: logging.Logger,
        sleep_time: float,
        task_callback: Callable = None,
        task_abort_event: Event = None,
    ):
        """Simulate some work for the leaf devices.

        :param logger: logger
        :type logger: logging.Logger
        :param sleep_time: Time to sleep between progress
        :type sleep_time: float
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """
        task_callback(status=TaskStatus.IN_PROGRESS)
        time.sleep(sleep_time)
        logger.info("Finished in leaf device %s", sleep_time)
        task_callback(status=TaskStatus.COMPLETED, result="Finished leaf node")

    def _all_children_completed_cb(self, task_callback, command_name, command_ids):
        self.logger.info("All children %s completed", self.client_devices)
        task_callback(
            status=TaskStatus.COMPLETED,
            result=f"All children completed {self.client_devices}",
        )

    def _call_children(
        self,
        logger: logging.Logger,
        sleep_time: float,
        task_callback: Callable = None,
        task_abort_event: Event = None,
    ):
        """Call child devices.

        :param logger: logger
        :type logger: logging.Logger
        :param sleep_time: How long children should sleep
        :type sleep_time: float
        :param task_callback: Update task status
        :type task_callback: Callable, optional
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """
        self.clients_interface.execute_long_running_command(
            "CallChildren",
            sleep_time,
            on_completion_callback=partial(
                self._all_children_completed_cb, task_callback
            ),
        )

    def call_children(self, sleep_time: float, task_callback: Callable = None):
        """Call child devices or sleep.

        If there are child devices, call them.
        If no children, sleep a bit to simulate some work.

        :param sleep_time: Time to sleep if this device does not have children.
        :type sleep_time: float
        :param task_callback: Update task status
        :type task_callback: Callable
        """
        if self.client_devices:
            task_status, response = self.submit_task(
                self._call_children,
                args=[self.logger, sleep_time],
                task_callback=task_callback,
            )
        else:
            task_status, response = self.submit_task(
                self._simulate_work,
                args=[self.logger, sleep_time],
                task_callback=task_callback,
            )

        return task_status, response
