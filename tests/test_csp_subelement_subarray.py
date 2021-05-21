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
import re
import pytest
import json

from tango import DevState, DevFailed

# PROTECTED REGION ID(CspSubelementSubarray.test_additional_imports) ENABLED START #
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import (
    ObsState, AdminMode, ControlMode, HealthState, SimulationMode, TestMode
)
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

    @pytest.mark.skip(reason="Not implemented")
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
        assert tango_context.device.State() == DevState.DISABLE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_State

    # PROTECTED REGION ID(CspSubelementSubarray.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in DISABLE state."
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_Status

    # PROTECTED REGION ID(CspSubelementSubarray.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'CspSubElementSubarray, ska_tango_base, [0-9]+.[0-9]+.[0-9]+, '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_GetVersionInfo

    # PROTECTED REGION ID(CspSubelementSubarray.test_configurationProgress_decorators) ENABLED START #
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'ska_tango_base, [0-9]+.[0-9]+.[0-9]+, '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_buildState

    # PROTECTED REGION ID(CspSubelementSubarray.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9]+.[0-9]+.[0-9]+')
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
        assert tango_context.device.adminMode == AdminMode.OFFLINE
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
        device_under_test = tango_context.device
        device_under_test.adminMode = AdminMode.MAINTENANCE
        device_under_test.On()
        assert device_under_test.scanID == 0
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
        actual = tango_context.device.sdpLinkActive
        n_links = len(actual)
        expected = [False for i in range(0, n_links)]
        assert all([a == b for a, b in zip(actual, expected)])
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_sdpLinkActive

    # PROTECTED REGION ID(CspSubelementSubarray.test_outputDataRateToSdp_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_outputDataRateToSdp_decorators
    def test_outputDataRateToSdp(self, tango_context):
        """Test for outputDataRateToSdp """
        # PROTECTED REGION ID(CspSubelementSubarray.test_outputDataRateToSdp) ENABLED START #
        assert tango_context.device.outputDataRateToSdp == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_outputDataRateToSdp

    # PROTECTED REGION ID(CspSubelementSubarray.test_listOfDevicesCompletedTasks_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_listOfDevicesCompletedTasks_decorators
    def test_listOfDevicesCompletedTasks(self, tango_context):
        """Test for listOfDevicesCompletedTasks """
        # PROTECTED REGION ID(CspSubelementSubarray.test_listOfDevicesCompletedTasks) ENABLED START #
        attr_value_as_dict = json.loads(tango_context.device.listOfDevicesCompletedTasks)
        assert not bool(attr_value_as_dict)
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_listOfDevicesCompletedTasks

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_decorators

    # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesMaximumDuration_decorators
    def test_assignResourcesMaximumDuration(self, tango_context):
        """Test for assignResourcesMaximumDuration """
        # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesMaximumDuration) ENABLED START #
        tango_context.device.assignResourcesMaximumDuration = 5
        assert tango_context.device.assignResourcesMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesMaximumDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_configureScanMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_configureScanMeasuredDuration_decorators
    def test_configureScanMeasuredDuration(self, tango_context):
        """Test for configureScanMeasuredDuration """
        # PROTECTED REGION ID(CspSubelementSubarray.test_configureScanMeasuredDuration) ENABLED START #
        assert tango_context.device.configureScanMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_configureScanMeasuredDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_configurationProgress_decorators
    def test_configurationProgress(self, tango_context):
        """Test for configurationProgress """
        # PROTECTED REGION ID(CspSubelementSubarray.test_configurationProgress) ENABLED START #
        assert tango_context.device.configurationProgress == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_configurationProgress

    # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesMeasuredDuration_decorators
    def test_assignResourcesMeasuredDuration(self, tango_context):
        """Test for assignResourcesMeasuredDuration """
        # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesMeasuredDuration) ENABLED START #
        assert tango_context.device.assignResourcesMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesMeasuredDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesProgress_decorators
    def test_assignResourcesProgress(self, tango_context):
        """Test for assignResourcesProgress """
        # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesProgress) ENABLED START #
        assert tango_context.device.assignResourcesProgress == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesProgress

    # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesMaximumDuration_decorators
    def test_releaseResourcesMaximumDuration(self, tango_context):
        """Test for releaseResourcesMaximumDuration """
        # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesMaximumDuration) ENABLED START #
        tango_context.device.releaseResourcesMaximumDuration = 5
        assert tango_context.device.releaseResourcesMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesMaximumDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesMeasuredDuration_decorators
    def test_releaseResourcesMeasuredDuration(self, tango_context):
        """Test for releaseResourcesMeasuredDuration """
        # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesMeasuredDuration) ENABLED START #
        assert tango_context.device.releaseResourcesMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesMeasuredDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesProgress_decorators
    def test_releaseResourcesProgress(self, tango_context):
        """Test for releaseResourcesProgress """
        # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesProgress) ENABLED START #
        assert tango_context.device.releaseResourcesProgress == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesProgress

    # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag_decorators
    def test_configureScanTimeoutExpiredFlag(self, tango_context):
        """Test for timeoutExpiredFlag """
        # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag) ENABLED START #
        assert tango_context.device.configureScanTimeoutExpiredFlag == False
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag

    # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag_decorators
    def test_assignResourcesTimeoutExpiredFlag(self, tango_context):
        """Test for timeoutExpiredFlag """
        # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag) ENABLED START #
        assert tango_context.device.assignResourcesTimeoutExpiredFlag == False
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag

    # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag_decorators
    def test_releaseResourcesTimeoutExpiredFlag(self, tango_context):
        """Test for timeoutExpiredFlag """
        # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag) ENABLED START #
        assert tango_context.device.releaseResourcesTimeoutExpiredFlag == False
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_decorators
    @pytest.mark.parametrize("command_alias", ["Configure", "ConfigureScan"])
    def test_ConfigureScan(self, tango_context, tango_change_event_helper, command_alias):
        """Test for ConfigureScan"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan) ENABLED START #
        device_under_test = tango_context.device
        device_under_test.adminMode = AdminMode.MAINTENANCE
        device_under_test.On()
        device_under_test.AssignResources(json.dumps([1,2,3]))
        assert device_under_test.obsState == ObsState.IDLE

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        scan_configuration = '{"id":"sbi-mvp01-20200325-00002"}'
        device_under_test.command_inout(command_alias, scan_configuration)
        obs_state_callback.assert_calls([ObsState.IDLE, ObsState.CONFIGURING, ObsState.READY])
        assert device_under_test.obsState == ObsState.READY
        assert tango_context.device.configurationID == "sbi-mvp01-20200325-00002"
        assert tango_context.device.lastScanConfiguration == scan_configuration
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state_decorators
    def test_ConfigureScan_when_in_wrong_state(self, tango_context):
        """Test for ConfigureScan when the device is in wrong state"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state) ENABLED START #
        # The device in in OFF/EMPTY state, not valid to invoke ConfigureScan.
        with pytest.raises(DevFailed, match="Command not permitted"):
            tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key_decorators
    def test_ConfigureScan_with_wrong_configId_key(self, tango_context):
        """Test for ConfigureScan when json configuration specifies a wrong key for
           configuration ID
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key) ENABLED START #
        tango_context.device.adminMode = AdminMode.MAINTENANCE
        tango_context.device.On()
        tango_context.device.AssignResources(json.dumps([1,2,3]))
        # wrong configurationID key
        assert tango_context.device.obsState == ObsState.IDLE

        wrong_configuration = '{"subid":"sbi-mvp01-20200325-00002"}'
        result_code, _ = tango_context.device.ConfigureScan(wrong_configuration)
        assert result_code == ResultCode.FAILED
        assert tango_context.device.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error_decorators
    def test_ConfigureScan_with_json_syntax_error(self, tango_context):
        """Test for ConfigureScan when syntax error in json configuration """
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error) ENABLED START #
        tango_context.device.adminMode = AdminMode.MAINTENANCE
        tango_context.device.On()
        tango_context.device.AssignResources(json.dumps([1,2,3]))
        assert tango_context.device.obsState == ObsState.IDLE

        result_code, _ = tango_context.device.ConfigureScan('{"foo": 1,}')
        assert result_code == ResultCode.FAILED
        assert tango_context.device.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error

    # PROTECTED REGION ID(CspSubelementSubarray.test_GoToIdle_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_GoToIdle_decorators
    @pytest.mark.parametrize("command_alias", ["GoToIdle", "End"])
    def test_GoToIdle(self, tango_context, tango_change_event_helper, command_alias):
        """Test for GoToIdle"""
        # PROTECTED REGION ID(CspSubelementSubarray.test_GoToIdle) ENABLED START #
        tango_context.device.adminMode = AdminMode.MAINTENANCE
        tango_context.device.On()
        tango_context.device.AssignResources(json.dumps([1,2,3]))
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback.assert_calls(
            [ObsState.IDLE, ObsState.CONFIGURING, ObsState.READY])
        tango_context.device.command_inout(command_alias)
        obs_state_callback.assert_call(ObsState.IDLE)
        assert tango_context.device.scanID == 0
        assert tango_context.device.configurationID == ''
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_GoToIdle
