#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKALogger project
#
#
#
#########################################################################################
"""Contain the tests for the SKALogger."""

# Path
import sys
import os
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from mock import MagicMock
from PyTango import DevState, DeviceProxy
import pytest
import re
import tango

# PROTECTED REGION ID(SKALogger.test_additional_imports) ENABLED START #
# PROTECTED REGION END #    //  SKALogger.test_additional_imports

# Device test case
@pytest.mark.usefixtures("tango_context", "initialize_device")
class TestSKALogger(object):
    """Test case for packet generation."""
    properties = {'SkaLevel': '1',
                  'MetricList': 'healthState',
                  'GroupDefinitions': '',
                  'CentralLoggingTarget': '',
                  'ElementLoggingTarget': '',
                  'StorageLoggingTarget': 'localhost',
                  'CentralLoggingLevelDefault': int(tango.LogLevel.LOG_ERROR),
                  'ElementLoggingLevelDefault': int(tango.LogLevel.LOG_WARN),
                  'StorageLoggingLevelDefault': int(tango.LogLevel.LOG_INFO),
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

    def test_Log(self, tango_context):
        """Test for Log"""
        # PROTECTED REGION ID(SKALogger.test_Log) ENABLED START #
        log_details = ["123456789", "ERROR", "logger/test/1",
                       "Error message", "0", "0"]
        assert tango_context.device.Log(log_details) == "Error message"
        # PROTECTED REGION END #    //  SKALogger.test_Log

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKALogger.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.UNKNOWN
        # PROTECTED REGION END #    //  SKALogger.test_State

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKALogger.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in UNKNOWN state."
        # PROTECTED REGION END #    //  SKALogger.test_Status

    @pytest.mark.parametrize("logging_level", [int(tango.LogLevel.LOG_INFO)])
    @pytest.mark.parametrize("logging_target", ["logger/test/1"])
    def test_SetCentralLoggingLevel(self, tango_context, logging_level, logging_target):
        """Test for SetCentralLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_SetCentralLoggingLevel) ENABLED START #
        levels = []
        levels.append(logging_level)
        targets = []
        targets.append(logging_target)
        device_details = []
        device_details.append(levels)
        device_details.append(targets)
        tango_context.device.SetCentralLoggingLevel(device_details)
        dev_proxy = DeviceProxy(logging_target)
        assert dev_proxy.centralLoggingLevel == logging_level
        # PROTECTED REGION END #    //  SKALogger.test_SetCentralLoggingLevel

    @pytest.mark.parametrize("logging_level", [int(tango.LogLevel.LOG_ERROR)])
    @pytest.mark.parametrize("logging_target", ["logger/test/1"])
    def test_SetElementLoggingLevel(self, tango_context, logging_level, logging_target):
        """Test for SetElementLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_SetElementLoggingLevel) ENABLED START #
        levels = []
        levels.append(logging_level)
        targets = []
        targets.append(logging_target)
        device_details = []
        device_details.append(levels)
        device_details.append(targets)
        tango_context.device.SetElementLoggingLevel(device_details)
        dev_proxy = DeviceProxy(logging_target)
        assert dev_proxy.elementLoggingLevel == logging_level
        # PROTECTED REGION END #    //  SKALogger.test_SetElementLoggingLevel

    @pytest.mark.parametrize("logging_level", [int(tango.LogLevel.LOG_WARN)])
    @pytest.mark.parametrize("logging_target", ["logger/test/1"])
    def test_SetStorageLoggingLevel(self, tango_context, logging_level, logging_target):
        """Test for SetStorageLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_SetStorageLoggingLevel) ENABLED START #
        levels = []
        levels.append(logging_level)
        targets = []
        targets.append(logging_target)
        device_details = []
        device_details.append(levels)
        device_details.append(targets)
        tango_context.device.SetStorageLoggingLevel(device_details)
        dev_proxy = DeviceProxy(logging_target)
        assert dev_proxy.storageLoggingLevel == logging_level
        # PROTECTED REGION END #    //  SKALogger.test_SetStorageLoggingLevel

    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKALogger.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'SKALogger, tangods-skalogger, [0-9].[0-9].[0-9], A generic logger device for SKA')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) != None
        # PROTECTED REGION END #    //  SKALogger.test_GetVersionInfo

    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SKALogger.test_Reset) ENABLED START #
        assert tango_context.device.Reset() == None
        # PROTECTED REGION END #    //  SKALogger.test_Reset

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKALogger.test_buildState) ENABLED START #
        assert tango_context.device.buildState == 'tangods-skalogger, 1.0.0, A generic logger device for SKA.'
        # PROTECTED REGION END #    //  SKALogger.test_buildState

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKALogger.test_versionId) ENABLED START #
        assert tango_context.device.versionId == '1.0.0'
        # PROTECTED REGION END #    //  SKALogger.test_versionId

    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_centralLoggingLevel) ENABLED START #
        assert tango_context.device.centralLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SKALogger.test_centralLoggingLevel

    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_elementLoggingLevel) ENABLED START #
        assert tango_context.device.elementLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SKALogger.test_elementLoggingLevel

    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_storageLoggingLevel) ENABLED START #
        assert tango_context.device.storageLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SKALogger.test_storageLoggingLevel

    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKALogger.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  SKALogger.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKALogger.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  SKALogger.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKALogger.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == 0
        # PROTECTED REGION END #    //  SKALogger.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKALogger.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == False
        # PROTECTED REGION END #    //  SKALogger.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKALogger.test_testMode) ENABLED START #
        assert tango_context.device.testMode == ''
        # PROTECTED REGION END #    //  SKALogger.test_testMode