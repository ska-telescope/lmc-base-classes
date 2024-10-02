# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module provides a convenience client API for invoking long running commands."""
from __future__ import annotations

import inspect
import json
import logging
import threading
import traceback
from typing import Any, Callable, Protocol

from ska_control_model import ResultCode, TaskStatus
from tango import (
    CommunicationFailed,
    ConnectionFailed,
    DevError,
    DevFailed,
    DeviceProxy,
    DeviceUnlocked,
    EventData,
    EventSystemFailed,
    EventType,
    Except,
)

from ska_tango_base.faults import CommandError, ResultCodeError

module_logger = logging.getLogger(__name__)

_SUPPORTED_LRC_PROTOCOL_VERSIONS = (1, 2)


# pylint: disable=too-few-public-methods
class LrcCallback(Protocol):
    """Expected LRC callback signature for typing.

    The LrcCallback will be called with some combination of the following arguments:

        - ``status``: ``TaskStatus``
        - ``progress``: ``int``
        - ``result``: ``Any``
        - ``error``: ``tuple[DevError]``

    Each of the above arguments is optional and the callback must check which
    are present by testing them again `None`.  The callback cannot assume
    that only one argument will be provided per call.

    It must accept a generic `**kwargs` parameter for forwards compatibility.
    """

    def __call__(  # noqa: D102
        self,
        status: TaskStatus | None = None,
        progress: int | None = None,
        result: Any | None = None,  # TODO: To be decided later
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
        self,
        command_id: str,
        unsubscribe_lrc_events: Callable[[], None],
        protocol_version: int,
    ) -> None:
        """
        Initialise a LrcSubscriptions instance.

        :param command_id: Unique command identifier.
        :param unsubscribe_lrc_events: Method to unsubscribe from all LRC change events.
        :param protocol_version: The LRC client-server protocol version used.
        """
        self._command_id = command_id
        self._unsubscribe_lrc_events = unsubscribe_lrc_events
        self._protocol_version = protocol_version

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

    @property
    def protocol_version(self) -> int:
        """
        The LRC client-server protocol version used.

        :returns: the protocol version.
        """
        return self._protocol_version


