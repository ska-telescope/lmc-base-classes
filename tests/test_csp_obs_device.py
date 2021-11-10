#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubelementObsDevice project
#
#
#
#########################################################################################
"""This module contains the tests for the CspSubelementObsDevice."""
# Imports
import re
import pytest
import json

from tango import DevState, DevFailed
from tango.test_context import MultiDeviceTestContext

# PROTECTED REGION ID(CspSubelementObsDevice.test_additional_imports) ENABLED START #
from ska_tango_base import SKAObsDevice, CspSubElementObsDevice
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import (
    ObsState,
    AdminMode,
    ControlMode,
    HealthState,
    SimulationMode,
    TestMode,
)
from ska_tango_base.csp import (
    CspSubElementObsStateModel,
    ReferenceCspObsComponentManager,
)

# PROTECTED REGION END #    //  CspSubElementObsDevice.test_additional_imports


# Device test case
# PROTECTED REGION ID(CspSubElementObsDevice.test_CspSubelementObsDevice_decorators) ENABLED START #
# PROTECTED REGION END #    // CspSubelementObsDevice.test_CspSubelementObsDevice_decorators


@pytest.fixture
def csp_subelement_obsdevice_state_model(logger):
    """
    Yield a new CspSubElementObsDevice StateModel for testing.

    :param logger: fixture that returns a logger
    """
    yield CspSubElementObsStateModel(logger)


