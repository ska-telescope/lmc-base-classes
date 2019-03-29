#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKASubarray project
#
#
#
#########################################################################################
"""Contain the tests for the SKASubarray."""

# Path
from builtins import object
import sys
import os
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
import pytest
from tango import DevState
import re

# PROTECTED REGION ID(SKASubarray.test_additional_imports) ENABLED START #
# PROTECTED REGION END #    //  SKASubarray.test_additional_imports


# Device test case
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION ID(SKASubarray.test_SKASubarray_decorators) ENABLED START #
# PROTECTED REGION END #    //  SKASubarray.test_SKASubarray_decorators
class TestSKASubarray(object):
    """Test case for packet generation."""

    properties = {
        'CapabilityTypes': '',
        'CentralLoggingTarget': '',
        'ElementLoggingTarget': '',
        'GroupDefinitions': '',
        'SkaLevel': '4',
        'StorageLoggingTarget': 'localhost',
        'SubID': '',
        }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKASubarray.numpy = MagicMock()
        # PROTECTED REGION ID(SKASubarray.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKASubarray.test_mocking

    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(SKASubarray.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKASubarray.test_properties
        pass

    # PROTECTED REGION ID(SKASubarray.test_Abort_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Abort_decorators
    def test_Abort(self, tango_context):
        """Test for Abort"""
        # PROTECTED REGION ID(SKASubarray.test_Abort) ENABLED START #
        assert tango_context.device.Abort() == None
        # PROTECTED REGION END #    //  SKASubarray.test_Abort

    # PROTECTED REGION ID(SKASubarray.test_ConfigureCapability_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_ConfigureCapability_decorators
    def test_ConfigureCapability(self, tango_context):
        """Test for ConfigureCapability"""
        # PROTECTED REGION ID(SKASubarray.test_ConfigureCapability) ENABLED START #
        assert tango_context.device.ConfigureCapability([[0], [""]]) == None
        # PROTECTED REGION END #    //  SKASubarray.test_ConfigureCapability

    # PROTECTED REGION ID(SKASubarray.test_DeconfigureAllCapabilities_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_DeconfigureAllCapabilities_decorators
    def test_DeconfigureAllCapabilities(self, tango_context):
        """Test for DeconfigureAllCapabilities"""
        # PROTECTED REGION ID(SKASubarray.test_DeconfigureAllCapabilities) ENABLED START #
        assert tango_context.device.DeconfigureAllCapabilities("") == None
        # PROTECTED REGION END #    //  SKASubarray.test_DeconfigureAllCapabilities

    # PROTECTED REGION ID(SKASubarray.test_DeconfigureCapability_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_DeconfigureCapability_decorators
    def test_DeconfigureCapability(self, tango_context):
        """Test for DeconfigureCapability"""
        # PROTECTED REGION ID(SKASubarray.test_DeconfigureCapability) ENABLED START #
        assert tango_context.device.DeconfigureCapability([[0], [""]]) == None
        # PROTECTED REGION END #    //  SKASubarray.test_DeconfigureCapability

    # PROTECTED REGION ID(SKASubarray.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKASubarray.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'SKASubarray, lmc-base-classes, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) != None
        # PROTECTED REGION END #    //  SKASubarray.test_GetVersionInfo

    # PROTECTED REGION ID(SKASubarray.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKASubarray.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in DISABLE state."
        # PROTECTED REGION END #    //  SKASubarray.test_Status

    # PROTECTED REGION ID(SKASubarray.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKASubarray.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.DISABLE
        # PROTECTED REGION END #    //  SKASubarray.test_State

    # PROTECTED REGION ID(SKASubarray.test_AssignResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_AssignResources_decorators
    def test_AssignResources(self, tango_context):
        """Test for AssignResources"""
        # PROTECTED REGION ID(SKASubarray.test_AssignResources) ENABLED START #
        assert tango_context.device.AssignResources([""]) == [""]
        # PROTECTED REGION END #    //  SKASubarray.test_AssignResources

    # PROTECTED REGION ID(SKASubarray.test_EndSB_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_EndSB_decorators
    def test_EndSB(self, tango_context):
        """Test for EndSB"""
        # PROTECTED REGION ID(SKASubarray.test_EndSB) ENABLED START #
        assert tango_context.device.EndSB() == None
        # PROTECTED REGION END #    //  SKASubarray.test_EndSB

    # PROTECTED REGION ID(SKASubarray.test_EndScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_EndScan_decorators
    def test_EndScan(self, tango_context):
        """Test for EndScan"""
        # PROTECTED REGION ID(SKASubarray.test_EndScan) ENABLED START #
        assert tango_context.device.EndScan() == None
        # PROTECTED REGION END #    //  SKASubarray.test_EndScan

    # PROTECTED REGION ID(SKASubarray.test_ObsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_ObsState_decorators
    def test_ObsState(self, tango_context):
        """Test for ObsState"""
        # PROTECTED REGION ID(SKASubarray.test_ObsState) ENABLED START #
        assert tango_context.device.ObsState == 0
        # PROTECTED REGION END #    //  SKASubarray.test_ObsState

    # PROTECTED REGION ID(SKASubarray.test_Pause_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Pause_decorators
    def test_Pause(self, tango_context):
        """Test for Pause"""
        # PROTECTED REGION ID(SKASubarray.test_Pause) ENABLED START #
        assert tango_context.device.Pause() == None
        # PROTECTED REGION END #    //  SKASubarray.test_Pause

    # PROTECTED REGION ID(SKASubarray.test_ReleaseAllResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_ReleaseAllResources_decorators
    def test_ReleaseAllResources(self, tango_context):
        """Test for ReleaseAllResources"""
        # PROTECTED REGION ID(SKASubarray.test_ReleaseAllResources) ENABLED START #
        assert tango_context.device.ReleaseAllResources() == [""]
        # PROTECTED REGION END #    //  SKASubarray.test_ReleaseAllResources

    # PROTECTED REGION ID(SKASubarray.test_ReleaseResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_ReleaseResources_decorators
    def test_ReleaseResources(self, tango_context):
        """Test for ReleaseResources"""
        # PROTECTED REGION ID(SKASubarray.test_ReleaseResources) ENABLED START #
        assert tango_context.device.ReleaseResources([""]) == [""]
        # PROTECTED REGION END #    //  SKASubarray.test_ReleaseResources

    # PROTECTED REGION ID(SKASubarray.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Reset_decorators
    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SKASubarray.test_Reset) ENABLED START #
        assert tango_context.device.Reset() == None
        # PROTECTED REGION END #    //  SKASubarray.test_Reset

    # PROTECTED REGION ID(SKASubarray.test_Resume_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Resume_decorators
    def test_Resume(self, tango_context):
        """Test for Resume"""
        # PROTECTED REGION ID(SKASubarray.test_Resume) ENABLED START #
        assert tango_context.device.Resume() == None
        # PROTECTED REGION END #    //  SKASubarray.test_Resume

    # PROTECTED REGION ID(SKASubarray.test_Scan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Scan_decorators
    def test_Scan(self, tango_context):
        """Test for Scan"""
        # PROTECTED REGION ID(SKASubarray.test_Scan) ENABLED START #
        assert tango_context.device.Scan([""]) == None
        # PROTECTED REGION END #    //  SKASubarray.test_Scan

    # PROTECTED REGION ID(SKASubarray.test_activationTime_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_activationTime_decorators
    def test_activationTime(self, tango_context):
        """Test for activationTime"""
        # PROTECTED REGION ID(SKASubarray.test_activationTime) ENABLED START #
        assert tango_context.device.activationTime == 0.0
        # PROTECTED REGION END #    //  SKASubarray.test_activationTime

    # PROTECTED REGION ID(SKASubarray.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKASubarray.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  SKASubarray.test_adminMode

    # PROTECTED REGION ID(SKASubarray.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKASubarray.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmc-base-classes, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) != None
        # PROTECTED REGION END #    //  SKASubarray.test_buildState

    # PROTECTED REGION ID(SKASubarray.test_centralLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_centralLoggingLevel_decorators
    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKASubarray.test_centralLoggingLevel) ENABLED START #
        assert tango_context.device.centralLoggingLevel == 0
        # PROTECTED REGION END #    //  SKASubarray.test_centralLoggingLevel

    # PROTECTED REGION ID(SKASubarray.test_configurationDelayExpected_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_configurationDelayExpected_decorators
    def test_configurationDelayExpected(self, tango_context):
        """Test for configurationDelayExpected"""
        # PROTECTED REGION ID(SKASubarray.test_configurationDelayExpected) ENABLED START #
        assert tango_context.device.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SKASubarray.test_configurationDelayExpected

    # PROTECTED REGION ID(SKASubarray.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_configurationProgress_decorators
    def test_configurationProgress(self, tango_context):
        """Test for configurationProgress"""
        # PROTECTED REGION ID(SKASubarray.test_configurationProgress) ENABLED START #
        assert tango_context.device.configurationProgress == 0
        # PROTECTED REGION END #    //  SKASubarray.test_configurationProgress

    # PROTECTED REGION ID(SKASubarray.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKASubarray.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == 0
        # PROTECTED REGION END #    //  SKASubarray.test_controlMode

    # PROTECTED REGION ID(SKASubarray.test_elementLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_elementLoggingLevel_decorators
    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKASubarray.test_elementLoggingLevel) ENABLED START #
        assert tango_context.device.elementLoggingLevel == 0
        # PROTECTED REGION END #    //  SKASubarray.test_elementLoggingLevel

    # PROTECTED REGION ID(SKASubarray.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKASubarray.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  SKASubarray.test_healthState

    # PROTECTED REGION ID(SKASubarray.test_obsMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_obsMode_decorators
    def test_obsMode(self, tango_context):
        """Test for obsMode"""
        # PROTECTED REGION ID(SKASubarray.test_obsMode) ENABLED START #
        assert tango_context.device.obsMode == 0
        # PROTECTED REGION END #    //  SKASubarray.test_obsMode

    # PROTECTED REGION ID(SKASubarray.test_obsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_obsState_decorators
    def test_obsState(self, tango_context):
        """Test for obsState"""
        # PROTECTED REGION ID(SKASubarray.test_obsState) ENABLED START #
        assert tango_context.device.obsState == 0
        # PROTECTED REGION END #    //  SKASubarray.test_obsState

    # PROTECTED REGION ID(SKASubarray.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKASubarray.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == False
        # PROTECTED REGION END #    //  SKASubarray.test_simulationMode

    # PROTECTED REGION ID(SKASubarray.test_storageLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_storageLoggingLevel_decorators
    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKASubarray.test_storageLoggingLevel) ENABLED START #
        assert tango_context.device.storageLoggingLevel == 0
        # PROTECTED REGION END #    //  SKASubarray.test_storageLoggingLevel

    # PROTECTED REGION ID(SKASubarray.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKASubarray.test_testMode) ENABLED START #
        assert tango_context.device.testMode == ''
        # PROTECTED REGION END #    //  SKASubarray.test_testMode

    # PROTECTED REGION ID(SKASubarray.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKASubarray.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) != None
        # PROTECTED REGION END #    //  SKASubarray.test_versionId

    # PROTECTED REGION ID(SKASubarray.test_assignedResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_assignedResources_decorators
    def test_assignedResources(self, tango_context):
        """Test for assignedResources"""
        # PROTECTED REGION ID(SKASubarray.test_assignedResources) ENABLED START #
        assert tango_context.device.assignedResources == ('',)
        # PROTECTED REGION END #    //  SKASubarray.test_assignedResources

    # PROTECTED REGION ID(SKASubarray.test_configuredCapabilities_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_configuredCapabilities_decorators
    def test_configuredCapabilities(self, tango_context):
        """Test for configuredCapabilities"""
        # PROTECTED REGION ID(SKASubarray.test_configuredCapabilities) ENABLED START #
        assert tango_context.device.configuredCapabilities == None
        # PROTECTED REGION END #    //  SKASubarray.test_configuredCapabilities


