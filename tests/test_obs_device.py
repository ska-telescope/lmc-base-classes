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
import pytest

from tango import DevState
from tango.test_context import MultiDeviceTestContext

# PROTECTED REGION ID(SKAObsDevice.test_additional_imports) ENABLED START #
from ska_tango_base import SKABaseDevice, SKAObsDevice
from ska_tango_base.base import ReferenceBaseComponentManager
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
@pytest.mark.usefixtures("tango_context", "initialize_device")
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
                self.op_state_model, logger=self.logger
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip("Not implemented")
    def test_properties(self, tango_context):
        """Test device properties."""
        # PROTECTED REGION ID(SKAObsDevice.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKAObsDevice.test_properties
        pass

    # PROTECTED REGION ID(SKAObsDevice.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_State_decorators
    def test_State(self, tango_context):
        """Test for State."""
        # PROTECTED REGION ID(SKAObsDevice.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.OFF
        # PROTECTED REGION END #    //  SKAObsDevice.test_State

    # PROTECTED REGION ID(SKAObsDevice.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status."""
        # PROTECTED REGION ID(SKAObsDevice.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKAObsDevice.test_Status

    # PROTECTED REGION ID(SKAObsDevice.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo."""
        # PROTECTED REGION ID(SKAObsDevice.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            f"{tango_context.device.info().dev_class}, ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            "A set of generic base devices for SKA Telescope."
        )
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  SKAObsDevice.test_GetVersionInfo

    # PROTECTED REGION ID(SKAObsDevice.test_obsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_obsState_decorators
    def test_obsState(self, tango_context, tango_change_event_helper):
        """Test for obsState."""
        # PROTECTED REGION ID(SKAObsDevice.test_obsState) ENABLED START #
        assert tango_context.device.obsState == ObsState.EMPTY

        # Check that events are working by subscribing and checking for that
        # initial event
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.EMPTY)
        # PROTECTED REGION END #    //  SKAObsDevice.test_obsState

    # PROTECTED REGION ID(SKAObsDevice.test_obsMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_obsMode_decorators
    def test_obsMode(self, tango_context):
        """Test for obsMode."""
        # PROTECTED REGION ID(SKAObsDevice.test_obsMode) ENABLED START #
        assert tango_context.device.obsMode == ObsMode.IDLE
        # PROTECTED REGION END #    //  SKAObsDevice.test_obsMode

    # PROTECTED REGION ID(SKAObsDevice.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_configurationProgress_decorators
    def test_configurationProgress(self, tango_context):
        """Test for configurationProgress."""
        # PROTECTED REGION ID(SKAObsDevice.test_configurationProgress) ENABLED START #
        assert tango_context.device.configurationProgress == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_configurationProgress

    # PROTECTED REGION ID(SKAObsDevice.test_configurationDelayExpected_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_configurationDelayExpected_decorators
    def test_configurationDelayExpected(self, tango_context):
        """Test for configurationDelayExpected."""
        # PROTECTED REGION ID(SKAObsDevice.test_configurationDelayExpected) ENABLED START #
        assert tango_context.device.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_configurationDelayExpected

    # PROTECTED REGION ID(SKAObsDevice.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState."""
        # PROTECTED REGION ID(SKAObsDevice.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  SKAObsDevice.test_buildState

    # PROTECTED REGION ID(SKAObsDevice.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId."""
        # PROTECTED REGION ID(SKAObsDevice.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  SKAObsDevice.test_versionId

    # PROTECTED REGION ID(SKAObsDevice.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState."""
        # PROTECTED REGION ID(SKAObsDevice.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SKAObsDevice.test_healthState

    # PROTECTED REGION ID(SKAObsDevice.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode."""
        # PROTECTED REGION ID(SKAObsDevice.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  SKAObsDevice.test_adminMode

    # PROTECTED REGION ID(SKAObsDevice.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode."""
        # PROTECTED REGION ID(SKAObsDevice.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKAObsDevice.test_controlMode

    # PROTECTED REGION ID(SKAObsDevice.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode."""
        # PROTECTED REGION ID(SKAObsDevice.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKAObsDevice.test_simulationMode

    # PROTECTED REGION ID(SKAObsDevice.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode."""
        # PROTECTED REGION ID(SKAObsDevice.test_testMode) ENABLED START #
        assert tango_context.device.testMode == TestMode.NONE
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
        assert proxy1.State() == DevState.DISABLE
        assert proxy2.State() == DevState.DISABLE