class TestCspSubElementObsDevice(object):
    """Test case for CSP SubElement ObsDevice class."""

    @pytest.fixture(scope="class")
    def device_properties(self):
        """Fixture that returns properties of the device under test."""
        return {"DeviceID": "11"}

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Specify device configuration, including properties and memorized attributes.

        This implementation provides a concrete subclass of the device
        class under test, some properties, and a memorized value for
        adminMode.
        """
        return {
            "device": CspSubElementObsDevice,
            "component_manager_patch": lambda self: ReferenceCspObsComponentManager(
                self.op_state_model, self.obs_state_model, logger=self.logger
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    # PROTECTED REGION ID(CspSubelementObsDevice.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_State_decorators
    def test_State(self, device_under_test):
        """Test for State."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_State) ENABLED START #
        assert device_under_test.State() == DevState.OFF
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_State

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Status_decorators
    def test_Status(self, device_under_test):
        """Test for Status."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Status) ENABLED START #
        assert device_under_test.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Status

    # PROTECTED REGION ID(CspSubelementObsDevice.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test):
        """Test for GetVersionInfo."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            f"['{device_under_test.info().dev_class}, ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            "A set of generic base devices for SKA Telescope.']"
        )
        device_under_test.GetVersionInfo()
        versionInfo = device_under_test.longRunningCommandResult[2]
        assert (re.match(versionPattern, versionInfo)) is not None
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GetVersionInfo

    # PROTECTED REGION ID(CspSubelementObsDevice.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_buildState_decorators
    def test_buildState(self, device_under_test):
        """Test for buildState."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, device_under_test.buildState)) is not None
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_buildState

    # PROTECTED REGION ID(CspSubelementObsDevice.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_versionId_decorators
    def test_versionId(self, device_under_test):
        """Test for versionId."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_versionId

    # PROTECTED REGION ID(CspSubelementObsDevice.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_healthState_decorators
    def test_healthState(self, device_under_test):
        """Test for healthState."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_healthState) ENABLED START #
        assert device_under_test.healthState == HealthState.OK
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_healthState

    # PROTECTED REGION ID(CspSubelementObsDevice.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_adminMode_decorators
    def test_adminMode(self, device_under_test):
        """Test for adminMode."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_adminMode) ENABLED START #
        assert device_under_test.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_adminMode

    # PROTECTED REGION ID(CspSubelementObsDevice.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_controlMode_decorators
    def test_controlMode(self, device_under_test):
        """Test for controlMode."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_controlMode) ENABLED START #
        assert device_under_test.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_controlMode

    # PROTECTED REGION ID(CspSubelementObsDevice.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_simulationMode_decorators
    def test_simulationMode(self, device_under_test):
        """Test for simulationMode."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_simulationMode) ENABLED START #
        assert device_under_test.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_simulationMode

    # PROTECTED REGION ID(CspSubelementObsDevice.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_testMode_decorators
    def test_testMode(self, device_under_test):
        """Test for testMode."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_testMode) ENABLED START #
        assert device_under_test.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_testMode

    # PROTECTED REGION ID(CspSubelementObsDevice.test_scanID_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_scanID_decorators
    def test_scanID(self, device_under_test):
        """Test for scanID."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_scanID) ENABLED START #
        device_under_test.On()

        assert device_under_test.scanID == 0
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_scanID

    # PROTECTED REGION ID(CspSubelementObsDevice.test_deviceID_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_deviceID_decorators
    def test_deviceID(self, device_under_test, device_properties):
        """Test for deviceID."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_scanID) ENABLED START #
        assert device_under_test.deviceID == int(device_properties["DeviceID"])
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_scanID

    # PROTECTED REGION ID(CspSubelementObsDevice.test_sdpDestinationAddresses_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_sdpDestinationAddresses_decorators
    def test_sdpDestinationAddresses(self, device_under_test):
        """Test for sdpDestinationAddresses."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_sdpDestinationAddresses) ENABLED START #
        addresses_dict = {"outputHost": [], "outputMac": [], "outputPort": []}
        assert device_under_test.sdpDestinationAddresses == json.dumps(addresses_dict)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_sdpDestinationAddresses

    # PROTECTED REGION ID(CspSubelementObsDevice.test_sdpLinkActive_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_sdpLinkActive_decorators
    def test_sdpLinkActivity(self, device_under_test):
        """Test for sdpLinkActive."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_sdpLinkActive) ENABLED START #
        actual = device_under_test.sdpLinkActive
        n_links = len(actual)
        expected = [False for i in range(0, n_links)]
        assert all([a == b for a, b in zip(actual, expected)])
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_sdpLinkActive

    # PROTECTED REGION ID(CspSubelementObsDevice.test_sdpLinkCapacity_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_sdpLinkCapacity_decorators
    def test_sdpLinkCapacity(self, device_under_test):
        """Test for sdpLinkCapacity."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_sdpLinkCapacity) ENABLED START #
        assert device_under_test.sdpLinkCapacity == 0
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_sdpLinkCapacity

    # PROTECTED REGION ID(CspSubelementObsDevice.test_healthFailureMessage_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_healthFailureMessage_decorators
    def test_healthFailureMessage(self, device_under_test):
        """Test for healthFailureMessage."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_healthFailureMessage) ENABLED START #
        assert device_under_test.healthFailureMessage == ""
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_healthFailureMessage

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_decorators
    def test_ConfigureScan(self, device_under_test, tango_change_event_helper):
        """Test for ConfigureScan."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan) ENABLED START #
        device_under_test.On()
        assert device_under_test.obsState == ObsState.IDLE

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        scan_configuration = '{"id":"sbi-mvp01-20200325-00002"}'
        device_under_test.ConfigureScan(scan_configuration)
        obs_state_callback.assert_calls(
            [ObsState.IDLE, ObsState.CONFIGURING, ObsState.READY]
        )
        assert device_under_test.obsState == ObsState.READY
        assert device_under_test.configurationID == "sbi-mvp01-20200325-00002"
        assert device_under_test.lastScanConfiguration == scan_configuration
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state_decorators
    def test_ConfigureScan_when_in_wrong_state(self, device_under_test):
        """Test for ConfigureScan when the device is in wrong state."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state) ENABLED START #
        # The device in in OFF/IDLE state, not valid to invoke ConfigureScan.

        with pytest.raises(DevFailed, match="Component is not ON"):
            device_under_test.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_with_wrong_input_args_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_with_wrong_input_args_decorators
    def test_ConfigureScan_with_wrong_input_args(self, device_under_test):
        """
        Test ConfigureScan's handling of wrong input arguments.

        Specifically, test when input argument specifies a wrong json
        configuration and the device is in IDLE state.
        """
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_with_wrong_input_args_when_idle) ENABLED START #
        device_under_test.On()
        # wrong configurationID key
        assert device_under_test.obsState == ObsState.IDLE

        wrong_configuration = '{"subid":"sbi-mvp01-20200325-00002"}'
        (result_code, _) = device_under_test.ConfigureScan(wrong_configuration)
        assert result_code == ResultCode.FAILED
        assert device_under_test.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_with_wrong_input_args

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_with_json_syntax_error) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_with_json_syntax_error_decorators
    def test_ConfigureScan_with_json_syntax_error(self, device_under_test):
        """Test for ConfigureScan when syntax error in json configuration."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_with_json_syntax_error) ENABLED START #
        device_under_test.On()
        assert device_under_test.obsState == ObsState.IDLE

        (result_code, _) = device_under_test.ConfigureScan('{"foo": 1,}')
        assert result_code == ResultCode.FAILED
        assert device_under_test.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_with_json_syntax_error

    # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GoToIdle_decorators
    def test_GoToIdle(self, device_under_test, tango_change_event_helper):
        """Test for GoToIdle."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle) ENABLED START #
        device_under_test.On()
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        device_under_test.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback.assert_calls(
            [ObsState.IDLE, ObsState.CONFIGURING, ObsState.READY]
        )
        device_under_test.GoToIdle()
        obs_state_callback.assert_call(ObsState.IDLE)
        assert device_under_test.scanID == 0
        assert device_under_test.configurationID == ""
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GoToIdle

    # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GoToIdle_when_in_wrong_state_decorators
    def test_GoToIdle_when_in_wrong_state(self, device_under_test):
        """Test for GoToIdle when the device is in wrong state."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle_when_in_wrong_state) ENABLED START #
        # The device in in OFF/IDLE state, not valid to invoke GoToIdle.
        with pytest.raises(DevFailed, match="Command not permitted by state model."):
            device_under_test.GoToIdle()

        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GoToIdle_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_decorators
    def test_Scan(self, device_under_test, tango_change_event_helper):
        """Test for Scan."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan) ENABLED START #
        device_under_test.On()
        device_under_test.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        device_under_test.Scan("1")
        obs_state_callback.assert_calls([ObsState.READY, ObsState.SCANNING])
        assert device_under_test.scanID == 1
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_when_in_wrong_state_decorators
    def test_Scan_when_in_wrong_state(self, device_under_test):
        """Test for Scan when the device is in wrong state."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_when_in_wrong_state) ENABLED START #
        # Set the device in ON/IDLE state
        device_under_test.On()
        with pytest.raises(DevFailed, match="Command not permitted by state model."):
            device_under_test.Scan("32")
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_with_wrong_argument_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_with_wrong_argument_decorators
    def test_Scan_with_wrong_argument(self, device_under_test):
        """Test for Scan when a wrong input argument is passed."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_with_wrong_argument) ENABLED START #
        # Set the device in ON/IDLE state
        device_under_test.On()
        device_under_test.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        (result_code, _) = device_under_test.Scan("abc")
        assert result_code == ResultCode.FAILED
        assert device_under_test.obsState == ObsState.READY
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_with_wrong_argument

    # PROTECTED REGION ID(CspSubelementObsDevice.test_EndScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_EndScan_decorators
    def test_EndScan(self, device_under_test, tango_change_event_helper):
        """Test for EndScan."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_EndScan) ENABLED START #
        device_under_test.On()
        device_under_test.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.READY)
        device_under_test.Scan("1")
        obs_state_callback.assert_call(ObsState.SCANNING)
        device_under_test.EndScan()
        obs_state_callback.assert_call(ObsState.READY)
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_EndScan

    # PROTECTED REGION ID(CspSubelementObsDevice.test_EndScan_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_EndScan_when_in_wrong_state_decorators
    def test_EndScan_when_in_wrong_state(self, device_under_test):
        """Test for EndScan when the device is in wrong state."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_EndScan_when_in_wrong_state) ENABLED START #
        # Set the device in ON/READY state
        device_under_test.On()
        device_under_test.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        with pytest.raises(DevFailed, match="Command not permitted by state model."):
            device_under_test.EndScan()

        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_EndScan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ObsReset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ObsReset_decorators
    def test_ObsReset(self, device_under_test, tango_change_event_helper):
        """Test for ObsReset."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ObsReset) ENABLED START #
        device_under_test.On()
        device_under_test.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.READY)
        device_under_test.Abort()
        obs_state_callback.assert_calls([ObsState.ABORTING, ObsState.ABORTED])
        device_under_test.ObsReset()
        obs_state_callback.assert_calls([ObsState.RESETTING, ObsState.IDLE])
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ObsReset

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ObsReset_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ObsReset_when_in_wrong_state_decorators
    def test_ObsReset_when_in_wrong_state(self, device_under_test):
        """Test for ObsReset when the device is in wrong state."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ObsReset_when_in_wrong_state) ENABLED START #
        # Set the device in ON/IDLE state
        device_under_test.On()
        with pytest.raises(DevFailed, match="Command not permitted by state model."):
            device_under_test.ObsReset()
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ObsReset_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Abort_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Abort_decorators
    def test_Abort(self, device_under_test, tango_change_event_helper):
        """Test for Abort."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Abort) ENABLED START #
        device_under_test.On()
        device_under_test.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        device_under_test.Abort()
        obs_state_callback.assert_calls(
            [ObsState.READY, ObsState.ABORTING, ObsState.ABORTED]
        )
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Abort


@pytest.mark.forked
def test_multiple_devices_in_same_process():
    """Test that we can run this device with other devices in a single process."""
    devices_info = (
        {"class": CspSubElementObsDevice, "devices": [{"name": "test/se/1"}]},
        {"class": SKAObsDevice, "devices": [{"name": "test/obsdevice/1"}]},
    )

    with MultiDeviceTestContext(devices_info, process=False) as context:
        proxy1 = context.get_device("test/se/1")
        proxy2 = context.get_device("test/obsdevice/1")
        assert proxy1.State() == DevState.DISABLE
        assert proxy2.State() == DevState.DISABLE
