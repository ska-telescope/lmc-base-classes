#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKAObsDevice project
#
#
#
#########################################################################################
"""Contain the tests for the SKAObsDevice."""

# Imports
import re
import time

import pytest
from tango import DevState
from tango.test_context import MultiDeviceTestContext

# PROTECTED REGION ID(SKAObsDevice.test_additional_imports) ENABLED START #
from ska_tango_base import SKABaseDevice, SKAObsDevice

from ska_tango_base.testing import (
    ReferenceBaseComponentManager,
)
from ska_tango_base.control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    ObsMode,
    ObsState,
    SimulationMode,
    TestMode,
)

# PROTECTED REGION END #    //  SKAObsDevice.test_additional_imports


# Device test case
# PROTECTED REGION ID(SKAObsDevice.test_SKAObsDevice_decorators) ENABLED START #
# PROTECTED REGION END #    //  SKAObsDevice.test_SKAObsDevice_decorators
class TestSKAObsDevice(object):
    """Test class for tests of the SKAObsDevice device class."""

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Specify device configuration, including properties and memorized attributes.

        This implementation provides a concrete subclass of the device
        class under test, some properties, and a memorized value for
        adminMode.
        """
        return {
            "device": SKAObsDevice,
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
        # PROTECTED REGION ID(SKAObsDevice.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKAObsDevice.test_properties
        pass

    # PROTECTED REGION ID(SKAObsDevice.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_State_decorators
    def test_State(self, device_under_test):
        """Test for State."""
        # PROTECTED REGION ID(SKAObsDevice.test_State) ENABLED START #
        time.sleep(0.2)
        assert device_under_test.state() == DevState.OFF
        # PROTECTED REGION END #    //  SKAObsDevice.test_State

    # PROTECTED REGION ID(SKAObsDevice.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_Status_decorators
    def test_Status(self, device_under_test):
        """Test for Status."""
        # PROTECTED REGION ID(SKAObsDevice.test_Status) ENABLED START #
        time.sleep(0.2)
        assert device_under_test.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKAObsDevice.test_Status

    # PROTECTED REGION ID(SKAObsDevice.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test):
        """Test for GetVersionInfo."""
        # PROTECTED REGION ID(SKAObsDevice.test_GetVersionInfo) ENABLED START #
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])
        # PROTECTED REGION END #    //  SKAObsDevice.test_GetVersionInfo

    # PROTECTED REGION ID(SKAObsDevice.test_obsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_obsState_decorators
    def test_obsState(self, device_under_test, tango_change_event_helper):
        """Test for obsState."""
        # PROTECTED REGION ID(SKAObsDevice.test_obsState) ENABLED START #
        assert device_under_test.obsState == ObsState.EMPTY

        # Check that events are working by subscribing and checking for that
        # initial event
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.EMPTY)
        # PROTECTED REGION END #    //  SKAObsDevice.test_obsState

    # PROTECTED REGION ID(SKAObsDevice.test_obsMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_obsMode_decorators
    def test_obsMode(self, device_under_test):
        """Test for obsMode."""
        # PROTECTED REGION ID(SKAObsDevice.test_obsMode) ENABLED START #
        assert device_under_test.obsMode == ObsMode.IDLE
        # PROTECTED REGION END #    //  SKAObsDevice.test_obsMode

    # PROTECTED REGION ID(SKAObsDevice.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_configurationProgress_decorators
    def test_configurationProgress(self, device_under_test):
        """Test for configurationProgress."""
        # PROTECTED REGION ID(SKAObsDevice.test_configurationProgress) ENABLED START #
        assert device_under_test.configurationProgress == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_configurationProgress

    # PROTECTED REGION ID(SKAObsDevice.test_configurationDelayExpected_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_configurationDelayExpected_decorators
    def test_configurationDelayExpected(self, device_under_test):
        """Test for configurationDelayExpected."""
        # PROTECTED REGION ID(SKAObsDevice.test_configurationDelayExpected) ENABLED START #
        assert device_under_test.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_configurationDelayExpected

    # PROTECTED REGION ID(SKAObsDevice.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_buildState_decorators
    def test_buildState(self, device_under_test):
        """Test for buildState."""
        # PROTECTED REGION ID(SKAObsDevice.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, device_under_test.buildState)) is not None
        # PROTECTED REGION END #    //  SKAObsDevice.test_buildState

    # PROTECTED REGION ID(SKAObsDevice.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_versionId_decorators
    def test_versionId(self, device_under_test):
        """Test for versionId."""
        # PROTECTED REGION ID(SKAObsDevice.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  SKAObsDevice.test_versionId

    # PROTECTED REGION ID(SKAObsDevice.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_healthState_decorators
    def test_healthState(self, device_under_test):
        """Test for healthState."""
        # PROTECTED REGION ID(SKAObsDevice.test_healthState) ENABLED START #
        assert device_under_test.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SKAObsDevice.test_healthState

    # PROTECTED REGION ID(SKAObsDevice.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_adminMode_decorators
    def test_adminMode(self, device_under_test):
        """Test for adminMode."""
        # PROTECTED REGION ID(SKAObsDevice.test_adminMode) ENABLED START #
        assert device_under_test.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  SKAObsDevice.test_adminMode

    # PROTECTED REGION ID(SKAObsDevice.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_controlMode_decorators
    def test_controlMode(self, device_under_test):
        """Test for controlMode."""
        # PROTECTED REGION ID(SKAObsDevice.test_controlMode) ENABLED START #
        assert device_under_test.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKAObsDevice.test_controlMode

    # PROTECTED REGION ID(SKAObsDevice.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_simulationMode_decorators
    def test_simulationMode(self, device_under_test):
        """Test for simulationMode."""
        # PROTECTED REGION ID(SKAObsDevice.test_simulationMode) ENABLED START #
        assert device_under_test.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKAObsDevice.test_simulationMode

    # PROTECTED REGION ID(SKAObsDevice.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_testMode_decorators
    def test_testMode(self, device_under_test):
        """Test for testMode."""
        # PROTECTED REGION ID(SKAObsDevice.test_testMode) ENABLED START #
        assert device_under_test.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKAObsDevice.test_testMode


@pytest.mark.forked
def test_multiple_devices_in_same_process():
    """Test that we can run this device with other devices in a single process."""
    # The order here is important - base class last, so that we can
    # test that the subclass isn't breaking anything.
    devices_info = (
        {"class": SKAObsDevice, "devices": [{"name": "test/obs/1"}]},
        {"class": SKABaseDevice, "devices": [{"name": "test/base/1"}]},
    )

    with MultiDeviceTestContext(devices_info, process=False) as context:
        proxy1 = context.get_device("test/obs/1")
        proxy2 = context.get_device("test/base/1")

        time.sleep(0.15)
        assert proxy1.state() == DevState.DISABLE
        assert proxy2.state() == DevState.DISABLE
