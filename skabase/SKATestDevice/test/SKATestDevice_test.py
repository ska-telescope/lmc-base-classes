#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKATestDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
#########################################################################################
"""Contain the tests for the SKATestDevice."""

# Path
import sys
import os
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
import pytest
from mock import MagicMock

from PyTango import DevState

# PROTECTED REGION ID(SKATestDevice.test_additional_imports) ENABLED START #
# PROTECTED REGION END #    //  SKATestDevice.test_additional_imports


# Device test case
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION ID(SKATestDevice.test_SKATestDevice_decorators) ENABLED START #
# PROTECTED REGION END #    //  SKATestDevice.test_SKATestDevice_decorators
class TestSKATestDevice(object):
    """Test case for packet generation."""

    properties = {
        'SkaLevel': '4',
        'CentralLoggingTarget': '',
        'ElementLoggingTarget': '',
        'StorageLoggingTarget': 'localhost',
        'CentralLoggingLevelDefault': '',
        'ElementLoggingLevelDefault': '',
        'StorageLoggingLevelStorage': '',
        'MetricList': 'healthState',
        'GroupDefinitions': '',
        'StorageLoggingLevelDefault': '',
        }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKATestDevice.numpy = MagicMock()
        # PROTECTED REGION ID(SKATestDevice.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKATestDevice.test_mocking

    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(SKATestDevice.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKATestDevice.test_properties
        pass

    # PROTECTED REGION ID(SKATestDevice.test_GetMetrics_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_GetMetrics_decorators
    def test_GetMetrics(self, tango_context):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(SKATestDevice.test_GetMetrics) ENABLED START #
        assert tango_context.device.GetMetrics() == ""
        # PROTECTED REGION END #    //  SKATestDevice.test_GetMetrics

    # PROTECTED REGION ID(SKATestDevice.test_ToJson_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_ToJson_decorators
    def test_ToJson(self, tango_context):
        """Test for ToJson"""
        # PROTECTED REGION ID(SKATestDevice.test_ToJson) ENABLED START #
        assert tango_context.device.ToJson("") == ""
        # PROTECTED REGION END #    //  SKATestDevice.test_ToJson

    # PROTECTED REGION ID(SKATestDevice.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKATestDevice.test_GetVersionInfo) ENABLED START #
        assert tango_context.device.GetVersionInfo() == [""]
        # PROTECTED REGION END #    //  SKATestDevice.test_GetVersionInfo

    # PROTECTED REGION ID(SKATestDevice.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKATestDevice.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.UNKNOWN
        # PROTECTED REGION END #    //  SKATestDevice.test_State

    # PROTECTED REGION ID(SKATestDevice.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKATestDevice.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in UNKNOWN state."
        # PROTECTED REGION END #    //  SKATestDevice.test_Status

    # PROTECTED REGION ID(SKATestDevice.test_RunGroupCommand_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_RunGroupCommand_decorators
    def test_RunGroupCommand(self, tango_context):
        """Test for RunGroupCommand"""
        # PROTECTED REGION ID(SKATestDevice.test_RunGroupCommand) ENABLED START #
        assert tango_context.device.RunGroupCommand("") == ""
        # PROTECTED REGION END #    //  SKATestDevice.test_RunGroupCommand

    # PROTECTED REGION ID(SKATestDevice.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_Reset_decorators
    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SKATestDevice.test_Reset) ENABLED START #
        assert tango_context.device.Reset() == None
        # PROTECTED REGION END #    //  SKATestDevice.test_Reset


    # PROTECTED REGION ID(SKATestDevice.test_obsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_obsState_decorators
    def test_obsState(self, tango_context):
        """Test for obsState"""
        # PROTECTED REGION ID(SKATestDevice.test_obsState) ENABLED START #
        assert tango_context.device.obsState == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_obsState

    # PROTECTED REGION ID(SKATestDevice.test_obsMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_obsMode_decorators
    def test_obsMode(self, tango_context):
        """Test for obsMode"""
        # PROTECTED REGION ID(SKATestDevice.test_obsMode) ENABLED START #
        assert tango_context.device.obsMode == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_obsMode

    # PROTECTED REGION ID(SKATestDevice.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_configurationProgress_decorators
    def test_configurationProgress(self, tango_context):
        """Test for configurationProgress"""
        # PROTECTED REGION ID(SKATestDevice.test_configurationProgress) ENABLED START #
        assert tango_context.device.configurationProgress == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_configurationProgress

    # PROTECTED REGION ID(SKATestDevice.test_configurationDelayExpected_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_configurationDelayExpected_decorators
    def test_configurationDelayExpected(self, tango_context):
        """Test for configurationDelayExpected"""
        # PROTECTED REGION ID(SKATestDevice.test_configurationDelayExpected) ENABLED START #
        assert tango_context.device.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_configurationDelayExpected

    # PROTECTED REGION ID(SKATestDevice.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKATestDevice.test_buildState) ENABLED START #
        assert tango_context.device.buildState == ''
        # PROTECTED REGION END #    //  SKATestDevice.test_buildState

    # PROTECTED REGION ID(SKATestDevice.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKATestDevice.test_versionId) ENABLED START #
        assert tango_context.device.versionId == ''
        # PROTECTED REGION END #    //  SKATestDevice.test_versionId

    # PROTECTED REGION ID(SKATestDevice.test_centralLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_centralLoggingLevel_decorators
    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKATestDevice.test_centralLoggingLevel) ENABLED START #
        assert tango_context.device.centralLoggingLevel == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_centralLoggingLevel

    # PROTECTED REGION ID(SKATestDevice.test_elementLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_elementLoggingLevel_decorators
    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKATestDevice.test_elementLoggingLevel) ENABLED START #
        assert tango_context.device.elementLoggingLevel == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_elementLoggingLevel

    # PROTECTED REGION ID(SKATestDevice.test_storageLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_storageLoggingLevel_decorators
    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKATestDevice.test_storageLoggingLevel) ENABLED START #
        assert tango_context.device.storageLoggingLevel == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_storageLoggingLevel

    # PROTECTED REGION ID(SKATestDevice.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKATestDevice.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_healthState

    # PROTECTED REGION ID(SKATestDevice.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKATestDevice.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_adminMode

    # PROTECTED REGION ID(SKATestDevice.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKATestDevice.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_controlMode

    # PROTECTED REGION ID(SKATestDevice.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKATestDevice.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == False
        # PROTECTED REGION END #    //  SKATestDevice.test_simulationMode

    # PROTECTED REGION ID(SKATestDevice.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKATestDevice.test_testMode) ENABLED START #
        assert tango_context.device.testMode == ''
        # PROTECTED REGION END #    //  SKATestDevice.test_testMode


