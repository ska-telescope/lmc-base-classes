# pylint: disable=invalid-name, too-many-lines
# TODO: Split logging service out from base_device module, then split these
# tests the same way.

# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module contains the tests for the SKABaseDevice."""
from __future__ import annotations

import json
import logging
import re
import socket
import time
import unittest
from typing import Any, cast
from unittest import mock

import pytest
from _pytest.fixtures import SubRequest
from ska_control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    LoggingLevel,
    ResultCode,
    SimulationMode,
    TaskStatus,
    TestMode,
)
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup
from tango import DevFailed, DeviceProxy, DevState, EventType, Logger

from ska_tango_base import SKABaseDevice
from ska_tango_base.base import CommandTracker
from ska_tango_base.base.base_device import _DEBUGGER_PORT
from ska_tango_base.base.logging import (
    _PYTHON_TO_TANGO_LOGGING_LEVEL,
    LoggingUtils,
    TangoLoggingServiceHandler,
    _Log4TangoLoggingLevel,
)
from ska_tango_base.faults import CommandError, LoggingTargetError
from ska_tango_base.long_running_commands_api import LrcCallback, invoke_lrc
from ska_tango_base.testing.reference import (
    ReferenceBaseComponentManager,
    ReferenceSkaBaseDevice,
)
from tests.conftest import Helpers


class TestTangoLoggingServiceHandler:
    """This class contains tests of the TangoLoggingServiceHandler class."""

    @pytest.fixture(name="tango_logger")
    def fixture_tango_logger(self: TestTangoLoggingServiceHandler) -> mock.MagicMock:
        """
        Return a mock logger for a Tango device.

        :return: a mock logger for a Tango device.
        """
        tango_logger = mock.MagicMock(spec=Logger)
        # setup methods used for handler __repr__
        tango_logger.get_name.return_value = "unit/test/dev"
        tango_logger.get_level.return_value = _Log4TangoLoggingLevel.DEBUG
        return tango_logger

    @pytest.fixture()
    def tls_handler(
        self: TestTangoLoggingServiceHandler,
        tango_logger: mock.MagicMock,
    ) -> TangoLoggingServiceHandler:
        """
        Return a logging service handler.

        :param tango_logger: a mock logger for a Tango device

        :return: the tango logging handler
        """
        return TangoLoggingServiceHandler(tango_logger)

    @pytest.fixture(
        params=[
            logging.DEBUG,
            logging.INFO,
            logging.WARN,
            logging.ERROR,
            logging.CRITICAL,
        ]
    )
    def python_log_level(
        self: TestTangoLoggingServiceHandler, request: SubRequest
    ) -> LoggingLevel:
        """
        Return a python logging level.

        :param request: pytest request

        :return: the requested logging level
        """
        return cast(LoggingLevel, request.param)

    def test_emit_message_at_correct_level(
        self: TestTangoLoggingServiceHandler,
        tango_logger: mock.MagicMock,
        tls_handler: TangoLoggingServiceHandler,
        python_log_level: LoggingLevel,
    ) -> None:
        """
        Test that emitted messages are logged at the right level.

        :param tango_logger: a mock logger for a Tango device
        :param tls_handler: tango logging service
        :param python_log_level: logging level
        """
        # arrange
        record = logging.LogRecord("test", python_log_level, "", 1, "message", (), None)
        # act
        tls_handler.emit(record)
        # assert
        expected_tango_level = _PYTHON_TO_TANGO_LOGGING_LEVEL[python_log_level]
        expected_calls = [mock.call(expected_tango_level, mock.ANY)]
        assert tango_logger.log.call_args_list == expected_calls

    def test_emit_message_is_formatted(
        self: TestTangoLoggingServiceHandler,
        tango_logger: mock.MagicMock,
        tls_handler: TangoLoggingServiceHandler,
    ) -> None:
        """
        Test that emitted messages are formatted as specified.

        :param tango_logger: a mock logger for a Tango device
        :param tls_handler: tango logging service
        """
        # arrange
        record = logging.LogRecord(
            "test", logging.INFO, "", 1, "message %s", ("param",), None
        )

        def format_stub(log_record: logging.LogRecord) -> str:
            return "LOG: " + log_record.getMessage()

        # monkey patch
        tls_handler.format = format_stub  # type: ignore[assignment]
        # act
        tls_handler.emit(record)
        # assert
        expected_tango_level = _PYTHON_TO_TANGO_LOGGING_LEVEL[logging.INFO]
        expected_message = "LOG: message param"
        expected_calls = [mock.call(expected_tango_level, expected_message)]
        assert tango_logger.log.call_args_list == expected_calls

    def test_emit_exception_error_handled(
        self: TestTangoLoggingServiceHandler,
        tango_logger: mock.MagicMock,
        tls_handler: TangoLoggingServiceHandler,
    ) -> None:
        """
        Test exception handling when a record is emitted.

        :param tango_logger: a mock logger for a Tango device
        :param tls_handler: tango logging service
        """
        # arrange
        record = logging.LogRecord("test", logging.INFO, "", 1, "message", (), None)

        def cause_exception(*args: Any, **kwargs: Any) -> None:
            raise RuntimeError("Testing")

        tango_logger.log.side_effect = cause_exception
        # monkey patch
        tls_handler.handleError = mock.MagicMock()  # type: ignore[method-assign]
        # act
        tls_handler.emit(record)
        # assert
        assert tls_handler.handleError.call_args_list == [mock.call(record)]

    def test_repr_normal(
        self: TestTangoLoggingServiceHandler, tls_handler: TangoLoggingServiceHandler
    ) -> None:
        """
        Test the string representation of a handler under normal conditions.

        :param tls_handler: tango logging service
        """
        expected = (
            "<TangoLoggingServiceHandler unit/test/dev (Python NOTSET, Tango DEBUG)>"
        )
        assert repr(tls_handler) == expected

    def test_repr_tango_logger_none(
        self: TestTangoLoggingServiceHandler, tls_handler: TangoLoggingServiceHandler
    ) -> None:
        """
        Test the string representation of a handler with no logger.

        :param tls_handler: tango logging service
        """
        tls_handler.tango_logger = None
        expected = (
            "<TangoLoggingServiceHandler !No Tango logger! (Python NOTSET, Tango "
            "UNKNOWN)>"
        )
        assert repr(tls_handler) == expected


