#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubelementSubarray project
#
#
#
#########################################################################################
"""This module tests the :py:mod:``ska_tango_base.csp.subarray_device`` module."""
# Imports
import re
import pytest
import json

from tango import DevState, DevFailed

# PROTECTED REGION ID(CspSubelementSubarray.test_additional_imports) ENABLED START #
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
    CspSubElementSubarray,
    ReferenceCspSubarrayComponentManager,
)

# PROTECTED REGION END #    //  CspSubElementSubarray.test_additional_imports


# Device test case
# PROTECTED REGION ID(CspSubElementSubarray.test_CspSubelementSubarray_decorators) ENABLED START #
# PROTECTED REGION END #    // CspSubelementSubarray.test_CspSubelementSubarray_decorators


class TestCspSubElementSubarray(object):
    """Test case for CSP SubElement Subarray class."""

    @pytest.fixture(scope="class")
    def device_properties(self):
        """Fixture that returns device properties of the device under test."""
        return {"CapabilityTypes": ["id"]}

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Return a specification of the device to be tested.

        The specification includes the device's properties and memorized
        attributes.

        This implementation provides a concrete subclass of the device
        class under test, some properties, and a memorized value for
        adminMode.
        """
        return {
            "device": CspSubElementSubarray,
            "component_manager_patch": lambda self: ReferenceCspSubarrayComponentManager(
                self.op_state_model,
                self.obs_state_model,
                self.CapabilityTypes,
                logger=self.logger,
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip(reason="Not implemented")
    def test_properties(self, device_under_test):
        """Test the device properties."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_properties
        pass

    # PROTECTED REGION ID(CspSubelementSubarray.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_State_decorators
    def test_State(self, device_under_test):
        """Test for State."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_State) ENABLED START #
        assert device_under_test.State() == DevState.OFF
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_State

    # PROTECTED REGION ID(CspSubelementSubarray.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_Status_decorators
    def test_Status(self, device_under_test):
        """Test for Status."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_Status) ENABLED START #
        assert device_under_test.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_Status

    # PROTECTED REGION ID(CspSubelementSubarray.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test):
        """Test for GetVersionInfo."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            f"['{device_under_test.info().dev_class}, ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            "A set of generic base devices for SKA Telescope.']"
        )
        device_under_test.GetVersionInfo()
        versionInfo = device_under_test.longRunningCommandResult[2]
        assert (re.match(versionPattern, versionInfo)) is not None
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_GetVersionInfo

    # PROTECTED REGION ID(CspSubelementSubarray.test_configurationProgress_decorators) ENABLED START #
    def test_buildState(self, device_under_test):
        """Test for buildState."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, device_under_test.buildState)) is not None
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_buildState

    # PROTECTED REGION ID(CspSubelementSubarray.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_versionId_decorators
    def test_versionId(self, device_under_test):
        """Test for versionId."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_versionId

    # PROTECTED REGION ID(CspSubelementSubarray.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_healthState_decorators
    def test_healthState(self, device_under_test):
        """Test for healthState."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_healthState) ENABLED START #
        assert device_under_test.healthState == HealthState.OK
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_healthState

    # PROTECTED REGION ID(CspSubelementSubarray.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_adminMode_decorators
    def test_adminMode(self, device_under_test):
        """Test for adminMode."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_adminMode) ENABLED START #
        assert device_under_test.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_adminMode

    # PROTECTED REGION ID(CspSubelementSubarray.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_controlMode_decorators
    def test_controlMode(self, device_under_test):
        """Test for controlMode."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_controlMode) ENABLED START #
        assert device_under_test.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_controlMode

    # PROTECTED REGION ID(CspSubelementSubarray.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_simulationMode_decorators
    def test_simulationMode(self, device_under_test):
        """Test for simulationMode."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_simulationMode) ENABLED START #
        assert device_under_test.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_simulationMode

    # PROTECTED REGION ID(CspSubelementSubarray.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_testMode_decorators
    def test_testMode(self, device_under_test):
        """Test for testMode."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_testMode) ENABLED START #
        assert device_under_test.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_testMode

    # PROTECTED REGION ID(CspSubelementSubarray.test_scanID_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_scanID_decorators
    def test_scanID(self, device_under_test):
        """Test for scanID."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_scanID) ENABLED START #
        device_under_test.On()
        assert device_under_test.scanID == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_scanID

    # PROTECTED REGION ID(CspSubelementSubarray.test_sdpDestinationAddresses_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_sdpDestinationAddresses_decorators
    def test_sdpDestinationAddresses(self, device_under_test):
        """Test for sdpDestinationAddresses."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_sdpDestinationAddresses) ENABLED START #
        addresses_dict = {"outputHost": [], "outputMac": [], "outputPort": []}
        device_under_test.sdpDestinationAddresses = json.dumps(addresses_dict)
        assert device_under_test.sdpDestinationAddresses == json.dumps(addresses_dict)
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_sdpDestinationAddresses

    # PROTECTED REGION ID(CspSubelementSubarray.test_sdpLinkActive_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_sdpLinkActive_decorators
    def test_sdpLinkActivity(self, device_under_test):
        """Test for sdpLinkActive."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_sdpLinkActive) ENABLED START #
        actual = device_under_test.sdpLinkActive
        n_links = len(actual)
        expected = [False for i in range(0, n_links)]
        assert all([a == b for a, b in zip(actual, expected)])
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_sdpLinkActive

    # PROTECTED REGION ID(CspSubelementSubarray.test_outputDataRateToSdp_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_outputDataRateToSdp_decorators
    def test_outputDataRateToSdp(self, device_under_test):
        """Test for outputDataRateToSdp."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_outputDataRateToSdp) ENABLED START #
        assert device_under_test.outputDataRateToSdp == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_outputDataRateToSdp

    # PROTECTED REGION ID(CspSubelementSubarray.test_listOfDevicesCompletedTasks_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_listOfDevicesCompletedTasks_decorators
    def test_listOfDevicesCompletedTasks(self, device_under_test):
        """Test for listOfDevicesCompletedTasks."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_listOfDevicesCompletedTasks) ENABLED START #
        attr_value_as_dict = json.loads(device_under_test.listOfDevicesCompletedTasks)
        assert not bool(attr_value_as_dict)
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_listOfDevicesCompletedTasks

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_decorators

    # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesMaximumDuration_decorators
    def test_assignResourcesMaximumDuration(self, device_under_test):
        """Test for assignResourcesMaximumDuration."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesMaximumDuration) ENABLED START #
        device_under_test.assignResourcesMaximumDuration = 5
        assert device_under_test.assignResourcesMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesMaximumDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_configureScanMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_configureScanMeasuredDuration_decorators
    def test_configureScanMeasuredDuration(self, device_under_test):
        """Test for configureScanMeasuredDuration."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_configureScanMeasuredDuration) ENABLED START #
        assert device_under_test.configureScanMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_configureScanMeasuredDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_configurationProgress_decorators
    def test_configurationProgress(self, device_under_test):
        """Test for configurationProgress."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_configurationProgress) ENABLED START #
        assert device_under_test.configurationProgress == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_configurationProgress

    # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesMeasuredDuration_decorators
    def test_assignResourcesMeasuredDuration(self, device_under_test):
        """Test for assignResourcesMeasuredDuration."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesMeasuredDuration) ENABLED START #
        assert device_under_test.assignResourcesMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesMeasuredDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesProgress_decorators
    def test_assignResourcesProgress(self, device_under_test):
        """Test for assignResourcesProgress."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesProgress) ENABLED START #
        assert device_under_test.assignResourcesProgress == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesProgress

    # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesMaximumDuration_decorators
    def test_releaseResourcesMaximumDuration(self, device_under_test):
        """Test for releaseResourcesMaximumDuration."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesMaximumDuration) ENABLED START #
        device_under_test.releaseResourcesMaximumDuration = 5
        assert device_under_test.releaseResourcesMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesMaximumDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesMeasuredDuration_decorators
    def test_releaseResourcesMeasuredDuration(self, device_under_test):
        """Test for releaseResourcesMeasuredDuration."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesMeasuredDuration) ENABLED START #
        assert device_under_test.releaseResourcesMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesMeasuredDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesProgress_decorators
    def test_releaseResourcesProgress(self, device_under_test):
        """Test for releaseResourcesProgress."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesProgress) ENABLED START #
        assert device_under_test.releaseResourcesProgress == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesProgress

    # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag_decorators
    def test_configureScanTimeoutExpiredFlag(self, device_under_test):
        """Test for timeoutExpiredFlag."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag) ENABLED START #
        assert not device_under_test.configureScanTimeoutExpiredFlag
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag

    # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag_decorators
    def test_assignResourcesTimeoutExpiredFlag(self, device_under_test):
        """Test for timeoutExpiredFlag."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag) ENABLED START #
        assert not device_under_test.assignResourcesTimeoutExpiredFlag
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag

    # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag_decorators
    def test_releaseResourcesTimeoutExpiredFlag(self, device_under_test):
        """Test for timeoutExpiredFlag."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag) ENABLED START #
        assert not device_under_test.releaseResourcesTimeoutExpiredFlag
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_decorators
    @pytest.mark.parametrize("command_alias", ["Configure", "ConfigureScan"])
    def test_ConfigureScan(
        self, device_under_test, tango_change_event_helper, command_alias
    ):
        """Test for ConfigureScan."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan) ENABLED START #
        device_under_test.On()
        device_under_test.AssignResources(json.dumps([1, 2, 3]))
        assert device_under_test.obsState == ObsState.IDLE

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        scan_configuration = '{"id":"sbi-mvp01-20200325-00002"}'
        device_under_test.command_inout(command_alias, scan_configuration)
        obs_state_callback.assert_calls(
            [ObsState.IDLE, ObsState.CONFIGURING, ObsState.READY]
        )
        assert device_under_test.obsState == ObsState.READY
        assert device_under_test.configurationID == "sbi-mvp01-20200325-00002"
        assert device_under_test.lastScanConfiguration == scan_configuration
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state_decorators
    def test_ConfigureScan_when_in_wrong_state(self, device_under_test):
        """Test for ConfigureScan when the device is in wrong state."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state) ENABLED START #
        # The device in in OFF/EMPTY state, not valid to invoke ConfigureScan.
        with pytest.raises(DevFailed, match="Command not permitted by state model."):
            device_under_test.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key_decorators
    def test_ConfigureScan_with_wrong_configId_key(self, device_under_test):
        """Test that ConfigureScan handles a wrong configuration id key."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key) ENABLED START #
        device_under_test.On()
        device_under_test.AssignResources(json.dumps([1, 2, 3]))
        # wrong configurationID key
        assert device_under_test.obsState == ObsState.IDLE

        wrong_configuration = '{"subid":"sbi-mvp01-20200325-00002"}'
        result_code, _ = device_under_test.ConfigureScan(wrong_configuration)
        assert result_code == ResultCode.FAILED
        assert device_under_test.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error_decorators
    def test_ConfigureScan_with_json_syntax_error(self, device_under_test):
        """Test for ConfigureScan when syntax error in json configuration."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error) ENABLED START #
        device_under_test.On()
        device_under_test.AssignResources(json.dumps([1, 2, 3]))
        assert device_under_test.obsState == ObsState.IDLE

        result_code, _ = device_under_test.ConfigureScan('{"foo": 1,}')
        assert result_code == ResultCode.FAILED
        assert device_under_test.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error

    # PROTECTED REGION ID(CspSubelementSubarray.test_GoToIdle_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_GoToIdle_decorators
    @pytest.mark.parametrize("command_alias", ["GoToIdle", "End"])
    def test_GoToIdle(
        self, device_under_test, tango_change_event_helper, command_alias
    ):
        """Test for GoToIdle."""
        # PROTECTED REGION ID(CspSubelementSubarray.test_GoToIdle) ENABLED START #
        device_under_test.On()
        device_under_test.AssignResources(json.dumps([1, 2, 3]))
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        device_under_test.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        obs_state_callback.assert_calls(
            [ObsState.IDLE, ObsState.CONFIGURING, ObsState.READY]
        )
        device_under_test.command_inout(command_alias)
        obs_state_callback.assert_call(ObsState.IDLE)
        assert device_under_test.scanID == 0
        assert device_under_test.configurationID == ""
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_GoToIdle
