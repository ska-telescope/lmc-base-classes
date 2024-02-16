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
from ..utils import deprecate_kwarg
from .executor import TaskExecutor, TaskFunctionType


# pylint: disable-next=abstract-method  # Yes this is an abstract class.
class TaskExecutorComponentManager(BaseComponentManager):
    """A component manager with support for asynchronous tasking."""

    @deprecate_kwarg("max_workers", "It will be fixed at 1 in a future release.")
    def __init__(
        self: TaskExecutorComponentManager,
        *args: Any,
        max_workers: int | None = 1,
        max_queue_size: int = 10,
        **kwargs: Any,
    ) -> None:
        """
        Initialise a new ComponentManager instance.

        :param args: additional positional arguments
        :param max_workers: optional maximum number of workers in the pool
        :param max_queue_size: optional maximum size of the input queue
        :param kwargs: additional keyword arguments
        """
        self._max_queue_size = max_queue_size
        self._task_executor = TaskExecutor(max_workers)
        super().__init__(*args, **kwargs)

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

        :return: tuple of taskstatus & message
        """
        input_queue_size = self._task_executor.get_input_queue_size()
        if input_queue_size < self._max_queue_size:
            return self._task_executor.submit(
                func, args, kwargs, is_cmd_allowed, task_callback=task_callback
            )

        return (
            TaskStatus.REJECTED,
            f"Input queue supports a maximum of {self._max_queue_size} commands",
        )

    def abort_commands(
        self: TaskExecutorComponentManager,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Tell the task executor to abort all tasks.

        :param task_callback: callback to be called whenever the status
            of this abort task changes.

        :return: tuple of taskstatus & message
        """
        if task_callback:
            task_callback(status=TaskStatus.IN_PROGRESS)
        return self._task_executor.abort(task_callback)
