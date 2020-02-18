#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKAObsDevice project
#
#
#
#########################################################################################
"""Contain the tests for the SKAObsDevice."""

# Standard imports
import sys
import os

# Imports
import re
import pytest
from tango import DevState

# Path
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# PROTECTED REGION ID(SKAObsDevice.test_additional_imports) ENABLED START #
from skabase.control_model import AdminMode, ControlMode, HealthState, ObsMode, ObsState
# PROTECTED REGION END #    //  SKAObsDevice.test_additional_imports

# Device test case
# PROTECTED REGION ID(SKAObsDevice.test_SKAObsDevice_decorators) ENABLED START #
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION END #    //  SKAObsDevice.test_SKAObsDevice_decorators
class TestSKAObsDevice(object):
    """Test case for packet generation."""

    properties = {
        'SkaLevel': '4',
        'LoggingTargetsDefault': '',
        'GroupDefinitions': '',
        }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKAObsDevice.numpy = MagicMock()
        # PROTECTED REGION ID(SKAObsDevice.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKAObsDevice.test_mocking

    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(SKAObsDevice.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKAObsDevice.test_properties
        pass

    # PROTECTED REGION ID(SKAObsDevice.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKAObsDevice.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.UNKNOWN
        # PROTECTED REGION END #    //  SKAObsDevice.test_State

    # PROTECTED REGION ID(SKAObsDevice.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKAObsDevice.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in UNKNOWN state."
        # PROTECTED REGION END #    //  SKAObsDevice.test_Status

    # PROTECTED REGION ID(SKAObsDevice.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKAObsDevice.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'SKAObsDevice, lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  SKAObsDevice.test_GetVersionInfo

    # PROTECTED REGION ID(SKAObsDevice.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_Reset_decorators
    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SKAObsDevice.test_Reset) ENABLED START #
        assert tango_context.device.Reset() is None
        # PROTECTED REGION END #    //  SKAObsDevice.test_Reset

    # PROTECTED REGION ID(SKAObsDevice.test_obsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_obsState_decorators
    def test_obsState(self, tango_context):
        """Test for obsState"""
        # PROTECTED REGION ID(SKAObsDevice.test_obsState) ENABLED START #
        assert tango_context.device.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  SKAObsDevice.test_obsState

    # PROTECTED REGION ID(SKAObsDevice.test_obsMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_obsMode_decorators
    def test_obsMode(self, tango_context):
        """Test for obsMode"""
        # PROTECTED REGION ID(SKAObsDevice.test_obsMode) ENABLED START #
        assert tango_context.device.obsMode == ObsMode.IDLE
        # PROTECTED REGION END #    //  SKAObsDevice.test_obsMode

    # PROTECTED REGION ID(SKAObsDevice.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_configurationProgress_decorators
    def test_configurationProgress(self, tango_context):
        """Test for configurationProgress"""
        # PROTECTED REGION ID(SKAObsDevice.test_configurationProgress) ENABLED START #
        assert tango_context.device.configurationProgress == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_configurationProgress

    # PROTECTED REGION ID(SKAObsDevice.test_configurationDelayExpected_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_configurationDelayExpected_decorators
    def test_configurationDelayExpected(self, tango_context):
        """Test for configurationDelayExpected"""
        # PROTECTED REGION ID(SKAObsDevice.test_configurationDelayExpected) ENABLED START #
        assert tango_context.device.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_configurationDelayExpected

    # PROTECTED REGION ID(SKAObsDevice.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKAObsDevice.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) != None
        # PROTECTED REGION END #    //  SKAObsDevice.test_buildState

    # PROTECTED REGION ID(SKAObsDevice.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKAObsDevice.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) != None
        # PROTECTED REGION END #    //  SKAObsDevice.test_versionId

    # PROTECTED REGION ID(SKAObsDevice.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKAObsDevice.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SKAObsDevice.test_healthState

    # PROTECTED REGION ID(SKAObsDevice.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKAObsDevice.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  SKAObsDevice.test_adminMode

    # PROTECTED REGION ID(SKAObsDevice.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKAObsDevice.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKAObsDevice.test_controlMode

    # PROTECTED REGION ID(SKAObsDevice.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKAObsDevice.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode is False
        # PROTECTED REGION END #    //  SKAObsDevice.test_simulationMode

    # PROTECTED REGION ID(SKAObsDevice.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKAObsDevice.test_testMode) ENABLED START #
        assert tango_context.device.testMode == ''
        # PROTECTED REGION END #    //  SKAObsDevice.test_testMode
