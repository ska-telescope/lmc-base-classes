#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubelementMaster project
#
#
#
#########################################################################################
"""Contain the tests for the CspSubelementMaster."""

# Imports
import re
import pytest

from tango import DevState, DevFailed
from tango.test_context import MultiDeviceTestContext

# PROTECTED REGION ID(CspSubelementMaster.test_additional_imports) ENABLED START #
from ska_tango_base import SKAMaster, CspSubElementMaster
from ska_tango_base.commands import ResultCode
from ska_tango_base.faults import CommandError
from ska_tango_base.control_model import (
    AdminMode, ControlMode, HealthState, SimulationMode, TestMode
)
# PROTECTED REGION END #    //  CspSubElementMaster.test_additional_imports


# Device test case
# PROTECTED REGION ID(CspSubElementMaster.test_CspSubelementMaster_decorators) ENABLED START #
# PROTECTED REGION END #    // CspSubelementMaster.test_CspSubelementMaster_decorators
class TestCspSubElementMaster(object):
    """Test case for CSP SubElement Master class."""

    properties = {
        'SkaLevel': '4',
        'LoggingTargetsDefault': '',
        'GroupDefinitions': '',
        'PowerDelayStandbyOn': 1.5,
        'PowerDelayStandbyOff': 1.0,
    }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = CspSubelementMaster.numpy = MagicMock()
        # PROTECTED REGION ID(CspSubelementMaster.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  CspSubelementMaster.test_mocking

    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(CspSubelementMaster.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  CspSubelementMaster.test_properties
        pass

    # PROTECTED REGION ID(CspSubelementMaster.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(CspSubelementMaster.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.OFF
        # PROTECTED REGION END #    //  CspSubelementMaster.test_State

    # PROTECTED REGION ID(CspSubelementMaster.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(CspSubelementMaster.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  CspSubelementMaster.test_Status

    # PROTECTED REGION ID(CspSubelementMaster.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(CspSubelementMaster.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'CspSubElementMaster, ska_tango_base, [0-9]+.[0-9]+.[0-9]+, '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  CspSubelementMaster.test_GetVersionInfo

    # PROTECTED REGION ID(CspSubelementMaster.test_configurationProgress_decorators) ENABLED START #
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(CspSubelementMaster.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'ska_tango_base, [0-9]+.[0-9]+.[0-9]+, '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  CspSubelementMaster.test_buildState

    # PROTECTED REGION ID(CspSubelementMaster.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(CspSubelementMaster.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9]+.[0-9]+.[0-9]+')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  CspSubelementMaster.test_versionId

    # PROTECTED REGION ID(CspSubelementMaster.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(CspSubelementMaster.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  CspSubelementMaster.test_healthState

    # PROTECTED REGION ID(CspSubelementMaster.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(CspSubelementMaster.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.MAINTENANCE
        # PROTECTED REGION END #    //  CspSubelementMaster.test_adminMode

    # PROTECTED REGION ID(CspSubelementMaster.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(CspSubelementMaster.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  CspSubelementMaster.test_controlMode

    # PROTECTED REGION ID(CspSubelementMaster.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(CspSubelementMaster.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  CspSubelementMaster.test_simulationMode

    # PROTECTED REGION ID(CspSubelementMaster.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(CspSubelementMaster.test_testMode) ENABLED START #
        assert tango_context.device.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  CspSubelementMaster.test_testMode

    # PROTECTED REGION ID(CspSubelementMaster.test_powerDelayStandbyOn_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_powerDelayStandbyOn_decorators
    def test_powerDelayStandbyOn(self, tango_context):
        """Test for powerDelayStandbyOn"""
        # PROTECTED REGION ID(CspSubelementMaster.test_testMode) ENABLED START #
        assert tango_context.device.powerDelayStandbyOn == self.properties['PowerDelayStandbyOn']
        tango_context.device.powerDelayStandbyOn = 3
        assert tango_context.device.powerDelayStandbyOn == 3
        # PROTECTED REGION END #    //  CspSubelementMaster.test_powerDelayStandbyOn

    # PROTECTED REGION ID(CspSubelementMaster.test_powerDelayStandbyOff_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_powerDelayStandbyOff_decorators
    def test_powerDelayStandbyOff(self, tango_context):
        """Test for powerDelayStandbyOff"""
        # PROTECTED REGION ID(CspSubelementMaster.test_testMode) ENABLED START #
        assert tango_context.device.powerDelayStandbyOff == self.properties['PowerDelayStandbyOff']
        tango_context.device.powerDelayStandbyOff = 2
        assert tango_context.device.powerDelayStandbyOff == 2
        # PROTECTED REGION END #    //  CspSubelementMaster.test_powerDelayStandbyOff

    # PROTECTED REGION ID(CspSubelementMaster.test_onProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_onProgress_decorators
    def test_onProgress(self, tango_context):
        """Test for onProgress"""
        # PROTECTED REGION ID(CspSubelementMaster.test_onProgress) ENABLED START #
        assert tango_context.device.onProgress == 0
        # PROTECTED REGION END #    //  CspSubelementMaster.test_onProgress

    # PROTECTED REGION ID(CspSubelementMaster.test_onMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_onMaximumDuration_decorators
    def test_onMaximumDuration(self, tango_context):
        """Test for onMaximumDuration"""
        # PROTECTED REGION ID(CspSubelementMaster.test_onMaximumDuration) ENABLED START #
        tango_context.device.onMaximumDuration = 5
        assert tango_context.device.onMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementMaster.test_onMaximumDuration

    # PROTECTED REGION ID(CspSubelementMaster.test_onMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_onMeasuredDuration_decorators
    def test_onMeasuredDuration(self, tango_context):
        """Test for onMeasuredDuration"""
        # PROTECTED REGION ID(CspSubelementMaster.test_onMeasuredDuration) ENABLED START #
        assert tango_context.device.onMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementMaster.test_onMeasuredDuration

    # PROTECTED REGION ID(CspSubelementMaster.test_standbyProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_standbyProgress_decorators
    def test_standbyProgress(self, tango_context):
        """Test for standbyProgress"""
        # PROTECTED REGION ID(CspSubelementMaster.test_standbyProgress) ENABLED START #
        assert tango_context.device.standbyProgress == 0
        # PROTECTED REGION END #    //  CspSubelementMaster.test_standbyProgress

    # PROTECTED REGION ID(CspSubelementMaster.test_standbyMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_standbyMaximumDuration_decorators
    def test_standbyMaximumDuration(self, tango_context):
        """Test for standbyMaximumDuration"""
        # PROTECTED REGION ID(CspSubelementMaster.test_standbyMaximumDuration) ENABLED START #
        tango_context.device.standbyMaximumDuration = 5
        assert tango_context.device.standbyMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementMaster.test_standbyMaximumDuration

    # PROTECTED REGION ID(CspSubelementMaster.test_standbyMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_standbyMeasuredDuration_decorators
    def test_standbyMeasuredDuration(self, tango_context):
        """Test for standbyMeasuredDuration"""
        # PROTECTED REGION ID(CspSubelementMaster.test_standbyMeasuredDuration) ENABLED START #
        assert tango_context.device.standbyMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementMaster.test_standbyMeasuredDuration

    # PROTECTED REGION ID(CspSubelementMaster.test_offProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_offProgress_decorators
    def test_offProgress(self, tango_context):
        """Test for offProgress"""
        # PROTECTED REGION ID(CspSubelementMaster.test_offProgress) ENABLED START #
        assert tango_context.device.offProgress == 0
        # PROTECTED REGION END #    //  CspSubelementMaster.test_offProgress

    # PROTECTED REGION ID(CspSubelementMaster.test_offMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_offMaximumDuration_decorators
    def test_offMaximumDuration(self, tango_context):
        """Test for offMaximumDuration"""
        # PROTECTED REGION ID(CspSubelementMaster.test_offMaximumDuration) ENABLED START #
        tango_context.device.offMaximumDuration = 5
        assert tango_context.device.offMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementMaster.test_offMaximumDuration

    # PROTECTED REGION ID(CspSubelementMaster.test_offMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_offMeasuredDuration_decorators
    def test_offMeasuredDuration(self, tango_context):
        """Test for offMeasuredDuration"""
        # PROTECTED REGION ID(CspSubelementMaster.test_offMeasuredDuration) ENABLED START #
        assert tango_context.device.offMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementMaster.test_offMeasuredDuration

    # PROTECTED REGION ID(CspSubelementMaster.test_loadFirmwareProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_loadFirmwareProgress_decorators
    def test_loadFirmwareProgress(self, tango_context):
        """Test for loadFirmwareProgress"""
        # PROTECTED REGION ID(CspSubelementMaster.test_loadFirmwareProgress) ENABLED START #
        assert tango_context.device.loadFirmwareProgress == 0
        # PROTECTED REGION END #    //  CspSubelementMaster.test_loadFirmwareProgress

    # PROTECTED REGION ID(CspSubelementMaster.test_loadFirmwareMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_loadFirmwareMaximumDuration_decorators
    def test_loadFirmwareMaximumDuration(self, tango_context):
        """Test for loadFirmwareMaximumDuration"""
        # PROTECTED REGION ID(CspSubelementMaster.test_loadFirmwareMaximumDuration) ENABLED START #
        tango_context.device.loadFirmwareMaximumDuration = 5
        assert tango_context.device.loadFirmwareMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementMaster.test_loadFirmwareMaximumDuration

    # PROTECTED REGION ID(CspSubelementMaster.test_loadFirmwareMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_loadFirmwareMeasuredDuration_decorators
    def test_loadFirmwareMeasuredDuration(self, tango_context):
        """Test for loadFirmwareMeasuredDuration"""
        # PROTECTED REGION ID(CspSubelementMaster.test_loadFirmwareMeasuredDuration) ENABLED START #
        assert tango_context.device.loadFirmwareMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementMaster.test_loadFirmwareMeasuredDuration

    # PROTECTED REGION ID(CspSubelementMaster.test_LoadFirmware_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_LoadFirmware_decorators
    def test_LoadFirmware(self, tango_context):
        """Test for LoadFirmware"""
        # PROTECTED REGION ID(CspSubelementMaster.test_LoadFirmware) ENABLED START #
        # After initialization the device is in the right state (OFF/MAINTENANCE) to
        # execute the command.
        assert tango_context.device.LoadFirmware(['file', 'test/dev/b', '918698a7fea3']) == [
            [ResultCode.OK], ["LoadFirmware command completed OK"]
        ]
        # PROTECTED REGION END #    //  CspSubelementMaster.test_LoadFirmware

    # PROTECTED REGION ID(CspSubelementMaster.test_LoadFirmware_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_LoadFirmware_wrong_state_decorators
    def test_LoadFirmware_when_in_wrong_state(self, tango_context):
        """Test for LoadFirmware when the device is in wrong state"""
        # PROTECTED REGION ID(CspSubelementMaster.test_LoadFirmware_when_in_wrong_state) ENABLED START #
        # Set the device in ON/ONLINE state
        tango_context.device.Disable()
        tango_context.device.adminMode = AdminMode.ONLINE
        tango_context.device.Off()
        tango_context.device.On()
        with pytest.raises(DevFailed) as df:
            tango_context.device.LoadFirmware(['file', 'test/dev/b', '918698a7fea3'])
        assert "LoadFirmwareCommand not allowed" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementMaster.test_LoadFirmware_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementMaster.test_PowerOnDevices_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_PowerOnDevices_decorators
    def test_PowerOnDevices(self, tango_context):
        """Test for PowerOnDevices"""
        # PROTECTED REGION ID(CspSubelementMaster.test_PowerOnDevices) ENABLED START #
        # put it in ON state
        tango_context.device.On()
        assert tango_context.device.PowerOnDevices(['test/dev/1', 'test/dev/2']) == [
            [ResultCode.OK], ["PowerOnDevices command completed OK"]
        ]
        # PROTECTED REGION END #    //  CspSubelementMaster.test_PowerOnDevices

    # PROTECTED REGION ID(CspSubelementMaster.test_PowerOnDevices_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_PowerOnDevices_decorators
    def test_PowerOnDevices_when_in_wrong_state(self, tango_context):
        """Test for PowerOnDevices when the Master is in wrong state"""
        # PROTECTED REGION ID(CspSubelementMaster.test_PowerOnDevices_when_in_wrong_state) ENABLED START #
        with pytest.raises(DevFailed) as df:
            tango_context.device.PowerOnDevices(['test/dev/1', 'test/dev/2'])
        assert "PowerOnDevicesCommand not allowed" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementMaster.test_PowerOnDevices_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementMaster.test_PowerOffDevices_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_PowerOffDevices_decorators
    def test_PowerOffDevices(self, tango_context):
        """Test for PowerOffDEvices"""
        # PROTECTED REGION ID(CspSubelementMaster.test_PowerOffDevices) ENABLED START #
        # put it in ON state
        tango_context.device.On()
        assert tango_context.device.PowerOffDevices(['test/dev/1', 'test/dev/2']) == [
            [ResultCode.OK], ["PowerOffDevices command completed OK"]
        ]
        # PROTECTED REGION END #    //  CspSubelementMaster.test_PowerOffDevices

    # PROTECTED REGION ID(CspSubelementMaster.test_PowerOffDevices_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_PowerOffDevices_decorators
    def test_PowerOffDevices_when_in_wrong_state(self, tango_context):
        """Test for PowerOffDevices when the Master is in wrong state"""
        # PROTECTED REGION ID(CspSubelementMaster.test_PowerOffDevices_when_in_wrong_state) ENABLED START #
        with pytest.raises(DevFailed) as df:
            tango_context.device.PowerOffDevices(['test/dev/1', 'test/dev/2'])
        assert "PowerOffDevicesCommand not allowed" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementMaster.test_PowerOffDevices_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementMaster.test_ReInitDevices_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_ReInitDevices_decorators
    def test_ReInitDevices(self, tango_context):
        """Test for ReInitDevices"""
        # PROTECTED REGION ID(CspSubelementMaster.test_ReInitDevices) ENABLED START #
        # put it in ON state
        tango_context.device.On()
        assert tango_context.device.ReInitDevices(['test/dev/1', 'test/dev/2']) == [
            [ResultCode.OK], ["ReInitDevices command completed OK"]
        ]
        # PROTECTED REGION END #    //  CspSubelementMaster.test_ReInitDevices

    # PROTECTED REGION ID(CspSubelementMaster.test_ReInitDevices_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementMaster.test_ReInitDevices_when_in_wrong_state_decorators
    def test_ReInitDevices_when_in_wrong_state(self, tango_context):
        """Test for ReInitDevices whe the device is in a wrong state"""
        # PROTECTED REGION ID(CspSubelementMaster.test_ReInitDevices_when_in_wrong_state) ENABLED START #
        # put it in ON state
        with pytest.raises(DevFailed) as df:
            tango_context.device.ReInitDevices(['test/dev/1', 'test/dev/2'])
        assert "ReInitDevicesCommand not allowed" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementMaster.test_ReInitDevices_when_in_wrong_state


def test_multiple_devices_in_same_process():

    # The order here is important - base class last, so that we can
    # test that the subclass isn't breaking anything.
    devices_info = (
        {"class": CspSubElementMaster, "devices": [{"name": "test/se/1"}]},
        {"class": SKAMaster, "devices": [{"name": "test/master/1"}]},
    )

    with MultiDeviceTestContext(devices_info, process=False) as context:
        proxy1 = context.get_device("test/se/1")
        proxy2 = context.get_device("test/master/1")
        assert proxy1.State() == DevState.OFF
        assert proxy2.State() == DevState.OFF
