#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#
#########################################################################################
"""This module contains the tests for the SKABaseDevice."""

# PROTECTED REGION ID(SKABaseDevice.test_additional_imports) ENABLED START #
import json
import logging
import re
import pytest
import socket
import time
from unittest import mock

import tango
from tango import DevFailed, DevState

import ska_tango_base.base.base_device

from ska_tango_base import SKABaseDevice
from ska_tango_base.base.base_device import (
    _CommandTracker,
    _DEBUGGER_PORT,
    _Log4TangoLoggingLevel,
    _PYTHON_TO_TANGO_LOGGING_LEVEL,
    LoggingUtils,
    LoggingTargetError,
    TangoLoggingServiceHandler,
)
from ska_tango_base.testing.reference import (
    ReferenceBaseComponentManager,
)
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    LoggingLevel,
    SimulationMode,
    TestMode,
)
from ska_tango_base.executor import TaskStatus

# PROTECTED REGION END #    //  SKABaseDevice.test_additional_imports
# Device test case
# PROTECTED REGION ID(SKABaseDevice.test_SKABaseDevice_decorators) ENABLED START #


class TestTangoLoggingServiceHandler:
    """This class contains tests of the TangoLoggingServiceHandler class."""

    @pytest.fixture()
    def tls_handler(self):
        """Return a logging service handler."""
        self.tango_logger = mock.MagicMock(spec=tango.Logger)
        # setup methods used for handler __repr__
        self.tango_logger.get_name.return_value = "unit/test/dev"
        self.tango_logger.get_level.return_value = _Log4TangoLoggingLevel.DEBUG
        return TangoLoggingServiceHandler(self.tango_logger)

    @pytest.fixture(
        params=[
            logging.DEBUG,
            logging.INFO,
            logging.WARN,
            logging.ERROR,
            logging.CRITICAL,
        ]
    )
    def python_log_level(self, request):
        """Return a python logging level."""
        return request.param

    def test_emit_message_at_correct_level(self, tls_handler, python_log_level):
        """Test that emitted messages are logged at the right level."""
        # arrange
        record = logging.LogRecord("test", python_log_level, "", 1, "message", (), None)
        # act
        tls_handler.emit(record)
        # assert
        expected_tango_level = _PYTHON_TO_TANGO_LOGGING_LEVEL[python_log_level]
        expected_calls = [mock.call(expected_tango_level, mock.ANY)]
        assert self.tango_logger.log.call_args_list == expected_calls

    def test_emit_message_is_formatted(self, tls_handler):
        """Test that emitted messages are formatted as specified."""
        # arrange
        record = logging.LogRecord(
            "test", logging.INFO, "", 1, "message %s", ("param",), None
        )

        def format_stub(log_record):
            return "LOG: " + log_record.getMessage()

        tls_handler.format = format_stub
        # act
        tls_handler.emit(record)
        # assert
        expected_tango_level = _PYTHON_TO_TANGO_LOGGING_LEVEL[logging.INFO]
        expected_message = "LOG: message param"
        expected_calls = [mock.call(expected_tango_level, expected_message)]
        assert self.tango_logger.log.call_args_list == expected_calls

    def test_emit_exception_error_handled(self, tls_handler):
        """Test exception handling when a record is emitted."""
        # arrange
        record = logging.LogRecord("test", logging.INFO, "", 1, "message", (), None)

        def cause_exception(*args, **kwargs):
            raise RuntimeError("Testing")

        self.tango_logger.log.side_effect = cause_exception
        tls_handler.handleError = mock.MagicMock()
        # act
        tls_handler.emit(record)
        # assert
        assert tls_handler.handleError.call_args_list == [mock.call(record)]

    def test_repr_normal(self, tls_handler):
        """Test the string representation of a handler under normal conditions."""
        expected = (
            "<TangoLoggingServiceHandler unit/test/dev (Python NOTSET, Tango DEBUG)>"
        )
        assert repr(tls_handler) == expected

    def test_repr_tango_logger_none(self, tls_handler):
        """Test the string representation of a handler with no logger."""
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
    def good_logging_targets(self, request):
        """Return some good logging targets for use in testing."""
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
    def bad_logging_targets(self, request):
        """Return some bad logging targets for use in testing."""
        targets_in = request.param
        dev_name = "my/dev/name"
        return targets_in, dev_name

    def test_sanitise_logging_targets_success(self, good_logging_targets):
        """Test that good logging targets can be sanitised."""
        targets_in, dev_name, expected = good_logging_targets
        actual = LoggingUtils.sanitise_logging_targets(targets_in, dev_name)
        assert actual == expected

    def test_sanitise_logging_targets_fail(self, bad_logging_targets):
        """Test that bad logging targets cannot be sanitised."""
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
    def good_syslog_url(self, request):
        """Return a good logging target URL."""
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
    def bad_syslog_url(self, request):
        """Return a bad logging target URL."""
        return request.param

    def test_get_syslog_address_and_socktype_success(self, good_syslog_url):
        """Test that logging successfully accepts a good target."""
        url, (expected_address, expected_socktype) = good_syslog_url
        (
            actual_address,
            actual_socktype,
        ) = LoggingUtils.get_syslog_address_and_socktype(url)
        assert actual_address == expected_address
        assert actual_socktype == expected_socktype

    def test_get_syslog_address_and_socktype_fail(self, bad_syslog_url):
        """Test that logging raises an error when given a bad target."""
        with pytest.raises(LoggingTargetError):
            LoggingUtils.get_syslog_address_and_socktype(bad_syslog_url)

    @mock.patch("ska_tango_base.base.base_device.TangoLoggingServiceHandler")
    @mock.patch("logging.handlers.SysLogHandler")
    @mock.patch("logging.handlers.RotatingFileHandler")
    @mock.patch("logging.StreamHandler")
    @mock.patch("ska_ser_logging.get_default_formatter")
    def test_create_logging_handler(
        self,
        mock_get_formatter,
        mock_stream_handler,
        mock_file_handler,
        mock_syslog_handler,
        mock_tango_handler,
    ):
        """Test that logging handlers can be created."""
        # Expect formatter be created using `get_default_formatter(tags=True)`
        # Use some mocks to check this.
        mock_formatter = mock.MagicMock()

        def get_formatter_if_tags_enabled(*args, **kwargs):
            if kwargs.get("tags", False):
                return mock_formatter

        mock_get_formatter.side_effect = get_formatter_if_tags_enabled
        mock_tango_logger = mock.MagicMock(spec=tango.Logger)

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

    def test_update_logging_handlers(self):
        """Test that logging handlers can be updated."""
        logger = logging.getLogger("testing")
        logger.tango_logger = mock.MagicMock(spec=tango.Logger)

        def null_creator(target, tango_logger):
            handler = logging.NullHandler()
            handler.name = target
            return handler

        orig_create_logging_handler = LoggingUtils.create_logging_handler
        try:
            mocked_creator = mock.MagicMock(side_effect=null_creator)
            LoggingUtils.create_logging_handler = mocked_creator

            # test adding first handler
            new_targets = ["console::cout"]
            LoggingUtils.update_logging_handlers(new_targets, logger)
            assert len(logger.handlers) == 1
            mocked_creator.assert_called_once_with("console::cout", logger.tango_logger)

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
                    mock.call("file::/tmp/dummy", logger.tango_logger),
                    mock.call("syslog::some/address", logger.tango_logger),
                    mock.call("tango::logger", logger.tango_logger),
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
            LoggingUtils.create_logging_handler = orig_create_logging_handler


