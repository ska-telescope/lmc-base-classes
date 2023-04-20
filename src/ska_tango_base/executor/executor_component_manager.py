# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module provides an abstract component manager for SKA Tango base devices."""
from __future__ import annotations

from typing import Any

from ska_control_model import TaskStatus

from ..base import BaseComponentManager, TaskCallbackType
from .executor import TaskExecutor, TaskFunctionType


# pylint: disable-next=abstract-method  # Yes this is an abstract class.
class TaskExecutorComponentManager(BaseComponentManager):
    """A component manager with support for asynchronous tasking."""

    def __init__(
        self: TaskExecutorComponentManager,
        *args: Any,
        max_workers: int | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialise a new ComponentManager instance.

        :param args: additional positional arguments
        :param max_workers: option maximum number of workers in the pool
        :param kwargs: additional keyword arguments
        """
        self._task_executor = TaskExecutor(max_workers)
        super().__init__(*args, **kwargs)

    def submit_task(
        self: TaskExecutorComponentManager,
        func: TaskFunctionType,
        args: Any = None,
        kwargs: Any = None,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Submit a task to the task executor.

        :param func: function/bound method to be run
        :param args: positional arguments to the function
        :param kwargs: keyword arguments to the function
        :param task_callback: callback to be called whenever the status
            of the task changes.

        :return: tuple of taskstatus & message
        """
        return self._task_executor.submit(
            func, args, kwargs, task_callback=task_callback
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
