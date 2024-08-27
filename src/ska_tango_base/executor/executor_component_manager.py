# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module provides an abstract component manager for SKA Tango base devices."""
from __future__ import annotations

from typing import Any, Callable

from ska_control_model import TaskStatus

from ..base import BaseComponentManager, TaskCallbackType
from .executor import TaskExecutor, TaskFunctionType


# pylint: disable-next=abstract-method  # Yes this is an abstract class.
class TaskExecutorComponentManager(BaseComponentManager):
    """A component manager with support for asynchronous tasking."""

    def __init__(
        self: TaskExecutorComponentManager,
        *args: Any,
        max_queue_size: int = 32,
        **kwargs: Any,
    ) -> None:
        """
        Initialise a new ComponentManager instance.

        :param args: additional positional arguments
        :param max_queue_size: optional maximum size of the tasks input queue
        :param kwargs: additional keyword arguments
        """
        self._task_executor = TaskExecutor()
        super().__init__(*args, **kwargs)
        self._max_queued_tasks = max_queue_size

    @property
    def max_queued_tasks(self) -> int:
        """
        Get the task queue size.

        :return: The task queue size
        """
        return self._max_queued_tasks

    def submit_task(  # pylint: disable=too-many-arguments
        self: TaskExecutorComponentManager,
        func: TaskFunctionType,
        args: Any = None,
        kwargs: Any = None,
        is_cmd_allowed: Callable[[], bool] | None = None,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Submit a task to the task executor.

        :param func: function/bound method to be run
        :param args: positional arguments to the function
        :param kwargs: keyword arguments to the function
        :param is_cmd_allowed: sanity check for func
        :param task_callback: callback to be called whenever the status
            of the task changes.

        :return: tuple of TaskStatus & message
        """
        input_queue_size = self._task_executor.get_input_queue_size()
        if input_queue_size < self.max_queued_tasks:
            return self._task_executor.submit(
                func, args, kwargs, is_cmd_allowed, task_callback=task_callback
            )

        return (
            TaskStatus.REJECTED,
            f"Input queue supports a maximum of {self.max_queued_tasks} commands",
        )

    def abort_tasks(
        self: TaskExecutorComponentManager,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Tell the task executor to abort all tasks.

        :param task_callback: callback to be called whenever the status
            of this abort task changes.

        :return: tuple of TaskStatus & message
        """
        if task_callback:
            task_callback(status=TaskStatus.IN_PROGRESS)
        return self._task_executor.abort(task_callback)
