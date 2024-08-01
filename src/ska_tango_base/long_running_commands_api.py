# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module provides a convenience client API for invoking long running commands."""
from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from typing import Any, Callable, Protocol

from ska_control_model import ResultCode, TaskStatus
from tango import DevError, DeviceProxy, EventData, EventType

from ska_tango_base.faults import CommandError, ResultCodeError


# pylint: disable=too-few-public-methods
class LrcCallback(Protocol):
    """Expected LRC callback signature for typing."""

    def __call__(  # noqa: D102
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
    :raises Exception: Any other tango exceptions from subscribe_event or command_inout.
    """
    calling_thread = threading.current_thread()
    submitted = threading.Event()
    command_id = None

    def wrap_lrc_callback(event: EventData) -> None:
        # Check for tango error
        if event.err:
            lrc_callback(error=event.errors)
            unsubscribe_lrc_events()
            return

        # Wait for the command to have an ID. Timeout is command_inout timeout + 1.
        if threading.current_thread() != calling_thread:
            if not submitted.wait(timeout=4):
                unsubscribe_lrc_events()
                return

        # proxy.subscribe_event emits an event in the calling thread when first called.
        # The attr_value.value will be ('','') and therefore the index() call below will
        # throw a ValueError. Subsequent events are from internal device thread.
        try:
            cmd_idx = event.attr_value.value.index(command_id)
            lrc_attr_value = event.attr_value.value[cmd_idx + 1]
        except (ValueError, IndexError):
            return
        match event.attr_value.name:
            case "longrunningcommandstatus":
                try:
                    status = TaskStatus[lrc_attr_value]
                except KeyError as e:
                    unsubscribe_lrc_events()
                    raise KeyError(
                        f"Received unknown TaskStatus from event: {lrc_attr_value}"
                    ) from e
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

    # Check for valid result codes
    if result_code == ResultCode.REJECTED:
        unsubscribe_lrc_events()
        raise CommandError(f"{command} command rejected: {command_id}")
    if result_code not in [ResultCode.QUEUED, ResultCode.STARTED]:
        unsubscribe_lrc_events()
        raise ResultCodeError(
            f"Unexpected result code for {command} command: {command_id}"
        )
    return LrcToken(command_id, result_code, unsubscribe_lrc_events)
