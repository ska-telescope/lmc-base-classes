"""Component Manager for Multi Device."""
import logging
from threading import Event
import time
from typing import Callable, List
import tango

from ska_tango_base.base.component_manager import TaskExecutorComponentManager
from ska_tango_base.executor import TaskStatus


class MultiDeviceComponentManager(TaskExecutorComponentManager):
    """Component Manager for Multi Device."""

    @staticmethod
    def _non_aborting_lrc(
        logger: logging.Logger,
        sleep_time: float,
        task_callback: Callable = None,
        task_abort_event: Event = None,
    ):
        """Take a long time to run.

        :param logger: logger
        :type logger: logging.Logger
        :param sleep_time: Time to sleep between iterations
        :type sleep_time: float
        :param task_callback: Update state, defaults to None
        :type task_callback: Callable, optional
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """
        retries = 45
        while retries > 0:
            retries -= 1
            time.sleep(sleep_time)  # This command takes long
            logger.info(
                "In NonAbortingTask repeating %s",
                retries,
            )
        task_callback(status=TaskStatus.COMPLETED, result="non_aborting_lrc OK")

    def non_aborting_lrc(self, argin: float, task_callback: Callable = None):
        """Take a long time to complete.

        :param argin: How long to sleep per iteration
        :type argin: float
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
        """
        task_status, response = self.submit_task(
            self._non_aborting_lrc,
            args=[self.logger, argin],
            task_callback=task_callback,
        )
        return task_status, response

    @staticmethod
    def _aborting_lrc(logger, sleep_time, task_callback=None, task_abort_event=None):
        retries = 45
        while (not task_abort_event.is_set()) and retries > 0:
            retries -= 1
            time.sleep(sleep_time)  # This command takes long
            logger.info("In NonAbortingTask repeating %s", retries)

        if retries == 0:  # Normal finish
            task_callback(
                status=TaskStatus.COMPLETED,
                result=f"NonAbortingTask completed {sleep_time}",
            )
        else:  # Aborted finish
            task_callback(
                status=TaskStatus.ABORTED,
                result=f"NonAbortingTask Aborted {sleep_time}",
            )

    def aborting_lrc(self, argin: float, task_callback: Callable = None):
        """Abort a task in progress.

        :param argin: How long to sleep per iteration
        :type argin: int
        :param task_callback: Update task state, defaults to None
        :type task_callback: Callable, optional
        """
        task_status, response = self.submit_task(
            self._aborting_lrc, args=[self.logger, argin], task_callback=task_callback
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

    def show_progress(self, argin, task_callback=None):
        """Illustrate progress.

        :param argin: Time to sleep between each progress update
        :type argin: float
        :param task_callback: Update task status
        :type task_callback: Callable
        """
        task_status, response = self.submit_task(
            self._show_progress, args=[self.logger, argin], task_callback=task_callback
        )
        return task_status, response

    @staticmethod
    def _call_children(
        logger: logging.Logger,
        sleep_time: float,
        client_devices: List,
        task_callback: Callable = None,
        task_abort_event: Event = None,
    ):
        """Call child devices.

        :param logger: logger
        :type logger: logging.Logger
        :param sleep_time: How long children should sleep
        :type sleep_time: float
        :param client_devices: List of child devices
        :type client_devices: List
        :param task_callback: Update task status
        :type task_callback: Callable, optional
        :param task_abort_event: Check for abort, defaults to None
        :type task_abort_event: Event, optional
        """
        if client_devices:
            for device in client_devices:
                logger.info("Calling child %s", device)
                proxy = tango.DeviceProxy(device)
                proxy.CallChildren(sleep_time)
            task_callback(
                status=TaskStatus.COMPLETED,
                result=f"Called children {client_devices}",
            )
        else:
            task_callback(status=TaskStatus.IN_PROGRESS)
            logger.info("Waiting in leaf device %s", sleep_time)
            time.sleep(sleep_time)
            task_callback(status=TaskStatus.COMPLETED, result="Finished leaf node")

    def call_children(
        self, argin: float, client_devices: List, task_callback: Callable = None
    ):
        """Call child devices.

        :param argin: Time to sleep if this device does not have children.
        :type argin: float
        :param client_devices: List of client devices
        :type client_devices: List
        :param task_callback: Update task status
        :type task_callback: Callable
        """
        task_status, response = self.submit_task(
            self._call_children,
            args=[self.logger, argin, client_devices],
            task_callback=task_callback,
        )
        return task_status, response