# PROTECTED REGION END #    //  SKABaseDevice.test_SKABaseDevice_decorators
class TestCommandTracker:
    """Tests of the _CommandTracker class."""

    @pytest.fixture
    def callbacks(self, mocker):
        """
        Return a dictionary of mocks for use as callbacks.

        These callbacks will be passed to the command tracker under
        test, and can then be used in testing to check that callbacks
        are called as expected.

        :param mocker: pytest fixture that wraps
            :py:mod:`unittest.mock`.
        """
        return {
            "queue": mocker.Mock(),
            "status": mocker.Mock(),
            "progress": mocker.Mock(),
            "result": mocker.Mock(),
            "exception": mocker.Mock(),
        }

    @pytest.fixture
    def removal_time(self) -> float:
        """
        Return how long the command tracker should retain memory of a completed command.

        :return: amount of time, in seconds.
        """
        return 0.1

    @pytest.fixture
    def command_tracker(self, callbacks, removal_time):
        """
        Return the command tracker under test.

        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """
        return _CommandTracker(
            queue_changed_callback=callbacks["queue"],
            status_changed_callback=callbacks["status"],
            progress_changed_callback=callbacks["progress"],
            result_callback=callbacks["result"],
            exception_callback=callbacks["exception"],
            removal_time=removal_time,
        )

    def test_command_tracker(self, command_tracker, removal_time, callbacks):
        """
        Test that the command tracker correctly tracks commands.

        :param command_tracker: the command tracker under test
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
        callbacks["queue"].reset_mock()
        callbacks["status"].assert_not_called()
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
            [(first_command_id, "first_command"), (second_command_id, "second_command")]
        )
        callbacks["queue"].reset_mock()
        callbacks["status"].assert_not_called()
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
            first_command_id,
            (ResultCode.OK, "a message string"),
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
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_called_once_with(
            second_command_id, exception_to_raise
        )


class TestSKABaseDevice(object):
    """Test cases for SKABaseDevice."""

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
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
            "device": SKABaseDevice,
            "component_manager_patch": lambda self: ReferenceBaseComponentManager(
                self.logger,
                self._communication_state_changed,
                self._component_state_changed,
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip("Not implemented")
    def test_properties(self, device_under_test):
        """
        Test device properties.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKABaseDevice.test_properties) ENABLED START #
        """
        Test device properties.

        :param device_under_test: a DeviceProxy to the device under
            test, running in a tango.DeviceTestContext
        :type device_under_test: :py:class:`tango.DeviceProxy`

        :return: None
        """
        # PROTECTED REGION END #    //  SKABaseDevice.test_properties
        # pass

    # PROTECTED REGION ID(SKABaseDevice.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_State_decorators
    def test_State(self, device_under_test):
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKABaseDevice.test_State) ENABLED START #
        assert device_under_test.state() == DevState.OFF

        # PROTECTED REGION END #    //  SKABaseDevice.test_State

    # PROTECTED REGION ID(SKABaseDevice.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_Status_decorators
    def test_Status(self, device_under_test):
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKABaseDevice.test_Status) ENABLED START #
        assert device_under_test.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKABaseDevice.test_Status

    # PROTECTED REGION ID(SKABaseDevice.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test):
        """
        Test for GetVersionInfo.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKABaseDevice.test_GetVersionInfo) ENABLED START #
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])

        # PROTECTED REGION END #    //  SKABaseDevice.test_GetVersionInfo

    def test_Reset(self, device_under_test):
        """
        Test for Reset.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKABaseDevice.test_Reset) ENABLED START #
        # The main test of this command is
        # TestSKABaseDevice_commands::test_ResetCommand
        assert device_under_test.state() == DevState.OFF

        with pytest.raises(
            DevFailed,
            match="Command Reset not allowed when the device is in OFF state",
        ):
            _ = device_under_test.Reset()
        # PROTECTED REGION END #    //  SKABaseDevice.test_Reset

    def test_On(self, device_under_test, tango_change_event_helper):
        """
        Test for On command.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        device_status_callback = tango_change_event_helper.subscribe("status")
        device_status_callback.assert_next_change_event("The device is in OFF state.")

        command_progress_callback = tango_change_event_helper.subscribe(
            "longRunningCommandProgress"
        )
        command_progress_callback.assert_next_change_event(None)

        command_status_callback = tango_change_event_helper.subscribe(
            "longRunningCommandStatus"
        )
        command_status_callback.assert_next_change_event(None)

        command_result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )
        command_result_callback.assert_next_change_event(("", ""))

        [[result_code], [command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED
        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        device_state_callback.assert_next_change_event(DevState.ON)
        device_status_callback.assert_next_change_event("The device is in ON state.")
        assert device_under_test.state() == DevState.ON

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "On command completed OK"]))
        )

        # Check what happens if we call On() when the device is already ON.
        [[result_code], [message]] = device_under_test.On()
        assert result_code == ResultCode.REJECTED
        assert message == "Device is already in ON state."

        command_status_callback.assert_not_called()
        command_progress_callback.assert_not_called()
        command_result_callback.assert_not_called()

        device_state_callback.assert_not_called()
        device_status_callback.assert_not_called()

    def test_Standby(self, device_under_test, tango_change_event_helper):
        """
        Test for Standby command.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        # Check that we can put it on standby
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        device_status_callback = tango_change_event_helper.subscribe("status")
        device_status_callback.assert_next_change_event("The device is in OFF state.")

        command_progress_callback = tango_change_event_helper.subscribe(
            "longRunningCommandProgress"
        )
        command_progress_callback.assert_next_change_event(None)

        command_status_callback = tango_change_event_helper.subscribe(
            "longRunningCommandStatus"
        )
        command_status_callback.assert_next_change_event(None)

        command_result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )
        command_result_callback.assert_next_change_event(("", ""))

        [[result_code], [command_id]] = device_under_test.Standby()
        assert result_code == ResultCode.QUEUED

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        device_state_callback.assert_next_change_event(DevState.STANDBY)
        device_status_callback.assert_next_change_event(
            "The device is in STANDBY state."
        )
        assert device_under_test.state() == DevState.STANDBY

        command_result_callback.assert_next_change_event(
            (
                command_id,
                json.dumps([int(ResultCode.OK), "Standby command completed OK"]),
            )
        )

        # Check what happens if we call Standby() when the device is already STANDBY.
        [[result_code], [message]] = device_under_test.Standby()
        assert result_code == ResultCode.REJECTED
        assert message == "Device is already in STANDBY state."

        command_status_callback.assert_not_called()
        command_progress_callback.assert_not_called()
        command_result_callback.assert_not_called()

        device_state_callback.assert_not_called()
        device_status_callback.assert_not_called()

    def test_Off(self, device_under_test, tango_change_event_helper):
        """
        Test for Off command.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        device_status_callback = tango_change_event_helper.subscribe("status")
        device_status_callback.assert_next_change_event("The device is in OFF state.")

        command_progress_callback = tango_change_event_helper.subscribe(
            "longRunningCommandProgress"
        )
        command_progress_callback.assert_next_change_event(None)

        command_status_callback = tango_change_event_helper.subscribe(
            "longRunningCommandStatus"
        )
        command_status_callback.assert_next_change_event(None)

        command_result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )
        command_result_callback.assert_next_change_event(("", ""))

        # Check what happens if we call Off() when the device is already OFF.
        [[result_code], [message]] = device_under_test.Off()
        assert result_code == ResultCode.REJECTED
        assert message == "Device is already in OFF state."

        device_state_callback.assert_not_called()
        device_status_callback.assert_not_called()
        command_progress_callback.assert_not_called()
        command_status_callback.assert_not_called()
        command_result_callback.assert_not_called()

    # PROTECTED REGION ID(SKABaseDevice.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_buildState_decorators
    def test_buildState(self, device_under_test):
        """
        Test for buildState.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKABaseDevice.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, device_under_test.buildState)) is not None
        # PROTECTED REGION END #    //  SKABaseDevice.test_buildState

    # PROTECTED REGION ID(SKABaseDevice.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_versionId_decorators
    def test_versionId(self, device_under_test):
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKABaseDevice.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  SKABaseDevice.test_versionId

    # PROTECTED REGION ID(SKABaseDevice.test_loggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_loggingLevel_decorators
    def test_loggingLevel(self, device_under_test):
        """
        Test for loggingLevel.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKABaseDevice.test_loggingLevel) ENABLED START #
        assert device_under_test.loggingLevel == LoggingLevel.INFO

        for level in LoggingLevel:
            device_under_test.loggingLevel = level
            assert device_under_test.loggingLevel == level
            assert device_under_test.get_logging_level() == level

        with pytest.raises(DevFailed):
            device_under_test.loggingLevel = LoggingLevel.FATAL + 100
        # PROTECTED REGION END #    //  SKABaseDevice.test_loggingLevel

    # PROTECTED REGION ID(SKABaseDevice.test_loggingTargets_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_loggingTargets_decorators
    def test_loggingTargets(self, device_under_test):
        """
        Test for loggingTargets.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKABaseDevice.test_loggingTargets) ENABLED START #
        # tango logging target must be enabled by default
        assert device_under_test.loggingTargets == ("tango::logger",)

        with mock.patch(
            "ska_tango_base.base.base_device.LoggingUtils.create_logging_handler"
        ) as mocked_creator:

            def null_creator(target, tango_logger):
                handler = logging.NullHandler()
                handler.name = target
                assert isinstance(tango_logger, tango.Logger)
                return handler

            mocked_creator.side_effect = null_creator

            # test console target
            device_under_test.loggingTargets = ["console::cout"]
            assert device_under_test.loggingTargets == ("console::cout",)
            mocked_creator.assert_called_once_with("console::cout", mock.ANY)

            # test adding file and syslog targets (already have console)
            mocked_creator.reset_mock()
            device_under_test.loggingTargets = [
                "console::cout",
                "file::/tmp/dummy",
                "syslog::udp://localhost:514",
            ]
            assert device_under_test.loggingTargets == (
                "console::cout",
                "file::/tmp/dummy",
                "syslog::udp://localhost:514",
            )
            assert mocked_creator.call_count == 2
            mocked_creator.assert_has_calls(
                [
                    mock.call("file::/tmp/dummy", mock.ANY),
                    mock.call("syslog::udp://localhost:514", mock.ANY),
                ],
                any_order=True,
            )

            # test adding tango logging again, now that mock is active
            # (it wasn't active when device was initialised)
            mocked_creator.reset_mock()
            device_under_test.loggingTargets = ["tango::logger"]
            assert device_under_test.loggingTargets == ("tango::logger",)
            mocked_creator.assert_called_once_with("tango::logger", mock.ANY)

            # test clearing all targets (note: PyTango returns None for empty spectrum attribute)
            device_under_test.loggingTargets = []
            assert device_under_test.loggingTargets is None

            mocked_creator.reset_mock()
            with pytest.raises(DevFailed):
                device_under_test.loggingTargets = ["invalid::type"]
            mocked_creator.assert_not_called()
        # PROTECTED REGION END #    //  SKABaseDevice.test_loggingTargets

    # PROTECTED REGION ID(SKABaseDevice.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_healthState_decorators
    def test_healthState(self, device_under_test):
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKABaseDevice.test_healthState) ENABLED START #
        assert device_under_test.healthState == HealthState.UNKNOWN
        # PROTECTED REGION END #    //  SKABaseDevice.test_healthState

    # PROTECTED REGION ID(SKABaseDevice.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_adminMode_decorators
    def test_adminMode(self, device_under_test, tango_change_event_helper):
        """
        Test for adminMode.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        # PROTECTED REGION ID(SKABaseDevice.test_adminMode) ENABLED START #
        assert device_under_test.state() == DevState.OFF

        state_callback = tango_change_event_helper.subscribe("state")
        status_callback = tango_change_event_helper.subscribe("status")
        admin_mode_callback = tango_change_event_helper.subscribe("adminMode")

        admin_mode_callback.assert_next_change_event(AdminMode.ONLINE)
        state_callback.assert_next_change_event(DevState.OFF)
        status_callback.assert_next_change_event("The device is in OFF state.")

        assert device_under_test.adminMode == AdminMode.ONLINE
        assert device_under_test.state() == DevState.OFF

        device_under_test.adminMode = AdminMode.OFFLINE
        admin_mode_callback.assert_next_change_event(AdminMode.OFFLINE)
        assert device_under_test.adminMode == AdminMode.OFFLINE

        state_callback.assert_next_change_event(DevState.DISABLE)
        status_callback.assert_next_change_event("The device is in DISABLE state.")
        assert device_under_test.state() == DevState.DISABLE

        device_under_test.adminMode = AdminMode.MAINTENANCE
        admin_mode_callback.assert_next_change_event(AdminMode.MAINTENANCE)
        assert device_under_test.adminMode == AdminMode.MAINTENANCE

        state_callback.assert_next_change_event(DevState.UNKNOWN)
        status_callback.assert_next_change_event("The device is in UNKNOWN state.")

        state_callback.assert_next_change_event(DevState.OFF)
        status_callback.assert_next_change_event("The device is in OFF state.")
        assert device_under_test.state() == DevState.OFF

        device_under_test.adminMode = AdminMode.ONLINE
        admin_mode_callback.assert_next_change_event(AdminMode.ONLINE)
        assert device_under_test.adminMode == AdminMode.ONLINE

        state_callback.assert_not_called()
        status_callback.assert_not_called()
        assert device_under_test.state() == DevState.OFF
        # PROTECTED REGION END #    //  SKABaseDevice.test_adminMode

    # PROTECTED REGION ID(SKABaseDevice.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_controlMode_decorators
    def test_controlMode(self, device_under_test):
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKABaseDevice.test_controlMode) ENABLED START #
        assert device_under_test.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKABaseDevice.test_controlMode

    # PROTECTED REGION ID(SKABaseDevice.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_simulationMode_decorators
    def test_simulationMode(self, device_under_test):
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKABaseDevice.test_simulationMode) ENABLED START #
        assert device_under_test.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKABaseDevice.test_simulationMode

    # PROTECTED REGION ID(SKABaseDevice.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_testMode_decorators
    def test_testMode(self, device_under_test):
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKABaseDevice.test_testMode) ENABLED START #
        assert device_under_test.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKABaseDevice.test_testMode

    def test_debugger_not_listening_by_default(self, device_under_test):
        """
        Test that DebugDevice is not active until enabled.

        :param device_under_test: a proxy to the device under test
        """
        assert not SKABaseDevice._global_debugger_listening
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            with pytest.raises(ConnectionRefusedError):
                s.connect(("localhost", _DEBUGGER_PORT))

    def test_DebugDevice_starts_listening_on_default_port(self, device_under_test):
        """
        Test that enabling DebugDevice makes it listen on its default port.

        :param device_under_test: a proxy to the device under test
        """
        port = device_under_test.DebugDevice()
        assert port == _DEBUGGER_PORT
        assert SKABaseDevice._global_debugger_listening
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", _DEBUGGER_PORT))
        assert device_under_test.state

    @pytest.mark.usefixtures("patch_debugger_to_start_on_ephemeral_port")
    def test_DebugDevice_twice_does_not_raise(self, device_under_test):
        """
        Test that it is safe to enable the DebugDevice when it is already enabled.

        :param device_under_test: a proxy to the device under test
        """
        device_under_test.DebugDevice()
        device_under_test.DebugDevice()
        assert SKABaseDevice._global_debugger_listening

    @pytest.mark.usefixtures("patch_debugger_to_start_on_ephemeral_port")
    def test_DebugDevice_does_not_break_a_command(
        self, device_under_test, tango_change_event_helper
    ):
        """
        Test that enabling the DebugDevice feature does not break device commands.

        :param device_under_test: a proxy to the device under test
        """
        device_under_test.DebugDevice()
        assert device_under_test.state() == DevState.OFF

        state_callback = tango_change_event_helper.subscribe("state")
        state_callback.assert_next_change_event(DevState.OFF)

        device_under_test.On()

        state_callback.assert_next_change_event(DevState.ON)

        assert device_under_test.state() == DevState.ON


@pytest.fixture()
def patch_debugger_to_start_on_ephemeral_port():
    """
    Patch the debugger so that it starts on an ephemeral port.

    This is necessary because of intermittent debugger test failures: if
    the previous test has used the debugger port, then when the test
    tries to bind to that port, it may find that the OS has not made it
    available for use yet.
    """
    ska_tango_base.base.base_device._DEBUGGER_PORT = 0
