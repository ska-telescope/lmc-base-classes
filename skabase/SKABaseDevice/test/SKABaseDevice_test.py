#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#
#########################################################################################
"""Contain the tests for the SKABASE."""

# Standard imports
import sys
import os
import re
import pytest

# Imports
from skabase.SKABaseDevice import SKABaseDevice

# Path
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# PROTECTED REGION ID(SKABaseDevice.test_additional_imports) ENABLED START #
import logging
from unittest import mock
from tango import DevFailed, DevState
from skabase.SKABaseDevice import TangoLoggingLevel
from skabase.SKABaseDevice.SKABaseDevice import (
    LoggingUtils,
    LoggingTargetError,
)
# PROTECTED REGION END #    //  SKABaseDevice.test_additional_imports
# Device test case
# PROTECTED REGION ID(SKABaseDevice.test_SKABaseDevice_decorators) ENABLED START #


class TestLoggingUtils:
    @pytest.fixture(params=[
            ([""], []),
            ([" \n\t "], []),
            (["console"], ["console::cout"]),
            (["console::"], ["console::cout"]),
            (["console::cout"], ["console::cout"]),
            (["console::anything"], ["console::anything"]),
            (["file"], ["file::my_dev_name.log"]),
            (["file::"], ["file::my_dev_name.log"]),
            (["file::/tmp/dummy"], ["file::/tmp/dummy"]),
            (["syslog::some/address"], ["syslog::some/address"]),
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


    @mock.patch('logging.handlers.SysLogHandler')
    @mock.patch('logging.handlers.RotatingFileHandler')
    @mock.patch('logging.StreamHandler')
    @mock.patch('ska_logging.get_default_formatter')
    def test_create_logging_handler(self,
                                    mock_get_formatter,
                                    mock_stream_handler,
                                    mock_file_handler,
                                    mock_syslog_handler):
        # Expect formatter be created using `get_default_formatter(tags=True)`
        # Use some mocks to check this.
        mock_formatter = mock.MagicMock()

        def get_formatter_if_tags_enabled(*args, **kwargs):
            if kwargs.get("tags", False):
                return mock_formatter

        mock_get_formatter.side_effect = get_formatter_if_tags_enabled

        handler = LoggingUtils.create_logging_handler("console::cout")
        assert handler == mock_stream_handler()
        handler.setFormatter.assert_called_once_with(mock_formatter)

        handler = LoggingUtils.create_logging_handler("file::/tmp/dummy")
        assert handler == mock_file_handler()
        handler.setFormatter.assert_called_once_with(mock_formatter)

        handler = LoggingUtils.create_logging_handler("syslog::some/address")
        assert handler == mock_syslog_handler()
        handler.setFormatter.assert_called_once_with(mock_formatter)

        with pytest.raises(LoggingTargetError):
            LoggingUtils.create_logging_handler("invalid::target")

        with pytest.raises(LoggingTargetError):
            LoggingUtils.create_logging_handler("invalid")

    def test_update_logging_handlers(self):
        logger = logging.getLogger('testing')

        def null_creator(target):
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
            mocked_creator.assert_called_once_with("console::cout")

            # test same handler is retained for same request
            old_handler = logger.handlers[0]
            new_targets = ["console::cout"]
            mocked_creator.reset_mock()
            LoggingUtils.update_logging_handlers(new_targets, logger)
            assert len(logger.handlers) == 1
            assert logger.handlers[0] is old_handler
            mocked_creator.assert_not_called()

            # test other valid target types
            new_targets = ["console::cout", "file::/tmp/dummy", "syslog::some/address"]
            mocked_creator.reset_mock()
            LoggingUtils.update_logging_handlers(new_targets, logger)
            assert len(logger.handlers) == 3
            assert mocked_creator.call_count == 2
            mocked_creator.assert_has_calls(
                [mock.call("file::/tmp/dummy"),
                 mock.call("syslog::some/address")],
                any_order=True,
            )

            # test clearing of 1 handler
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


@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION END #    //  SKABaseDevice.test_SKABaseDevice_decorators
class TestSKABaseDevice(object):
    """Test case for packet generation."""

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
        assert tango_context.device.State() == DevState.UNKNOWN
        # PROTECTED REGION END #    //  SKABaseDevice.test_State

    # PROTECTED REGION ID(SKABaseDevice.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKABaseDevice.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in UNKNOWN state."
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
        assert tango_context.device.Reset() is None
        # PROTECTED REGION END #    //  SKABaseDevice.test_Reset

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
        assert tango_context.device.loggingLevel == TangoLoggingLevel.INFO

        for level in TangoLoggingLevel:
            tango_context.device.loggingLevel = level
            assert tango_context.device.loggingLevel == level
            assert tango_context.device.get_logging_level() == level

        with pytest.raises(DevFailed):
            tango_context.device.loggingLevel = TangoLoggingLevel.FATAL + 100
        # PROTECTED REGION END #    //  SKABaseDevice.test_loggingLevel

    # PROTECTED REGION ID(SKABaseDevice.test_loggingTargets_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_loggingTargets_decorators
    def test_loggingTargets(self, tango_context):
        """Test for loggingTargets"""
        # PROTECTED REGION ID(SKABaseDevice.test_loggingTargets) ENABLED START #
        assert tango_context.device.loggingTargets == tuple()

        with mock.patch("SKABaseDevice.LoggingUtils.create_logging_handler") as mocked_creator:

            def null_creator(target):
                handler = logging.NullHandler()
                handler.name = target
                return handler

            mocked_creator.side_effect = null_creator

            # test adding console target
            tango_context.device.loggingTargets = ["console::cout"]
            assert tango_context.device.loggingTargets == ("console::cout", )
            mocked_creator.assert_called_once_with("console::cout")

            # test adding file and syslog targets (already have console)
            mocked_creator.reset_mock()
            tango_context.device.loggingTargets = [
                "console::cout", "file::/tmp/dummy", "syslog::some/address"]
            assert tango_context.device.loggingTargets == (
                "console::cout", "file::/tmp/dummy", "syslog::some/address")
            assert mocked_creator.call_count == 2
            mocked_creator.assert_has_calls(
                [mock.call("file::/tmp/dummy"),
                 mock.call("syslog::some/address")],
                any_order=True)

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
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  SKABaseDevice.test_healthState

    # PROTECTED REGION ID(SKABaseDevice.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  SKABaseDevice.test_adminMode

    # PROTECTED REGION ID(SKABaseDevice.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == 0
        # PROTECTED REGION END #    //  SKABaseDevice.test_controlMode

    # PROTECTED REGION ID(SKABaseDevice.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode is False
        # PROTECTED REGION END #    //  SKABaseDevice.test_simulationMode

    # PROTECTED REGION ID(SKABaseDevice.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_testMode) ENABLED START #
        assert tango_context.device.testMode == ''
        # PROTECTED REGION END #    //  SKABaseDevice.test_testMode

    # TODO: Fix this test case when "Error in get_name() of tango.DeviceImpl while using pytest" is resolved.
    # def test_get_device_commands(self, tango_context):
        # Test the get_device_commands method
        # commands = SKABaseDevice.get_device_commands(SKABaseDevice)
        #assert commands == [{'parameters': [], 'name': 'GetVersionInfo', 'component_type': 'nodb', 'component_id': 'skabasedevice'}, {'parameters': [], 'name': 'Init', 'component_type': 'nodb', 'component_id': 'skabasedevice'}, {'parameters': [], 'name': 'Reset', 'component_type': 'nodb', 'component_id': 'skabasedevice'}, {'parameters': [], 'name': 'State', 'component_type': 'nodb', 'component_id': 'skabasedevice'}, {'parameters': [], 'name': 'Status', 'component_type': 'nodb', 'component_id': 'skabasedevice'}]

    # TODO: Fix this test case when "Error in get_name() of tango.DeviceImpl while using pytest" is resolved.
    # def test_get_device_attributes(self, tango_context):
    #     # Test the get_device_attributes method
    #     attributes = SKABaseDevice.get_device_attributes(SKABaseDevice)
    #     assert attributes == 1

    def test__parse_argin(self, tango_context):
        result = SKABaseDevice._parse_argin(SKABaseDevice, '{"class": "SKABaseDevice"}')
        assert result == {'class': 'SKABaseDevice'}

    def test__parse_argin_with_required(self, tango_context):
        SKABaseDevice._parse_argin(
            SKABaseDevice, '{"class":"SKABaseDevice"}', required=['class'])
        with pytest.raises(Exception):
            SKABaseDevice._parse_argin(
                SKABaseDevice, '{"class":"SKABaseDevice"}', required=['missing'])

    # TODO: Fix this test case when "__DeviceImpl__debug_stream() missing 'msg' argument" is resolved.
    # def test_dev_logging(self, tango_context):
    #     SKABaseDevice._central_logging_level = int(tango.LogLevel.LOG_DEBUG)
    #     SKABaseDevice._element_logging_level = int(tango.LogLevel.LOG_DEBUG)
    #     SKABaseDevice._storage_logging_level = int(tango.LogLevel.LOG_DEBUG)
    #     result = SKABaseDevice.dev_logging(SKABaseDevice, "test message", int(tango.LogLevel.LOG_DEBUG))
    #     result = []
    #     SKABaseDevice.error_stream(SKABaseDevice, "Syslog cannot be initialized")
    #     assert result == None
