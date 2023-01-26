# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module implements the logging framework for the SKA base device."""
from __future__ import annotations

import enum
import logging
import logging.handlers
import socket
import sys
import warnings
from typing import Any, Optional, Union, cast
from urllib.parse import urlparse
from urllib.request import url2pathname

import ska_ser_logging
import tango
from ska_control_model import LoggingLevel

from ..faults import LoggingTargetError

_LOG_FILE_SIZE = 1024 * 1024  # Log file size 1MB.


__all__ = [
    "_Log4TangoLoggingLevel",
    "_PYTHON_TO_TANGO_LOGGING_LEVEL",
    "_LMC_TO_TANGO_LOGGING_LEVEL",
    "_LMC_TO_PYTHON_LOGGING_LEVEL",
    "TangoLoggingServiceHandler",
    "LoggingUtils",
]


class _Log4TangoLoggingLevel(enum.IntEnum):
    """
    Python enumerated type for Tango log4tango logging levels.

    This is different to tango.LogLevel, and is required if using
    a device's set_log_level() method.  It is not currently exported
    via PyTango, so we hard code it here in the interim.

    Source:
       https://gitlab.com/tango-controls/cppTango/blob/
       4feffd7c8e24b51c9597a40b9ef9982dd6e99cdf/log4tango/include/log4tango/Level.hh#L86-93
    """

    OFF = 100
    FATAL = 200
    ERROR = 300
    WARN = 400
    INFO = 500
    DEBUG = 600


_PYTHON_TO_TANGO_LOGGING_LEVEL = {
    logging.CRITICAL: _Log4TangoLoggingLevel.FATAL,
    logging.ERROR: _Log4TangoLoggingLevel.ERROR,
    logging.WARNING: _Log4TangoLoggingLevel.WARN,
    logging.INFO: _Log4TangoLoggingLevel.INFO,
    logging.DEBUG: _Log4TangoLoggingLevel.DEBUG,
}

_LMC_TO_TANGO_LOGGING_LEVEL = {
    LoggingLevel.OFF: _Log4TangoLoggingLevel.OFF,
    LoggingLevel.FATAL: _Log4TangoLoggingLevel.FATAL,
    LoggingLevel.ERROR: _Log4TangoLoggingLevel.ERROR,
    LoggingLevel.WARNING: _Log4TangoLoggingLevel.WARN,
    LoggingLevel.INFO: _Log4TangoLoggingLevel.INFO,
    LoggingLevel.DEBUG: _Log4TangoLoggingLevel.DEBUG,
}

_LMC_TO_PYTHON_LOGGING_LEVEL = {
    LoggingLevel.OFF: logging.CRITICAL,  # there is no "off"
    LoggingLevel.FATAL: logging.CRITICAL,
    LoggingLevel.ERROR: logging.ERROR,
    LoggingLevel.WARNING: logging.WARNING,
    LoggingLevel.INFO: logging.INFO,
    LoggingLevel.DEBUG: logging.DEBUG,
}


class TangoLoggingServiceHandler(logging.Handler):
    """Handler that emit logs via Tango device's logger to TLS."""

    def __init__(self: TangoLoggingServiceHandler, tango_logger: tango.Logger) -> None:
        """
        Initialise a new instance.

        :param tango_logger: the tango logger to use to emit logs
        """
        super().__init__()
        self.tango_logger = tango_logger

    def emit(self: TangoLoggingServiceHandler, record: logging.LogRecord) -> None:
        """
        Emit a log record.

        :param record: the log to be emitted.
        """
        try:
            msg = self.format(record)
            tango_level = _PYTHON_TO_TANGO_LOGGING_LEVEL[record.levelno]
            self.acquire()
            try:
                self.tango_logger.log(tango_level, msg)
            finally:
                self.release()
        except Exception:  # pylint: disable=broad-except
            self.handleError(record)

    def __repr__(self: TangoLoggingServiceHandler) -> str:
        """
        Return a printable representation of this service handler.

        :return: a printable representation of this service handler.
        """
        python_level = logging.getLevelName(self.level)
        if self.tango_logger:
            tango_level = _Log4TangoLoggingLevel(self.tango_logger.get_level()).name
            name = self.tango_logger.get_name()
        else:
            tango_level = "UNKNOWN"
            name = "!No Tango logger!"
        return (
            f"<{self.__class__.__name__} {name} (Python {python_level}, Tango "
            f"{tango_level})>"
        )


