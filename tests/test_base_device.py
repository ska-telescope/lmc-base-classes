#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#
#########################################################################################
"""
This module contains the tests for the SKABaseDevice.
"""

# PROTECTED REGION ID(SKABaseDevice.test_additional_imports) ENABLED START #
import logging
import re
import pytest
import socket
import tango

from unittest import mock
from tango import DevFailed, DevState
from ska.base.control_model import (
    AdminMode, ControlMode, HealthState, LoggingLevel, SimulationMode, TestMode
)
from ska.base.base_device import (
    _Log4TangoLoggingLevel,
    _PYTHON_TO_TANGO_LOGGING_LEVEL,
    LoggingUtils,
    LoggingTargetError,
    SKABaseDeviceStateModel,
    TangoLoggingServiceHandler,
)
from ska.base.faults import StateModelError

from .conftest import load_data, StateMachineTester

# PROTECTED REGION END #    //  SKABaseDevice.test_additional_imports
# Device test case
# PROTECTED REGION ID(SKABaseDevice.test_SKABaseDevice_decorators) ENABLED START #


class TestTangoLoggingServiceHandler:

    @pytest.fixture()
    def tls_handler(self):
        self.tango_logger = mock.MagicMock(spec=tango.Logger)
        # setup methods used for handler __repr__
        self.tango_logger.get_name.return_value = "unit/test/dev"
        self.tango_logger.get_level.return_value = _Log4TangoLoggingLevel.DEBUG
        return TangoLoggingServiceHandler(self.tango_logger)

    @pytest.fixture(params=[
            logging.DEBUG,
            logging.INFO,
            logging.WARN,
            logging.ERROR,
            logging.CRITICAL,
        ])
    def python_log_level(self, request):
        return request.param

    def test_emit_message_at_correct_level(self, tls_handler, python_log_level):
        # arrange
        record = logging.LogRecord('test', python_log_level, '', 1, 'message', (), None)
        # act
        tls_handler.emit(record)
        # assert
        expected_tango_level = _PYTHON_TO_TANGO_LOGGING_LEVEL[python_log_level]
        expected_calls = [mock.call(expected_tango_level, mock.ANY)]
        assert self.tango_logger.log.call_args_list == expected_calls

    def test_emit_message_is_formatted(self, tls_handler):
        # arrange
        record = logging.LogRecord('test', logging.INFO, '', 1, 'message %s', ('param',), None)

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
        # arrange
        record = logging.LogRecord('test', logging.INFO, '', 1, 'message', (), None)

        def cause_exception(*args, **kwargs):
            raise RuntimeError("Testing")

        self.tango_logger.log.side_effect = cause_exception
        tls_handler.handleError = mock.MagicMock()
        # act
        tls_handler.emit(record)
        # assert
        assert tls_handler.handleError.call_args_list == [mock.call(record)]

    def test_repr_normal(self, tls_handler):
        expected = '<TangoLoggingServiceHandler unit/test/dev (Python NOTSET, Tango DEBUG)>'
        assert repr(tls_handler) == expected

    def test_repr_tango_logger_none(self, tls_handler):
        tls_handler.tango_logger = None
        expected = '<TangoLoggingServiceHandler !No Tango logger! (Python NOTSET, Tango UNKNOWN)>'
        assert repr(tls_handler) == expected


