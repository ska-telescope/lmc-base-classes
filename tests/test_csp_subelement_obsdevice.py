#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubelementObsDevice project
#
#
#
#########################################################################################
"""Contain the tests for the CspSubelementObsDevice and the State model implemented by
   such device.
"""
# Imports
import logging
import re
import pytest
import json

from tango import DevState, DevFailed
from tango.test_context import MultiDeviceTestContext

# PROTECTED REGION ID(CspSubelementObsDevice.test_additional_imports) ENABLED START #
from ska.base import SKAObsDevice, CspSubElementObsDevice, CspSubElementObsDeviceStateModel
from ska.base.commands import ResultCode
from ska.base.control_model import (
    ObsState, AdminMode, ControlMode, HealthState, SimulationMode, TestMode
)
from .conftest import load_state_machine_spec, ModelStateMachineTester
# PROTECTED REGION END #    //  CspSubElementObsDevice.test_additional_imports


# Device test case
# PROTECTED REGION ID(CspSubElementObsDevice.test_CspSubelementObsDevice_decorators) ENABLED START #
# PROTECTED REGION END #    // CspSubelementObsDevice.test_CspSubelementObsDevice_decorators

@pytest.fixture
def csp_subelement_obsdevice_state_model():
    """
    Yields a new SKASubarrayStateModel for testing
    """
    yield CspSubElementObsDeviceStateModel(logging.getLogger())


@pytest.mark.state_machine_tester(load_state_machine_spec("csp_subelement_obsdevice_state_machine"))
class TestCspSubElementObsDeviceStateModel(ModelStateMachineTester):
    """
    This class contains the test for the SKASubarrayStateModel class.
    """

    @pytest.fixture
    def machine(self, csp_subelement_obsdevice_state_model):
        """
        Fixture that returns the state machine under test in this class
        """
        yield csp_subelement_obsdevice_state_model

    def assert_state(self, machine, state):
        """
        Assert the current state of this state machine, based on the
        values of the adminMode, opState and obsState attributes of this
        model.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param state: the state that we are asserting to be the current
            state of the state machine under test
        :type state: str
        """
        assert machine.admin_mode == state["admin_mode"]
        assert machine.op_state == state["op_state"]
        assert machine.obs_state == state["obs_state"]