class LoggingUtils:
    """
    Utility functions to aid logger configuration.

    These functions are encapsulated in class to aid testing - it
    allows dependent functions to be mocked.
    """

    @staticmethod
    def sanitise_logging_targets(targets: list[str], device_name: str) -> list[str]:
        """
        Validate and return logging targets '<type>::<name>' strings.

        :param targets:
            List of candidate logging target strings, like '<type>[::<name>]'
            Empty and whitespace-only strings are ignored.  Can also be None.

        :param device_name:
            Tango device name, like 'domain/family/member', used
            for the default file name

        :return: list of '<type>::<name>' strings, with default name, if applicable

        :raises LoggingTargetError: for invalid target string that cannot be corrected
        """
        default_target_names: dict[str, str | None] = {
            "console": "cout",
            "file": f"{device_name.replace('/', '_')}.log",
            "syslog": None,
            "tango": "logger",
        }

        valid_targets = []
        if targets:
            for target in targets:
                target = target.strip()
                if not target:
                    continue
                if "::" in target:
                    target_type, target_name = target.split("::", 1)
                else:
                    target_type = target
                    target_name = ""
                if target_type not in default_target_names:
                    raise LoggingTargetError(
                        f"Invalid target type: {target_type} - options are "
                        f"{list(default_target_names.keys())}"
                    )
                if not target_name:
                    target_name = cast(str, default_target_names[target_type])
                if not target_name:
                    raise LoggingTargetError(
                        f"Target name required for type {target_type}"
                    )
                valid_target = f"{target_type}::{target_name}"
                valid_targets.append(valid_target)

        return valid_targets

    @staticmethod
    def get_syslog_address_and_socktype(
        url: str,
    ) -> tuple[Union[tuple[str, int], str], socket.SocketKind | None]:  # noqa: F821
        """
        Parse syslog URL and extract address and socktype parameters for SysLogHandler.

        :param url: Universal resource locator string for syslog target.
            Three types are supported: file path, remote UDP server,
            remote TCP server.

            - Output to a file: 'file://<path to file>'. For example,
              'file:///dev/log' will write to '/dev/log'.

            - Output to remote server over UDP:
              'udp://<hostname>:<port>'. For example,
              'udp://syslog.com:514' will send to host 'syslog.com' on
              UDP port 514

            - Output to remote server over TCP:
              'tcp://<hostname>:<port>'. For example,
              'tcp://rsyslog.com:601' will send to host 'rsyslog.com' on
              TCP port 601

            For backwards compatibility, if the protocol prefix is
            missing, the type is interpreted as file. This is
            deprecated. For example, '/dev/log' is equivalent to
            'file:///dev/log'.

        :return: An (address, socktype) tuple.

            For file types:

            - the address is the file path as as string

            - socktype is None

            For UDP and TCP:

            - the address is tuple of (hostname, port), with hostname a
              string, and port an integer.

            - socktype is socket.SOCK_DGRAM for UDP, or
              socket.SOCK_STREAM for TCP.

        :raises LoggingTargetError: for invalid url string
        """
        address: tuple[str, int] | str = ""
        socktype = None
        parsed = urlparse(url)
        if parsed.scheme in ["file", ""]:
            address = url2pathname(parsed.netloc + parsed.path)
            socktype = None
            if not address:
                raise LoggingTargetError(
                    f"Invalid syslog URL - empty file path from '{url}'"
                )
            if parsed.scheme == "":
                warnings.warn(
                    "Specifying syslog URL without protocol is deprecated, "
                    f"use 'file://{url}' instead of '{url}'",
                    DeprecationWarning,
                )
        elif parsed.scheme in ["udp", "tcp"]:
            if not parsed.hostname:
                raise LoggingTargetError(
                    f"Invalid syslog URL - could not extract hostname from '{url}'"
                )
            try:
                port = parsed.port
                if not port:
                    raise LoggingTargetError(
                        f"Invalid syslog URL - could not extract integer port number "
                        f"from '{url}'"
                    )
            except (TypeError, ValueError) as exc:
                raise LoggingTargetError(
                    f"Invalid syslog URL - could not extract integer port number from "
                    f"'{url}'"
                ) from exc
            address = (parsed.hostname, port)
            socktype = (
                socket.SOCK_DGRAM if parsed.scheme == "udp" else socket.SOCK_STREAM
            )
        else:
            raise LoggingTargetError(
                f"Invalid syslog URL - expected file, udp or tcp protocol scheme in "
                f"'{url}'"
            )
        return address, socktype

    @staticmethod
    def create_logging_handler(
        target: str, tango_logger: Optional[tango.Logger] = None
    ) -> Any:
        """
        Create a Python log handler based on the target type.

        Supported target types are "console", "file", "syslog", "tango".

        :param target:
            Logging target for logger, <type>::<name>

        :param tango_logger:
            Instance of tango.Logger, optional.  Only required if creating
            a target of type "tango".

        :return: StreamHandler, RotatingFileHandler, SysLogHandler, or
            TangoLoggingServiceHandler

        :raises LoggingTargetError: for invalid target string
        """
        if "::" in target:
            target_type, target_name = target.split("::", 1)
        else:
            raise LoggingTargetError(
                f"Invalid target requested - missing '::' separator: {target}"
            )
        handler: Union[
            logging.StreamHandler,
            logging.handlers.RotatingFileHandler,
            logging.handlers.SysLogHandler,
            TangoLoggingServiceHandler,
        ]
        if target_type == "console":
            handler = logging.StreamHandler(sys.stdout)
        elif target_type == "file":
            log_file_name = target_name
            handler = logging.handlers.RotatingFileHandler(
                log_file_name, "a", _LOG_FILE_SIZE, 2, None, False
            )
        elif target_type == "syslog":
            address, socktype = LoggingUtils.get_syslog_address_and_socktype(
                target_name
            )
            handler = logging.handlers.SysLogHandler(
                address=address,
                facility=logging.handlers.SysLogHandler.LOG_SYSLOG,
                socktype=socktype,
            )
        elif target_type == "tango":
            if tango_logger:
                handler = TangoLoggingServiceHandler(tango_logger)
            else:
                raise LoggingTargetError(
                    "Missing tango_logger instance for 'tango' target type"
                )
        else:
            raise LoggingTargetError(
                f"Invalid target type requested: '{target_type}' in '{target}'"
            )
        formatter = ska_ser_logging.get_default_formatter(tags=True)
        handler.setFormatter(formatter)
        handler.name = target
        return handler

    @staticmethod
    def update_logging_handlers(targets: list[str], logger: logging.Logger) -> None:
        """
        Update a logger's handlers.

        :param targets: a list of handler names. Current handlers whose
            name is not included here will be removed. Names for which
            the logger currently does not have a handler will have
            handlers created and added.
        :param logger: the logger whose handlers are to be updated.
        """
        old_targets = [handler.name for handler in logger.handlers]
        added_targets = set(targets) - set(old_targets)
        removed_targets = set(old_targets) - set(targets)

        for handler in list(logger.handlers):
            if handler.name in removed_targets:
                logger.removeHandler(handler)
        for target in targets:
            if target in added_targets:
                handler = LoggingUtils.create_logging_handler(
                    # TODO investigate this type: ignore.
                    target,
                    logger.tango_logger,  # type: ignore[attr-defined]
                )
                logger.addHandler(handler)

        logger.info("Logging targets set to %s", targets)
