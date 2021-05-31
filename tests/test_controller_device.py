#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKAController project
#
#
#
#########################################################################################
"""Contain the tests for the SKAController."""

import re
import pytest
from tango import DevState

# PROTECTED REGION ID(SKAController.test_additional_imports) ENABLED START #
from ska_tango_base import SKAController
from ska_tango_base.base import ReferenceBaseComponentManager
from ska_tango_base.control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    SimulationMode,
    TestMode,
)

# PROTECTED REGION END #    //  SKAController.test_additional_imports


# PROTECTED REGION ID(SKAController.test_SKAController_decorators) ENABLED START #
@pytest.mark.usefixtures("tango_context")
# PROTECTED REGION END #    //  SKAController.test_SKAController_decorators
class TestSKAController(object):
    """
    Test class for tests of the SKAController device class.
    """

    # capabilities = ['BAND1:1', 'BAND2:1', 'BAND3:0', 'BAND4:0', 'BAND5:0']

    @pytest.fixture(scope="class")
    def device_properties(self):
        """
        Fixture that returns device_properties to be provided to the
        device under test.
        """
        return {
            "SkaLevel": "4",
            "LoggingTargetsDefault": "",
            "GroupDefinitions": "",
            "NrSubarrays": "16",
            "CapabilityTypes": "",
            "MaxCapabilities": ["BAND1:1", "BAND2:1"],
        }

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Fixture that specifies the device to be tested, along with its
        properties and memorized attributes.

        This implementation provides a concrete subclass of the device
        class under test, some properties, and a memorized value for
        adminMode.
        """
        return {
            "device": SKAController,
            "component_manager_patch": lambda self: ReferenceBaseComponentManager(
                self.op_state_model, logger=self.logger
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip("Not implemented")
    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(SKAController.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKAController.test_properties
        pass

    # PROTECTED REGION ID(SKAController.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKAController.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.OFF
        # PROTECTED REGION END #    //  SKAController.test_State

    # PROTECTED REGION ID(SKAController.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKAController.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKAController.test_Status

    # PROTECTED REGION ID(SKAController.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKAController.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            f"{tango_context.device.info().dev_class}, ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            "A set of generic base devices for SKA Telescope."
        )
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  SKAController.test_GetVersionInfo

    # PROTECTED REGION ID(SKAController.test_isCapabilityAchievable_failure_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_isCapabilityAchievable_failure_decorators
    def test_isCapabilityAchievable_failure(self, tango_context):
        """Test for isCapabilityAchievable to test failure condition"""
        # PROTECTED REGION ID(SKAController.test_isCapabilityAchievable_failure) ENABLED START #
        assert tango_context.device.isCapabilityAchievable([[2], ["BAND1"]]) is False
        # PROTECTED REGION END #    //  SKAController.test_isCapabilityAchievable_failure

        # PROTECTED REGION ID(SKAController.test_isCapabilityAchievable_success_decorators) ENABLED START #
        # PROTECTED REGION END #    //  SKAController.test_isCapabilityAchievable_success_decorators

    def test_isCapabilityAchievable_success(self, tango_context):
        """Test for isCapabilityAchievable to test success condition"""
        # PROTECTED REGION ID(SKAController.test_isCapabilityAchievable_success) ENABLED START #
        assert tango_context.device.isCapabilityAchievable([[1], ["BAND1"]]) is True
        # PROTECTED REGION END #    //  SKAController.test_isCapabilityAchievable_success

    # PROTECTED REGION ID(SKAController.test_elementLoggerAddress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_elementLoggerAddress_decorators
    def test_elementLoggerAddress(self, tango_context):
        """Test for elementLoggerAddress"""
        # PROTECTED REGION ID(SKAController.test_elementLoggerAddress) ENABLED START #
        assert tango_context.device.elementLoggerAddress == ""
        # PROTECTED REGION END #    //  SKAController.test_elementLoggerAddress

    # PROTECTED REGION ID(SKAController.test_elementAlarmAddress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_elementAlarmAddress_decorators
    def test_elementAlarmAddress(self, tango_context):
        """Test for elementAlarmAddress"""
        # PROTECTED REGION ID(SKAController.test_elementAlarmAddress) ENABLED START #
        assert tango_context.device.elementAlarmAddress == ""
        # PROTECTED REGION END #    //  SKAController.test_elementAlarmAddress

    # PROTECTED REGION ID(SKAController.test_elementTelStateAddress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_elementTelStateAddress_decorators
    def test_elementTelStateAddress(self, tango_context):
        """Test for elementTelStateAddress"""
        # PROTECTED REGION ID(SKAController.test_elementTelStateAddress) ENABLED START #
        assert tango_context.device.elementTelStateAddress == ""
        # PROTECTED REGION END #    //  SKAController.test_elementTelStateAddress

    # PROTECTED REGION ID(SKAController.test_elementDatabaseAddress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_elementDatabaseAddress_decorators
    def test_elementDatabaseAddress(self, tango_context):
        """Test for elementDatabaseAddress"""
        # PROTECTED REGION ID(SKAController.test_elementDatabaseAddress) ENABLED START #
        assert tango_context.device.elementDatabaseAddress == ""
        # PROTECTED REGION END #    //  SKAController.test_elementDatabaseAddress

    # PROTECTED REGION ID(SKAController.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKAController.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  SKAController.test_buildState

    # PROTECTED REGION ID(SKAController.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKAController.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  SKAController.test_versionId

    # PROTECTED REGION ID(SKAController.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKAController.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SKAController.test_healthState

    # PROTECTED REGION ID(SKAController.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKAController.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  SKAController.test_adminMode

    # PROTECTED REGION ID(SKAController.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKAController.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKAController.test_controlMode

    # PROTECTED REGION ID(SKAController.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKAController.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKAController.test_simulationMode

    # PROTECTED REGION ID(SKAController.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKAController.test_testMode) ENABLED START #
        assert tango_context.device.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKAController.test_testMode

    # PROTECTED REGION ID(SKAController.test_maxCapabilities_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_maxCapabilities_decorators
    def test_maxCapabilities(self, tango_context):
        """Test for maxCapabilities"""
        # PROTECTED REGION ID(SKAController.test_maxCapabilities) ENABLED START #
        assert tango_context.device.maxCapabilities == ("BAND1:1", "BAND2:1")
        # PROTECTED REGION END #    //  SKAController.test_maxCapabilities

    # PROTECTED REGION ID(SKAController.test_availableCapabilities_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_availableCapabilities_decorators
    def test_availableCapabilities(self, tango_context):
        """Test for availableCapabilities"""
        # PROTECTED REGION ID(SKAController.test_availableCapabilities) ENABLED START #
        assert tango_context.device.availableCapabilities == ("BAND1:1", "BAND2:1")
        # PROTECTED REGION END #    //  SKAController.test_availableCapabilities
