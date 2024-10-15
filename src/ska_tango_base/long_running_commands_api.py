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
from abc import ABC, abstractmethod
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

from ska_tango_base.base.base_component_manager import JSONData
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
    are present by testing them for `None`.  The callback cannot assume
    that only one argument will be provided per call.

    It must accept a generic `**kwargs` parameter for forwards compatibility.
    """

    def __call__(  # noqa: D102
        self,
        status: TaskStatus | None = None,
        progress: int | None = None,
        result: JSONData | None = None,
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


class _LrcProtocol(ABC):
    """Abstract base class for a LRC client-server protocol."""

    # pylint: disable=too-many-arguments,too-many-instance-attributes
    def __init__(
        self,
        lrc_callback: LrcCallback,
        proxy: DeviceProxy,
        logger: logging.Logger,
        command: str,
        command_args: tuple[Any] | None = None,
    ) -> None:
        """
        Initialise a LRC protocol instance.

        :param lrc_callback: of client to wrap.
        :param proxy: Tango DeviceProxy.
        :param logger: to use for logging exceptions.
        :param command: Name of command to invoke.
        :param command_args: Optional arguments for the command, defaults to None.
        """
        # Class parameters
        self._lrc_callback = lrc_callback
        self._proxy = proxy
        self._logger = logger
        self._command = command
        self._command_args = command_args
        # Other variables
        self._calling_thread = threading.current_thread()
        self._submitted = threading.Event()
        self._lock = threading.Lock()
        self._command_id: str = ""
        self._event_ids: list[int] = []

    @abstractmethod
    def invoke_lrc(self) -> LrcSubscriptions:
        """Invoke the LRC."""
        raise NotImplementedError("_LrcProtocol is abstract.")

    @abstractmethod
    def _wrap_lrc_callback(self, event: EventData) -> None:
        """
        Wrap the instance's given user LRC callback.

        :param event: tango attribute change event
        """
        raise NotImplementedError("_LrcProtocol is abstract.")

    def _subscribe_lrc_events(self, attributes: list[str]) -> None:
        """
        Subscribe to LRC attributes' events.

        :param attributes: List of LRC attributes to subscribe to.
        """
        for attr in attributes:
            try:
                event_id = self._proxy.subscribe_event(
                    attr, EventType.CHANGE_EVENT, self._wrap_lrc_callback
                )
                self._event_ids.append(event_id)
            except EventSystemFailed as exc:
                self._unsubscribe_lrc_events()
                self._re_throw_exception(
                    exc, f"Subscribing to '{attr}' change event failed."
                )

    def _unsubscribe_lrc_events(self) -> None:
        """Unsubscribe from LRC attributes' events."""
        if self._event_ids:
            with self._lock:
                events = self._event_ids.copy()
                self._event_ids.clear()
            for event_id in events:
                try:
                    self._proxy.unsubscribe_event(event_id)
                except EventSystemFailed as e:
                    self._logger.warning(
                        f"proxy.unsubscribe_event({event_id}) failed with: {e}"
                    )

    def _execute_command(self) -> None:
        """
        Execute the LRC on the device proxy and check the result code.

        :raises CommandError: If the command is rejected.
        :raises ResultCodeError: If the command returns an unexpected result code.
        """
        try:
            inout_args = (
                (self._command, *self._command_args)
                if self._command_args is not None
                else (self._command,)
            )
            [[result_code], [self._command_id]] = self._proxy.command_inout(*inout_args)
        except (
            ConnectionFailed,
            CommunicationFailed,
            DeviceUnlocked,
            DevFailed,
        ) as exc:
            self._unsubscribe_lrc_events()
            self._re_throw_exception(
                exc,
                f"Invocation of command '{self._command}' failed with args: "
                f"{self._command_args}",
            )
        else:
            # Check for valid result codes
            if result_code == ResultCode.REJECTED:
                msg = f"{self._command} command rejected: {self._command_id}"
                self._logger.error(msg)
                self._unsubscribe_lrc_events()
                raise CommandError(msg)
            if result_code not in [ResultCode.QUEUED, ResultCode.STARTED]:
                msg = (
                    f"Unexpected result code for {self._command} command: {result_code}"
                )
                self._logger.error(msg)
                self._unsubscribe_lrc_events()
                raise ResultCodeError(msg)
        finally:
            # Command submitted, proceed with "subsequent" events.
            self._submitted.set()

    @staticmethod
    def _re_throw_exception(exception: Exception, description: str) -> None:
        """
        Re-throw a Tango DevFailed exception.

        :param exception: Tango exception.
        :param description: Description to include in the exception information.
        """
        calling_fn = inspect.getouterframes(inspect.currentframe())[2].function
        frame = traceback.extract_tb(exception.__traceback__)[0]
        Except.re_throw_exception(
            exception,
            "SKA_InvokeLrcFailed",  # Reason
            description,
            # Origin
            f"{calling_fn}::{frame.name} at ({frame.filename}:{frame.lineno})",
        )

    def _convert_and_check_status(
        self,
        raw_status: str | int,
    ) -> TaskStatus | None:
        """Convert the raw status to a TaskStatus enum.

        :param raw_status: Status as string or integer
        :return: TaskStatus
        """
        try:
            if isinstance(raw_status, str):
                status = TaskStatus[raw_status]
            else:
                status = TaskStatus(raw_status)
        except (KeyError, ValueError, TypeError) as exc:
            status = None
            self._logger.exception(
                f"Received unknown TaskStatus from '{self._command_id}' command: "
                f"{raw_status}"
            )
            self._lrc_callback(
                error=Except.to_dev_failed(type(exc), exc, exc.__traceback__).args
            )
        else:
            if status in [
                TaskStatus.ABORTED,
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.REJECTED,
            ]:
                self._unsubscribe_lrc_events()
        return status