class TestLoggingUtils:
    """This class contains tests of the LoggingUtils class."""

    @pytest.fixture(
        params=[
            (None, []),
            ([""], []),
            ([" \n\t "], []),
            (["console"], ["console::cout"]),
            (["console::"], ["console::cout"]),
            (["console::cout"], ["console::cout"]),
            (["console::anything"], ["console::anything"]),
            (["file"], ["file::my_dev_name.log"]),
            (["file::"], ["file::my_dev_name.log"]),
            (["file::/tmp/dummy"], ["file::/tmp/dummy"]),
            (["syslog::some/path"], ["syslog::some/path"]),
            (["syslog::file://some/path"], ["syslog::file://some/path"]),
            (
                ["syslog::protocol://somehost:1234"],
                ["syslog::protocol://somehost:1234"],
            ),
            (["tango"], ["tango::logger"]),
            (["tango::"], ["tango::logger"]),
            (["tango::logger"], ["tango::logger"]),
            (["tango::anything"], ["tango::anything"]),
            (["console", "file"], ["console::cout", "file::my_dev_name.log"]),
        ]
    )
    def good_logging_targets(
        self: TestLoggingUtils, request: SubRequest
    ) -> tuple[str, str, list[str]]:
        """
        Return some good logging targets for use in testing.

        :param request: request

        :return: the target, device name and expected target
        """
        targets_in, expected = request.param
        dev_name = "my/dev/name"
        return targets_in, dev_name, expected

    @pytest.fixture(
        params=[
            ["invalid"],
            ["invalid", "console"],
            ["invalid::type"],
            ["syslog"],
        ]
    )
    def bad_logging_targets(
        self: TestLoggingUtils, request: SubRequest
    ) -> tuple[str, str]:
        """
        Return some bad logging targets for use in testing.

        :param request: request

        :return: the target and device name
        """
        targets_in = request.param
        dev_name = "my/dev/name"
        return targets_in, dev_name

    def test_sanitise_logging_targets_success(
        self: TestLoggingUtils,
        good_logging_targets: tuple[list[str] | None, str, list[str]],
    ) -> None:
        """
        Test that good logging targets can be sanitised.

        :param good_logging_targets: OK logging destination
        """
        targets_in, dev_name, expected = good_logging_targets
        actual = LoggingUtils.sanitise_logging_targets(targets_in, dev_name)
        assert actual == expected

    def test_sanitise_logging_targets_fail(
        self: TestLoggingUtils, bad_logging_targets: tuple[list[str], str]
    ) -> None:
        """
        Test that bad logging targets cannot be sanitised.

        :param bad_logging_targets: bad logging destination
        """
        targets_in, dev_name = bad_logging_targets
        with pytest.raises(LoggingTargetError):
            LoggingUtils.sanitise_logging_targets(targets_in, dev_name)

    @pytest.fixture(
        params=[
            ("deprecated/path", ["deprecated/path", None]),
            ("file:///abs/path", ["/abs/path", None]),
            ("file://relative/path", ["relative/path", None]),
            ("file://some/spaced%20path", ["some/spaced path", None]),
            (
                "udp://somehost.domain:1234",
                [("somehost.domain", 1234), socket.SOCK_DGRAM],
            ),
            ("udp://127.0.0.1:1234", [("127.0.0.1", 1234), socket.SOCK_DGRAM]),
            ("tcp://somehost:1234", [("somehost", 1234), socket.SOCK_STREAM]),
            (
                "tcp://127.0.0.1:1234",
                [("127.0.0.1", 1234), socket.SOCK_STREAM],
            ),
        ]
    )
    def good_syslog_url(
        self: TestLoggingUtils, request: SubRequest
    ) -> tuple[str, tuple[str, socket.SocketKind]]:
        """
        Return a good logging target URL.

        :param request: request

        :return: the URL and a tuple with address & socket  type
        """
        url, (expected_address, expected_socktype) = request.param
        return url, (expected_address, expected_socktype)

    @pytest.fixture(
        params=[
            None,
            "",
            "file://",
            "udp://",
            "udp://somehost",
            "udp://somehost:",
            "udp://somehost:not_integer_port",
            "udp://:1234",
            "tcp://",
            "tcp://somehost",
            "tcp://somehost:",
            "tcp://somehost:not_integer_port",
            "tcp://:1234",
            "invalid://somehost:1234",
        ]
    )
    def bad_syslog_url(self: TestLoggingUtils, request: SubRequest) -> str | None:
        """
        Return a bad logging target URL.

        :param request: request??

        :return: any return code
        """
        return cast(str | None, request.param)

    def test_get_syslog_address_and_socktype_success(
        self: TestLoggingUtils,
        good_syslog_url: tuple[str, tuple[str, socket.SocketKind]],
    ) -> None:
        """
        Test that logging successfully accepts a good target.

        :param good_syslog_url: good url
        """
        url, (expected_address, expected_socktype) = good_syslog_url
        (
            actual_address,
            actual_socktype,
        ) = LoggingUtils.get_syslog_address_and_socktype(url)
        assert actual_address == expected_address
        assert actual_socktype == expected_socktype

    def test_get_syslog_address_and_socktype_fail(
        self: TestLoggingUtils, bad_syslog_url: str
    ) -> None:
        """
        Test that logging raises an error when given a bad target.

        :param bad_syslog_url: bad url
        """
        with pytest.raises(LoggingTargetError):
            LoggingUtils.get_syslog_address_and_socktype(bad_syslog_url)

    @mock.patch("ska_tango_base.base.logging.TangoLoggingServiceHandler")
    @mock.patch("logging.handlers.SysLogHandler")
    @mock.patch("logging.handlers.RotatingFileHandler")
    @mock.patch("logging.StreamHandler")
    @mock.patch("ska_ser_logging.get_default_formatter")
    def test_create_logging_handler(  # pylint: disable=too-many-arguments
        self: TestLoggingUtils,
        mock_get_formatter: mock.MagicMock,
        mock_stream_handler: mock.MagicMock,
        mock_file_handler: mock.MagicMock,
        mock_syslog_handler: mock.MagicMock,
        mock_tango_handler: mock.MagicMock,
    ) -> None:
        """
        Test that logging handlers can be created.

        :param mock_get_formatter: mock
        :param mock_stream_handler: mock
        :param mock_file_handler: mock
        :param mock_syslog_handler: mock
        :param mock_tango_handler: mock
        """
        # Expect formatter be created using `get_default_formatter(tags=True)`
        # Use some mocks to check this.
        mock_formatter = mock.MagicMock()

        def get_formatter_if_tags_enabled(
            *args: Any, **kwargs: Any  # pylint: disable=unused-argument
        ) -> mock.MagicMock | None:
            if kwargs.get("tags", False):
                return mock_formatter
            return None

        mock_get_formatter.side_effect = get_formatter_if_tags_enabled
        mock_tango_logger = mock.MagicMock(spec=Logger)

        handler = LoggingUtils.create_logging_handler("console::cout")
        assert handler == mock_stream_handler()
        handler.setFormatter.assert_called_once_with(mock_formatter)

        handler = LoggingUtils.create_logging_handler("file::/tmp/dummy")
        assert handler == mock_file_handler()
        handler.setFormatter.assert_called_once_with(mock_formatter)

        handler = LoggingUtils.create_logging_handler("syslog::udp://somehost:1234")
        mock_syslog_handler.assert_called_once_with(
            address=("somehost", 1234),
            facility=mock_syslog_handler.LOG_SYSLOG,
            socktype=socket.SOCK_DGRAM,
        )
        assert handler == mock_syslog_handler()
        handler.setFormatter.assert_called_once_with(mock_formatter)

        mock_syslog_handler.reset_mock()
        handler = LoggingUtils.create_logging_handler("syslog::file:///tmp/path")
        mock_syslog_handler.assert_called_once_with(
            address="/tmp/path",
            facility=mock_syslog_handler.LOG_SYSLOG,
            socktype=None,
        )
        assert handler == mock_syslog_handler()
        handler.setFormatter.assert_called_once_with(mock_formatter)

        handler = LoggingUtils.create_logging_handler(
            "tango::logger", mock_tango_logger
        )
        mock_tango_handler.assert_called_once_with(mock_tango_logger)
        assert handler == mock_tango_handler()
        handler.setFormatter.assert_called_once_with(mock_formatter)

        with pytest.raises(LoggingTargetError):
            LoggingUtils.create_logging_handler("invalid::target")

        with pytest.raises(LoggingTargetError):
            LoggingUtils.create_logging_handler("invalid")

        with pytest.raises(LoggingTargetError):
            LoggingUtils.create_logging_handler("tango::logger", tango_logger=None)

    def test_update_logging_handlers(self: TestLoggingUtils) -> None:
        """Test that logging handlers can be updated."""
        logger = logging.getLogger("testing")
        logger.tango_logger = mock.MagicMock(spec=Logger)  # type: ignore[attr-defined]

        # The arguments of this method must match LoggingUtils.create_logging_handler
        def null_creator(
            target: str, tango_logger: Logger  # pylint: disable=unused-argument
        ) -> logging.NullHandler:
            handler = logging.NullHandler()
            handler.name = target
            return handler

        orig_create_logging_handler = LoggingUtils.create_logging_handler
        try:
            mocked_creator = mock.MagicMock(side_effect=null_creator)
            LoggingUtils.create_logging_handler = (  # type: ignore[method-assign]
                mocked_creator
            )

            # test adding first handler
            new_targets = ["console::cout"]
            LoggingUtils.update_logging_handlers(new_targets, logger)
            assert len(logger.handlers) == 1
            mocked_creator.assert_called_once_with(
                "console::cout", logger.tango_logger  # type: ignore[attr-defined]
            )
            # test same handler is retained for same request
            old_handler = logger.handlers[0]
            new_targets = ["console::cout"]
            mocked_creator.reset_mock()
            LoggingUtils.update_logging_handlers(new_targets, logger)
            assert len(logger.handlers) == 1
            assert logger.handlers[0] is old_handler
            mocked_creator.assert_not_called()

            # test other valid target types
            new_targets = [
                "console::cout",
                "file::/tmp/dummy",
                "syslog::some/address",
                "tango::logger",
            ]
            mocked_creator.reset_mock()
            LoggingUtils.update_logging_handlers(new_targets, logger)
            assert len(logger.handlers) == 4
            assert mocked_creator.call_count == 3
            mocked_creator.assert_has_calls(
                [
                    mock.call(
                        "file::/tmp/dummy",
                        logger.tango_logger,  # type: ignore[attr-defined]
                    ),
                    mock.call(
                        "syslog::some/address",
                        logger.tango_logger,  # type: ignore[attr-defined]
                    ),
                    mock.call(
                        "tango::logger",
                        logger.tango_logger,  # type: ignore[attr-defined]
                    ),
                ],
                any_order=True,
            )

            # test clearing of 2 handlers
            new_targets = ["console::cout", "syslog::some/address"]
            mocked_creator.reset_mock()
            LoggingUtils.update_logging_handlers(new_targets, logger)
            assert len(logger.handlers) == 2
            mocked_creator.assert_not_called()

            # test clearing all handlers
            new_targets = []
            mocked_creator.reset_mock()
            LoggingUtils.update_logging_handlers(new_targets, logger)
            assert len(logger.handlers) == 0
            mocked_creator.assert_not_called()

        finally:
            # monkey patch
            LoggingUtils.create_logging_handler = (  # type: ignore[method-assign]
                orig_create_logging_handler
            )


