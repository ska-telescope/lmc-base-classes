#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubelementObsDevice project
#
#
#
#########################################################################################
"""Contain the tests for the CspSubelementObsDevice."""

# Imports
import re
import pytest

from tango import DevState, DevFailed
from tango.test_context import MultiDeviceTestContext

# PROTECTED REGION ID(CspSubelementObsDevice.test_additional_imports) ENABLED START #
from ska.base import SKAObsDevice, CspSubElementObsDevice
from ska.base.commands import ResultCode
from ska.base.faults import CommandError
from ska.base.control_model import (
    ObsState, AdminMode, ControlMode, HealthState, SimulationMode, TestMode
)
# PROTECTED REGION END #    //  CspSubElementObsDevice.test_additional_imports


# Device test case
# PROTECTED REGION ID(CspSubElementObsDevice.test_CspSubelementObsDevice_decorators) ENABLED START #
# PROTECTED REGION END #    // CspSubelementObsDevice.test_CspSubelementObsDevice_decorators
class TestCspSubElementObsDevice(object):
    """Test case for CSP SubElement ObsDevice class."""

    properties = {
        'SkaLevel': '4',
        'LoggingTargetsDefault': '',
        'GroupDefinitions': '',
        'DeviceId': '11',
        }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = CspSubelementObsDevice.numpy = MagicMock()
        # PROTECTED REGION ID(CspSubelementObsDevice.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_mocking

    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(CspSubelementObsDevice.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_properties
        pass

    # PROTECTED REGION ID(CspSubelementObsDevice.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.OFF
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_State

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Status

    # PROTECTED REGION ID(CspSubelementObsDevice.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'CspSubElementObsDevice, lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GetVersionInfo

    # PROTECTED REGION ID(CspSubelementObsDevice.test_configurationProgress_decorators) ENABLED START #
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_buildState

    # PROTECTED REGION ID(CspSubelementObsDevice.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_versionId

    # PROTECTED REGION ID(CspSubelementObsDevice.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_healthState

    # PROTECTED REGION ID(CspSubelementObsDevice.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.MAINTENANCE
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_adminMode

    # PROTECTED REGION ID(CspSubelementObsDevice.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_controlMode

    # PROTECTED REGION ID(CspSubelementObsDevice.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_simulationMode

    # PROTECTED REGION ID(CspSubelementObsDevice.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_testMode) ENABLED START #
        assert tango_context.device.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_testMode

    # PROTECTED REGION ID(CspSubelementObsDevice.test_subarrayMembership_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_subarrayMembership_decorators
    def test_subarrayMembership(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_subarrayMembership) ENABLED START #
        tango_context.device.subarrayMembership = [1,2,5]
        assert set(tango_context.device.subarrayMembership) == {1,2,5}
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_subarrayMembership

    # PROTECTED REGION ID(CspSubelementObsDevice.test_scanID_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_scanID_decorators
    def test_scanID(self, tango_context):
        """Test for scanID"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_scanID) ENABLED START #
        assert tango_context.device.scanID == 0
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_scanID


    # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_decorators
    def test_ConfigureScan(self, tango_context, tango_change_event_helper):
        """Test for ConfigureScan"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan) ENABLED START #

        tango_context.device.On()
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback.assert_calls([ObsState.IDLE,ObsState.CONFIGURING])
        #assert tango_context.device.obsState == ObsState.CONFIGURING
        assert tango_context.device.configurationID == "sbi-mvp01-20200325-00002"
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_statedecorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_statedecorators
    def test_ConfigureScan_when_in_wrong_state(self, tango_context):
        """Test for ConfigureScan when the device is in wrong state"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state) ENABLED START #
        # The device in in OFF/IDLE state, not valid to invoke ConfigureScan.
        with pytest.raises(DevFailed) as df:
            tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        assert "ConfigureScanCommand not allowed" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GoToIdle_decorators
    def test_GoToIdle(self, tango_context):
        """Test for GoToIdle"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle) ENABLED START #

        tango_context.device.On()
        tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        tango_context.device.GoToIdle()
        assert tango_context.device.scanID == 0
        assert tango_context.device.configurationID == ''
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GoToIdle

    # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle_when_in_wrong_statedecorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GoToIdle_when_in_wrong_statedecorators
    def test_GoToIdle_when_in_wrong_state(self, tango_context):
        """Test for GoToIdle when the device is in wrong state"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle_when_in_wrong_state) ENABLED START #
        # The device in in OFF/IDLE state, not valid to invoke GoToIdle.
        with pytest.raises(DevFailed) as df:
            tango_context.device.GoToIdle()
        assert "GoToIdleCommand not allowed" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GoToIdle_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_decorators
    def test_Scan(self, tango_context, tango_change_event_helper):
        """Test for Scan"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan) ENABLED START #
        tango_context.device.On()
        tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        tango_context.device.Scan('1')
        #obs_state_callback.assert_calls([ObsState.READY, ObsState.SCANNING])
        assert tango_context.device.obsState == ObsState.SCANNING
        assert tango_context.device.scanID == 1
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_when_in_wrong_statedecorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_when_in_wrong_statedecorators
    def test_Scan_when_in_wrong_state(self, tango_context):
        """Test for ConfigureScan when the device is in wrong state"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_when_in_wrong_state) ENABLED START #
        # Set the device in ON/IDLE state
        tango_context.device.On()
        with pytest.raises(DevFailed) as df:
            tango_context.device.Scan('32')
        assert "ScanCommand not allowed" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_EndScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_EndScan_decorators
    def test_EndScan(self, tango_context, tango_change_event_helper):
        """Test for EndScan"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_EndScan) ENABLED START #
        tango_context.device.On()
        tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.READY)
        tango_context.device.Scan('1')
        obs_state_callback.assert_call(ObsState.SCANNING)
        tango_context.device.EndScan()
        obs_state_callback.assert_call(ObsState.READY)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_EndScan

    # PROTECTED REGION ID(CspSubelementObsDevice.test_EndScan_when_in_wrong_statedecorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_EndScan_when_in_wrong_statedecorators
    def test_EndScan_when_in_wrong_state(self, tango_context):
        """Test for ConfigureScan when the device is in wrong state"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state) ENABLED START #
        # Set the device in ON/READY state
        tango_context.device.On()
        tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        assert tango_context.device.obsState == ObsState.READY
        with pytest.raises(DevFailed) as df:
            tango_context.device.EndScan()
        assert "EndScanCommand not allowed" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_when_in_wrong_state


def test_multiple_devices_in_same_process():
    devices_info = (
        {"class": CspSubElementObsDevice, "devices": [{"name": "test/se/1"}]},
        {"class": SKAObsDevice, "devices": [{"name": "test/obsdevice/1"}]},
    )

    with MultiDeviceTestContext(devices_info, process=False) as context:
        proxy1 = context.get_device("test/se/1")
        proxy2 = context.get_device("test/obsdevice/1")
        assert proxy1.State() == DevState.OFF
        assert proxy2.State() == DevState.OFF
