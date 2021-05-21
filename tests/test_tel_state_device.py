#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKATelState project
#
#
#
#########################################################################################
"""Contain the tests for the SKATelState."""

import re
import pytest
from tango import DevState

# PROTECTED REGION ID(SKATelState.test_additional_imports) ENABLED START #
from ska_tango_base.control_model import AdminMode, ControlMode, HealthState, SimulationMode, TestMode
# PROTECTED REGION END #    //  SKATelState.test_additional_imports


# PROTECTED REGION ID(SKATelState.test_SKATelState_decorators) ENABLED START #
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION END #    //  SKATelState.test_SKATelState_decorators
class TestSKATelState(object):
    """Test case for packet generation."""

    properties = {
        'TelStateConfigFile': '',
        'SkaLevel': '4',
        'GroupDefinitions': '',
        'LoggingTargetsDefault': '',
    }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKATelState.numpy = MagicMock()
        # PROTECTED REGION ID(SKATelState.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKATelState.test_mocking

    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(SKATelState.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKATelState.test_properties
        pass

    # PROTECTED REGION ID(SKATelState.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKATelState.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.DISABLE
        # PROTECTED REGION END #    //  SKATelState.test_State

    # PROTECTED REGION ID(SKATelState.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKATelState.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in DISABLE state."
        # PROTECTED REGION END #    //  SKATelState.test_Status

    # PROTECTED REGION ID(SKATelState.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKATelState.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'SKATelState, ska_tango_base, [0-9]+.[0-9]+.[0-9]+, '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  SKATelState.test_GetVersionInfo

    # PROTECTED REGION ID(SKATelState.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKATelState.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'ska_tango_base, [0-9]+.[0-9]+.[0-9]+, '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  SKATelState.test_buildState

    # PROTECTED REGION ID(SKATelState.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKATelState.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9]+.[0-9]+.[0-9]+')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  SKATelState.test_versionId

    # PROTECTED REGION ID(SKATelState.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKATelState.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SKATelState.test_healthState

    # PROTECTED REGION ID(SKATelState.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKATelState.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.OFFLINE
        # PROTECTED REGION END #    //  SKATelState.test_adminMode

    # PROTECTED REGION ID(SKATelState.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKATelState.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKATelState.test_controlMode

    # PROTECTED REGION ID(SKATelState.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKATelState.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKATelState.test_simulationMode

    # PROTECTED REGION ID(SKATelState.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKATelState.test_testMode) ENABLED START #
        assert tango_context.device.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKATelState.test_testMode
