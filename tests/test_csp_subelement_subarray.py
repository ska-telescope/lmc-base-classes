#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubelementSubarray project
#
#
#
#########################################################################################
"""Contain the tests for the CspSubelementSubarray and the State model implemented by
   such device.
"""
# Imports
import logging
import re
import pytest
import json

from tango import DevState, DevFailed
from tango.test_context import MultiDeviceTestContext

# PROTECTED REGION ID(CspSubelementSubarray.test_additional_imports) ENABLED START #
from ska.base import SKASubarray, CspSubElementSubarray
from ska.base.commands import ResultCode
from ska.base.faults import StateModelError
from ska.base.control_model import (
    ObsState, AdminMode, ControlMode, HealthState, SimulationMode, TestMode
)
from .conftest import load_state_machine_spec, StateMachineTester
# PROTECTED REGION END #    //  CspSubElementSubarray.test_additional_imports


# Device test case
# PROTECTED REGION ID(CspSubElementSubarray.test_CspSubelementSubarray_decorators) ENABLED START #
# PROTECTED REGION END #    // CspSubelementSubarray.test_CspSubelementSubarray_decorators

class TestCspSubElementSubarray(object):
    """Test case for CSP SubElement Subarray class."""

    properties = {
        'SkaLevel': '4',
        'LoggingTargetsDefault': '',
        'GroupDefinitions': '',
        }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = CspSubelementSubarray.numpy = MagicMock()
        # PROTECTED REGION ID(CspSubelementSubarray.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_mocking

    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(CspSubelementSubarray.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_properties
        pass

    # PROTECTED REGION ID(CspSubelementSubarray.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.OFF
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_State

    # PROTECTED REGION ID(CspSubelementSubarray.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_Status

    # PROTECTED REGION ID(CspSubelementSubarray.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'CspSubElementSubarray, lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_GetVersionInfo

    # PROTECTED REGION ID(CspSubelementSubarray.test_configurationProgress_decorators) ENABLED START #
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_buildState

    # PROTECTED REGION ID(CspSubelementSubarray.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_versionId

    # PROTECTED REGION ID(CspSubelementSubarray.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_healthState

    # PROTECTED REGION ID(CspSubelementSubarray.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.MAINTENANCE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_adminMode

    # PROTECTED REGION ID(CspSubelementSubarray.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_controlMode

    # PROTECTED REGION ID(CspSubelementSubarray.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_simulationMode

    # PROTECTED REGION ID(CspSubelementSubarray.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_testMode) ENABLED START #
        assert tango_context.device.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_testMode

    # PROTECTED REGION ID(CspSubelementSubarray.test_scanID_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_scanID_decorators
    def test_scanID(self, tango_context):
        """Test for scanID"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_scanID) ENABLED START #
        assert tango_context.device.scanID == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_scanID

    # PROTECTED REGION ID(CspSubelementSubarray.test_sdpDestinationAddresses_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_sdpDestinationAddresses_decorators
    def test_sdpDestinationAddresses(self, tango_context):
        """Test for sdpDestinationAddresses"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_sdpDestinationAddresses) ENABLED START #
        addresses_dict = {'outputHost': [], 'outputMac': [], 'outputPort': []}
        tango_context.device.sdpDestinationAddresses = json.dumps(addresses_dict)
        assert tango_context.device.sdpDestinationAddresses == json.dumps(addresses_dict)
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_sdpDestinationAddresses

    # PROTECTED REGION ID(CspSubelementSubarray.test_sdpLinkActive_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_sdpLinkActive_decorators
    def test_sdpLinkActivity(self, tango_context):
        """Test for sdpLinkActive """
        # PROTECTED REGION ID(CspSubelementSubarray.test_sdpLinkActive) ENABLED START #
        expected = tango_context.device.sdpLinkActive
        if expected is not None:
            n_links = len(expected)
            actual  = [ False for i in range(0, n_links)]
            assert all([a == b for a, b in zip(actual, expected)])
        else:
            assert expected is None
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_sdpLinkActive

    # PROTECTED REGION ID(CspSubelementSubarray.test_outputDataRateToSdp_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_outputDataRateToSdp_decorators
    def test_outputDataRateToSdp(self, tango_context):
        """Test for outputDataRateToSdp """
        # PROTECTED REGION ID(CspSubelementSubarray.test_outputDataRateToSdp) ENABLED START #
        assert tango_context.device.outputDataRateToSdp == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_outputDataRateToSdp

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_decorators
    def test_ConfigureScan(self, tango_context, tango_change_event_helper):
        """Test for ConfigureScan"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan) ENABLED START #
        tango_context.device.On()
        tango_context.device.AssignResources('{"example": [1,2,3]}')
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        scan_configuration = '{"id":"sbi-mvp01-20200325-00002"}'
        tango_context.device.ConfigureScan(scan_configuration)
        obs_state_callback.assert_calls([ObsState.IDLE,ObsState.CONFIGURING])
        assert tango_context.device.configurationID == "sbi-mvp01-20200325-00002"
        assert tango_context.device.lastScanConfiguration == scan_configuration
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan

    # PROTECTED REGION ID(CspSubelementSubarray.test_Configure_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_Configure_decorators
    def test_Configure(self, tango_context, tango_change_event_helper):
        """Test for ConfigureScan"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_Configure) ENABLED START #
        tango_context.device.On()
        tango_context.device.AssignResources('{"example": [1,2,3]}')
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        scan_configuration = '{"id":"sbi-mvp01-20200325-00002"}'
        tango_context.device.Configure(scan_configuration)
        obs_state_callback.assert_calls([ObsState.IDLE,ObsState.CONFIGURING])
        assert tango_context.device.configurationID == "sbi-mvp01-20200325-00002"
        assert tango_context.device.lastScanConfiguration == scan_configuration
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_Configure

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state_decorators
    def test_ConfigureScan_when_in_wrong_state(self, tango_context):
        """Test for ConfigureScan when the device is in wrong state"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state) ENABLED START #
        # The device in in OFF/EMPTY state, not valid to invoke ConfigureScan.
        with pytest.raises(DevFailed) as df:
            tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        assert "Error executing command ConfigureScanCommand" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key_decorators
    def test_ConfigureScan_with_wrong_configId_key(self, tango_context):
        """Test for ConfigureScan when json configuration specifies a wrong key for 
           configuration ID
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key) ENABLED START #
        tango_context.device.On()
        tango_context.device.AssignResources('{"example": [1,2,3]}')
        # wrong configurationID key
        wrong_configuration = '{"subid":"sbi-mvp01-20200325-00002"}'
        result_code, msg = tango_context.device.ConfigureScan(wrong_configuration)
        assert result_code == ResultCode.FAILED
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error_decorators
    def test_ConfigureScan_with_json_syntax_error(self, tango_context):
        """Test for ConfigureScan when syntax error in json configuration """
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error) ENABLED START #
        tango_context.device.On()
        tango_context.device.AssignResources('{"example": [1,2,3]}')
        result_code, msg = tango_context.device.ConfigureScan('{"foo": 1,}')
        assert result_code == ResultCode.FAILED
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error

    # PROTECTED REGION ID(CspSubelementSubarray.test_GoToIdle_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_GoToIdle_decorators
    def test_GoToIdle(self, tango_context, tango_change_event_helper):
        """Test for GoToIdle"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_GoToIdle) ENABLED START #
        tango_context.device.On()
        tango_context.device.AssignResources('{"example": [1,2,3]}')
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback.assert_calls([ObsState.IDLE,ObsState.CONFIGURING, ObsState.READY])
        tango_context.device.GoToIdle()
        obs_state_callback.assert_call(ObsState.IDLE)
        assert tango_context.device.scanID == 0
        assert tango_context.device.configurationID == ''
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_GoToIdle

def test_multiple_devices_in_same_process():
    devices_info = (
        {"class": CspSubElementSubarray, "devices": [{"name": "test/se/1"}]},
        {"class": SKASubarray, "devices": [{"name": "test/obsdevice/1"}]},
    )

    with MultiDeviceTestContext(devices_info, process=False) as context:
        proxy1 = context.get_device("test/se/1")
        proxy2 = context.get_device("test/obsdevice/1")
        assert proxy1.State() == DevState.OFF
        assert proxy2.State() == DevState.OFF
