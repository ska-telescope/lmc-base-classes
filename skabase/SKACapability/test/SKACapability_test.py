#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKACapability project
#
#
#
#########################################################################################
"""Contain the tests for the SKACapability."""


# standard imports
import sys
import os

# Imports
import re
import pytest
from tango import DevState

# Path
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))




# PROTECTED REGION ID(SKACapability.test_additional_imports) ENABLED START #
# PROTECTED REGION END #    //  SKACapability.test_additional_imports


# Device test case
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION ID(SKACapability.test_SKACapability_decorators) ENABLED START #
# PROTECTED REGION END #    //  SKACapability.test_SKACapability_decorators
class TestSKACapability(object):
    """Test case for packet generation."""

    properties = {
        'SkaLevel': '4',
        'CentralLoggingTarget': '',
        'ElementLoggingTarget': '',
        'StorageLoggingTarget': 'localhost',
        'GroupDefinitions': '',
        'CapType': '',
        'CapID': '',
        'subID': '',
        }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKACapability.numpy = MagicMock()
        # PROTECTED REGION ID(SKACapability.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKACapability.test_mocking

    def test_properties(self, tango_context):
        """Test device properties"""
        # Test the properties
        # PROTECTED REGION ID(SKACapability.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKACapability.test_properties

    # PROTECTED REGION ID(SKACapability.test_ObsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_ObsState_decorators
    def test_ObsState(self, tango_context):
        """Test for ObsState"""
        # PROTECTED REGION ID(SKACapability.test_ObsState) ENABLED START #
        assert tango_context.device.ObsState == 0
        # PROTECTED REGION END #    //  SKACapability.test_ObsState

    # PROTECTED REGION ID(SKACapability.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKACapability.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.UNKNOWN
        # PROTECTED REGION END #    //  SKACapability.test_State

    # PROTECTED REGION ID(SKACapability.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKACapability.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in UNKNOWN state."
        # PROTECTED REGION END #    //  SKACapability.test_Status

    # PROTECTED REGION ID(SKACapability.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKACapability.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'SKACapability, lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  SKACapability.test_GetVersionInfo

    # PROTECTED REGION ID(SKACapability.test_ConfigureInstances_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_ConfigureInstances_decorators
    def test_ConfigureInstances(self, tango_context):
        """Test for ConfigureInstances"""
        # PROTECTED REGION ID(SKACapability.test_ConfigureInstances) ENABLED START #
        assert tango_context.device.ConfigureInstances(0) is None
        # PROTECTED REGION END #    //  SKACapability.test_ConfigureInstances

    # PROTECTED REGION ID(SKACapability.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_Reset_decorators
    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SKACapability.test_Reset) ENABLED START #
        assert tango_context.device.Reset() is None
        # PROTECTED REGION END #    //  SKACapability.test_Reset


    # PROTECTED REGION ID(SKACapability.test_activationTime_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_activationTime_decorators
    def test_activationTime(self, tango_context):
        """Test for activationTime"""
        # PROTECTED REGION ID(SKACapability.test_activationTime) ENABLED START #
        assert tango_context.device.activationTime == 0.0
        # PROTECTED REGION END #    //  SKACapability.test_activationTime

    # PROTECTED REGION ID(SKACapability.test_obsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_obsState_decorators
    def test_obsState(self, tango_context):
        """Test for obsState"""
        # PROTECTED REGION ID(SKACapability.test_obsState) ENABLED START #
        assert tango_context.device.obsState == 0
        # PROTECTED REGION END #    //  SKACapability.test_obsState

    # PROTECTED REGION ID(SKACapability.test_obsMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_obsMode_decorators
    def test_obsMode(self, tango_context):
        """Test for obsMode"""
        # PROTECTED REGION ID(SKACapability.test_obsMode) ENABLED START #
        assert tango_context.device.obsMode == 0
        # PROTECTED REGION END #    //  SKACapability.test_obsMode

    # PROTECTED REGION ID(SKACapability.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_configurationProgress_decorators
    def test_configurationProgress(self, tango_context):
        """Test for configurationProgress"""
        # PROTECTED REGION ID(SKACapability.test_configurationProgress) ENABLED START #
        assert tango_context.device.configurationProgress == 0
        # PROTECTED REGION END #    //  SKACapability.test_configurationProgress

    # PROTECTED REGION ID(SKACapability.test_configurationDelayExpected_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_configurationDelayExpected_decorators
    def test_configurationDelayExpected(self, tango_context):
        """Test for configurationDelayExpected"""
        # PROTECTED REGION ID(SKACapability.test_configurationDelayExpected) ENABLED START #
        assert tango_context.device.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SKACapability.test_configurationDelayExpected

    # PROTECTED REGION ID(SKACapability.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKACapability.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  SKACapability.test_buildState

    # PROTECTED REGION ID(SKACapability.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKACapability.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  SKACapability.test_versionId

    # PROTECTED REGION ID(SKACapability.test_centralLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_centralLoggingLevel_decorators
    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKACapability.test_centralLoggingLevel) ENABLED START #
        assert tango_context.device.centralLoggingLevel == 0
        # PROTECTED REGION END #    //  SKACapability.test_centralLoggingLevel

    # PROTECTED REGION ID(SKACapability.test_elementLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_elementLoggingLevel_decorators
    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKACapability.test_elementLoggingLevel) ENABLED START #
        assert tango_context.device.elementLoggingLevel == 0
        # PROTECTED REGION END #    //  SKACapability.test_elementLoggingLevel

    # PROTECTED REGION ID(SKACapability.test_storageLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_storageLoggingLevel_decorators
    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKACapability.test_storageLoggingLevel) ENABLED START #
        assert tango_context.device.storageLoggingLevel == 0
        # PROTECTED REGION END #    //  SKACapability.test_storageLoggingLevel

    # PROTECTED REGION ID(SKACapability.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKACapability.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  SKACapability.test_healthState

    # PROTECTED REGION ID(SKACapability.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKACapability.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  SKACapability.test_adminMode

    # PROTECTED REGION ID(SKACapability.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKACapability.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == 0
        # PROTECTED REGION END #    //  SKACapability.test_controlMode

    # PROTECTED REGION ID(SKACapability.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKACapability.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode is False
        # PROTECTED REGION END #    //  SKACapability.test_simulationMode

    # PROTECTED REGION ID(SKACapability.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKACapability.test_testMode) ENABLED START #
        assert tango_context.device.testMode == ''
        # PROTECTED REGION END #    //  SKACapability.test_testMode

    # PROTECTED REGION ID(SKACapability.test_configuredInstances_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_configuredInstances_decorators
    def test_configuredInstances(self, tango_context):
        """Test for configuredInstances"""
        # PROTECTED REGION ID(SKACapability.test_configuredInstances) ENABLED START #
        assert tango_context.device.configuredInstances == 0
        # PROTECTED REGION END #    //  SKACapability.test_configuredInstances

    # PROTECTED REGION ID(SKACapability.test_usedComponents_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_usedComponents_decorators
    def test_usedComponents(self, tango_context):
        """Test for usedComponents"""
        # PROTECTED REGION ID(SKACapability.test_usedComponents) ENABLED START #
        assert tango_context.device.usedComponents == ('',)
        # PROTECTED REGION END #    //  SKACapability.test_usedComponents
