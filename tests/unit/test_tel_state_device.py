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
from ska_tango_base import SKATelState

from ska_tango_base.testing.reference import (
    ReferenceBaseComponentManager,
)
from ska_tango_base.control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    SimulationMode,
    TestMode,
)

# PROTECTED REGION END #    //  SKATelState.test_additional_imports


# PROTECTED REGION ID(SKATelState.test_SKATelState_decorators) ENABLED START #
# PROTECTED REGION END #    //  SKATelState.test_SKATelState_decorators
class TestSKATelState(object):
    """Test class for tests of the SKATelState device class."""

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Specification of the device under test.

        The specification includes the device's properties and memorized
        attributes.
        """
        return {
            "device": SKATelState,
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
        # PROTECTED REGION ID(SKATelState.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKATelState.test_properties
        pass

    # PROTECTED REGION ID(SKATelState.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_State_decorators
    def test_State(self, device_under_test):
        """Test for State."""
        # PROTECTED REGION ID(SKATelState.test_State) ENABLED START #
        assert device_under_test.state() == DevState.OFF
        # PROTECTED REGION END #    //  SKATelState.test_State

    # PROTECTED REGION ID(SKATelState.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_Status_decorators
    def test_Status(self, device_under_test):
        """Test for Status."""
        # PROTECTED REGION ID(SKATelState.test_Status) ENABLED START #
        assert device_under_test.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKATelState.test_Status

    # PROTECTED REGION ID(SKATelState.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test):
        """Test for GetVersionInfo."""
        # PROTECTED REGION ID(SKATelState.test_GetVersionInfo) ENABLED START #
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])
        # PROTECTED REGION END #    //  SKATelState.test_GetVersionInfo

    # PROTECTED REGION ID(SKATelState.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_buildState_decorators
    def test_buildState(self, device_under_test):
        """Test for buildState."""
        # PROTECTED REGION ID(SKATelState.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, device_under_test.buildState)) is not None
        # PROTECTED REGION END #    //  SKATelState.test_buildState

    # PROTECTED REGION ID(SKATelState.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_versionId_decorators
    def test_versionId(self, device_under_test):
        """Test for versionId."""
        # PROTECTED REGION ID(SKATelState.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  SKATelState.test_versionId

    # PROTECTED REGION ID(SKATelState.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_healthState_decorators
    def test_healthState(self, device_under_test):
        """Test for healthState."""
        # PROTECTED REGION ID(SKATelState.test_healthState) ENABLED START #
        assert device_under_test.healthState == HealthState.UNKNOWN
        # PROTECTED REGION END #    //  SKATelState.test_healthState

    # PROTECTED REGION ID(SKATelState.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_adminMode_decorators
    def test_adminMode(self, device_under_test):
        """Test for adminMode."""
        # PROTECTED REGION ID(SKATelState.test_adminMode) ENABLED START #
        assert device_under_test.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  SKATelState.test_adminMode

    # PROTECTED REGION ID(SKATelState.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_controlMode_decorators
    def test_controlMode(self, device_under_test):
        """Test for controlMode."""
        # PROTECTED REGION ID(SKATelState.test_controlMode) ENABLED START #
        assert device_under_test.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKATelState.test_controlMode

    # PROTECTED REGION ID(SKATelState.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_simulationMode_decorators
    def test_simulationMode(self, device_under_test):
        """Test for simulationMode."""
        # PROTECTED REGION ID(SKATelState.test_simulationMode) ENABLED START #
        assert device_under_test.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKATelState.test_simulationMode

    # PROTECTED REGION ID(SKATelState.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.test_testMode_decorators
    def test_testMode(self, device_under_test):
        """Test for testMode."""
        # PROTECTED REGION ID(SKATelState.test_testMode) ENABLED START #
        assert device_under_test.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKATelState.test_testMode
