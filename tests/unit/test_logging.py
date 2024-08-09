# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module contains the tests for the TangoLoggingServiceHandler and utils."""
from __future__ import annotations

import logging
import socket
from typing import Any, cast
from unittest import mock

import pytest
from _pytest.fixtures import SubRequest
from ska_control_model import LoggingLevel
from tango import Logger

from ska_tango_base.base.logging import (
    _PYTHON_TO_TANGO_LOGGING_LEVEL,
    LoggingUtils,
    TangoLoggingServiceHandler,
    _Log4TangoLoggingLevel,
)
from ska_tango_base.faults import LoggingTargetError


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

    # pylint: disable=too-many-arguments
    @mock.patch("ska_tango_base.base.logging.TangoLoggingServiceHandler")
    @mock.patch("logging.handlers.SysLogHandler")
    @mock.patch("logging.handlers.RotatingFileHandler")
    @mock.patch("logging.StreamHandler")
    @mock.patch("ska_ser_logging.get_default_formatter")
    def test_create_logging_handler(
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
