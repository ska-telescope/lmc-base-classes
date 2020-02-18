#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKALogger project
#
#
#
#########################################################################################
"""Contain the tests for the SKALogger."""

# Standard imports
import sys
import os

# Imports
import re
import pytest
from tango import DevState, DeviceProxy

import tango

# Path
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# PROTECTED REGION ID(SKALogger.test_additional_imports) ENABLED START #
from skabase.control_model import AdminMode, ControlMode, HealthState, LoggingLevel
# PROTECTED REGION END #    //  SKALogger.test_additional_imports
# Device test case
# PROTECTED REGION ID(SKALogger.test_SKALogger_decorators) ENABLED START #
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION END #    //  SKALogger.test_SKALogger_decorators
class TestSKALogger(object):
    """Test case for packet generation."""
    properties = {'SkaLevel': '1',
                  'GroupDefinitions': '',
                  }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKALogger.numpy = MagicMock()
        # PROTECTED REGION ID(SKALogger.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKALogger.test_mocking

    def test_properties(self, tango_context):
        # test the properties
        # PROTECTED REGION ID(SKALogger.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKALogger.test_properties
        pass

    # PROTECTED REGION ID(SKALogger.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKALogger.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.UNKNOWN
        # PROTECTED REGION END #    //  SKALogger.test_State

    # PROTECTED REGION ID(SKALogger.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKALogger.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in UNKNOWN state."
        # PROTECTED REGION END #    //  SKALogger.test_Status

    # PROTECTED REGION ID(SKALogger.test_SetLoggingLevel_decorators) ENABLED START #
    @pytest.mark.parametrize("logging_level", [int(tango.LogLevel.LOG_ERROR)])
    @pytest.mark.parametrize("logging_target", ["logger/test/1"])
    # PROTECTED REGION END #    //  SKALogger.test_SetLoggingLevel_decorators
    def test_SetLoggingLevel(self, tango_context, setup_log_test_device,
                             logging_level, logging_target):
        """Test for SetLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_SetLoggingLevel) ENABLED START #
        # initial setting must not be same as what it will be set to
        dev_proxy = DeviceProxy(logging_target)
        dev_proxy.loggingLevel = int(tango.LogLevel.LOG_FATAL)
        assert dev_proxy.loggingLevel != logging_level

        levels = []
        levels.append(logging_level)
        targets = []
        targets.append(logging_target)
        device_details = []
        device_details.append(levels)
        device_details.append(targets)
        tango_context.device.SetLoggingLevel(device_details)
        assert dev_proxy.loggingLevel == logging_level
        # PROTECTED REGION END #    //  SKALogger.test_SetLoggingLevel

    # PROTECTED REGION ID(SKALogger.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKALogger.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'SKALogger, lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  SKALogger.test_GetVersionInfo

    # PROTECTED REGION ID(SKALogger.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_Reset_decorators
    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SKALogger.test_Reset) ENABLED START #
        assert tango_context.device.Reset() is None
        # PROTECTED REGION END #    //  SKALogger.test_Reset

    # PROTECTED REGION ID(SKALogger.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKALogger.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  SKALogger.test_buildState

    # PROTECTED REGION ID(SKALogger.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKALogger.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  SKALogger.test_versionId

    # PROTECTED REGION ID(SKALogger.test_loggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_loggingLevel_decorators
    def test_loggingLevel(self, tango_context):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_loggingLevel) ENABLED START #
        assert tango_context.device.loggingLevel == LoggingLevel.INFO
        # PROTECTED REGION END #    //  SKALogger.test_loggingLevel

    # PROTECTED REGION ID(SKALogger.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKALogger.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SKALogger.test_healthState

    # PROTECTED REGION ID(SKALogger.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKALogger.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  SKALogger.test_adminMode

    # PROTECTED REGION ID(SKALogger.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKALogger.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKALogger.test_controlMode

    # PROTECTED REGION ID(SKALogger.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKALogger.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode is False
        # PROTECTED REGION END #    //  SKALogger.test_simulationMode

    # PROTECTED REGION ID(SKALogger.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKALogger.test_testMode) ENABLED START #
        assert tango_context.device.testMode == ''
        # PROTECTED REGION END #    //  SKALogger.test_testMode
