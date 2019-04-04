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
from builtins import object
import sys
import os
import time

path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from tango import DevState, DeviceProxy
import pytest
import re


# PROTECTED REGION ID(SKALogger.test_additional_imports) ENABLED START #
import tango
# PROTECTED REGION END #    //  SKALogger.test_additional_imports

# Device test case
# PROTECTED REGION ID(SKALogger.test_SKALogger_decorators) ENABLED START #
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION END #    //  SKALogger.test_SKALogger_decorators
class TestSKALogger(object):
    """Test case for packet generation."""
    properties = {'SkaLevel': '1',
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

    # PROTECTED REGION ID(SKALogger.test_Log_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_Log_decorators
    def test_Log(self, tango_context):
        """Test for Log"""
        # PROTECTED REGION ID(SKALogger.test_Log) ENABLED START #
        log_details = ["123456789", "ERROR", "logger/test/1",
                       "Error message", "0", "0"]
        assert tango_context.device.Log(log_details) == "Error message"
        # PROTECTED REGION END #    //  SKALogger.test_Log

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

    # PROTECTED REGION ID(SKALogger.test_SetCentralLoggingLevel_decorators) ENABLED START #
    @pytest.mark.parametrize("logging_level", [int(tango.LogLevel.LOG_INFO)])
    @pytest.mark.parametrize("logging_target", ["logger/test/1"])
    # PROTECTED REGION END #    //  SKALogger.test_SetCentralLoggingLevel_decorators
    def test_SetCentralLoggingLevel(self, tango_context, setup_log_test_device,
                                    logging_level, logging_target):
        """Test for SetCentralLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_SetCentralLoggingLevel) ENABLED START #
        levels = []
        levels.append(logging_level)
        targets = []
        targets.append(logging_target)
        device_details = []
        device_details.append(levels)
        device_details.append(targets)
        print("device_details: ", device_details)
        tango_context.device.SetCentralLoggingLevel(device_details)
        dev_proxy = DeviceProxy(logging_target)
        print("dev_proxy: ", dev_proxy)
        assert dev_proxy.centralLoggingLevel == logging_level
        # PROTECTED REGION END #    //  SKALogger.test_SetCentralLoggingLevel

    # PROTECTED REGION ID(SKALogger.test_SetElementLoggingLevel_decorators) ENABLED START #
    @pytest.mark.parametrize("logging_level", [int(tango.LogLevel.LOG_ERROR)])
    @pytest.mark.parametrize("logging_target", ["logger/test/1"])
    # PROTECTED REGION END #    //  SKALogger.test_SetElementLoggingLevel_decorators
    def test_SetElementLoggingLevel(self, tango_context, setup_log_test_device,
                                    logging_level, logging_target):
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

    # PROTECTED REGION ID(SKALogger.test_SetStorageLoggingLevel_decorators) ENABLED START #
    @pytest.mark.parametrize("logging_level", [int(tango.LogLevel.LOG_WARN)])
    @pytest.mark.parametrize("logging_target", ["logger/test/1"])
    # PROTECTED REGION END #    //  SKALogger.test_SetStorageLoggingLevel_decorators
    def test_SetStorageLoggingLevel(self, tango_context, setup_log_test_device,
                                    logging_level, logging_target):
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

    # PROTECTED REGION ID(SKALogger.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKALogger.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'SKALogger, lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) != None
        # PROTECTED REGION END #    //  SKALogger.test_GetVersionInfo

    # PROTECTED REGION ID(SKALogger.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_Reset_decorators
    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SKALogger.test_Reset) ENABLED START #
        assert tango_context.device.Reset() == None
        # PROTECTED REGION END #    //  SKALogger.test_Reset

    # PROTECTED REGION ID(SKALogger.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKALogger.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) != None
        # PROTECTED REGION END #    //  SKALogger.test_buildState

    # PROTECTED REGION ID(SKALogger.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKALogger.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) != None
        # PROTECTED REGION END #    //  SKALogger.test_versionId

    # PROTECTED REGION ID(SKALogger.test_centralLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_centralLoggingLevel_decorators
    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_centralLoggingLevel) ENABLED START #
        assert tango_context.device.centralLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SKALogger.test_centralLoggingLevel

    # PROTECTED REGION ID(SKALogger.test_elementLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_elementLoggingLevel_decorators
    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_elementLoggingLevel) ENABLED START #
        assert tango_context.device.elementLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SKALogger.test_elementLoggingLevel

    # PROTECTED REGION ID(SKALogger.test_storageLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_storageLoggingLevel_decorators
    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_storageLoggingLevel) ENABLED START #
        assert tango_context.device.storageLoggingLevel == int(tango.LogLevel.LOG_DEBUG)
        # PROTECTED REGION END #    //  SKALogger.test_storageLoggingLevel

    # PROTECTED REGION ID(SKALogger.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKALogger.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  SKALogger.test_healthState

    # PROTECTED REGION ID(SKALogger.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKALogger.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  SKALogger.test_adminMode

    # PROTECTED REGION ID(SKALogger.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKALogger.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == 0
        # PROTECTED REGION END #    //  SKALogger.test_controlMode

    # PROTECTED REGION ID(SKALogger.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKALogger.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == False
        # PROTECTED REGION END #    //  SKALogger.test_simulationMode

    # PROTECTED REGION ID(SKALogger.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKALogger.test_testMode) ENABLED START #
        assert tango_context.device.testMode == ''
        # PROTECTED REGION END #    //  SKALogger.test_testMode
