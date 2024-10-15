# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module implements the CommandTracker and its supporting classes/functions."""
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from itertools import chain
from typing import Any, Callable, TypedDict
from warnings import warn

from ska_control_model import ResultCode, TaskStatus

from ..utils import generate_command_id
from .base_component_manager import JSONData

__all__ = ["CommandTracker"]


class _ThreadContextManager:
    def __init__(self) -> None:
        self._thread: threading.Thread | None = None

    def __enter__(self) -> None:
        self._thread = threading.current_thread()

    def __exit__(self, *args: Any) -> None:
        self._thread = None

    def get_thread(self) -> threading.Thread | None:
        """
        Get the current thread in this context.

        :return: the current thread or None if context not used.
        """
        return self._thread


class _CommandData(TypedDict, total=False):
    name: str
    status: TaskStatus
    submitted_time: str
    started_time: str  # Optional
    progress: int  # Optional
    result: JSONData  # Optional
    finished_time: str  # Optional
    completed_callback: Callable[[], None]  # Optional
    removed: bool  # TODO: This key is needed for the deprecated LRC attributes to
    #                      retain the removal timer functionality.


UserLrcAttr = dict[str, _CommandData]
LRC_FINISHED_MAX_LENGTH = 100


class CommandTracker:  # pylint: disable=too-many-instance-attributes
    """A class for keeping track of the state and progress of long runnning commands."""

    def __init__(  # pylint: disable=too-many-arguments
        self: CommandTracker,
        queue_changed_callback: Callable[[list[tuple[str, str]]], None],
        status_changed_callback: Callable[[list[tuple[str, TaskStatus]]], None],
        progress_changed_callback: Callable[[list[tuple[str, int]]], None],
        result_callback: Callable[[str, JSONData], None],
        exception_callback: Callable[[str, Exception], None] | None = None,
        event_callback: Callable[[str, JSONData], None] | None = None,
        update_user_attributes_callback: (
            Callable[[UserLrcAttr, UserLrcAttr, UserLrcAttr], None] | None
        ) = None,
        removal_time: float = 10.0,
    ) -> None:
        """
        Initialise a new instance.

        :param queue_changed_callback: called when the queue changes
        :param status_changed_callback: called when the status changes
        :param progress_changed_callback: called when the progress changes
        :param result_callback: called when command finishes
        :param exception_callback: called in the event of an exception
        :param event_callback: called for any and all change events
        :param update_user_attributes_callback: called for any and all change events
        :param removal_time: timer
        """
        # Take __thread_with_lock if you are going to do a Tango operation
        # while holding __lock
        self.__lock = threading.RLock()
        self.__thread_with_lock = _ThreadContextManager()
        self._queue_changed_callback = queue_changed_callback
        self._status_changed_callback = status_changed_callback
        self._progress_changed_callback = progress_changed_callback
        self._result_callback = result_callback
        self._most_recent_result: tuple[str, JSONData] | None = None
        self._exception_callback = exception_callback
        self._most_recent_exception: tuple[str, Exception] | None = None
        self._event_callback = event_callback
        self._update_user_attributes_callback = update_user_attributes_callback
        self._lrc_stage_queue: UserLrcAttr = {}
        self._lrc_executing: UserLrcAttr = {}
        self._lrc_finished: UserLrcAttr = {}
        self._removal_time = removal_time
        # TODO: This private variable may be overridden by SKABaseDevice to support
        # a longer length of the deprecated LRC attributes, until they are removed.
        self._lrc_finished_max_length = LRC_FINISHED_MAX_LENGTH

        # Keep track of the command IDs which have been evicted from the list
        # being reported by the LRC attributes because we have run out of space
        # so that we only log each one once
        self._evicted_commands_logged: list[str] = []

    def new_command(
        self: CommandTracker,
        command_name: str,
        completed_callback: Callable[[], None] | None = None,
    ) -> str:
        """
        Create a new command.

        :param command_name: the command name
        :param completed_callback: an optional callback for command completion

        :return: a unique command id
        """
        command_id = generate_command_id(command_name)

        self._lrc_stage_queue[command_id] = {
            "name": command_name,
            "status": TaskStatus.STAGING,
            "submitted_time": datetime.now(timezone.utc).isoformat(),
        }
        if completed_callback is not None:
            self._lrc_stage_queue[command_id]["completed_callback"] = completed_callback
        self._queue_changed_callback(self.commands_in_queue)
        self._status_changed_callback(self.command_statuses)
        if self._event_callback is not None:
            self._event_callback(command_id, {"status": TaskStatus.STAGING})
        return command_id

    def _schedule_removal(self: CommandTracker, command_id: str) -> None:
        def remove(command_id: str) -> None:
            if command_id in self._lrc_finished:
                self._lrc_finished[command_id]["removed"] = True
            if command_id in self._evicted_commands_logged:
                self._evicted_commands_logged.remove(command_id)
            self._queue_changed_callback(self.commands_in_queue)

        threading.Timer(self._removal_time, remove, (command_id,)).start()

    # pylint: disable=too-many-arguments, too-many-branches, too-many-statements
    def update_command_info(  # noqa: C901
        self: CommandTracker,
        command_id: str,
        status: TaskStatus | None = None,
        progress: int | None = None,
        result: JSONData = None,
        exception: Exception | None = None,
    ) -> None:
        """
        Update status information on the command.

        :param command_id: the unique command id
        :param status: the status of the asynchronous task
        :param progress: the progress of the asynchronous task
        :param result: the result of the completed asynchronous task
        :param exception: any exception caught in the running task
        :raises TypeError: if status is not the TaskStatus enum type
        """
        # All changes to the _lrc_stage_queue, _lrc_executing and _lrc_finished dicts
        # are made here while the CommandTracker has a lock, as well as the callbacks
        # updating the deprecated and new LRC attributes. This is to ensure any events
        # received by this method (used as a callback in commands) are completely
        # processed before subsequent events, thereby preventing race conditions.
        #
        # A command can only be in one of the three dicts at a time, given its status:
        # STAGING       -> _lrc_stage_queue
        # QUEUED        -> _lrc_stage_queue
        # IN_PROGRESS   -> _lrc_executing
        # ABORTED       -> _lrc_finished
        # COMPLETED     -> _lrc_finished
        # REJECTED      -> _lrc_finished
        # FAILED        -> _lrc_finished
        # The update_user_attributes_callback() is called for all status changes except
        # the initial STAGING status, therefore the lrcQueue tango attribute only
        # contain commands in QUEUED status. A new command can go from _lrc_stage_queue
        # to _lrc_executing or straight to _lrc_finished if REJECTED or ABORTED.
        #
        # TODO: At the time of writing, this method is overly complex because the
        # deprecated LRC attributes and the order of their change events must be
        # preserved while supporting the newer user facing LRC attributes: lrcQueue,
        # lrcExecuting and lrcFinished that correspond to the three private LRC dicts.
        # When the deprecated LRC attributes are eventually removed, this method
        # (and the rest of the CommandTracker) can be simplified.
        with self.__lock, self.__thread_with_lock:
            if exception is not None:
                self._most_recent_exception = (command_id, exception)
                if self._exception_callback is not None:
                    self._exception_callback(command_id, exception)
                # Set a default result for an exception if one is not provided
                if result is None:
                    result = (ResultCode.FAILED, str(exception))
            event: dict[str, Any] = {}
            if status is not None:
                if not isinstance(status, TaskStatus):
                    raise TypeError(
                        f"'{command_id}' command's status is invalid type: "
                        f"{type(status)}. Must be 'TaskStatus' enum!"
                    )
                event["status"] = status
                if command_id in self._lrc_stage_queue:
                    self._lrc_stage_queue[command_id]["status"] = status
                if (
                    status == TaskStatus.IN_PROGRESS
                    and command_id in self._lrc_stage_queue
                ):
                    self._lrc_executing[command_id] = self._lrc_stage_queue.pop(
                        command_id
                    )
                    self._lrc_executing[command_id]["started_time"] = datetime.now(
                        timezone.utc
                    ).isoformat()
                elif status in [
                    TaskStatus.ABORTED,
                    TaskStatus.COMPLETED,
                    TaskStatus.REJECTED,
                    TaskStatus.FAILED,
                ]:
                    if command_id in self._lrc_stage_queue:
                        self._lrc_finished[command_id] = self._lrc_stage_queue.pop(
                            command_id
                        )
                    elif command_id in self._lrc_executing:
                        self._lrc_finished[command_id] = self._lrc_executing.pop(
                            command_id
                        )
                    self._lrc_finished[command_id].pop("progress", None)
                    self._lrc_finished[command_id].update(
                        {
                            "finished_time": datetime.now(timezone.utc).isoformat(),
                            "status": status,
                        }
                    )
            if result is not None:
                try:
                    json.dumps(result)
                    event["result"] = result
                except TypeError:
                    warn(
                        f"'{command_id}' command's result is not JSON serialisable: "
                        "Converting it to a str. "
                        "Its type(s) may be checked and enforced in the future.",
                        FutureWarning,
                    )
                    event["result"] = str(result)
                if command_id in self._lrc_stage_queue:
                    self._lrc_stage_queue[command_id]["result"] = event["result"]
                elif command_id in self._lrc_executing:
                    self._lrc_executing[command_id]["result"] = event["result"]
                elif command_id in self._lrc_finished:
                    self._lrc_finished[command_id]["result"] = event["result"]
                self._most_recent_result = (command_id, event["result"])
                self._result_callback(command_id, event["result"])
            if progress is not None:
                try:
                    event["progress"] = int(progress)
                except (ValueError, TypeError):
                    warn(
                        f"'{command_id}' command's progress is not an int, "
                        f"but {type(progress)}: Converting it to a str. "
                        "Its type may be checked and enforced in the future.",
                        FutureWarning,
                    )
                    event["progress"] = str(progress)
                if command_id in self._lrc_stage_queue:
                    self._lrc_stage_queue[command_id]["progress"] = event["progress"]
                elif command_id in self._lrc_executing:
                    self._lrc_executing[command_id]["progress"] = event["progress"]
                elif command_id in self._lrc_finished:
                    self._lrc_finished[command_id]["progress"] = event["progress"]
                self._progress_changed_callback(self.command_progresses)
            # The status related callbacks are called after result/progress to preserve
            # the order of change events for the deprecated LRC attributes.
            if status is not None:
                self._status_changed_callback(self.command_statuses)

                if status == TaskStatus.COMPLETED:
                    completed_callback = self._lrc_finished[command_id].get(
                        "completed_callback"
                    )
                    if completed_callback is not None:
                        completed_callback()
                if status in [
                    TaskStatus.ABORTED,
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                    TaskStatus.REJECTED,
                ]:
                    self._schedule_removal(command_id)
            if self._event_callback is not None:
                self._event_callback(command_id, event)
            # Prune oldest finished commands
            if len(self._lrc_finished) > self._lrc_finished_max_length:
                oldest = next(iter(self._lrc_finished))
                self._lrc_finished.pop(oldest)
            # This callback must always be last to ensure all required updates are done
            if self._update_user_attributes_callback is not None:
                self._update_user_attributes_callback(
                    self._lrc_stage_queue, self._lrc_executing, self._lrc_finished
                )

    def has_current_thread_locked(self: CommandTracker) -> bool:
        """
        Has CommandTracker locked the current thread for updating the LRC attributes.

        :return: if current thread is locked by CommandTracker.
        """
        return self.__thread_with_lock.get_thread() == threading.current_thread()

    @property
    def commands_in_queue(self: CommandTracker) -> list[tuple[str, str]]:
        """
        Return a list of commands in the queue.

        :return: a list of (command_id, command_name) tuples, ordered by
            when invoked.
        """
        with self.__lock:
            return list(
                (command_id, command["name"])
                for command_id, command in chain(
                    self._lrc_finished.items(),
                    self._lrc_executing.items(),
                    self._lrc_stage_queue.items(),
                )
                if "removed" not in command
            )

    @property
    def command_statuses(self: CommandTracker) -> list[tuple[str, TaskStatus]]:
        """
        Return a list of command statuses for commands in the queue.

        :return: a list of (command_id, status) tuples, ordered by when
            invoked.
        """
        with self.__lock:
            return list(
                (command_id, command["status"])
                for command_id, command in chain(
                    self._lrc_finished.items(),
                    self._lrc_executing.items(),
                    self._lrc_stage_queue.items(),
                )
                if "removed" not in command
            )

    @property
    def command_progresses(self: CommandTracker) -> list[tuple[str, int]]:
        """
        Return a list of command progresses for commands in the queue.

        :return: a list of (command_id, progress) tuples, ordered by
            when invoked.
        """
        with self.__lock:
            return list(
                (command_id, command["progress"])
                for command_id, command in chain(
                    self._lrc_finished.items(),
                    self._lrc_executing.items(),
                    self._lrc_stage_queue.items(),
                )
                if "progress" in command and "removed" not in command
            )

    @property
    def command_result(
        self: CommandTracker,
    ) -> tuple[str, JSONData] | None:
        """
        Return the result of the most recently completed command.

        :return: a (command_id, result) tuple. If no command has
            completed yet, then None.
        """
        return self._most_recent_result

    @property
    def command_exception(self: CommandTracker) -> tuple[str, Exception] | None:
        """
        Return the most recent exception, if any.

        :return: a (command_id, exception) tuple. If no command has
            raised an uncaught exception, then None.
        """
        return self._most_recent_exception

    def get_command_status(self: CommandTracker, command_id: str) -> TaskStatus:
        """
        Return the current status of a running command.

        :param command_id: the unique command id

        :return: a status of the asynchronous task.
        """
        with self.__lock:
            for lrc_dict in (
                self._lrc_stage_queue,
                self._lrc_executing,
                self._lrc_finished,
            ):
                if command_id in lrc_dict:
                    return lrc_dict[command_id]["status"]
        return TaskStatus.NOT_FOUND

    def evict_command(self: CommandTracker, command_id: str) -> bool:
        """
        Add to the list of commands not to be reported by the LRC attributes.

        This is used to ensure we don't overflow the attribute bounds when
        there are too many finished commands lingering for the removal_period.

        :param command_id: the unique command id
        :return: True if the command was not already evicted.
        """
        if command_id not in self._evicted_commands_logged:
            self._evicted_commands_logged.append(command_id)
            return True
        return False
