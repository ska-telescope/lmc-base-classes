#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKAMaster project
#
#
#
#########################################################################################
"""Contain the tests for the SKAMaster."""

# Standard imports
import sys
import os

# Imports
import re
import pytest
from tango import DevState

# PROTECTED REGION ID(SKAMaster.test_additional_imports) ENABLED START #
from ska.base.control_model import AdminMode, ControlMode, HealthState, SimulationMode, TestMode
# PROTECTED REGION END #    //  SKAMaster.test_additional_imports
# Device test case
# PROTECTED REGION ID(SKAMaster.test_SKAMaster_decorators) ENABLED START #
@pytest.mark.usefixtures("tango_context")
# PROTECTED REGION END #    //  SKAMaster.test_SKAMaster_decorators
class TestSKAMaster(object):
    """Test case for packet generation."""

    capabilities = ['BAND1:1', 'BAND2:1', 'BAND3:0', 'BAND4:0', 'BAND5:0']
    properties = {
        'SkaLevel': '4',
        'LoggingTargetsDefault': '',
        'GroupDefinitions': '',
        'NrSubarrays': '16',
        'CapabilityTypes': '',
        'MaxCapabilities': 'BAND1:1'
        }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKAMaster.numpy = MagicMock()
        # PROTECTED REGION ID(SKAMaster.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKAMaster.test_mocking

    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(SKAMaster.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKAMaster.test_properties
        pass

    # PROTECTED REGION ID(SKAMaster.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKAMaster.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.UNKNOWN
        # PROTECTED REGION END #    //  SKAMaster.test_State

    # PROTECTED REGION ID(SKAMaster.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKAMaster.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in UNKNOWN state."
        # PROTECTED REGION END #    //  SKAMaster.test_Status

    # PROTECTED REGION ID(SKAMaster.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKAMaster.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'SKAMaster, lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) != None
        # PROTECTED REGION END #    //  SKAMaster.test_GetVersionInfo

    # PROTECTED REGION ID(SKAMaster.test_isCapabilityAchievable_failure_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_isCapabilityAchievable_failure_decorators
    def test_isCapabilityAchievable_failure(self, tango_context):
        """Test for isCapabilityAchievable to test failure condition"""
        # PROTECTED REGION ID(SKAMaster.test_isCapabilityAchievable_failure) ENABLED START #
        assert tango_context.device.isCapabilityAchievable([[2], ['BAND1']]) is False
        # PROTECTED REGION END #    //  SKAMaster.test_isCapabilityAchievable_failure

        # PROTECTED REGION ID(SKAMaster.test_isCapabilityAchievable_success_decorators) ENABLED START #
        # PROTECTED REGION END #    //  SKAMaster.test_isCapabilityAchievable_success_decorators
    def test_isCapabilityAchievable_success(self, tango_context):
        """Test for isCapabilityAchievable to test success condition"""
        # PROTECTED REGION ID(SKAMaster.test_isCapabilityAchievable_success) ENABLED START #
        assert tango_context.device.isCapabilityAchievable([[1], ['BAND1']]) is True
        # PROTECTED REGION END #    //  SKAMaster.test_isCapabilityAchievable_success

    # PROTECTED REGION ID(SKAMaster.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_Reset_decorators
    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SKAMaster.test_Reset) ENABLED START #
        assert tango_context.device.Reset() is None
        # PROTECTED REGION END #    //  SKAMaster.test_Reset


    # PROTECTED REGION ID(SKAMaster.test_elementLoggerAddress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_elementLoggerAddress_decorators
    def test_elementLoggerAddress(self, tango_context):
        """Test for elementLoggerAddress"""
        # PROTECTED REGION ID(SKAMaster.test_elementLoggerAddress) ENABLED START #
        assert tango_context.device.elementLoggerAddress == ''
        # PROTECTED REGION END #    //  SKAMaster.test_elementLoggerAddress

    # PROTECTED REGION ID(SKAMaster.test_elementAlarmAddress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_elementAlarmAddress_decorators
    def test_elementAlarmAddress(self, tango_context):
        """Test for elementAlarmAddress"""
        # PROTECTED REGION ID(SKAMaster.test_elementAlarmAddress) ENABLED START #
        assert tango_context.device.elementAlarmAddress == ''
        # PROTECTED REGION END #    //  SKAMaster.test_elementAlarmAddress

    # PROTECTED REGION ID(SKAMaster.test_elementTelStateAddress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_elementTelStateAddress_decorators
    def test_elementTelStateAddress(self, tango_context):
        """Test for elementTelStateAddress"""
        # PROTECTED REGION ID(SKAMaster.test_elementTelStateAddress) ENABLED START #
        assert tango_context.device.elementTelStateAddress == ''
        # PROTECTED REGION END #    //  SKAMaster.test_elementTelStateAddress

    # PROTECTED REGION ID(SKAMaster.test_elementDatabaseAddress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_elementDatabaseAddress_decorators
    def test_elementDatabaseAddress(self, tango_context):
        """Test for elementDatabaseAddress"""
        # PROTECTED REGION ID(SKAMaster.test_elementDatabaseAddress) ENABLED START #
        assert tango_context.device.elementDatabaseAddress == ''
        # PROTECTED REGION END #    //  SKAMaster.test_elementDatabaseAddress

    # PROTECTED REGION ID(SKAMaster.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKAMaster.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) != None
        # PROTECTED REGION END #    //  SKAMaster.test_buildState

    # PROTECTED REGION ID(SKAMaster.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKAMaster.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) != None
        # PROTECTED REGION END #    //  SKAMaster.test_versionId

    # PROTECTED REGION ID(SKAMaster.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKAMaster.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SKAMaster.test_healthState

    # PROTECTED REGION ID(SKAMaster.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKAMaster.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  SKAMaster.test_adminMode

    # PROTECTED REGION ID(SKAMaster.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKAMaster.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKAMaster.test_controlMode

    # PROTECTED REGION ID(SKAMaster.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKAMaster.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKAMaster.test_simulationMode

    # PROTECTED REGION ID(SKAMaster.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKAMaster.test_testMode) ENABLED START #
        assert tango_context.device.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKAMaster.test_testMode

    # PROTECTED REGION ID(SKAMaster.test_maxCapabilities_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_maxCapabilities_decorators
    def test_maxCapabilities(self, tango_context):
        """Test for maxCapabilities"""
        # PROTECTED REGION ID(SKAMaster.test_maxCapabilities) ENABLED START #
        assert tango_context.device.maxCapabilities == ('BAND1:1', 'BAND2:1')
        # PROTECTED REGION END #    //  SKAMaster.test_maxCapabilities

    # PROTECTED REGION ID(SKAMaster.test_availableCapabilities_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_availableCapabilities_decorators
    def test_availableCapabilities(self, tango_context):
        """Test for availableCapabilities"""
        # PROTECTED REGION ID(SKAMaster.test_availableCapabilities) ENABLED START #
        assert tango_context.device.availableCapabilities == ('BAND1:1', 'BAND2:1')
        # PROTECTED REGION END #    //  SKAMaster.test_availableCapabilities
