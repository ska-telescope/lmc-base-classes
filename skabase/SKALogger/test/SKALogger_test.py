#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKALogger project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
#########################################################################################
"""Contain the tests for the SKALogger."""

# Path
import sys
import os
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
import pytest
from mock import MagicMock

from PyTango import DevState

# PROTECTED REGION ID(SKALogger.test_additional_imports) ENABLED START #
# PROTECTED REGION END #    //  SKALogger.test_additional_imports


# Device test case
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION ID(SKALogger.test_SKALogger_decorators) ENABLED START #
# PROTECTED REGION END #    //  SKALogger.test_SKALogger_decorators
class TestSKALogger(object):
    """Test case for packet generation."""

    properties = {
        'SkaLevel': '4',
        'MetricList': 'healthState',
        'GroupDefinitions': '',
        'CentralLoggingTarget': '',
        'ElementLoggingTarget': '',
        'StorageLoggingTarget': 'localhost',
        'CentralLoggingLevelDefault': '2',
        'ElementLoggingLevelDefault': '3',
        'StorageLoggingLevelDefault': '4',
        }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKALogger.numpy = MagicMock()
        # PROTECTED REGION ID(SKALogger.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKALogger.test_mocking

    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(SKALogger.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKALogger.test_properties
        pass

    # PROTECTED REGION ID(SKALogger.test_Log_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_Log_decorators
    def test_Log(self, tango_context):
        """Test for Log"""
        # PROTECTED REGION ID(SKALogger.test_Log) ENABLED START #
        assert tango_context.device.Log([""]) == None
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
    # PROTECTED REGION END #    //  SKALogger.test_SetCentralLoggingLevel_decorators
    def test_SetCentralLoggingLevel(self, tango_context):
        """Test for SetCentralLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_SetCentralLoggingLevel) ENABLED START #
        assert tango_context.device.SetCentralLoggingLevel("") == None
        # PROTECTED REGION END #    //  SKALogger.test_SetCentralLoggingLevel

    # PROTECTED REGION ID(SKALogger.test_SetElementLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_SetElementLoggingLevel_decorators
    def test_SetElementLoggingLevel(self, tango_context):
        """Test for SetElementLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_SetElementLoggingLevel) ENABLED START #
        assert tango_context.device.SetElementLoggingLevel("") == None
        # PROTECTED REGION END #    //  SKALogger.test_SetElementLoggingLevel

    # PROTECTED REGION ID(SKALogger.test_SetStorageLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_SetStorageLoggingLevel_decorators
    def test_SetStorageLoggingLevel(self, tango_context):
        """Test for SetStorageLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_SetStorageLoggingLevel) ENABLED START #
        assert tango_context.device.SetStorageLoggingLevel("") == None
        # PROTECTED REGION END #    //  SKALogger.test_SetStorageLoggingLevel

    # PROTECTED REGION ID(SKALogger.test_GetMetrics_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_GetMetrics_decorators
    def test_GetMetrics(self, tango_context):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(SKALogger.test_GetMetrics) ENABLED START #
        assert tango_context.device.GetMetrics() == ""
        # PROTECTED REGION END #    //  SKALogger.test_GetMetrics

    # PROTECTED REGION ID(SKALogger.test_ToJson_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_ToJson_decorators
    def test_ToJson(self, tango_context):
        """Test for ToJson"""
        # PROTECTED REGION ID(SKALogger.test_ToJson) ENABLED START #
        assert tango_context.device.ToJson("") == ""
        # PROTECTED REGION END #    //  SKALogger.test_ToJson

    # PROTECTED REGION ID(SKALogger.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKALogger.test_GetVersionInfo) ENABLED START #
        assert tango_context.device.GetVersionInfo() == [""]
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
        assert tango_context.device.buildState == ''
        # PROTECTED REGION END #    //  SKALogger.test_buildState

    # PROTECTED REGION ID(SKALogger.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKALogger.test_versionId) ENABLED START #
        assert tango_context.device.versionId == ''
        # PROTECTED REGION END #    //  SKALogger.test_versionId

    # PROTECTED REGION ID(SKALogger.test_centralLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_centralLoggingLevel_decorators
    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_centralLoggingLevel) ENABLED START #
        assert tango_context.device.centralLoggingLevel == 0
        # PROTECTED REGION END #    //  SKALogger.test_centralLoggingLevel

    # PROTECTED REGION ID(SKALogger.test_elementLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_elementLoggingLevel_decorators
    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_elementLoggingLevel) ENABLED START #
        assert tango_context.device.elementLoggingLevel == 0
        # PROTECTED REGION END #    //  SKALogger.test_elementLoggingLevel

    # PROTECTED REGION ID(SKALogger.test_storageLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_storageLoggingLevel_decorators
    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_storageLoggingLevel) ENABLED START #
        assert tango_context.device.storageLoggingLevel == 0
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