class TestCspSubElementObsDevice(object):
    """Test case for CSP SubElement ObsDevice class."""

    properties = {
        'SkaLevel': '4',
        'LoggingTargetsDefault': '',
        'GroupDefinitions': '',
        'DeviceID': 11,
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

    # PROTECTED REGION ID(CspSubelementObsDevice.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_buildState_decorators
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

    # PROTECTED REGION ID(CspSubelementObsDevice.test_scanID_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_scanID_decorators
    def test_scanID(self, tango_context):
        """Test for scanID"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_scanID) ENABLED START #
        assert tango_context.device.scanID == 0
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_scanID

    # PROTECTED REGION ID(CspSubelementObsDevice.test_deviceID_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_deviceID_decorators
    def test_deviceID(self, tango_context):
        """Test for deviceID"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_scanID) ENABLED START #
        assert tango_context.device.deviceID == self.properties['DeviceID']
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_scanID

    # PROTECTED REGION ID(CspSubelementObsDevice.test_sdpDestinationAddresses_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_sdpDestinationAddresses_decorators
    def test_sdpDestinationAddresses(self, tango_context):
        """Test for sdpDestinationAddresses"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_sdpDestinationAddresses) ENABLED START #
        addresses_dict = {'outputHost': [], 'outputMac': [], 'outputPort': []}
        assert tango_context.device.sdpDestinationAddresses == json.dumps(addresses_dict)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_sdpDestinationAddresses

    # PROTECTED REGION ID(CspSubelementObsDevice.test_sdpLinkActive_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_sdpLinkActive_decorators
    def test_sdpLinkActivity(self, tango_context):
        """Test for sdpLinkActive """
        # PROTECTED REGION ID(CspSubelementObsDevice.test_sdpLinkActive) ENABLED START #
        expected = tango_context.device.sdpLinkActive
        if expected is not None:
            n_links = len(expected)
            actual  = [ False for i in range(0, n_links)]
            assert all([a == b for a, b in zip(actual, expected)])
        else:
            assert expected is None
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_sdpLinkActive

    # PROTECTED REGION ID(CspSubelementObsDevice.test_sdpLinkCapacity_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_sdpLinkCapacity_decorators
    def test_sdpLinkCapacity(self, tango_context):
        """Test for sdpLinkCapacity """
        # PROTECTED REGION ID(CspSubelementObsDevice.test_sdpLinkCapacity) ENABLED START #
        assert tango_context.device.sdpLinkCapacity == 0
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_sdpLinkCapacity

    # PROTECTED REGION ID(CspSubelementObsDevice.test_healthFailureMessage_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_healthFailureMessage_decorators
    def test_healthFailureMessage(self, tango_context):
        """Test for healthFailureMessage """
        # PROTECTED REGION ID(CspSubelementObsDevice.test_healthFailureMessage) ENABLED START #
        assert tango_context.device.healthFailureMessage == ''
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_healthFailureMessage

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_decorators
    def test_ConfigureScan(self, tango_context, tango_change_event_helper):
        """Test for ConfigureScan"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan) ENABLED START #
        tango_context.device.On()
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        scan_configuration = '{"id":"sbi-mvp01-20200325-00002"}'
        tango_context.device.ConfigureScan(scan_configuration)
        obs_state_callback.assert_calls([ObsState.IDLE, ObsState.CONFIGURING])
        assert tango_context.device.configurationID == "sbi-mvp01-20200325-00002"
        assert tango_context.device.lastScanConfiguration == scan_configuration
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state_decorators
    def test_ConfigureScan_when_in_wrong_state(self, tango_context):
        """Test for ConfigureScan when the device is in wrong state"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state) ENABLED START #
        # The device in in OFF/IDLE state, not valid to invoke ConfigureScan.
        with pytest.raises(DevFailed) as df:
            tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        assert "Error executing command ConfigureScanCommand" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_with_wrong_input_args_when_idle_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_with_wrong_input_args_when_idle_decorators
    def test_ConfigureScan_with_wrong_input_args_when_idle(self, tango_context):
        """Test for ConfigureScan when input argument specifies a wrong json configuration
           and the device is in IDLE state.
        """
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_with_wrong_input_args_when_idle) ENABLED START #
        tango_context.device.On()
        init_obs_state = tango_context.device.obsState
        # wrong configurationID key
        wrong_configuration = '{"subid":"sbi-mvp01-20200325-00002"}'
        with pytest.raises(DevFailed) as df:
            tango_context.device.ConfigureScan(wrong_configuration)
        assert tango_context.device.obsState == init_obs_state
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_with_wrong_input_args_when_idle

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_with_wrong_input_args_when_ready_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_with_wrong_configId_key_decorators
    def test_ConfigureScan_with_wrong_input_args_when_ready(self, tango_context):
        """Test for ConfigureScan when json configuration specifies a wrong data and the device is
           in ON/READY state.
        """
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_with_wrong_input_args_when_ready) ENABLED START #
        tango_context.device.On()
        # wrong configurationID key
        valid_configuration = '{"id":"sbi-mvp01-20200325-00002"}'
        tango_context.device.ConfigureScan(valid_configuration)
        current_obs_state = tango_context.device.obsState
        wrong_configuration = '{"subid":"sbi-mvp01-20200325-00002"}'
        with pytest.raises(DevFailed) as df:
            tango_context.device.ConfigureScan(wrong_configuration)
        assert tango_context.device.obsState == current_obs_state
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_with_wrong_input_args_when_ready

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_with_json_syntax_error) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_with_json_syntax_error_decorators
    def test_ConfigureScan_with_json_syntax_error(self, tango_context):
        """Test for ConfigureScan when syntax error in json configuration """
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_with_json_syntax_error) ENABLED START #
        tango_context.device.On()
        init_obs_state = tango_context.device.obsState
        with pytest.raises(DevFailed) as df:
            tango_context.device.ConfigureScan('{"foo": 1,}')
        assert tango_context.device.obsState == init_obs_state
        assert tango_context.device.obsState != ObsState.FAULT
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_with_json_syntax_error

    # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GoToIdle_decorators
    def test_GoToIdle(self, tango_context, tango_change_event_helper):
        """Test for GoToIdle"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle) ENABLED START #
        tango_context.device.On()
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback.assert_calls([ObsState.IDLE,ObsState.CONFIGURING, ObsState.READY])
        tango_context.device.GoToIdle()
        obs_state_callback.assert_call(ObsState.IDLE)
        assert tango_context.device.scanID == 0
        assert tango_context.device.configurationID == ''
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GoToIdle

    # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GoToIdle_when_in_wrong_state_decorators
    def test_GoToIdle_when_in_wrong_state(self, tango_context):
        """Test for GoToIdle when the device is in wrong state"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle_when_in_wrong_state) ENABLED START #
        # The device in in OFF/IDLE state, not valid to invoke GoToIdle.
        with pytest.raises(DevFailed) as df:
            tango_context.device.GoToIdle()
        assert "Error executing command GoToIdleCommand" in str(df.value.args[0].desc)
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
        obs_state_callback.assert_calls([ObsState.READY, ObsState.SCANNING])
        assert tango_context.device.scanID == 1
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_when_in_wrong_state_decorators
    def test_Scan_when_in_wrong_state(self, tango_context):
        """Test for Scan when the device is in wrong state"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_when_in_wrong_state) ENABLED START #
        # Set the device in ON/IDLE state
        tango_context.device.On()
        with pytest.raises(DevFailed) as df:
            tango_context.device.Scan('32')
        assert "Error executing command ScanCommand" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_with_wrong_argument_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_with_wrong_argument_decorators
    def test_Scan_with_wrong_argument(self, tango_context):
        """Test for Scan when a wrong input argument is passed. """
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_with_wrong_argument) ENABLED START #
        # Set the device in ON/IDLE state
        tango_context.device.On()
        tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        current_obs_state = tango_context.device.obsState
        with pytest.raises(DevFailed) as df:
            tango_context.device.Scan('abc')
        assert tango_context.device.obsState == current_obs_state
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_with_wrong_argument

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

    # PROTECTED REGION ID(CspSubelementObsDevice.test_EndScan_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_EndScan_when_in_wrong_state_decorators
    def test_EndScan_when_in_wrong_state(self, tango_context):
        """Test for EndScan when the device is in wrong state"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_EndScan_when_in_wrong_state) ENABLED START #
        # Set the device in ON/READY state
        tango_context.device.On()
        tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        with pytest.raises(DevFailed) as df:
            tango_context.device.EndScan()
        assert "Error executing command EndScanCommand" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_EndScan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ObsReset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ObsReset_decorators
    def test_ObsReset(self, tango_context, tango_change_event_helper):
        """Test for ObsReset"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ObsReset) ENABLED START #
        tango_context.device.On()
        tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.READY)
        tango_context.device.Abort()
        obs_state_callback.assert_calls([ObsState.ABORTING, ObsState.ABORTED])
        tango_context.device.ObsReset()
        obs_state_callback.assert_call(ObsState.IDLE)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ObsReset

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ObsReset_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ObsReset_when_in_wrong_state_decorators
    def test_ObsReset_when_in_wrong_state(self, tango_context):
        """Test for ObsReset when the device is in wrong state"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ObsReset_when_in_wrong_state) ENABLED START #
        # Set the device in ON/IDLE state
        tango_context.device.On()
        with pytest.raises(DevFailed) as df:
            tango_context.device.ObsReset()
        assert "Error executing command ObsResetCommand" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ObsReset_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Abort_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Abort_decorators
    def test_Abort(self, tango_context, tango_change_event_helper):
        """Test for Abort"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Abort) ENABLED START #
        tango_context.device.On()
        tango_context.device.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        tango_context.device.Abort()
        obs_state_callback.assert_calls([ObsState.READY, ObsState.ABORTING, ObsState.ABORTED])
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Abort

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Abort_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Abort_when_in_wrong_state_decorators
    def test_Abort_when_in_wrong_state(self, tango_context):
        """Test for Abort when the device is in wrong state"""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Abort_when_in_wrong_state) ENABLED START #
        with pytest.raises(DevFailed) as df:
            tango_context.device.Abort()
        assert "Error executing command AbortCommand" in str(df.value.args[0].desc)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Abort_when_in_wrong_state


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
