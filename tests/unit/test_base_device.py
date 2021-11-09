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
import logging
import re
import pytest
import socket
import tango

from unittest import mock
from tango import DevFailed, DevState

import ska_tango_base.base.base_device

from ska_tango_base import SKABaseDevice
from ska_tango_base.base import OpStateModel, ReferenceBaseComponentManager
from ska_tango_base.base.base_device import (
    _DEBUGGER_PORT,
    _Log4TangoLoggingLevel,
    _PYTHON_TO_TANGO_LOGGING_LEVEL,
    LoggingUtils,
    LoggingTargetError,
    TangoLoggingServiceHandler,
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
from ska_tango_base.faults import CommandError

from .state.conftest import load_state_machine_spec

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
        expected = "<TangoLoggingServiceHandler !No Tango logger! (Python NOTSET, Tango UNKNOWN)>"
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
            ("tcp://127.0.0.1:1234", [("127.0.0.1", 1234), socket.SOCK_STREAM]),
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
        actual_address, actual_socktype = LoggingUtils.get_syslog_address_and_socktype(
            url
        )
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
            address="/tmp/path", facility=mock_syslog_handler.LOG_SYSLOG, socktype=None
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
class TestSKABaseDevice(object):
    """Test cases for SKABaseDevice."""

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Specify device configuration, including properties and memorized attributes.

        This implementation provides a concrete subclass of
        SKABaseDevice, and a memorized value for adminMode.
        """
        return {
            "device": SKABaseDevice,
            "component_manager_patch": lambda self: ReferenceBaseComponentManager(
                self.op_state_model, logger=self.logger
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip("Not implemented")
    def test_properties(self, device_under_test):
        """Test device properties."""
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
        """Test for State."""
        # PROTECTED REGION ID(SKABaseDevice.test_State) ENABLED START #
        assert device_under_test.State() == DevState.OFF
        # PROTECTED REGION END #    //  SKABaseDevice.test_State

    # PROTECTED REGION ID(SKABaseDevice.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_Status_decorators
    def test_Status(self, device_under_test):
        """Test for Status."""
        # PROTECTED REGION ID(SKABaseDevice.test_Status) ENABLED START #
        assert device_under_test.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKABaseDevice.test_Status

    # PROTECTED REGION ID(SKABaseDevice.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test):
        """Test for GetVersionInfo."""
        # PROTECTED REGION ID(SKABaseDevice.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            f"['{device_under_test.info().dev_class}, ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            "A set of generic base devices for SKA Telescope.']"
        )
        device_under_test.GetVersionInfo()
        versionInfo = device_under_test.longRunningCommandResult[2]
        assert (re.match(versionPattern, versionInfo)) is not None
        # PROTECTED REGION END #    //  SKABaseDevice.test_GetVersionInfo

    # PROTECTED REGION ID(SKABaseDevice.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_Reset_decorators
    def test_Reset(self, device_under_test):
        """Test for Reset."""
        # PROTECTED REGION ID(SKABaseDevice.test_Reset) ENABLED START #
        # The main test of this command is
        # TestSKABaseDevice_commands::test_ResetCommand
        device_under_test.Reset()
        assert f"{ResultCode.FAILED}" == device_under_test.longRunningCommandResult[1]
        assert (
            "Action reset_invoked is not allowed in op_state OFF"
            in device_under_test.longRunningCommandResult[2]
        )
        # PROTECTED REGION END #    //  SKABaseDevice.test_Reset

    def test_On(self, device_under_test, tango_change_event_helper):
        """Test for On command."""
        state_callback = tango_change_event_helper.subscribe("state")
        status_callback = tango_change_event_helper.subscribe("status")
        state_callback.assert_call(DevState.OFF)
        status_callback.assert_call("The device is in OFF state.")

        # Check that we can turn a freshly initialised device on
        device_under_test.On()
        state_callback.assert_call(DevState.ON)
        status_callback.assert_call("The device is in ON state.")

        # Check that we can turn it on when it is already on
        device_under_test.On()
        state_callback.assert_not_called()
        status_callback.assert_not_called()

    def test_Standby(self, device_under_test):
        """Test for Standby command."""
        # Check that we can put it on standby
        device_under_test.Standby()
        assert device_under_test.state() == DevState.STANDBY

        # Check that we can put it on standby when it is already on standby
        device_under_test.Standby()

    def test_Off(self, device_under_test, tango_change_event_helper):
        """Test for Off command."""
        state_callback = tango_change_event_helper.subscribe("state")
        status_callback = tango_change_event_helper.subscribe("status")
        state_callback.assert_call(DevState.OFF)
        status_callback.assert_call("The device is in OFF state.")

        # Check that we can turn off a device that is already off
        device_under_test.Off()
        state_callback.assert_not_called()
        status_callback.assert_not_called()

    # PROTECTED REGION ID(SKABaseDevice.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_buildState_decorators
    def test_buildState(self, device_under_test):
        """Test for buildState."""
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
        """Test for versionId."""
        # PROTECTED REGION ID(SKABaseDevice.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  SKABaseDevice.test_versionId

    # PROTECTED REGION ID(SKABaseDevice.test_loggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_loggingLevel_decorators
    def test_loggingLevel(self, device_under_test):
        """Test for loggingLevel."""
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
        """Test for loggingTargets."""
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
        """Test for healthState."""
        # PROTECTED REGION ID(SKABaseDevice.test_healthState) ENABLED START #
        assert device_under_test.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SKABaseDevice.test_healthState

    # PROTECTED REGION ID(SKABaseDevice.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_adminMode_decorators
    def test_adminMode(self, device_under_test, tango_change_event_helper):
        """Test for adminMode."""
        # PROTECTED REGION ID(SKABaseDevice.test_adminMode) ENABLED START #
        assert device_under_test.adminMode == AdminMode.ONLINE
        assert device_under_test.state() == DevState.OFF

        admin_mode_callback = tango_change_event_helper.subscribe("adminMode")
        admin_mode_callback.assert_call(AdminMode.ONLINE)

        device_under_test.adminMode = AdminMode.OFFLINE
        assert device_under_test.adminMode == AdminMode.OFFLINE
        admin_mode_callback.assert_call(AdminMode.OFFLINE)
        assert device_under_test.state() == DevState.DISABLE

        device_under_test.adminMode = AdminMode.MAINTENANCE
        assert device_under_test.adminMode == AdminMode.MAINTENANCE
        admin_mode_callback.assert_call(AdminMode.MAINTENANCE)
        assert device_under_test.state() == DevState.OFF

        device_under_test.adminMode = AdminMode.ONLINE
        assert device_under_test.adminMode == AdminMode.ONLINE
        admin_mode_callback.assert_call(AdminMode.ONLINE)
        assert device_under_test.state() == DevState.OFF
        # PROTECTED REGION END #    //  SKABaseDevice.test_adminMode

    # PROTECTED REGION ID(SKABaseDevice.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_controlMode_decorators
    def test_controlMode(self, device_under_test):
        """Test for controlMode."""
        # PROTECTED REGION ID(SKABaseDevice.test_controlMode) ENABLED START #
        assert device_under_test.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKABaseDevice.test_controlMode

    # PROTECTED REGION ID(SKABaseDevice.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_simulationMode_decorators
    def test_simulationMode(self, device_under_test):
        """Test for simulationMode."""
        # PROTECTED REGION ID(SKABaseDevice.test_simulationMode) ENABLED START #
        assert device_under_test.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKABaseDevice.test_simulationMode

    # PROTECTED REGION ID(SKABaseDevice.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_testMode_decorators
    def test_testMode(self, device_under_test):
        """Test for testMode."""
        # PROTECTED REGION ID(SKABaseDevice.test_testMode) ENABLED START #
        assert device_under_test.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKABaseDevice.test_testMode

    def test_debugger_not_listening_by_default(self, device_under_test):
        """Test that DebugDevice is not active until enabled."""
        assert not SKABaseDevice._global_debugger_listening
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            with pytest.raises(ConnectionRefusedError):
                s.connect(("localhost", _DEBUGGER_PORT))

    def test_DebugDevice_starts_listening_on_default_port(self, device_under_test):
        """Test that enabling DebugDevice makes it listen on its default port."""
        port = device_under_test.DebugDevice()
        assert port == _DEBUGGER_PORT
        assert SKABaseDevice._global_debugger_listening
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", _DEBUGGER_PORT))
        assert device_under_test.state

    @pytest.mark.usefixtures("patch_debugger_to_start_on_ephemeral_port")
    def test_DebugDevice_twice_does_not_raise(self, device_under_test):
        """Test that it is safe to enable the DebugDevice when it is already enabled."""
        device_under_test.DebugDevice()
        device_under_test.DebugDevice()
        assert SKABaseDevice._global_debugger_listening

    @pytest.mark.usefixtures("patch_debugger_to_start_on_ephemeral_port")
    def test_DebugDevice_does_not_break_a_command(self, device_under_test):
        """Test that enabling the DebugDevice feature does not break device commands."""
        device_under_test.DebugDevice()
        assert device_under_test.State() == DevState.OFF
        device_under_test.On()
        assert device_under_test.State() == DevState.ON


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


class TestSKABaseDevice_commands:
    """This class contains tests of SKABaseDevice commands."""

    @pytest.fixture
    def op_state_model(self, logger):
        """
        Yield a new OpStateModel for testing.

        :yields: a OpStateModel instance to be tested
        """
        yield OpStateModel(logger)

    @pytest.fixture
    def command_factory(self, mocker, op_state_model):
        """
        Return a factory that constructs a command object for a given class.

        :returns: a factory that constructs a command object for a given
            class
        """

        def _command_factory(command):
            return command(mocker.Mock(), op_state_model)

        return _command_factory

    @pytest.fixture
    def machine_spec(self):
        """Return a state machine specification."""
        return load_state_machine_spec("op_state_machine")

    @pytest.fixture()
    def op_state_mapping(self):
        """Return a mapping from state machine state to model state."""
        return {
            "_UNINITIALISED": None,
            "INIT_DISABLE": DevState.INIT,
            "INIT_UNKNOWN": DevState.INIT,
            "INIT_OFF": DevState.INIT,
            "INIT_STANDBY": DevState.INIT,
            "INIT_ON": DevState.INIT,
            "INIT_FAULT": DevState.INIT,
            "DISABLE": DevState.DISABLE,
            "UNKNOWN": DevState.UNKNOWN,
            "OFF": DevState.OFF,
            "STANDBY": DevState.STANDBY,
            "ON": DevState.ON,
            "FAULT": DevState.FAULT,
        }

    @pytest.mark.parametrize(
        ("command_class", "slug"),
        [
            (SKABaseDevice.ResetCommand, "reset"),
            (SKABaseDevice.OffCommand, "off"),
            (SKABaseDevice.StandbyCommand, "standby"),
            (SKABaseDevice.OnCommand, "on"),
        ],
    )
    def test_Command(
        self,
        machine_spec,
        op_state_mapping,
        command_factory,
        op_state_model,
        command_class,
        slug,
    ):
        """
        Test command invokation.

        Specifically, test that certain commands can only be invoked in
        certain states, and that the result of invoking the command is
        as expected.
        """
        command = command_factory(command_class)

        states = machine_spec["states"]
        transitions = machine_spec["transitions"]
        transitions = [t for t in transitions if t.get("trigger") == f"{slug}_invoked"]

        for state in states:
            op_state_model._straight_to_state(state)

            transitions_from_state = [t for t in transitions if t.get("from") == state]

            if transitions_from_state:
                # this command is permitted in the current state, should succeed,
                # should result in the correct transition.
                assert command.is_allowed()
                (result_code, _) = command()
                assert result_code == ResultCode.OK
                expected = transitions_from_state[0]["to"]
            else:
                # this command is not permitted, should not be allowed,
                # should fail, should have no side-effect.
                assert not command.is_allowed()
                with pytest.raises(CommandError):
                    command()
                expected = state
            assert op_state_model.op_state == op_state_mapping[expected]