class TestCommandTracker:
    """Tests of the CommandTracker class."""

    @pytest.fixture
    def callbacks(
        self: TestCommandTracker, mocker: unittest.mock.Mock
    ) -> dict[str, unittest.mock.Mock]:
        """
        Return a dictionary of mocks for use as callbacks.

        These callbacks will be passed to the command tracker under
        test, and can then be used in testing to check that callbacks
        are called as expected.

        :param mocker: pytest fixture that wraps
            :py:mod:`unittest.mock`.

        :return: a dictionary of mocks for use as callbacks
        """
        return {
            "queue": mocker.Mock(),
            "status": mocker.Mock(),
            "progress": mocker.Mock(),
            "result": mocker.Mock(),
            "exception": mocker.Mock(),
        }

    @pytest.fixture
    def removal_time(self: TestCommandTracker) -> float:
        """
        Return how long the command tracker should retain memory of a completed command.

        :return: amount of time, in seconds.
        """
        return 0.1

    @pytest.fixture
    def command_tracker(
        self: TestCommandTracker,
        callbacks: dict[str, unittest.mock.Mock],
        removal_time: float,
    ) -> CommandTracker:
        """
        Return the command tracker under test.

        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        :param removal_time: how long completed command is retained

        :return: the command tracker under test
        """
        return CommandTracker(
            queue_changed_callback=callbacks["queue"],
            status_changed_callback=callbacks["status"],
            progress_changed_callback=callbacks["progress"],
            result_callback=callbacks["result"],
            exception_callback=callbacks["exception"],
            removal_time=removal_time,
        )

    # TODO pylint: disable=too-many-statements
    def test_command_tracker(
        self: TestCommandTracker,
        command_tracker: CommandTracker,
        removal_time: float,
        callbacks: dict[str, unittest.mock.Mock],
    ) -> None:
        """
        Test that the command tracker correctly tracks commands.

        :param command_tracker: the command tracker under test
        :param removal_time: how long completed command is retained
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """
        assert command_tracker.commands_in_queue == []
        assert command_tracker.command_statuses == []
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result is None
        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_not_called()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        first_command_id = command_tracker.new_command("first_command")
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command")
        ]
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.STAGING)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result is None
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_called_once_with(
            [(first_command_id, "first_command")]
        )
        callbacks["status"].assert_called_once_with(
            [(first_command_id, TaskStatus.STAGING)]
        )
        callbacks["queue"].reset_mock()
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        command_tracker.update_command_info(
            first_command_id, status=TaskStatus.IN_PROGRESS
        )
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command")
        ]
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.IN_PROGRESS)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result is None
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_called_once_with(
            [(first_command_id, TaskStatus.IN_PROGRESS)]
        )
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        second_command_id = command_tracker.new_command("second_command")
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command"),
            (second_command_id, "second_command"),
        ]
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.IN_PROGRESS),
            (second_command_id, TaskStatus.STAGING),
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result is None
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_called_once_with(
            [
                (first_command_id, "first_command"),
                (second_command_id, "second_command"),
            ]
        )
        callbacks["status"].assert_called_once_with(
            [
                (first_command_id, TaskStatus.IN_PROGRESS),
                (second_command_id, TaskStatus.STAGING),
            ]
        )
        callbacks["queue"].reset_mock()
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        command_tracker.update_command_info(first_command_id, progress=50)
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command"),
            (second_command_id, "second_command"),
        ]
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.IN_PROGRESS),
            (second_command_id, TaskStatus.STAGING),
        ]
        assert command_tracker.command_progresses == [(first_command_id, 50)]
        assert command_tracker.command_result is None
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_not_called()
        callbacks["progress"].assert_called_once_with([(first_command_id, 50)])
        callbacks["progress"].reset_mock()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        command_tracker.update_command_info(
            first_command_id, result=(ResultCode.OK, "a message string")
        )
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.IN_PROGRESS),
            (second_command_id, TaskStatus.STAGING),
        ]
        assert command_tracker.command_progresses == [(first_command_id, 50)]
        assert command_tracker.command_result == (
            first_command_id,
            (ResultCode.OK, "a message string"),
        )
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_not_called()
        callbacks["progress"].assert_not_called()
        callbacks["progress"].reset_mock()
        callbacks["result"].assert_called_once_with(
            first_command_id, (ResultCode.OK, "a message string")
        )
        callbacks["result"].reset_mock()
        callbacks["exception"].assert_not_called()

        command_tracker.update_command_info(
            first_command_id, status=TaskStatus.COMPLETED
        )
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command"),
            (second_command_id, "second_command"),
        ]
        time.sleep(removal_time + 0.1)
        assert command_tracker.commands_in_queue == [
            (second_command_id, "second_command")
        ]
        assert command_tracker.command_statuses == [
            (second_command_id, TaskStatus.STAGING)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result == (
            first_command_id,
            (ResultCode.OK, "a message string"),
        )
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_called_once_with(
            [(second_command_id, "second_command")]
        )
        callbacks["queue"].reset_mock()
        callbacks["status"].assert_called_once_with(
            [
                (first_command_id, TaskStatus.COMPLETED),
                (second_command_id, TaskStatus.STAGING),
            ]
        )
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        command_tracker.update_command_info(
            second_command_id, status=TaskStatus.IN_PROGRESS
        )
        assert command_tracker.commands_in_queue == [
            (second_command_id, "second_command")
        ]
        assert command_tracker.command_statuses == [
            (second_command_id, TaskStatus.IN_PROGRESS)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result == (
            first_command_id,
            (ResultCode.OK, "a message string"),
        )
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_called_once_with(
            [
                (second_command_id, TaskStatus.IN_PROGRESS),
            ]
        )
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        exception_to_raise = ValueError("Exception under test")

        command_tracker.update_command_info(
            second_command_id,
            status=TaskStatus.FAILED,
            exception=exception_to_raise,
        )
        assert command_tracker.commands_in_queue == [
            (second_command_id, "second_command")
        ]
        assert command_tracker.command_statuses == [
            (second_command_id, TaskStatus.FAILED)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result == (
            second_command_id,
            (ResultCode.FAILED, str(exception_to_raise)),
        )
        assert command_tracker.command_exception == (
            second_command_id,
            exception_to_raise,
        )

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_called_once_with(
            [
                (second_command_id, TaskStatus.FAILED),
            ]
        )
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_called_once_with(
            second_command_id, (ResultCode.FAILED, str(exception_to_raise))
        )
        callbacks["exception"].assert_called_once_with(
            second_command_id, exception_to_raise
        )


class TestSKABaseDevice:  # pylint: disable=too-many-public-methods
    """Test cases for SKABaseDevice."""

    @pytest.fixture(scope="class")
    def device_test_config(
        self: TestSKABaseDevice, device_properties: dict[str, str]
    ) -> dict[str, Any]:
        """
        Specify device configuration, including properties and memorized attributes.

        This implementation provides a concrete subclass of
        SKABaseDevice, and a memorized value for adminMode.

        :param device_properties: fixture that returns device properties
            of the device under test

        :return: specification of how the device under test should be
            configured
        """
        return {
            "device": ReferenceSkaBaseDevice,
            "component_manager_patch": lambda self: ReferenceBaseComponentManager(
                self.logger,
                self._communication_state_changed,
                self._component_state_changed,
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip("Not implemented")
    def test_properties(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test device properties.

        :param device_under_test: a DeviceProxy to the device under
            test, running in a DeviceTestContext
        """

    def test_State(self: TestSKABaseDevice, device_under_test: DeviceProxy) -> None:
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.state() == DevState.OFF

    def test_commandedState(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for commandedState.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        device_under_test.SetCommandTrackerRemovalTime(0)
        assert device_under_test.adminMode == AdminMode.ONLINE
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "commandedState",
            "longRunningCommandStatus",
        ]:
            device_under_test.subscribe_event(
                attribute,
                EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )
        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["commandedState"].assert_change_event("None")
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(())

        # ON command
        [[result_code], [on_command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED
        Helpers.assert_lrcstatus_change_event_staging_queued_in_progress(
            change_event_callbacks, on_command_id
        )
        change_event_callbacks["commandedState"].assert_change_event("ON")
        change_event_callbacks["state"].assert_change_event(DevState.ON)
        assert device_under_test.commandedState == device_under_test.state().name
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "COMPLETED")
        )

        # Simulate fault
        device_under_test.SimulateFault()
        change_event_callbacks["state"].assert_change_event(DevState.FAULT)
        with pytest.raises(
            DevFailed,
            match="Command On not allowed when the device is in FAULT state",
        ):
            device_under_test.On()
        with pytest.raises(
            DevFailed,
            match="Command Standby not allowed when the device is in FAULT state",
        ):
            device_under_test.Standby()
        assert device_under_test.commandedState == "ON"

        # RESET command
        [[result_code], [reset_command_id]] = device_under_test.Reset()
        assert result_code == ResultCode.QUEUED
        Helpers.assert_lrcstatus_change_event_staging_queued_in_progress(
            change_event_callbacks, reset_command_id
        )
        change_event_callbacks["state"].assert_change_event(DevState.ON)
        assert device_under_test.commandedState == device_under_test.state().name
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (reset_command_id, "COMPLETED")
        )

        # STANDBY command
        [[result_code], [standby_command_id]] = device_under_test.Standby()
        assert result_code == ResultCode.QUEUED
        Helpers.assert_lrcstatus_change_event_staging_queued_in_progress(
            change_event_callbacks, standby_command_id
        )
        change_event_callbacks["commandedState"].assert_change_event("STANDBY")
        change_event_callbacks["state"].assert_change_event(DevState.STANDBY)
        assert device_under_test.commandedState == device_under_test.state().name
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (standby_command_id, "COMPLETED")
        )

        # OFF command
        [[result_code], [off_command_id]] = device_under_test.Off()
        assert result_code == ResultCode.QUEUED
        Helpers.assert_lrcstatus_change_event_staging_queued_in_progress(
            change_event_callbacks, off_command_id
        )
        change_event_callbacks["commandedState"].assert_change_event("OFF")
        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        assert device_under_test.commandedState == device_under_test.state().name
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (off_command_id, "COMPLETED")
        )
        with pytest.raises(
            DevFailed,
            match="Command Reset not allowed when the device is in OFF state",
        ):
            device_under_test.Reset()

    def test_Status(self: TestSKABaseDevice, device_under_test: DeviceProxy) -> None:
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.Status() == "The device is in OFF state."

    def test_GetVersionInfo(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test for GetVersionInfo.

        :param device_under_test: a proxy to the device under test
        """
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])

    def test_Reset(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        successful_lrc_callback: LrcCallback,
    ) -> None:
        """
        Test for Reset.

        :param successful_lrc_callback: callback fixture to use with invoke_lrc.
        :param device_under_test: a proxy to the device under test
        """
        # The main test of this command is
        # TestSKABaseDevice_commands::test_ResetCommand
        assert device_under_test.state() == DevState.OFF

        with pytest.raises(
            DevFailed,
            match="Command Reset not allowed when the device is in OFF state",
        ):
            _ = invoke_lrc(device_under_test, successful_lrc_callback, "Reset")

    def test_On(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        successful_lrc_callback: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test for On command.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support.
        :param successful_lrc_callback: callback fixture to use with invoke_lrc.
        :param caplog: pytest LogCaptureFixture
        """
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "status",
            "longRunningCommandInProgress",
        ]:
            device_under_test.subscribe_event(
                attribute,
                EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandInProgress"].assert_change_event(())

        lrc_token = invoke_lrc(device_under_test, successful_lrc_callback, "On")
        on_command = lrc_token.command_id.split("_", 2)[2]
        change_event_callbacks.assert_change_event(
            "longRunningCommandInProgress", (on_command,)
        )
        change_event_callbacks.assert_change_event("state", DevState.ON)
        change_event_callbacks.assert_change_event(
            "status", "The device is in ON state."
        )
        assert device_under_test.state() == DevState.ON
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                "lrc_callback(status=STAGING)",
                "lrc_callback(status=QUEUED)",
                "lrc_callback(status=IN_PROGRESS)",
                "lrc_callback(progress=33)",
                "lrc_callback(progress=66)",
                "lrc_callback(result=[0, 'On command completed OK'])",
                "lrc_callback(status=COMPLETED)",
            ],
        )
        change_event_callbacks["longRunningCommandInProgress"].assert_change_event(())

        # Check what happens if we call On() when the device is already ON.
        with pytest.raises(
            CommandError, match="On command rejected: Device is already in ON state."
        ):
            _ = invoke_lrc(device_under_test, successful_lrc_callback, "On")
        change_event_callbacks.assert_not_called()

    def test_Standby(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        successful_lrc_callback: LrcCallback,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test for Standby command.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support.
        :param successful_lrc_callback: callback fixture to use with invoke_lrc.
        :param caplog: pytest LogCaptureFixture
        """
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "status",
            "longRunningCommandInProgress",
        ]:
            device_under_test.subscribe_event(
                attribute,
                EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandInProgress"].assert_change_event(())

        lrc_token = invoke_lrc(device_under_test, successful_lrc_callback, "Standby")
        standby_command = lrc_token.command_id.split("_", 2)[2]
        change_event_callbacks.assert_change_event(
            "longRunningCommandInProgress", (standby_command,)
        )
        change_event_callbacks.assert_change_event("state", DevState.STANDBY)
        change_event_callbacks.assert_change_event(
            "status", "The device is in STANDBY state."
        )
        assert device_under_test.state() == DevState.STANDBY
        Helpers.assert_expected_logs(
            caplog,
            [  # Log messages must be in this exact order
                "lrc_callback(status=STAGING)",
                "lrc_callback(status=QUEUED)",
                "lrc_callback(status=IN_PROGRESS)",
                "lrc_callback(progress=33)",
                "lrc_callback(progress=66)",
                "lrc_callback(result=[0, 'Standby command completed OK'])",
                "lrc_callback(status=COMPLETED)",
            ],
        )
        change_event_callbacks.assert_change_event("longRunningCommandInProgress", ())
        assert (
            device_under_test.CheckLongRunningCommandStatus(lrc_token.command_id)
            == "COMPLETED"
        )

        # Check what happens if we call Standby() when the device is already STANDBY.
        with pytest.raises(
            CommandError,
            match="Standby command rejected: Device is already in STANDBY state.",
        ):
            _ = invoke_lrc(device_under_test, successful_lrc_callback, "Standby")
        change_event_callbacks.assert_not_called()

    def test_Off(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
        successful_lrc_callback: LrcCallback,
    ) -> None:
        """
        Test for Off command.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        :param successful_lrc_callback: callback fixture to use with invoke_lrc.
        """
        assert device_under_test.state() == DevState.OFF

        for attribute in [
            "state",
            "status",
        ]:
            device_under_test.subscribe_event(
                attribute,
                EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )

        # Check what happens if we call Off() when the device is already OFF.
        with pytest.raises(
            CommandError,
            match="Off command rejected: Device is already in OFF state.",
        ):
            _ = invoke_lrc(device_under_test, successful_lrc_callback, "Off")
        change_event_callbacks.assert_not_called()

    def test_command_exception(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for when a command encounters an Exception.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        for attribute in [
            "longRunningCommandStatus",
            "longRunningCommandResult",
        ]:
            device_under_test.subscribe_event(
                attribute,
                EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(())
        change_event_callbacks["longRunningCommandResult"].assert_change_event(("", ""))

        # Queue On() followed by two commands that both raise exceptions
        command_ids = []
        for cmd in ("On", "SimulateCommandError", "SimulateIsCmdAllowedError"):
            [[result_code], [cmd_id]] = device_under_test.command_inout(cmd)
            command_ids.append(cmd_id)
            assert result_code == ResultCode.QUEUED
        # pylint: disable=unbalanced-tuple-unpacking
        on_command_id, command_error_id, command_allowed_error_id = command_ids

        # Each command goes STAGING to QUEUED, then On() goes IN_PROGRESS to COMPLETED,
        # and the other two commands go to FAILED/REJECTED.
        # We just assert the final results and statuses.
        for _ in range(7):
            change_event_callbacks.assert_against_call("longRunningCommandStatus")
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                on_command_id,
                json.dumps([int(ResultCode.OK), "On command completed OK"]),
            ),
        )
        change_event_callbacks.assert_against_call("longRunningCommandStatus")
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                command_error_id,
                json.dumps(
                    [
                        int(ResultCode.FAILED),
                        "Unhandled exception during execution: "
                        "Command encountered unexpected error",
                    ]
                ),
            ),
        )
        change_event_callbacks.assert_against_call("longRunningCommandStatus")
        assert device_under_test.longRunningCommandResult == (
            command_allowed_error_id,
            json.dumps(
                [
                    int(ResultCode.REJECTED),
                    "Exception from 'is_cmd_allowed' method: "
                    "'is_cmd_allowed' method encountered unexpected error",
                ]
            ),
        )
        change_event_callbacks.assert_against_call("longRunningCommandResult")
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                command_error_id,
                "FAILED",
                command_allowed_error_id,
                "REJECTED",
            ),
        )

    def test_lrcStatusQueue(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test the LRC status queue is pruned when there are too many commands to report.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        # Set the removal time long enough to cover the execution time of the test
        device_under_test.SetCommandTrackerRemovalTime(1000)
        max_queued_tasks = 32  # Set in TaskExecutorComponentManager
        assert device_under_test.state() == DevState.OFF

        device_under_test.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            change_event_callbacks["longRunningCommandResult"],
        )

        # Queue enough commands to fill the buffer
        command_ids = []
        for _ in range(max_queued_tasks):
            result_code, cmd_id = device_under_test.STANDBY()
            assert ResultCode(int(result_code)) == ResultCode.QUEUED
            command_ids.append(cmd_id[0])

        # Wait for them all to complete and queue another batch:
        for cmd_id in command_ids:
            change_event_callbacks.assert_change_event(
                "longRunningCommandResult",
                (
                    cmd_id,
                    json.dumps([int(ResultCode.OK), "Standby command completed OK"]),
                ),
                lookahead=max_queued_tasks,
                consume_nonmatches=True,
            )
        for _ in range(max_queued_tasks):
            result_code, cmd_id = device_under_test.ON()
            assert ResultCode(int(result_code)) == ResultCode.QUEUED
            command_ids.append(cmd_id[0])

        # Verify all commands reported in the Status attribute at this stage
        status_attribute = device_under_test.read_attribute("longRunningCommandStatus")
        for cmd_id in command_ids:
            assert cmd_id in status_attribute.value

        # Queue another ten to push the number over the array bounds
        for cmd_id in command_ids[32:42]:
            change_event_callbacks.assert_change_event(
                "longRunningCommandResult",
                (
                    cmd_id,
                    json.dumps([int(ResultCode.OK), "On command completed OK"]),
                ),
                lookahead=max_queued_tasks,
            )
        for _ in range(10):
            result_code, cmd_id = device_under_test.OFF()
            assert ResultCode(int(result_code)) == ResultCode.QUEUED
            command_ids.append(cmd_id[0])

        # max_queued_tasks = 32 and max_executing_tasks = 1,
        # so the attribute bounds are 32*2 + 1 = 65
        # Since we have submitted 74 commands, the first nine
        # completed commands should have been removed
        expected_removed_items = command_ids[:9]
        expected_present_items = command_ids[9:]
        status_attribute = device_under_test.read_attribute("longRunningCommandStatus")

        for cmd_id in expected_removed_items:
            assert cmd_id not in status_attribute.value
        for cmd_id in expected_present_items:
            assert cmd_id in status_attribute.value

    def test_buildState(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test for buildState.

        :param device_under_test: a proxy to the device under test
        """
        build_pattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(build_pattern, device_under_test.buildState)) is not None

    def test_versionId(self: TestSKABaseDevice, device_under_test: DeviceProxy) -> None:
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        version_id_pattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(version_id_pattern, device_under_test.versionId)) is not None

    def test_loggingLevel(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test for loggingLevel.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.loggingLevel == LoggingLevel.INFO

        for level in LoggingLevel:
            device_under_test.loggingLevel = level
            assert device_under_test.loggingLevel == level
            assert device_under_test.get_logging_level() == level

        with pytest.raises(DevFailed):
            device_under_test.loggingLevel = LoggingLevel.FATAL + 100

    def test_loggingTargets(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test for loggingTargets.

        :param device_under_test: a proxy to the device under test
        """
        # tango logging target must be enabled by default
        assert device_under_test.loggingTargets == ("tango::logger",)

        # test console target
        device_under_test.loggingTargets = ("console::cout",)
        assert device_under_test.loggingTargets == ("console::cout",)
        device_under_test.loggingTargets = (
            "console::cout",
            "file::/tmp/dummy",
            "syslog::udp://localhost:514",
        )
        assert device_under_test.loggingTargets == (
            "console::cout",
            "file::/tmp/dummy",
            "syslog::udp://localhost:514",
        )
        device_under_test.loggingTargets = ("tango::logger",)
        assert device_under_test.loggingTargets == ("tango::logger",)
        device_under_test.loggingTargets = tuple()
        assert device_under_test.loggingTargets == ()
        with pytest.raises(DevFailed):
            device_under_test.loggingTargets = ("invalid::type",)

    def test_healthState(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.healthState == HealthState.UNKNOWN

    def test_adminMode(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test for adminMode.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        assert device_under_test.state() == DevState.OFF

        for attribute in ["state", "status", "adminMode"]:
            device_under_test.subscribe_event(
                attribute,
                EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["adminMode"].assert_change_event(AdminMode.ONLINE)

        assert device_under_test.adminMode == AdminMode.ONLINE
        assert device_under_test.state() == DevState.OFF

        device_under_test.adminMode = AdminMode.OFFLINE

        change_event_callbacks.assert_change_event("adminMode", AdminMode.OFFLINE)
        assert device_under_test.adminMode == AdminMode.OFFLINE

        change_event_callbacks.assert_change_event("state", DevState.DISABLE)
        change_event_callbacks.assert_change_event(
            "status", "The device is in DISABLE state."
        )
        assert device_under_test.state() == DevState.DISABLE

        device_under_test.adminMode = AdminMode.ENGINEERING
        change_event_callbacks.assert_change_event("adminMode", AdminMode.ENGINEERING)
        assert device_under_test.adminMode == AdminMode.ENGINEERING

        change_event_callbacks.assert_change_event("state", DevState.UNKNOWN)
        change_event_callbacks.assert_change_event(
            "status", "The device is in UNKNOWN state."
        )

        change_event_callbacks.assert_change_event("state", DevState.OFF)
        change_event_callbacks.assert_change_event(
            "status", "The device is in OFF state."
        )
        assert device_under_test.state() == DevState.OFF

        device_under_test.adminMode = AdminMode.ONLINE
        change_event_callbacks.assert_change_event("adminMode", AdminMode.ONLINE)
        assert device_under_test.adminMode == AdminMode.ONLINE

        change_event_callbacks.assert_not_called()

        assert device_under_test.state() == DevState.OFF

    def test_controlMode(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.controlMode == ControlMode.REMOTE

    def test_simulationMode(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.simulationMode == SimulationMode.FALSE

    def test_testMode(self: TestSKABaseDevice, device_under_test: DeviceProxy) -> None:
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.testMode == TestMode.NONE

    def test_debugger_not_listening_by_default(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,  # pylint: disable=unused-argument
    ) -> None:
        """
        Test that DebugDevice is not active until enabled.

        :param device_under_test: a proxy to the device under test. This
            is not actually used, but the inclusion of the fixture
            ensures the device is running, which is a pre-condition of
            the test.
        """
        # pylint: disable-next=protected-access
        assert not SKABaseDevice._global_debugger_listening
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            with pytest.raises(ConnectionRefusedError):
                s.connect(("localhost", _DEBUGGER_PORT))

    def test_DebugDevice_starts_listening_on_default_port(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test that enabling DebugDevice makes it listen on its default port.

        :param device_under_test: a proxy to the device under test
        """
        port = device_under_test.DebugDevice()
        assert port == _DEBUGGER_PORT
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", _DEBUGGER_PORT))
        assert device_under_test.state

    @pytest.mark.usefixtures("patch_debugger_to_start_on_ephemeral_port")
    def test_DebugDevice_twice_does_not_raise(
        self: TestSKABaseDevice, device_under_test: DeviceProxy
    ) -> None:
        """
        Test that it is safe to enable the DebugDevice when it is already enabled.

        :param device_under_test: a proxy to the device under test
        """
        device_under_test.DebugDevice()
        port = device_under_test.DebugDevice()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", port))

    @pytest.mark.usefixtures("patch_debugger_to_start_on_ephemeral_port")
    def test_DebugDevice_does_not_break_a_command(
        self: TestSKABaseDevice,
        device_under_test: DeviceProxy,
        change_event_callbacks: MockTangoEventCallbackGroup,
    ) -> None:
        """
        Test that enabling the DebugDevice feature does not break device commands.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        device_under_test.DebugDevice()
        assert device_under_test.state() == DevState.OFF

        device_under_test.subscribe_event(
            "state",
            EventType.CHANGE_EVENT,
            change_event_callbacks["state"],
        )
        change_event_callbacks.assert_change_event("state", DevState.OFF)

        device_under_test.On()

        change_event_callbacks.assert_change_event("state", DevState.ON)

        assert device_under_test.state() == DevState.ON
