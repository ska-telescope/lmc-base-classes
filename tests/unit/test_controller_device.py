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

from ska_tango_base.testing import (
    ReferenceBaseComponentManager,
)

from ska_tango_base.control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    SimulationMode,
    TestMode,
)

# PROTECTED REGION END #    //  SKAController.test_additional_imports


# PROTECTED REGION ID(SKAController.test_SKAController_decorators) ENABLED START #
# PROTECTED REGION END #    //  SKAController.test_SKAController_decorators
class TestSKAController(object):
    """Test class for tests of the SKAController device class."""

    # capabilities = ['BAND1:1', 'BAND2:1', 'BAND3:0', 'BAND4:0', 'BAND5:0']

    @pytest.fixture(scope="class")
    def device_properties(self):
        """Fixture that returns properties of the device under test."""
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
        Specification of the device under test.

        The specification includes the device's properties and
        memorized attributes.

        This implementation provides a concrete subclass of the device
        class under test, some properties, and a memorized value for
        adminMode.
        """
        return {
            "device": SKAController,
            "component_manager_patch": lambda self: ReferenceBaseComponentManager(
                self.logger,
                self._communication_state_changed,
                self._component_state_changed,
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip("Not implemented")
    def test_properties(self, device_under_test):
        """Test device properties."""
        # PROTECTED REGION ID(SKAController.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKAController.test_properties
        pass

    # PROTECTED REGION ID(SKAController.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_State_decorators
    def test_State(self, device_under_test):
        """Test for State."""
        # PROTECTED REGION ID(SKAController.test_State) ENABLED START #
        assert device_under_test.state() == DevState.OFF
        # PROTECTED REGION END #    //  SKAController.test_State

    # PROTECTED REGION ID(SKAController.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_Status_decorators
    def test_Status(self, device_under_test):
        """Test for Status."""
        # PROTECTED REGION ID(SKAController.test_Status) ENABLED START #
        assert device_under_test.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKAController.test_Status

    # PROTECTED REGION ID(SKAController.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test):
        """Test for GetVersionInfo."""
        # PROTECTED REGION ID(SKAController.test_GetVersionInfo) ENABLED START #
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])
        # PROTECTED REGION END #    //  SKAController.test_GetVersionInfo

    # PROTECTED REGION ID(SKAController.test_isCapabilityAchievable_failure_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_isCapabilityAchievable_failure_decorators
    @pytest.mark.parametrize(
        ("capability", "success"), [([[2], ["BAND1"]], False), ([[1], ["BAND1"]], True)]
    )
    def test_isCapabilityAchievable(self, device_under_test, capability, success):
        """Test for isCapabilityAchievable to test failure condition."""
        # PROTECTED REGION ID(SKAController.test_isCapabilityAchievable) ENABLED START #
        assert success == device_under_test.isCapabilityAchievable(capability)
        # PROTECTED REGION END #    //  SKAController.test_isCapabilityAchievable

    # PROTECTED REGION ID(SKAController.test_elementLoggerAddress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_elementLoggerAddress_decorators
    def test_elementLoggerAddress(self, device_under_test):
        """Test for elementLoggerAddress."""
        # PROTECTED REGION ID(SKAController.test_elementLoggerAddress) ENABLED START #
        assert device_under_test.elementLoggerAddress == ""
        # PROTECTED REGION END #    //  SKAController.test_elementLoggerAddress

    # PROTECTED REGION ID(SKAController.test_elementAlarmAddress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_elementAlarmAddress_decorators
    def test_elementAlarmAddress(self, device_under_test):
        """Test for elementAlarmAddress."""
        # PROTECTED REGION ID(SKAController.test_elementAlarmAddress) ENABLED START #
        assert device_under_test.elementAlarmAddress == ""
        # PROTECTED REGION END #    //  SKAController.test_elementAlarmAddress

    # PROTECTED REGION ID(SKAController.test_elementTelStateAddress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_elementTelStateAddress_decorators
    def test_elementTelStateAddress(self, device_under_test):
        """Test for elementTelStateAddress."""
        # PROTECTED REGION ID(SKAController.test_elementTelStateAddress) ENABLED START #
        assert device_under_test.elementTelStateAddress == ""
        # PROTECTED REGION END #    //  SKAController.test_elementTelStateAddress

    # PROTECTED REGION ID(SKAController.test_elementDatabaseAddress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_elementDatabaseAddress_decorators
    def test_elementDatabaseAddress(self, device_under_test):
        """Test for elementDatabaseAddress."""
        # PROTECTED REGION ID(SKAController.test_elementDatabaseAddress) ENABLED START #
        assert device_under_test.elementDatabaseAddress == ""
        # PROTECTED REGION END #    //  SKAController.test_elementDatabaseAddress

    # PROTECTED REGION ID(SKAController.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_buildState_decorators
    def test_buildState(self, device_under_test):
        """Test for buildState."""
        # PROTECTED REGION ID(SKAController.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, device_under_test.buildState)) is not None
        # PROTECTED REGION END #    //  SKAController.test_buildState

    # PROTECTED REGION ID(SKAController.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_versionId_decorators
    def test_versionId(self, device_under_test):
        """Test for versionId."""
        # PROTECTED REGION ID(SKAController.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  SKAController.test_versionId

    # PROTECTED REGION ID(SKAController.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_healthState_decorators
    def test_healthState(self, device_under_test):
        """Test for healthState."""
        # PROTECTED REGION ID(SKAController.test_healthState) ENABLED START #
        assert device_under_test.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SKAController.test_healthState

    # PROTECTED REGION ID(SKAController.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_adminMode_decorators
    def test_adminMode(self, device_under_test):
        """Test for adminMode."""
        # PROTECTED REGION ID(SKAController.test_adminMode) ENABLED START #
        assert device_under_test.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  SKAController.test_adminMode

    # PROTECTED REGION ID(SKAController.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_controlMode_decorators
    def test_controlMode(self, device_under_test):
        """Test for controlMode."""
        # PROTECTED REGION ID(SKAController.test_controlMode) ENABLED START #
        assert device_under_test.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKAController.test_controlMode

    # PROTECTED REGION ID(SKAController.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_simulationMode_decorators
    def test_simulationMode(self, device_under_test):
        """Test for simulationMode."""
        # PROTECTED REGION ID(SKAController.test_simulationMode) ENABLED START #
        assert device_under_test.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKAController.test_simulationMode

    # PROTECTED REGION ID(SKAController.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_testMode_decorators
    def test_testMode(self, device_under_test):
        """Test for testMode."""
        # PROTECTED REGION ID(SKAController.test_testMode) ENABLED START #
        assert device_under_test.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKAController.test_testMode

    # PROTECTED REGION ID(SKAController.test_maxCapabilities_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_maxCapabilities_decorators
    def test_maxCapabilities(self, device_under_test):
        """Test for maxCapabilities."""
        # PROTECTED REGION ID(SKAController.test_maxCapabilities) ENABLED START #
        assert device_under_test.maxCapabilities == ("BAND1:1", "BAND2:1")
        # PROTECTED REGION END #    //  SKAController.test_maxCapabilities

    # PROTECTED REGION ID(SKAController.test_availableCapabilities_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAController.test_availableCapabilities_decorators
    def test_availableCapabilities(self, device_under_test):
        """Test for availableCapabilities."""
        # PROTECTED REGION ID(SKAController.test_availableCapabilities) ENABLED START #
        assert device_under_test.availableCapabilities == ("BAND1:1", "BAND2:1")
        # PROTECTED REGION END #    //  SKAController.test_availableCapabilities