class TestLoggingUtils:
    @pytest.fixture(params=[
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
            (["syslog::protocol://somehost:1234"], ["syslog::protocol://somehost:1234"]),
            (["tango"], ["tango::logger"]),
            (["tango::"], ["tango::logger"]),
            (["tango::logger"], ["tango::logger"]),
            (["tango::anything"], ["tango::anything"]),
            (["console", "file"], ["console::cout", "file::my_dev_name.log"]),
        ])
    def good_logging_targets(self, request):
        targets_in, expected = request.param
        dev_name = "my/dev/name"
        return targets_in, dev_name, expected

    @pytest.fixture(params=[
            ["invalid"],
            ["invalid", "console"],
            ["invalid::type"],
            ["syslog"],
        ])
    def bad_logging_targets(self, request):
        targets_in = request.param
        dev_name = "my/dev/name"
        return targets_in, dev_name

    def test_sanitise_logging_targets_success(self, good_logging_targets):
        targets_in, dev_name, expected = good_logging_targets
        actual = LoggingUtils.sanitise_logging_targets(targets_in, dev_name)
        assert actual == expected

    def test_sanitise_logging_targets_fail(self, bad_logging_targets):
        targets_in, dev_name = bad_logging_targets
        with pytest.raises(LoggingTargetError):
            LoggingUtils.sanitise_logging_targets(targets_in, dev_name)

    @pytest.fixture(params=[
            ("deprecated/path", ["deprecated/path", None]),
            ("file:///abs/path", ["/abs/path", None]),
            ("file://relative/path", ["relative/path", None]),
            ("file://some/spaced%20path", ["some/spaced path", None]),
            ("udp://somehost.domain:1234", [("somehost.domain", 1234), socket.SOCK_DGRAM]),
            ("udp://127.0.0.1:1234", [("127.0.0.1", 1234), socket.SOCK_DGRAM]),
            ("tcp://somehost:1234", [("somehost", 1234), socket.SOCK_STREAM]),
            ("tcp://127.0.0.1:1234", [("127.0.0.1", 1234), socket.SOCK_STREAM]),
    ])
    def good_syslog_url(self, request):
        url, (expected_address, expected_socktype) = request.param
        return url, (expected_address, expected_socktype)

    @pytest.fixture(params=[
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
        "invalid://somehost:1234"
    ])
    def bad_syslog_url(self, request):
        return request.param

    def test_get_syslog_address_and_socktype_success(self, good_syslog_url):
        url, (expected_address, expected_socktype) = good_syslog_url
        actual_address, actual_socktype = LoggingUtils.get_syslog_address_and_socktype(url)
        assert actual_address == expected_address
        assert actual_socktype == expected_socktype

    def test_get_syslog_address_and_socktype_fail(self, bad_syslog_url):
        with pytest.raises(LoggingTargetError):
            LoggingUtils.get_syslog_address_and_socktype(bad_syslog_url)

    @mock.patch('ska.base.base_device.TangoLoggingServiceHandler')
    @mock.patch('logging.handlers.SysLogHandler')
    @mock.patch('logging.handlers.RotatingFileHandler')
    @mock.patch('logging.StreamHandler')
    @mock.patch('ska.logging.get_default_formatter')
    def test_create_logging_handler(self,
                                    mock_get_formatter,
                                    mock_stream_handler,
                                    mock_file_handler,
                                    mock_syslog_handler,
                                    mock_tango_handler):
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
            socktype=socket.SOCK_DGRAM
        )
        assert handler == mock_syslog_handler()
        handler.setFormatter.assert_called_once_with(mock_formatter)

        mock_syslog_handler.reset_mock()
        handler = LoggingUtils.create_logging_handler("syslog::file:///tmp/path")
        mock_syslog_handler.assert_called_once_with(
            address="/tmp/path",
            facility=mock_syslog_handler.LOG_SYSLOG,
            socktype=None
        )
        assert handler == mock_syslog_handler()
        handler.setFormatter.assert_called_once_with(mock_formatter)

        handler = LoggingUtils.create_logging_handler("tango::logger", mock_tango_logger)
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
        logger = logging.getLogger('testing')
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
                "console::cout", "file::/tmp/dummy", "syslog::some/address", "tango::logger"]
            mocked_creator.reset_mock()
            LoggingUtils.update_logging_handlers(new_targets, logger)
            assert len(logger.handlers) == 4
            assert mocked_creator.call_count == 3
            mocked_creator.assert_has_calls(
                [mock.call("file::/tmp/dummy", logger.tango_logger),
                 mock.call("syslog::some/address", logger.tango_logger),
                 mock.call("tango::logger", logger.tango_logger)],
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


@pytest.fixture
def device_state_model():
    """
    Yields a new SKABaseDeviceStateModel for testing
    """
    yield SKABaseDeviceStateModel(logging.getLogger())


@pytest.mark.state_machine_tester(load_data("base_device_state_machine"))
class TestSKABaseDeviceStateModel(StateMachineTester):
    """
    This class contains the test suite for the ska.base.SKABaseDevice class.
    """
    @pytest.fixture
    def machine(self, device_state_model):
        """
        Fixture that returns the state machine under test in this class
        """
        yield device_state_model

    state_checks = {
        "UNINITIALISED":
            (None, None),
        "FAULT_ENABLED":
            ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.FAULT),
        "FAULT_DISABLED":
            ([AdminMode.NOT_FITTED, AdminMode.OFFLINE], DevState.FAULT),
        "INIT_ENABLED":
            ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.INIT),
        "INIT_DISABLED":
            ([AdminMode.NOT_FITTED, AdminMode.OFFLINE], DevState.INIT),
        "DISABLED":
            ([AdminMode.NOT_FITTED, AdminMode.OFFLINE], DevState.DISABLE),
        "OFF":
            ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.OFF),
        "ON":
            ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON),
    }

    def assert_state(self, machine, state):
        """
        Assert the current state of this state machine, based on the
        values of the adminMode, opState and obsState attributes of this
        model.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param state: the state that we are asserting to be the current
            state of the state machine under test
        :type state: str
        """

        (admin_modes, op_state) = self.state_checks[state]
        if admin_modes is None:
            assert machine.admin_mode is None
        else:
            assert machine.admin_mode in admin_modes
        if op_state is None:
            assert machine.op_state is None
        else:
            assert machine.op_state == op_state

    def perform_action(self, machine, action):
        """
        Perform a given action on the state machine under test.

        :param action: action to be performed on the state machine
        :type action: str
        """
        machine.perform_action(action)

    def check_action_disallowed(self, machine, action):
        """
        Assert that performing a given action on the state maching under
        test fails in its current state.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        with pytest.raises(StateModelError):
            self.perform_action(machine, action)

    def to_state(self, machine, target_state):
        """
        Transition the state machine to a target state.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param target_state: the state that we want to get the state
            machine under test into
        :type target_state: str
        """
        machine._straight_to_state(target_state)


# PROTECTED REGION END #    //  SKABaseDevice.test_SKABaseDevice_decorators
class TestSKABaseDevice(object):
    """
    Test cases for SKABaseDevice.
    """

    properties = {
        'SkaLevel': '4',
        'GroupDefinitions': '',
        'LoggingTargetsDefault': ''
        }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKABaseDevice.numpy = MagicMock()
        # PROTECTED REGION ID(SKABaseDevice.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKABaseDevice.test_mocking

    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(SKABaseDevice.test_properties) ENABLED START #
        """
        Test device properties.

        :param tango_context: Object
            Tango device object

        :return: None
        """
        # PROTECTED REGION END #    //  SKABaseDevice.test_properties
        # pass

    # PROTECTED REGION ID(SKABaseDevice.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKABaseDevice.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.OFF
        # PROTECTED REGION END #    //  SKABaseDevice.test_State

    # PROTECTED REGION ID(SKABaseDevice.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKABaseDevice.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKABaseDevice.test_Status

    # PROTECTED REGION ID(SKABaseDevice.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKABaseDevice.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'SKABaseDevice, lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  SKABaseDevice.test_GetVersionInfo

    # PROTECTED REGION ID(SKABaseDevice.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_Reset_decorators
    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SKABaseDevice.test_Reset) ENABLED START #
        # This is a pretty weak test, but Reset() is only allowed from
        # device state FAULT, and we have no way of putting into FAULT
        # state through its interface.
        with pytest.raises(DevFailed):
            tango_context.device.Reset()
        # PROTECTED REGION END #    //  SKABaseDevice.test_Reset

    def test_On(self, tango_context, tango_change_event_helper):
        """
        Test for On command
        """

        state_callback = tango_change_event_helper.subscribe("state")
        status_callback = tango_change_event_helper.subscribe("status")
        state_callback.assert_call(DevState.OFF)
        status_callback.assert_call("The device is in OFF state.")

        # Check that we can turn a freshly initialised device on
        tango_context.device.On()
        state_callback.assert_call(DevState.ON)
        status_callback.assert_call("The device is in ON state.")

        # Check that we can't turn it on when it is already on
        with pytest.raises(DevFailed):
            tango_context.device.On()
        state_callback.assert_not_called()
        status_callback.assert_not_called()

        # Now turn it off and check that we can turn it on again.
        tango_context.device.Off()
        state_callback.assert_call(DevState.OFF)
        status_callback.assert_call("The device is in OFF state.")

        tango_context.device.On()
        state_callback.assert_call(DevState.ON)
        status_callback.assert_call("The device is in ON state.")

    def test_Off(self, tango_context, tango_change_event_helper):
        """
        Test for On command
        """
        state_callback = tango_change_event_helper.subscribe("state")
        status_callback = tango_change_event_helper.subscribe("status")
        state_callback.assert_call(DevState.OFF)
        status_callback.assert_call("The device is in OFF state.")

        # Check that we can't turn off a device that isn't on
        with pytest.raises(DevFailed):
            tango_context.device.Off()
        state_callback.assert_not_called()
        status_callback.assert_not_called()

        # Now turn it on and check that we can turn it off
        tango_context.device.On()
        state_callback.assert_call(DevState.ON)
        status_callback.assert_call("The device is in ON state.")

        tango_context.device.Off()
        state_callback.assert_call(DevState.OFF)
        status_callback.assert_call("The device is in OFF state.")

    # PROTECTED REGION ID(SKABaseDevice.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKABaseDevice.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  SKABaseDevice.test_buildState

    # PROTECTED REGION ID(SKABaseDevice.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKABaseDevice.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  SKABaseDevice.test_versionId

    # PROTECTED REGION ID(SKABaseDevice.test_loggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_loggingLevel_decorators
    def test_loggingLevel(self, tango_context):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(SKABaseDevice.test_loggingLevel) ENABLED START #
        assert tango_context.device.loggingLevel == LoggingLevel.INFO

        for level in LoggingLevel:
            tango_context.device.loggingLevel = level
            assert tango_context.device.loggingLevel == level
            assert tango_context.device.get_logging_level() == level

        with pytest.raises(DevFailed):
            tango_context.device.loggingLevel = LoggingLevel.FATAL + 100
        # PROTECTED REGION END #    //  SKABaseDevice.test_loggingLevel

    # PROTECTED REGION ID(SKABaseDevice.test_loggingTargets_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_loggingTargets_decorators
    def test_loggingTargets(self, tango_context):
        """Test for loggingTargets"""
        # PROTECTED REGION ID(SKABaseDevice.test_loggingTargets) ENABLED START #
        # tango logging target must be enabled by default
        assert tango_context.device.loggingTargets == ("tango::logger", )

        with mock.patch(
            "ska.base.base_device.LoggingUtils.create_logging_handler"
        ) as mocked_creator:

            def null_creator(target, tango_logger):
                handler = logging.NullHandler()
                handler.name = target
                assert isinstance(tango_logger, tango.Logger)
                return handler

            mocked_creator.side_effect = null_creator

            # test console target
            tango_context.device.loggingTargets = ["console::cout"]
            assert tango_context.device.loggingTargets == ("console::cout", )
            mocked_creator.assert_called_once_with("console::cout", mock.ANY)

            # test adding file and syslog targets (already have console)
            mocked_creator.reset_mock()
            tango_context.device.loggingTargets = [
                "console::cout", "file::/tmp/dummy", "syslog::udp://localhost:514"]
            assert tango_context.device.loggingTargets == (
                "console::cout", "file::/tmp/dummy", "syslog::udp://localhost:514")
            assert mocked_creator.call_count == 2
            mocked_creator.assert_has_calls(
                [mock.call("file::/tmp/dummy", mock.ANY),
                 mock.call("syslog::udp://localhost:514", mock.ANY)],
                any_order=True)

            # test adding tango logging again, now that mock is active
            # (it wasn't active when device was initialised)
            mocked_creator.reset_mock()
            tango_context.device.loggingTargets = ["tango::logger"]
            assert tango_context.device.loggingTargets == ("tango::logger",)
            mocked_creator.assert_called_once_with("tango::logger", mock.ANY)

            # test clearing all targets (note: PyTango returns None for empty spectrum attribute)
            tango_context.device.loggingTargets = []
            assert tango_context.device.loggingTargets is None

            mocked_creator.reset_mock()
            with pytest.raises(DevFailed):
                tango_context.device.loggingTargets = ["invalid::type"]
            mocked_creator.assert_not_called()
        # PROTECTED REGION END #    //  SKABaseDevice.test_loggingTargets

    # PROTECTED REGION ID(SKABaseDevice.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKABaseDevice.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SKABaseDevice.test_healthState

    # PROTECTED REGION ID(SKABaseDevice.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_adminMode_decorators
    def test_adminMode(self, tango_context, tango_change_event_helper):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.MAINTENANCE

        admin_mode_callback = tango_change_event_helper.subscribe("adminMode")
        admin_mode_callback.assert_call(AdminMode.MAINTENANCE)

        tango_context.device.adminMode = AdminMode.ONLINE
        assert tango_context.device.adminMode == AdminMode.ONLINE
        admin_mode_callback.assert_call(AdminMode.ONLINE)

        # PROTECTED REGION END #    //  SKABaseDevice.test_adminMode

    # PROTECTED REGION ID(SKABaseDevice.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKABaseDevice.test_controlMode

    # PROTECTED REGION ID(SKABaseDevice.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKABaseDevice.test_simulationMode

    # PROTECTED REGION ID(SKABaseDevice.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_testMode) ENABLED START #
        assert tango_context.device.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKABaseDevice.test_testMode
