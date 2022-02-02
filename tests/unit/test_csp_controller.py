#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubelementController project
#
#
#
#########################################################################################
"""Contain the tests for the CspSubelementController."""

# Imports
import re
import pytest

from tango import DevState, DevFailed
from tango.test_context import MultiDeviceTestContext

# PROTECTED REGION ID(CspSubelementController.test_additional_imports) ENABLED START #
from ska_tango_base import SKAController, CspSubElementController
from ska_tango_base.testing.reference import (
    ReferenceBaseComponentManager,
)

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    SimulationMode,
    TestMode,
)

# PROTECTED REGION END #    //  CspSubElementController.test_additional_imports


# Device test case
# PROTECTED REGION ID(CspSubElementController.test_CspSubelementController_decorators) ENABLED START #
# PROTECTED REGION END #    // CspSubelementController.test_CspSubelementController_decorators
class TestCspSubElementController(object):
    """Test case for CSP SubElement Controller class."""

    @pytest.fixture(scope="class")
    def device_properties(self):
        """
        Fixture that returns properties of the device under test.

        :return: properties of the device under test
        """
        return {"PowerDelayStandbyOn": "1.5", "PowerDelayStandbyOff": "1.0"}

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Specify device configuration, including properties and memorized attributes.

        This implementation provides a concrete subclass of the device
        class under test, some properties, and a memorized value for
        adminMode.

        :param device_properties: fixture that returns device properties
            of the device under test

        :return: specification of how the device under test should be
            configured
        """
        return {
            "device": CspSubElementController,
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
        """
        Test device properties.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  CspSubelementController.test_properties
        pass

    # PROTECTED REGION ID(CspSubelementController.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_State_decorators
    def test_State(self, device_under_test):
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_State) ENABLED START #
        assert device_under_test.state() == DevState.OFF
        # PROTECTED REGION END #    //  CspSubelementController.test_State

    # PROTECTED REGION ID(CspSubelementController.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_Status_decorators
    def test_Status(self, device_under_test):
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_Status) ENABLED START #
        assert device_under_test.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  CspSubelementController.test_Status

    # PROTECTED REGION ID(CspSubelementController.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test):
        """
        Test for GetVersionInfo.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_GetVersionInfo) ENABLED START #
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])
        # PROTECTED REGION END #    //  CspSubelementController.test_GetVersionInfo

    # PROTECTED REGION ID(CspSubelementController.test_configurationProgress_decorators) ENABLED START #
    def test_buildState(self, device_under_test):
        """
        Test for buildState.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, device_under_test.buildState)) is not None
        # PROTECTED REGION END #    //  CspSubelementController.test_buildState

    # PROTECTED REGION ID(CspSubelementController.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_versionId_decorators
    def test_versionId(self, device_under_test):
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  CspSubelementController.test_versionId

    # PROTECTED REGION ID(CspSubelementController.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_healthState_decorators
    def test_healthState(self, device_under_test):
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_healthState) ENABLED START #
        assert device_under_test.healthState == HealthState.UNKNOWN
        # PROTECTED REGION END #    //  CspSubelementController.test_healthState

    # PROTECTED REGION ID(CspSubelementController.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_adminMode_decorators
    def test_adminMode(self, device_under_test):
        """
        Test for adminMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_adminMode) ENABLED START #
        assert device_under_test.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  CspSubelementController.test_adminMode

    # PROTECTED REGION ID(CspSubelementController.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_controlMode_decorators
    def test_controlMode(self, device_under_test):
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_controlMode) ENABLED START #
        assert device_under_test.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  CspSubelementController.test_controlMode

    # PROTECTED REGION ID(CspSubelementController.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_simulationMode_decorators
    def test_simulationMode(self, device_under_test):
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_simulationMode) ENABLED START #
        assert device_under_test.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  CspSubelementController.test_simulationMode

    # PROTECTED REGION ID(CspSubelementController.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_testMode_decorators
    def test_testMode(self, device_under_test):
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_testMode) ENABLED START #
        assert device_under_test.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  CspSubelementController.test_testMode

    # PROTECTED REGION ID(CspSubelementController.test_powerDelayStandbyOn_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_powerDelayStandbyOn_decorators
    def test_powerDelayStandbyOn(self, device_under_test, device_properties):
        """
        Test for powerDelayStandbyOn.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_testMode) ENABLED START #
        assert device_under_test.powerDelayStandbyOn == pytest.approx(
            float(device_properties["PowerDelayStandbyOn"])
        )
        device_under_test.powerDelayStandbyOn = 3
        assert device_under_test.powerDelayStandbyOn == 3
        # PROTECTED REGION END #    //  CspSubelementController.test_powerDelayStandbyOn

    # PROTECTED REGION ID(CspSubelementController.test_powerDelayStandbyOff_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_powerDelayStandbyOff_decorators
    def test_powerDelayStandbyOff(self, device_under_test, device_properties):
        """
        Test for powerDelayStandbyOff.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_testMode) ENABLED START #
        assert device_under_test.powerDelayStandbyOff == pytest.approx(
            float(device_properties["PowerDelayStandbyOff"])
        )
        device_under_test.powerDelayStandbyOff = 2
        assert device_under_test.powerDelayStandbyOff == 2
        # PROTECTED REGION END #    //  CspSubelementController.test_powerDelayStandbyOff

    # PROTECTED REGION ID(CspSubelementController.test_onProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_onProgress_decorators
    def test_onProgress(self, device_under_test):
        """
        Test for onProgress.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_onProgress) ENABLED START #
        assert device_under_test.onProgress == 0
        # PROTECTED REGION END #    //  CspSubelementController.test_onProgress

    # PROTECTED REGION ID(CspSubelementController.test_onMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_onMaximumDuration_decorators
    def test_onMaximumDuration(self, device_under_test):
        """
        Test for onMaximumDuration.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_onMaximumDuration) ENABLED START #
        device_under_test.onMaximumDuration = 5
        assert device_under_test.onMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementController.test_onMaximumDuration

    # PROTECTED REGION ID(CspSubelementController.test_onMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_onMeasuredDuration_decorators
    def test_onMeasuredDuration(self, device_under_test):
        """
        Test for onMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_onMeasuredDuration) ENABLED START #
        assert device_under_test.onMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementController.test_onMeasuredDuration

    # PROTECTED REGION ID(CspSubelementController.test_standbyProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_standbyProgress_decorators
    def test_standbyProgress(self, device_under_test):
        """
        Test for standbyProgress.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_standbyProgress) ENABLED START #
        assert device_under_test.standbyProgress == 0
        # PROTECTED REGION END #    //  CspSubelementController.test_standbyProgress

    # PROTECTED REGION ID(CspSubelementController.test_standbyMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_standbyMaximumDuration_decorators
    def test_standbyMaximumDuration(self, device_under_test):
        """
        Test for standbyMaximumDuration.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_standbyMaximumDuration) ENABLED START #
        device_under_test.standbyMaximumDuration = 5
        assert device_under_test.standbyMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementController.test_standbyMaximumDuration

    # PROTECTED REGION ID(CspSubelementController.test_standbyMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_standbyMeasuredDuration_decorators
    def test_standbyMeasuredDuration(self, device_under_test):
        """
        Test for standbyMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_standbyMeasuredDuration) ENABLED START #
        assert device_under_test.standbyMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementController.test_standbyMeasuredDuration

    # PROTECTED REGION ID(CspSubelementController.test_offProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_offProgress_decorators
    def test_offProgress(self, device_under_test):
        """
        Test for offProgress.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_offProgress) ENABLED START #
        assert device_under_test.offProgress == 0
        # PROTECTED REGION END #    //  CspSubelementController.test_offProgress

    # PROTECTED REGION ID(CspSubelementController.test_offMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_offMaximumDuration_decorators
    def test_offMaximumDuration(self, device_under_test):
        """
        Test for offMaximumDuration.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_offMaximumDuration) ENABLED START #
        device_under_test.offMaximumDuration = 5
        assert device_under_test.offMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementController.test_offMaximumDuration

    # PROTECTED REGION ID(CspSubelementController.test_offMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_offMeasuredDuration_decorators
    def test_offMeasuredDuration(self, device_under_test):
        """
        Test for offMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_offMeasuredDuration) ENABLED START #
        assert device_under_test.offMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementController.test_offMeasuredDuration

    # PROTECTED REGION ID(CspSubelementController.test_loadFirmwareProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_loadFirmwareProgress_decorators
    def test_loadFirmwareProgress(self, device_under_test):
        """
        Test for loadFirmwareProgress.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_loadFirmwareProgress) ENABLED START #
        assert device_under_test.loadFirmwareProgress == 0
        # PROTECTED REGION END #    //  CspSubelementController.test_loadFirmwareProgress

    # PROTECTED REGION ID(CspSubelementController.test_loadFirmwareMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_loadFirmwareMaximumDuration_decorators
    def test_loadFirmwareMaximumDuration(self, device_under_test):
        """
        Test for loadFirmwareMaximumDuration.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_loadFirmwareMaximumDuration) ENABLED START #
        device_under_test.loadFirmwareMaximumDuration = 5
        assert device_under_test.loadFirmwareMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementController.test_loadFirmwareMaximumDuration

    # PROTECTED REGION ID(CspSubelementController.test_loadFirmwareMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_loadFirmwareMeasuredDuration_decorators
    def test_loadFirmwareMeasuredDuration(self, device_under_test):
        """
        Test for loadFirmwareMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_loadFirmwareMeasuredDuration) ENABLED START #
        assert device_under_test.loadFirmwareMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementController.test_loadFirmwareMeasuredDuration

    # PROTECTED REGION ID(CspSubelementController.test_LoadFirmware_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_LoadFirmware_decorators
    def test_LoadFirmware(self, device_under_test):
        """
        Test for LoadFirmware.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_LoadFirmware) ENABLED START #
        # After initialization the device is in the right state (OFF/MAINTENANCE) to
        # execute the command.
        device_under_test.adminMode = AdminMode.MAINTENANCE
        assert device_under_test.LoadFirmware(
            ["file", "test/dev/b", "918698a7fea3"]
        ) == [[ResultCode.OK], ["LoadFirmware command completed OK"]]
        # PROTECTED REGION END #    //  CspSubelementController.test_LoadFirmware

    # PROTECTED REGION ID(CspSubelementController.test_LoadFirmware_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_LoadFirmware_wrong_state_decorators
    def test_LoadFirmware_when_in_wrong_state(self, device_under_test):
        """
        Test for LoadFirmware when the device is in wrong state.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_LoadFirmware_when_in_wrong_state) ENABLED START #
        # Set the device in ON/ONLINE state
        device_under_test.On()
        with pytest.raises(
            DevFailed,
            match="LoadFirmware not allowed when the device is in OFF state",
        ):
            device_under_test.LoadFirmware(["file", "test/dev/b", "918698a7fea3"])
        # PROTECTED REGION END #    //  CspSubelementController.test_LoadFirmware_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementController.test_PowerOnDevices_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_PowerOnDevices_decorators
    def test_power_on_and_off_devices(
        self, device_under_test, tango_change_event_helper
    ):
        """
        Test for PowerOnDevices.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        # PROTECTED REGION ID(CspSubelementController.test_PowerOnDevices) ENABLED START #
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        [[result_code], [_]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        device_state_callback.assert_next_change_event(DevState.ON)
        assert device_under_test.state() == DevState.ON

        # Test power on devices
        [[result_code], [_]] = device_under_test.PowerOnDevices(
            ["test/dev/1", "test/dev/2"]
        )
        assert result_code == ResultCode.OK

        # Test power off devices
        [[result_code], [_]] = device_under_test.PowerOffDevices(
            ["test/dev/1", "test/dev/2"]
        )
        assert result_code == ResultCode.OK

        # PROTECTED REGION END #    //  CspSubelementController.test_PowerOnDevices

    # PROTECTED REGION ID(CspSubelementController.test_PowerOnDevices_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_PowerOnDevices_decorators
    def test_PowerOnDevices_when_in_wrong_state(self, device_under_test):
        """
        Test for PowerOnDevices when the Controller is in wrong state.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_PowerOnDevices_when_in_wrong_state) ENABLED START #
        with pytest.raises(
            DevFailed,
            match="Command PowerOnDevices not allowed when the device is in OFF state",
        ):
            device_under_test.PowerOnDevices(["test/dev/1", "test/dev/2"])
        # PROTECTED REGION END #    //  CspSubelementController.test_PowerOnDevices_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementController.test_PowerOffDevices_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_PowerOffDevices_decorators
    def test_PowerOffDevices_when_in_wrong_state(self, device_under_test):
        """
        Test for PowerOffDevices when the Controller is in wrong state.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_PowerOffDevices_when_in_wrong_state) ENABLED START #
        with pytest.raises(
            DevFailed,
            match="Command PowerOffDevices not allowed when the device is in OFF state",
        ):
            device_under_test.PowerOffDevices(["test/dev/1", "test/dev/2"])
        # PROTECTED REGION END #    //  CspSubelementController.test_PowerOffDevices_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementController.test_ReInitDevices_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_ReInitDevices_decorators
    def test_ReInitDevices(self, device_under_test, tango_change_event_helper):
        """
        Test for ReInitDevices.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        # PROTECTED REGION ID(CspSubelementController.test_ReInitDevices) ENABLED START #
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        [[result_code], [_]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        device_state_callback.assert_next_change_event(DevState.ON)
        assert device_under_test.state() == DevState.ON

        # Test power on devices
        [[result_code], [_]] = device_under_test.PowerOnDevices(
            ["test/dev/1", "test/dev/2"]
        )
        assert device_under_test.ReInitDevices(["test/dev/1", "test/dev/2"]) == [
            [ResultCode.OK],
            ["ReInitDevices command completed OK"],
        ]
        # PROTECTED REGION END #    //  CspSubelementController.test_ReInitDevices

    # PROTECTED REGION ID(CspSubelementController.test_ReInitDevices_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementController.test_ReInitDevices_when_in_wrong_state_decorators
    def test_ReInitDevices_when_in_wrong_state(self, device_under_test):
        """
        Test for ReInitDevices whe the device is in a wrong state.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementController.test_ReInitDevices_when_in_wrong_state) ENABLED START #
        # put it in ON state
        with pytest.raises(
            DevFailed,
            match="ReInitDevices not allowed when the device is in OFF state",
        ):
            device_under_test.ReInitDevices(["test/dev/1", "test/dev/2"])
        # PROTECTED REGION END #    //  CspSubelementController.test_ReInitDevices_when_in_wrong_state


@pytest.mark.forked
def test_multiple_devices_in_same_process(mocker):
    """Test that we can run this device with other devices in a single process."""
    # Patch abstract method/s; it doesn't matter what we patch them with, so long as
    # they don't raise NotImplementedError.
    mocker.patch.object(SKAController, "create_component_manager")
    mocker.patch.object(CspSubElementController, "create_component_manager")

    # The order here is important - base class last, so that we can
    # test that the subclass isn't breaking anything.
    devices_info = (
        {"class": CspSubElementController, "devices": [{"name": "test/se/1"}]},
        {"class": SKAController, "devices": [{"name": "test/control/1"}]},
    )

    with MultiDeviceTestContext(devices_info, process=False) as context:
        proxy1 = context.get_device("test/se/1")
        proxy2 = context.get_device("test/control/1")
        assert proxy1.state() == DevState.DISABLE
        assert proxy2.state() == DevState.DISABLE