# pylint: disable=too-many-statements,too-many-locals
def invoke_lrc(  # noqa: C901
    lrc_callback: LrcCallback,
    proxy: DeviceProxy,
    command: str,
    command_args: tuple[Any] | None = None,
    logger: logging.Logger | None = None,
) -> LrcSubscriptions:
    """
    Invoke a long running command (LRC) and monitor its progress with callbacks.

    Subscribe to the relevant LRC attributes and inform the client about change events
    via the provided lrc_callback with either the status, progress, result or error.

    :param lrc_callback: Client LRC callback to call whenever the LRC's state changes.
    :param proxy: Tango DeviceProxy.
    :param command: Name of command to invoke.
    :param command_args: Optional arguments for the command, defaults to None.
    :param logger: Logger to use for logging exceptions. If not provided, then a default
        module logger will be used.
    :return: LrcSubscriptions class instance, containing the command ID.
        A reference to the instance must be kept until the command is completed or the
        client is not interested in its events anymore, as deleting the instance
        unsubscribes from the LRC change events and thus stops any further callbacks.
    :raises CommandError: If the command is rejected.
    :raises ResultCodeError: If the command returns an unexpected result code.
    :raises ValueError: If the lrc_callback does not accept `**kwargs`.
    :raises RuntimeError: If the supported client-server protocol versions do not
        overlap.
    """
    if not _is_future_proof_lrc_callback(lrc_callback):
        raise ValueError("lrc_callback must accept **kwargs")

    logger = logger or module_logger
    calling_thread = threading.current_thread()
    submitted = threading.Event()
    lock = threading.Lock()
    command_id = None
    event_ids: list[int] = []
    protocol_version = _find_latest_compatible_protocol_version(proxy)

    def unsubscribe_lrc_events() -> None:
        if event_ids:
            with lock:
                events = event_ids.copy()
                event_ids.clear()
            for event_id in events:
                try:
                    proxy.unsubscribe_event(event_id)
                except EventSystemFailed as e:
                    logger.warning(
                        f"proxy.unsubscribe_event({event_id}) failed with: {e}"
                    )

    def convert_and_check_status(
        raw_status: str | int,
    ) -> TaskStatus | None:
        try:
            if isinstance(raw_status, str):
                status = TaskStatus[raw_status]
            else:
                status = TaskStatus(raw_status)
        except KeyError as exc:
            status = None
            logger.exception(
                f"Received unknown TaskStatus from '{command_id}' command: "
                f"{raw_status}"
            )
            lrc_callback(
                error=Except.to_dev_failed(type(exc), exc, exc.__traceback__).args
            )
        if status in [
            TaskStatus.ABORTED,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.REJECTED,
        ]:
            unsubscribe_lrc_events()
        return status

    def wrap_lrc_callback(event: EventData) -> None:
        # Check for tango error
        if event.err:
            logger.error(f"'{command_id}' command encountered error(s): {event.errors}")
            lrc_callback(error=event.errors)
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
        except IndexError as exc:
            logger.exception(
                f"'{command_id}' command has no status/progress/result value"
            )
            lrc_callback(
                error=Except.to_dev_failed(type(exc), exc, exc.__traceback__).args
            )
            return
        match event.attr_value.name:
            # Protocol v2
            case "_lrcevent":
                event = json.loads(lrc_attr_value)
                if "status" in event:
                    event["status"] = convert_and_check_status(event["status"])
                lrc_callback(**event)
            # Protocol v1
            case "longrunningcommandstatus":
                status = convert_and_check_status(lrc_attr_value)
                lrc_callback(status=status)
            case "longrunningcommandprogress":
                lrc_callback(progress=int(lrc_attr_value))
            case "longrunningcommandresult":
                lrc_callback(result=json.loads(lrc_attr_value))

    # Decide which version of the client-server protocol to use
    match protocol_version:
        case 2:
            attributes = ["_lrcEvent"]
        case 1:
            attributes = [
                "longRunningCommandStatus",
                "longRunningCommandProgress",
                "longRunningCommandResult",
            ]
        case _:
            msg = (
                "This version of invoke_lrc() is not compatible with any of the "
                "server's supported LRC protocols! Client version min, max = "
                f"{_SUPPORTED_LRC_PROTOCOL_VERSIONS} - Server version min, max = "
                f"{tuple(proxy.lrcProtocolVersions)}"
            )
            logger.error(msg)
            raise RuntimeError(msg)

    # Subscribe to LRC attributes' change events with above callback
    for attr in attributes:
        try:
            event_id = proxy.subscribe_event(
                attr, EventType.CHANGE_EVENT, wrap_lrc_callback
            )
            event_ids.append(event_id)
        except EventSystemFailed as exc:
            unsubscribe_lrc_events()
            _re_throw_exception(exc, f"Subscribing to '{attr}' change event failed.")

    # Try to execute LRC on device proxy
    try:
        inout_args = (
            (command, *command_args) if command_args is not None else (command,)
        )
        [[result_code], [command_id]] = proxy.command_inout(*inout_args)
    except (ConnectionFailed, CommunicationFailed, DeviceUnlocked, DevFailed) as exc:
        unsubscribe_lrc_events()
        _re_throw_exception(
            exc, f"Invocation of command '{command}' failed with args: {command_args}"
        )
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
    return LrcSubscriptions(str(command_id), unsubscribe_lrc_events, protocol_version)


###############################################
# Private static functions used in invoke_lrc #
###############################################
def _is_future_proof_lrc_callback(lrc_callback: LrcCallback) -> bool:
    sig = inspect.signature(lrc_callback)
    for param in sig.parameters.values():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True
    return False


def _find_latest_compatible_protocol_version(server_proxy: DeviceProxy) -> int | None:
    """
    Find latest compatible protocol between client's and server's supported versions.

    :param server_proxy: Server proxy to queury lrcProtocolVersions.
    :return: Highest compatible version, or None if there is no overlap.
    """
    server_min, server_max = (
        server_proxy.lrcProtocolVersions
        if "lrcProtocolVersions" in server_proxy.get_attribute_list()
        else (1, 1)  # Assume server supports only the 1st version of the protocol
    )
    client_min, client_max = _SUPPORTED_LRC_PROTOCOL_VERSIONS
    if server_min <= client_max and client_min <= server_max:
        return min(server_max, client_max)  # type: ignore
    return None


def _re_throw_exception(exception: Exception, description: str) -> None:
    calling_fn = inspect.getouterframes(inspect.currentframe())[2].function
    frame = traceback.extract_tb(exception.__traceback__)[0]
    Except.re_throw_exception(
        exception,
        "SKA_InvokeLrcFailed",  # Reason
        description,
        # Origin
        f"{calling_fn}::{frame.name} at ({frame.filename}:{frame.lineno})",
    )
