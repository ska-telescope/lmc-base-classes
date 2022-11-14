# type: ignore
#######################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubelementController project
#
#
#
#######################################################################################
"""Contain the tests for the CspSubelementController."""

import re

import pytest
import tango
from ska_control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    SimulationMode,
    TestMode,
)
from tango.test_context import MultiDeviceTestContext

from ska_tango_base import CspSubElementController, SKAController
from ska_tango_base.commands import ResultCode
from ska_tango_base.testing.reference import ReferenceBaseComponentManager


class TestCspSubElementController:  # pylint: disable=too-many-public-methods
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

    def test_State(self, device_under_test):
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.state() == tango.DevState.OFF

    def test_Status(self, device_under_test):
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.Status() == "The device is in OFF state."

    def test_GetVersionInfo(self, device_under_test):
        """
        Test for GetVersionInfo.

        :param device_under_test: a proxy to the device under test
        """
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])

    def test_buildState(self, device_under_test):
        """
        Test for buildState.

        :param device_under_test: a proxy to the device under test
        """
        build_pattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(build_pattern, device_under_test.buildState)) is not None

    def test_versionId(self, device_under_test):
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        version_id_pattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(version_id_pattern, device_under_test.versionId)) is not None

    def test_healthState(self, device_under_test):
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.healthState == HealthState.UNKNOWN

    def test_adminMode(self, device_under_test):
        """
        Test for adminMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.adminMode == AdminMode.ONLINE

    def test_controlMode(self, device_under_test):
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.controlMode == ControlMode.REMOTE

    def test_simulationMode(self, device_under_test):
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.simulationMode == SimulationMode.FALSE

    def test_testMode(self, device_under_test):
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.testMode == TestMode.NONE

    def test_powerDelayStandbyOn(self, device_under_test, device_properties):
        """
        Test for powerDelayStandbyOn.

        :param device_under_test: a proxy to the device under test
        :param device_properties: fixture that returns device properties
            of the device under test
        """
        assert device_under_test.powerDelayStandbyOn == pytest.approx(
            float(device_properties["PowerDelayStandbyOn"])
        )
        device_under_test.powerDelayStandbyOn = 3
        assert device_under_test.powerDelayStandbyOn == 3

    def test_powerDelayStandbyOff(self, device_under_test, device_properties):
        """
        Test for powerDelayStandbyOff.

        :param device_under_test: a proxy to the device under test
        :param device_properties: fixture that returns device properties
            of the device under test
        """
        assert device_under_test.powerDelayStandbyOff == pytest.approx(
            float(device_properties["PowerDelayStandbyOff"])
        )
        device_under_test.powerDelayStandbyOff = 2
        assert device_under_test.powerDelayStandbyOff == 2

    def test_onProgress(self, device_under_test):
        """
        Test for onProgress.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.onProgress == 0

    def test_onMaximumDuration(self, device_under_test):
        """
        Test for onMaximumDuration.

        :param device_under_test: a proxy to the device under test
        """
        device_under_test.onMaximumDuration = 5
        assert device_under_test.onMaximumDuration == 5

    def test_onMeasuredDuration(self, device_under_test):
        """
        Test for onMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.onMeasuredDuration == 0

    def test_standbyProgress(self, device_under_test):
        """
        Test for standbyProgress.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.standbyProgress == 0

    def test_standbyMaximumDuration(self, device_under_test):
        """
        Test for standbyMaximumDuration.

        :param device_under_test: a proxy to the device under test
        """
        device_under_test.standbyMaximumDuration = 5
        assert device_under_test.standbyMaximumDuration == 5

    def test_standbyMeasuredDuration(self, device_under_test):
        """
        Test for standbyMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.standbyMeasuredDuration == 0

    def test_offProgress(self, device_under_test):
        """
        Test for offProgress.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.offProgress == 0

    def test_offMaximumDuration(self, device_under_test):
        """
        Test for offMaximumDuration.

        :param device_under_test: a proxy to the device under test
        """
        device_under_test.offMaximumDuration = 5
        assert device_under_test.offMaximumDuration == 5

    def test_offMeasuredDuration(self, device_under_test):
        """
        Test for offMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.offMeasuredDuration == 0

    def test_loadFirmwareProgress(self, device_under_test):
        """
        Test for loadFirmwareProgress.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.loadFirmwareProgress == 0

    def test_loadFirmwareMaximumDuration(self, device_under_test):
        """
        Test for loadFirmwareMaximumDuration.

        :param device_under_test: a proxy to the device under test
        """
        device_under_test.loadFirmwareMaximumDuration = 5
        assert device_under_test.loadFirmwareMaximumDuration == 5

    def test_loadFirmwareMeasuredDuration(self, device_under_test):
        """
        Test for loadFirmwareMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.loadFirmwareMeasuredDuration == 0

    def test_LoadFirmware(self, device_under_test):
        """
        Test for LoadFirmware.

        :param device_under_test: a proxy to the device under test
        """
        # After initialization the device is in the right state (OFF/MAINTENANCE) to
        # execute the command.
        device_under_test.adminMode = AdminMode.MAINTENANCE
        assert device_under_test.LoadFirmware(
            ["file", "test/dev/b", "918698a7fea3"]
        ) == [[ResultCode.OK], ["LoadFirmware command completed OK"]]

    def test_LoadFirmware_when_in_wrong_state(self, device_under_test):
        """
        Test for LoadFirmware when the device is in wrong state.

        :param device_under_test: a proxy to the device under test
        """
        # Set the device in ON/ONLINE state
        device_under_test.On()
        with pytest.raises(
            tango.DevFailed,
            match="LoadFirmware not allowed when the device is in OFF state",
        ):
            device_under_test.LoadFirmware(["file", "test/dev/b", "918698a7fea3"])

    def test_power_on_and_off_devices(self, device_under_test, change_event_callbacks):
        """
        Test for PowerOnDevices.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        assert device_under_test.state() == tango.DevState.OFF

        device_under_test.subscribe_event(
            "state",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["state"],
        )
        change_event_callbacks.assert_change_event("state", tango.DevState.OFF)

        [[result_code], [_]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("state", tango.DevState.ON)
        assert device_under_test.state() == tango.DevState.ON

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

    def test_PowerOnDevices_when_in_wrong_state(self, device_under_test):
        """
        Test for PowerOnDevices when the Controller is in wrong state.

        :param device_under_test: a proxy to the device under test
        """
        with pytest.raises(
            tango.DevFailed,
            match="Command PowerOnDevices not allowed when the device is in OFF state",
        ):
            device_under_test.PowerOnDevices(["test/dev/1", "test/dev/2"])

    def test_PowerOffDevices_when_in_wrong_state(self, device_under_test):
        """
        Test for PowerOffDevices when the Controller is in wrong state.

        :param device_under_test: a proxy to the device under test
        """
        with pytest.raises(
            tango.DevFailed,
            match="Command PowerOffDevices not allowed when the device is in OFF state",
        ):
            device_under_test.PowerOffDevices(["test/dev/1", "test/dev/2"])

    def test_ReInitDevices(self, device_under_test, change_event_callbacks):
        """
        Test for ReInitDevices.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        assert device_under_test.state() == tango.DevState.OFF

        device_under_test.subscribe_event(
            "state",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["state"],
        )
        change_event_callbacks.assert_change_event("state", tango.DevState.OFF)

        [[result_code], [_]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("state", tango.DevState.ON)
        assert device_under_test.state() == tango.DevState.ON

        # Test power on devices
        [[result_code], [_]] = device_under_test.PowerOnDevices(
            ["test/dev/1", "test/dev/2"]
        )
        assert device_under_test.ReInitDevices(["test/dev/1", "test/dev/2"]) == [
            [ResultCode.OK],
            ["ReInitDevices command completed OK"],
        ]

    def test_ReInitDevices_when_in_wrong_state(self, device_under_test):
        """
        Test for ReInitDevices whe the device is in a wrong state.

        :param device_under_test: a proxy to the device under test
        """
        # put it in ON state
        with pytest.raises(
            tango.DevFailed,
            match="ReInitDevices not allowed when the device is in OFF state",
        ):
            device_under_test.ReInitDevices(["test/dev/1", "test/dev/2"])


@pytest.mark.forked
def test_multiple_devices_in_same_process(mocker):
    """
    Test that we can run this device with other devices in a single process.

    :param mocker: pytest fixture that wraps :py:mod:`unittest.mock`.
    """
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
        assert proxy1.state() == tango.DevState.DISABLE
        assert proxy2.state() == tango.DevState.DISABLE
