"""Component Manager for Multi Device."""
from __future__ import annotations

import logging
import time
from functools import partial
from threading import Event
from typing import Any, NoReturn, cast

from ska_control_model import TaskStatus

from ska_tango_base.base import TaskCallbackType
from ska_tango_base.executor import TaskExecutorComponentManager

from .utils import LongRunningDeviceInterface


# TODO: Is it really okay that this method doesn't implement
# start_communicating() and stop_communicating()?
# pylint: disable-next=abstract-method
class MultiDeviceComponentManager(TaskExecutorComponentManager):
    """Component Manager for Multi Device."""

    def __init__(
        self: MultiDeviceComponentManager,
        logger: logging.Logger,
        *args: Any,
        client_devices: list[str],
        **kwargs: Any,
    ) -> None:
        """
        Init MultiDeviceComponentManager.

        :param args: positional arguments to pass to the parent class.
        :param client_devices: list of client devices.
        :param logger: a logger for this component manager to log with.
        :param kwargs: keyword arguments to pass to the parent class.
        """
        self.client_devices = client_devices

        self.clients_interface = None
        if self.client_devices:
            self.clients_interface = LongRunningDeviceInterface(
                self.client_devices, logger
            )

        super().__init__(logger, *args, matrix_operation="", **kwargs)

    def _non_aborting_lrc(
        self: MultiDeviceComponentManager,
        sleep_time: float,
        *,
        task_callback: TaskCallbackType,
        task_abort_event: Event,  # pylint: disable=unused-argument
    ) -> None:
        """
        Take a long time to run.

        :param sleep_time: Time to sleep between iterations
        :param task_callback: Update state, defaults to None
        :param task_abort_event: Check for abort, defaults to None
        """
        retries = 45
        self.logger.info("NonAbortingTask started")
        while retries > 0:
            retries -= 1
            time.sleep(sleep_time)  # This command takes long
        self.logger.info("NonAbortingTask finished")
        if task_callback is not None:
            task_callback(status=TaskStatus.COMPLETED, result="non_aborting_lrc OK")

    def non_aborting_lrc(
        self: MultiDeviceComponentManager,
        sleep_time: float,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Take a long time to complete.

        :param sleep_time: How long to sleep per iteration
        :param task_callback: Update task state, defaults to None

        :return: a tuple consisting of a task status code and a
            human-readable status message.
        """
        task_status, response = self.submit_task(
            self._non_aborting_lrc,
            args=[sleep_time],
            task_callback=task_callback,
        )
        return task_status, response

    def _aborting_lrc(
        self: MultiDeviceComponentManager,
        sleep_time: float,
        *,
        task_callback: TaskCallbackType,
        task_abort_event: Event,
    ) -> None:
        """
        Abort the task.

        :param sleep_time: Time to sleep between iterations
        :param task_callback: Update task state, defaults to None
        :param task_abort_event: Check for abort, defaults to None
        """
        retries = 45
        self.logger.info("AbortingTask started")
        while (not task_abort_event.is_set()) and retries > 0:
            retries -= 1
            time.sleep(sleep_time)  # This command takes long

        if retries == 0:  # Normal finish
            self.logger.info("AbortingTask finished normal")
            if task_callback is not None:
                task_callback(
                    status=TaskStatus.COMPLETED,
                    result=f"AbortingTask completed {sleep_time}",
                )
        else:  # Aborted finish
            self.logger.info("AbortingTask finished aborted")
            if task_callback is not None:
                task_callback(
                    status=TaskStatus.ABORTED,
                    result=f"AbortingTask Aborted {sleep_time}",
                )

    def aborting_lrc(
        self: MultiDeviceComponentManager,
        sleep_time: float,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Abort a task in progress.

        :param sleep_time: How long to sleep per iteration
        :param task_callback: Update task state, defaults to None

        :return: a tuple consisting of a task status code and a
            human-readable status message
        """
        task_status, response = self.submit_task(
            self._aborting_lrc, args=[sleep_time], task_callback=task_callback
        )
        return task_status, response

    @staticmethod
    def _throw_exc(
        logger: logging.Logger,  # pylint: disable-next=unused-argument
        task_callback: TaskCallbackType | None = None,
        task_abort_event: Event | None = None,  # pylint: disable=unused-argument
    ) -> NoReturn:
        """
        Throw an exception.

        :param logger: logger
        :param task_callback: Update task state, defaults to None
        :param task_abort_event: Check for abort, defaults to None
        :raises RuntimeError: Just to indicate an issue
        """
        logger.info("About to raise an error")
        raise RuntimeError("Something went wrong")

    def throw_exc(
        self: MultiDeviceComponentManager, task_callback: TaskCallbackType | None = None
    ) -> tuple[TaskStatus, str]:
        """
        Illustrate exceptions.

        :param task_callback: Update task status

        :return: a tuple consisting of a task status code and a
            human-readable status message.
        """
        task_status, response = self.submit_task(
            self._throw_exc, args=[self.logger], task_callback=task_callback
        )
        return task_status, response

    @staticmethod
    def _show_progress(
        logger: logging.Logger,
        sleep_time: float,
        task_callback: TaskCallbackType | None = None,
        task_abort_event: Event | None = None,  # pylint: disable=unused-argument
    ) -> None:
        """
        Illustrate progress.

        :param logger: logger
        :param sleep_time: Time to sleep between progress
        :param task_callback: Update task state, defaults to None
        :param task_abort_event: Check for abort, defaults to None
        """
        if task_callback is not None:
            task_callback(status=TaskStatus.IN_PROGRESS)
        for progress in [1, 25, 50, 74, 100]:
            if task_callback is not None:
                task_callback(progress=progress)
            logger.info("Progress %s", progress)
            time.sleep(sleep_time)
        if task_callback is not None:
            task_callback(status=TaskStatus.COMPLETED, result="Progress completed")

    def show_progress(
        self: MultiDeviceComponentManager,
        sleep_time: float,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Illustrate progress.

        :param sleep_time: Time to sleep between each progress update
        :param task_callback: Update task status

        :return: a tuple consisting of the task status code and a
            human-readable status message
        """
        task_status, response = self.submit_task(
            self._show_progress,
            args=[self.logger, sleep_time],
            task_callback=task_callback,
        )
        return task_status, response

    @staticmethod
    def _simulate_work(
        logger: logging.Logger,
        sleep_time: float,
        task_callback: TaskCallbackType | None = None,
        task_abort_event: Event | None = None,  # pylint: disable=unused-argument
    ) -> None:
        """
        Simulate some work for the leaf devices.

        :param logger: logger
        :param sleep_time: Time to sleep between progress
        :param task_callback: Update task state, defaults to None
        :param task_abort_event: Check for abort, defaults to None
        """
        if task_callback is not None:
            task_callback(status=TaskStatus.IN_PROGRESS)
        time.sleep(sleep_time)
        logger.info("Finished in leaf device %s", sleep_time)
        if task_callback is not None:
            task_callback(status=TaskStatus.COMPLETED, result="Finished leaf node")

    def _all_children_completed_cb(
        self: MultiDeviceComponentManager,
        task_callback: TaskCallbackType | None,
        command_name: str,
        command_ids: list[str],
    ) -> None:
        self.logger.info("All children %s completed", self.client_devices)
        if task_callback is not None:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=f"All children completed {self.client_devices}",
            )

    def _call_children(
        self: MultiDeviceComponentManager,
        logger: logging.Logger,  # pylint: disable=unused-argument
        sleep_time: float,
        task_callback: TaskCallbackType | None = None,
        task_abort_event: Event | None = None,  # pylint: disable=unused-argument
    ) -> None:
        """
        Call child devices.

        :param logger: logger
        :param sleep_time: How long children should sleep
        :param task_callback: Update task status
        :param task_abort_event: Check for abort, defaults to None
        """
        assert self.clients_interface is not None  # for the type checker
        self.clients_interface.execute_long_running_command(
            "CallChildren",
            sleep_time,
            on_completion_callback=partial(
                self._all_children_completed_cb, task_callback
            ),
        )

    def call_children(
        self: MultiDeviceComponentManager,
        sleep_time: float,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Call child devices or sleep.

        If there are child devices, call them.
        If no children, sleep a bit to simulate some work.

        :param sleep_time: Time to sleep if this device does not have children.
        :param task_callback: Update task status

        :return: a tuple consisting of the task status code and a
            human-readable status message.
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

    def is_transpose_allowed(self: MultiDeviceComponentManager) -> bool:
        """Determine whether transpose is allowed.

        :return: A boolean indicating the matrix is already transposed
        """
        matrix_operation = self.component_state["matrix_operation"]
        return cast(bool, matrix_operation != "transpose")

    def _transpose(
        self: MultiDeviceComponentManager,
        task_callback: TaskCallbackType,
        task_abort_event: Event,  # pylint: disable=unused-argument
    ) -> None:
        """
        Simulate matrix transpose.

        :param task_callback: Update state, defaults to None
        :param task_abort_event: Check for abort, defaults to None
        """
        time.sleep(3.5)
        self._update_component_state(matrix_operation="transpose")
        if task_callback is not None:
            task_callback(status=TaskStatus.COMPLETED, result="Transpose complete")

    def transpose(
        self: MultiDeviceComponentManager,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Transpose a matrix.

        :param task_callback: Update task state, defaults to None

        :return: a tuple consisting of a task status code and a
            human-readable status message.
        """
        task_status, response = self.submit_task(
            self._transpose,
            is_cmd_allowed=self.is_transpose_allowed,
            task_callback=task_callback,
        )
        return task_status, response

    def is_inverse_allowed(self: MultiDeviceComponentManager) -> bool:
        """Determine whether inverse is allowed.

        :return: A boolean indicating the matrix is already inversed
        """
        matrix_operation = self.component_state["matrix_operation"]
        return cast(bool, matrix_operation != "inverse")

    def _invert(
        self: MultiDeviceComponentManager,
        task_callback: TaskCallbackType,
        task_abort_event: Event,  # pylint: disable=unused-argument
    ) -> None:
        """
        Simulate matrix inverstion.

        :param task_callback: Update state, defaults to None
        :param task_abort_event: Check for abort, defaults to None
        """
        time.sleep(3.5)
        self._update_component_state(matrix_operation="inverse")
        if task_callback is not None:
            task_callback(status=TaskStatus.COMPLETED, result="Inverse complete")

    def invert(
        self: MultiDeviceComponentManager,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Invert a matrix.

        :param task_callback: Update task state, defaults to None

        :return: a tuple consisting of a task status code and a
            human-readable status message.
        """
        task_status, response = self.submit_task(
            self._invert,
            is_cmd_allowed=self.is_inverse_allowed,
            task_callback=task_callback,
        )
        return task_status, response