class _LrcProtocolV1(_LrcProtocol):

    def invoke_lrc(self) -> LrcSubscriptions:
        """
        Invoke the LRC with protocol version 1.

        :return: LrcSubscriptions
        """
        self._subscribe_lrc_events(
            [
                "longRunningCommandStatus",
                "longRunningCommandProgress",
                "longRunningCommandResult",
            ]
        )
        self._execute_command()
        return LrcSubscriptions(self._command_id, self._unsubscribe_lrc_events, 1)

    def _wrap_lrc_callback(self, event: EventData) -> None:
        """
        Wrap the instance's given user LRC callback with protocol version 1.

        :param event: tango attribute change event
        """
        # Check for tango error
        if event.err:
            self._logger.error(
                f"'{self._command_id}' command encountered error(s): {event.errors}"
            )
            self._lrc_callback(error=event.errors)
            return

        # Wait for the command to have an ID. Timeout is command_inout timeout + 1.
        if threading.current_thread() != self._calling_thread:
            if not self._submitted.wait(timeout=4):
                self._unsubscribe_lrc_events()
                return

        # proxy.subscribe_event emits an event in the calling thread when first called.
        # The attr_value.value will be ('','') and therefore the index() call below will
        # throw a ValueError. Subsequent events are from internal device thread.
        try:
            cmd_idx = event.attr_value.value.index(self._command_id)
            lrc_attr_value = event.attr_value.value[cmd_idx + 1]
        except ValueError:
            pass  # Do nothing, as will often be called for unrelated events
        except IndexError as exc:
            self._logger.exception(
                f"'{self._command_id}' command has no status/progress/result value"
            )
            self._lrc_callback(
                error=Except.to_dev_failed(type(exc), exc, exc.__traceback__).args
            )
        else:
            match event.attr_value.name:
                case "longrunningcommandstatus":
                    status = self._convert_and_check_status(lrc_attr_value)
                    self._lrc_callback(status=status)
                case "longrunningcommandprogress":
                    self._lrc_callback(progress=int(lrc_attr_value))
                case "longrunningcommandresult":
                    self._lrc_callback(result=json.loads(lrc_attr_value))


class _LrcProtocolV2(_LrcProtocol):

    def invoke_lrc(self) -> LrcSubscriptions:
        """
        Invoke the LRC with protocol version 2.

        :return: LrcSubscriptions
        """
        self._subscribe_lrc_events(["_lrcEvent"])
        self._execute_command()
        return LrcSubscriptions(self._command_id, self._unsubscribe_lrc_events, 2)

    def _wrap_lrc_callback(self, event: EventData) -> None:
        """
        Wrap the instance's given user LRC callback with protocol version 2.

        :param event: tango attribute change event
        """
        # Check for tango error
        if event.err:
            self._logger.error(
                f"'{self._command_id}' command encountered error(s): {event.errors}"
            )
            self._lrc_callback(error=event.errors)
            return

        # Wait for the command to have an ID. Timeout is command_inout timeout + 1.
        if threading.current_thread() != self._calling_thread:
            if not self._submitted.wait(timeout=4):
                self._unsubscribe_lrc_events()
                return

        # proxy.subscribe_event emits an event in the calling thread when first called.
        # The attr_value.value will be ('','') and therefore the index() call below will
        # throw a ValueError. Subsequent events are from internal device thread.
        try:
            cmd_idx = event.attr_value.value.index(self._command_id)
            lrc_attr_value = event.attr_value.value[cmd_idx + 1]
        except ValueError:
            pass  # Do nothing, as will often be called for unrelated events
        except IndexError as exc:
            self._logger.exception(
                f"'{self._command_id}' command has no status/progress/result value"
            )
            self._lrc_callback(
                error=Except.to_dev_failed(type(exc), exc, exc.__traceback__).args
            )
        else:
            event = json.loads(lrc_attr_value)
            if "status" in event:
                event["status"] = self._convert_and_check_status(event["status"])
            if "progress" in event and not isinstance(event["progress"], int):
                self._logger.warning(
                    f"'{self._command}' command's progress is not an int, but "
                    f"{type(event['progress'])}. "
                    "Its type may be checked and enforced in the future."
                )
            self._lrc_callback(**event)


def invoke_lrc(
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
    """  # noqa: DAR402
    if not _is_future_proof_lrc_callback(lrc_callback):
        raise ValueError("lrc_callback must accept **kwargs")

    logger = logger or module_logger
    protocol_version = _find_latest_compatible_protocol_version(proxy)

    match protocol_version:
        case 2:
            return _LrcProtocolV2(
                lrc_callback, proxy, logger, command, command_args
            ).invoke_lrc()
        case 1:
            return _LrcProtocolV1(
                lrc_callback, proxy, logger, command, command_args
            ).invoke_lrc()
        case _:
            msg = (
                "This version of invoke_lrc() is not compatible with any of the "
                "server's supported LRC protocols! Client version min, max = "
                f"{_SUPPORTED_LRC_PROTOCOL_VERSIONS} - Server version min, max = "
                f"{tuple(proxy.lrcProtocolVersions)}"
            )
            logger.error(msg)
            raise RuntimeError(msg)


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
