# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
This module provides utils used by SKABaseDevice to keep track of long running commands.

It implements the CommandTracker and its supporting classes/functions.
"""
from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from typing import Any, Callable, Protocol, TypedDict

from ska_control_model import ResultCode, TaskStatus
from tango import DevError, DeviceProxy, EventData, EventType

from ..faults import CommandError, ResultCodeError
from ..utils import generate_command_id

__all__ = ["CommandTracker"]


# pylint: disable=too-few-public-methods
class LrcCallback(Protocol):
    """Expected LRC callback signature for typing."""

    def __call__(
        self,
        status: TaskStatus | None = None,
        progress: int | None = None,
        result: dict[str, Any] | list[Any] | None = None,  # TODO: To be decided later
        error: tuple[DevError] | None = None,
        **kwargs: Any,
    ) -> None:
        raise NotImplementedError("LrcCallback is a protocol used only for typing.")


@dataclass
class LrcToken:
    """LRC token that is returned by invoke_lrc."""

    command_id: str
    result_code: ResultCode
    abandon: Callable[[], None]


def invoke_lrc(  # noqa: C901
    proxy: DeviceProxy,
    lrc_callback: LrcCallback,
    command: str,
    command_args: tuple[Any] | None = None,
) -> LrcToken:
    """
    Invoke a long running command (LRC) and monitor its progress with callbacks.

    Subscribe to the relevant LRC attributes and inform the client about change events
    via the provided lrc_callback with either the status, progress, result or error.

    :param proxy: Tango DeviceProxy.
    :param lrc_callback: of client to wrap.
    :param command: name to invoke.
    :param command_args: optional arguments for the command, defaults to None.
    :return: a LrcToken containing the command ID, result code and abandon method.
    :raises CommandError: if the command is rejected.
    :raises ResultCodeError: if the command returns an unexpected result code.
    :raises Exception: Re-raises any exceptions from command_inout.
    """
    calling_thread = threading.current_thread()
    submitted = threading.Event()
    command_id = None

    def wrap_lrc_callback(event: EventData) -> None:
        if event.err:
            lrc_callback(error=event.errors)
            unsubscribe_lrc_events()
            return

        # proxy.subscribe_event emits an event in the calling thread when
        # first called. Their attr_value.value will be ('','') and therefore
        # the index() call below will throw a ValueError.
        # Subsequent events are from internal device thread.
        if threading.current_thread() != calling_thread:
            # Wait for the command to have an ID. Timeout is
            # command_inout timeout + 1.
            if not submitted.wait(timeout=4):
                unsubscribe_lrc_events()
                return

        try:
            cmd_idx = event.attr_value.value.index(command_id)
            lrc_attr_value = event.attr_value.value[cmd_idx + 1]
        except (ValueError, IndexError):
            return
        match event.attr_value.name:
            case "longrunningcommandstatus":
                status = TaskStatus[lrc_attr_value]
                lrc_callback(status=status)
                if status in [
                    TaskStatus.ABORTED,
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                    TaskStatus.REJECTED,
                ]:
                    unsubscribe_lrc_events()
            case "longrunningcommandprogress":
                lrc_callback(progress=int(lrc_attr_value))
            case "longrunningcommandresult":
                lrc_callback(result=json.loads(lrc_attr_value))

    lrc_status_event_id = proxy.subscribe_event(
        "longRunningCommandStatus", EventType.CHANGE_EVENT, wrap_lrc_callback
    )
    lrc_progress_event_id = proxy.subscribe_event(
        "longRunningCommandProgress", EventType.CHANGE_EVENT, wrap_lrc_callback
    )
    lrc_result_event_id = proxy.subscribe_event(
        "longRunningCommandResult", EventType.CHANGE_EVENT, wrap_lrc_callback
    )

    def unsubscribe_lrc_events() -> None:
        proxy.unsubscribe_event(lrc_status_event_id)
        proxy.unsubscribe_event(lrc_progress_event_id)
        proxy.unsubscribe_event(lrc_result_event_id)

    try:
        inout_args = (
            (command, *command_args) if command_args is not None else (command,)
        )
        [[result_code], [command_id]] = proxy.command_inout(*inout_args)
    except Exception:
        unsubscribe_lrc_events()
        raise
    finally:
        # Command submitted, proceed with "subsequent" events.
        submitted.set()

    if result_code == ResultCode.REJECTED:
        unsubscribe_lrc_events()
        raise CommandError(f"{command} command rejected: {command_id}")
    if result_code not in [ResultCode.QUEUED, ResultCode.STARTED]:
        unsubscribe_lrc_events()
        raise ResultCodeError(
            f"Unexpected result code for {command} command: {command_id}"
        )
    return LrcToken(command_id, result_code, unsubscribe_lrc_events)


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


class _CommandData(TypedDict):
    name: str
    status: TaskStatus
    progress: int | None
    completed_callback: Callable[[], None] | None


class CommandTracker:  # pylint: disable=too-many-instance-attributes
    """A class for keeping track of the state and progress of long runnning commands."""

    def __init__(  # pylint: disable=too-many-arguments
        self: CommandTracker,
        queue_changed_callback: Callable[[list[tuple[str, str]]], None],
        status_changed_callback: Callable[[list[tuple[str, TaskStatus]]], None],
        progress_changed_callback: Callable[[list[tuple[str, int]]], None],
        result_callback: Callable[[str, tuple[ResultCode, str]], None],
        exception_callback: Callable[[str, Exception], None] | None = None,
        removal_time: float = 10.0,
    ) -> None:
        """
        Initialise a new instance.

        :param queue_changed_callback: called when the queue changes
        :param status_changed_callback: called when the status changes
        :param progress_changed_callback: called when the progress changes
        :param result_callback: called when command finishes
        :param exception_callback: called in the event of an exception
        :param removal_time: timer
        """
        self.__lock = threading.RLock()
        self.__thread_with_lock = _ThreadContextManager()
        self._queue_changed_callback = queue_changed_callback
        self._status_changed_callback = status_changed_callback
        self._progress_changed_callback = progress_changed_callback
        self._result_callback = result_callback
        self._most_recent_result: tuple[str, tuple[ResultCode, str] | None] | None = (
            None
        )
        self._exception_callback = exception_callback
        self._most_recent_exception: tuple[str, Exception] | None = None
        self._commands: dict[str, _CommandData] = {}
        self._removal_time = removal_time

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

        self._commands[command_id] = {
            "name": command_name,
            "status": TaskStatus.STAGING,
            "progress": None,
            "completed_callback": completed_callback,
        }
        self._queue_changed_callback(self.commands_in_queue)
        self._status_changed_callback(self.command_statuses)
        return command_id

    def _schedule_removal(self: CommandTracker, command_id: str) -> None:
        def remove(command_id: str) -> None:
            del self._commands[command_id]
            if command_id in self._evicted_commands_logged:
                self._evicted_commands_logged.remove(command_id)
            self._queue_changed_callback(self.commands_in_queue)

        threading.Timer(self._removal_time, remove, (command_id,)).start()

    def update_command_info(  # pylint: disable=too-many-arguments
        self: CommandTracker,
        command_id: str,
        status: TaskStatus | None = None,
        progress: int | None = None,
        result: tuple[ResultCode, str] | None = None,
        exception: Exception | None = None,
    ) -> None:
        """
        Update status information on the command.

        :param command_id: the unique command id
        :param status: the status of the asynchronous task
        :param progress: the progress of the asynchronous task
        :param result: the result of the completed asynchronous task
        :param exception: any exception caught in the running task
        """
        with self.__lock, self.__thread_with_lock:
            if exception is not None:
                self._most_recent_exception = (command_id, exception)
                if self._exception_callback is not None:
                    self._exception_callback(command_id, exception)
                # Set a default result for an exception if one is not provided
                if result is None:
                    result = (ResultCode.FAILED, str(exception))
            if result is not None:
                self._most_recent_result = (command_id, result)
                self._result_callback(command_id, result)
            if progress is not None:
                self._commands[command_id]["progress"] = progress
                self._progress_changed_callback(self.command_progresses)
            if status is not None:
                self._commands[command_id]["status"] = status
                self._status_changed_callback(self.command_statuses)

                if status == TaskStatus.COMPLETED:
                    completed_callback = self._commands[command_id][
                        "completed_callback"
                    ]
                    if completed_callback is not None:
                        completed_callback()
                if status in [
                    TaskStatus.ABORTED,
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                    TaskStatus.REJECTED,
                ]:
                    self._commands[command_id]["progress"] = None
                    self._schedule_removal(command_id)

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
                for command_id, command in self._commands.items()
                if command["name"] is not None
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
                for command_id, command in self._commands.items()
                if command["status"] is not None
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
                for command_id, command in self._commands.items()
                if command["progress"] is not None
            )

    @property
    def command_result(
        self: CommandTracker,
    ) -> tuple[str, tuple[ResultCode, str] | None] | None:
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
        if command_id in self._commands:
            return self._commands[command_id]["status"]
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
