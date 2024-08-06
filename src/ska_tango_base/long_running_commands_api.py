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
from logging import Logger
from time import sleep
from typing import Any, Callable, Protocol

from ska_control_model import ResultCode, TaskStatus
from tango import DevError, DeviceProxy, EventData, EventSystemFailed, EventType

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


class LrcSubscriptions:
    """
    LRC event subscriptions that is returned by invoke_lrc.

    Unsubscribes from all events when the instance is deleted.
    """

    def __init__(
        self, command_id: str, unsubscribe_lrc_events: Callable[[], None]
    ) -> None:
        """
        Initialise a LrcSubscriptions instance.

        :param command_id: Unique command identifier.
        :param unsubscribe_lrc_events: Method to unsubscribe from all LRC change events.
        """
        self._command_id = command_id
        self._unsubscribe_lrc_events = unsubscribe_lrc_events

    def __del__(self) -> None:
        """Delete the LrcSubscriptions instance."""
        self._unsubscribe_lrc_events()

    @property
    def command_id(self) -> str:
        """
        The command ID.

        :returns: the command ID.
        """
        return self._command_id


# pylint: disable=too-many-statements,too-many-locals
def invoke_lrc(  # noqa: C901
    proxy: DeviceProxy,
    logger: Logger,
    lrc_callback: LrcCallback,
    command: str,
    command_args: tuple[Any] | None = None,
) -> LrcSubscriptions:
    """
    Invoke a long running command (LRC) and monitor its progress with callbacks.

    Subscribe to the relevant LRC attributes and inform the client about change events
    via the provided lrc_callback with either the status, progress, result or error.

    :param proxy: Tango DeviceProxy.
    :param logger: Logger to use for logging exceptions.
    :param lrc_callback: Client LRC callback to wrap.
    :param command: Name of command to invoke.
    :param command_args: Optional arguments for the command, defaults to None.
    :return: LrcSubscriptions class instance, containing the command ID.
        A reference to the instance must be kept until the command is completed or the
        client is not interested in its events anymore, as deleting the instance
        unsubscribes from the LRC change events and thus stops any further callbacks.
    :raises CommandError: If the command is rejected.
    :raises ResultCodeError: If the command returns an unexpected result code.
    :raises Exception: Any other tango exceptions from subscribe_event or command_inout.
    """
    calling_thread = threading.current_thread()
    submitted = threading.Event()
    command_id = None
    event_ids: list[int] = []

    def unsubscribe_lrc_events() -> None:
        for event_id in event_ids.copy():
            try:
                proxy.unsubscribe_event(event_id)
                event_ids.remove(event_id)
            except EventSystemFailed as e:
                logger.warning(f"proxy.unsubscribe_event({event_id}) failed with: {e}")

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
        except ValueError:
            return  # Do nothing, as will often be called for unrelated events
        except IndexError as e:
            msg = f"'{command_id}' command has no status/progress/result value"
            logger.exception(msg)
            raise IndexError(msg) from e
        match event.attr_value.name:
            case "longrunningcommandstatus":
                try:
                    status = TaskStatus[lrc_attr_value]
                except KeyError as e:
                    msg = f"Received unknown TaskStatus from event: {lrc_attr_value}"
                    logger.exception(msg)
                    raise KeyError(msg) from e
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

    # Subscribe to LRC attributes' change events with above callback
    for attr in [
        "longRunningCommandStatus",
        "longRunningCommandProgress",
        "longRunningCommandResult",
    ]:
        try:
            event_id = _retry_tango_method(
                logger,
                proxy.subscribe_event,
                (attr, EventType.CHANGE_EVENT, wrap_lrc_callback),
            )
            event_ids.append(event_id)
        except Exception:
            logger.exception(
                f"Subscribing to '{attr}' change event failed. "
                "Unsubscribing from other LRC attributes"
            )
            unsubscribe_lrc_events()
            raise

    # Try to execute LRC on device proxy
    try:
        inout_args = (
            (command, *command_args) if command_args is not None else (command,)
        )
        [[result_code], [command_id]] = _retry_tango_method(
            logger, proxy.command_inout, inout_args
        )
    except Exception:
        logger.exception("Command call failed. Unsubscribing from LRC attributes")
        unsubscribe_lrc_events()
        raise
    finally:
        # Command submitted, proceed with "subsequent" events.
        submitted.set()

    # Check for valid result codes
    if result_code == ResultCode.REJECTED:
        msg = f"{command} command rejected: {command_id}"
        logger.error(msg)
        unsubscribe_lrc_events()
        raise CommandError(msg)
    if result_code not in [ResultCode.QUEUED, ResultCode.STARTED]:
        msg = f"Unexpected result code for {command} command: {result_code}"
        logger.error(msg)
        unsubscribe_lrc_events()
        raise ResultCodeError(msg)
    return LrcSubscriptions(command_id, unsubscribe_lrc_events)


# pylint: disable=inconsistent-return-statements
def _retry_tango_method(
    logger: Logger,
    method: Callable[..., Any],
    args: tuple[Any, ...] = (),
    max_retries: int = 3,
    delay: int = 2,
) -> Any:
    """
    Call a tango method on a device proxy, retrying if it raises an exception.

    :param logger: to use for logging exceptions.
    :param method: The method to call.
    :param args: Positional arguments to pass to the method. Defaults to ().
    :param max_retries: Maximum number of retry attempts. Defaults to 3.
    :param delay: Delay in seconds between retry attempts. Defaults to 2.
    :return: The result of the method if it succeeds.
    :raises Exception: If the method fails after the maximum number of retries.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return method(*args)  # Call the tango method with its arguments
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning(
                f"{method.__name__}{args} failed attempt {attempt} with: {e}"
            )
            if attempt < max_retries:
                sleep(delay)  # Wait before retrying
            else:
                logger.error(f"All retries of {method.__name__}{args} failed")
                raise  # Re-raise the exception if max retries are reached
