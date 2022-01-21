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
import json
import re
import time

import pytest
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
from ska_tango_base.csp import CspSubElementObsStateModel
from ska_tango_base.testing.reference import ReferenceCspObsComponentManager

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
                self.logger,
                self._communication_state_changed,
                self._component_state_changed,
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    # PROTECTED REGION ID(CspSubelementObsDevice.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_State_decorators
    def test_State(self, device_under_test):
        """Test for State."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_State) ENABLED START #
        assert device_under_test.state() == DevState.OFF
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
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])
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
        assert device_under_test.healthState == HealthState.UNKNOWN
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
    def test_scanID(self, device_under_test, tango_change_event_helper):
        """Test for scanID."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_scanID) ENABLED START #
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        device_under_test.On()

        device_state_callback.assert_next_change_event(DevState.ON)
        assert device_under_test.state() == DevState.ON

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
    def test_ConfigureScan_and_GoToIdle(
        self, device_under_test, tango_change_event_helper
    ):
        """Test for ConfigureScan."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan) ENABLED START #
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        device_status_callback = tango_change_event_helper.subscribe("status")
        device_status_callback.assert_next_change_event("The device is in OFF state.")

        command_progress_callback = tango_change_event_helper.subscribe(
            "longRunningCommandProgress"
        )
        command_progress_callback.assert_next_change_event(None)

        command_status_callback = tango_change_event_helper.subscribe(
            "longRunningCommandStatus"
        )
        command_status_callback.assert_next_change_event(None)

        command_result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )
        command_result_callback.assert_next_change_event(("", ""))

        [[result_code], [command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED
        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        device_state_callback.assert_next_change_event(DevState.ON)
        device_status_callback.assert_next_change_event("The device is in ON state.")
        assert device_under_test.state() == DevState.ON

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "On command completed OK"]))
        )

        # assignment of resources
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        # TODO: Everything above here is just to turn on the device and clear the queue
        # attributes. We need a better way to handle this.

        assert device_under_test.configurationId == ""

        config_id = "sbi-mvp01-20200325-00002"

        [[result_code], [command_id]] = device_under_test.ConfigureScan(
            json.dumps({"id": config_id})
        )
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.CONFIGURING)

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.READY)

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "Configure completed OK"]))
        )

        assert device_under_test.configurationId == config_id

        # test deconfigure
        [[result_code], [command_id]] = device_under_test.GoToIdle()
        assert result_code == ResultCode.QUEUED

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "Deconfigure completed OK"]))
        )

        assert device_under_test.configurationId == ""

        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state_decorators
    def test_ConfigureScan_when_in_wrong_state(self, device_under_test):
        """Test for ConfigureScan when the device is in wrong state."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ConfigureScan_when_in_wrong_state) ENABLED START #
        # The device in in OFF/IDLE state, not valid to invoke ConfigureScan.

        with pytest.raises(DevFailed, match="Component is not powered ON"):
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

    # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GoToIdle_when_in_wrong_state_decorators
    def test_GoToIdle_when_in_wrong_state(self, device_under_test):
        """Test for GoToIdle when the device is in wrong state."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_GoToIdle_when_in_wrong_state) ENABLED START #
        # The device in in OFF/IDLE state, not valid to invoke GoToIdle.
        with pytest.raises(
            DevFailed, match="GoToIdle command not permitted in observation state IDLE"
        ):
            device_under_test.GoToIdle()

        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_GoToIdle_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_decorators
    def test_Scan_and_EndScan(self, device_under_test, tango_change_event_helper):
        """Test for Scan."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan) ENABLED START #

        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        device_status_callback = tango_change_event_helper.subscribe("status")
        device_status_callback.assert_next_change_event("The device is in OFF state.")

        command_progress_callback = tango_change_event_helper.subscribe(
            "longRunningCommandProgress"
        )
        command_progress_callback.assert_next_change_event(None)

        command_status_callback = tango_change_event_helper.subscribe(
            "longRunningCommandStatus"
        )
        command_status_callback.assert_next_change_event(None)

        command_result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )
        command_result_callback.assert_next_change_event(("", ""))

        [[result_code], [command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED
        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        device_state_callback.assert_next_change_event(DevState.ON)
        device_status_callback.assert_next_change_event("The device is in ON state.")
        assert device_under_test.state() == DevState.ON

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "On command completed OK"]))
        )

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        assert device_under_test.scanId == 0

        config_id = "sbi-mvp01-20200325-00002"

        [[result_code], [command_id]] = device_under_test.ConfigureScan(
            json.dumps({"id": config_id})
        )
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.CONFIGURING)

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.READY)

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "Configure completed OK"]))
        )

        assert device_under_test.configurationId == config_id

        # TODO: Everything above here is just to turn on the device, configure it, and
        # clear the queue attributes. We need a better way to handle this.

        scan_id = 1
        [[result_code], [command_id]] = device_under_test.Scan(str(scan_id))
        assert result_code == ResultCode.QUEUED

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.SCANNING)

        command_result_callback.assert_next_change_event(
            (
                command_id,
                json.dumps([int(ResultCode.OK), "Scan commencement completed OK"]),
            )
        )

        assert device_under_test.scanId == scan_id

        # test end_scan
        [[result_code], [command_id]] = device_under_test.EndScan()
        assert result_code == ResultCode.QUEUED

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.READY)

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "End scan completed OK"]))
        )

        assert device_under_test.scanId == 0
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_when_in_wrong_state_decorators
    def test_Scan_when_in_wrong_state(
        self, device_under_test, tango_change_event_helper
    ):
        """Test for Scan when the device is in wrong state."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_when_in_wrong_state) ENABLED START #
        # Set the device in ON/IDLE state
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        [[result_code], [command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        device_state_callback.assert_next_change_event(DevState.ON)

        with pytest.raises(
            DevFailed, match="Scan command not permitted in observation state IDLE"
        ):
            device_under_test.Scan("32")
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_with_wrong_argument_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_with_wrong_argument_decorators
    def test_Scan_with_wrong_argument(
        self, device_under_test, tango_change_event_helper
    ):
        """Test for Scan when a wrong input argument is passed."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Scan_with_wrong_argument) ENABLED START #
        # Set the device in ON/IDLE state
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        [[result_code], [command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        device_state_callback.assert_next_change_event(DevState.ON)

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        config_id = "sbi-mvp01-20200325-00002"

        [[result_code], [command_id]] = device_under_test.ConfigureScan(
            json.dumps({"id": config_id})
        )
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.CONFIGURING)
        obs_state_callback.assert_next_change_event(ObsState.READY)

        assert device_under_test.configurationId == config_id

        (result_code, _) = device_under_test.Scan("abc")
        assert result_code == ResultCode.FAILED

        obs_state_callback.assert_not_called()
        assert device_under_test.obsState == ObsState.READY
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Scan_with_wrong_argument

    # PROTECTED REGION ID(CspSubelementObsDevice.test_EndScan_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_EndScan_when_in_wrong_state_decorators
    def test_EndScan_when_in_wrong_state(
        self, device_under_test, tango_change_event_helper
    ):
        """Test for EndScan when the device is in wrong state."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_EndScan_when_in_wrong_state) ENABLED START #
        # Set the device in ON/READY state
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        [[result_code], [command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        device_state_callback.assert_next_change_event(DevState.ON)

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        config_id = "sbi-mvp01-20200325-00002"

        [[result_code], [command_id]] = device_under_test.ConfigureScan(
            json.dumps({"id": config_id})
        )
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.CONFIGURING)
        obs_state_callback.assert_next_change_event(ObsState.READY)

        assert device_under_test.configurationId == config_id

        with pytest.raises(
            DevFailed, match="EndScan command not permitted in observation state READY"
        ):
            device_under_test.EndScan()

        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_EndScan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementObsDevice.test_Abort_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Abort_decorators
    def test_abort_and_obsreset(self, device_under_test, tango_change_event_helper):
        """Test for Abort."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_Abort) ENABLED START #
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        device_status_callback = tango_change_event_helper.subscribe("status")
        device_status_callback.assert_next_change_event("The device is in OFF state.")

        command_progress_callback = tango_change_event_helper.subscribe(
            "longRunningCommandProgress"
        )
        command_progress_callback.assert_next_change_event(None)

        command_status_callback = tango_change_event_helper.subscribe(
            "longRunningCommandStatus"
        )
        command_status_callback.assert_next_change_event(None)

        command_result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )
        command_result_callback.assert_next_change_event(("", ""))

        [[result_code], [command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED
        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        device_state_callback.assert_next_change_event(DevState.ON)
        device_status_callback.assert_next_change_event("The device is in ON state.")
        assert device_under_test.state() == DevState.ON

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "On command completed OK"]))
        )

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        # TODO: Everything above here is just to turn on the device and clear the queue
        # attributes. We need a better way to handle this.

        # Start configuring but then abort
        [[result_code], [configure_command_id]] = device_under_test.ConfigureScan(
            json.dumps({"id": "sbi-mvp01-20200325-00002"})
        )
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.CONFIGURING)

        command_status_callback.assert_next_change_event(
            (configure_command_id, "QUEUED")
        )
        command_status_callback.assert_next_change_event(
            (configure_command_id, "IN_PROGRESS")
        )

        [[result_code], [abort_command_id]] = device_under_test.Abort()
        assert result_code == ResultCode.STARTED

        obs_state_callback.assert_next_change_event(ObsState.ABORTING)

        command_status_callback.assert_next_change_event(
            (configure_command_id, "IN_PROGRESS", abort_command_id, "IN_PROGRESS")
        )

        status_call = command_status_callback.get_next_change_event()
        if status_call == (
            configure_command_id,
            "ABORTED",
            abort_command_id,
            "IN_PROGRESS",
        ):
            # event announcing abort of configure arrived first,
            # now we expect abort to complete
            command_status_callback.assert_next_change_event(
                (abort_command_id, "COMPLETED")
            )
        else:
            # event announcing completion of abort arrived first,
            # now we expect configure to abort.
            assert status_call == (
                configure_command_id,
                "IN_PROGRESS",
                abort_command_id,
                "COMPLETED",
            )
            command_status_callback.assert_next_change_event(
                (configure_command_id, "ABORTED")
            )
        #    ((configure_command_id, 'ABORTED', abort_command_id, 'COMPLETED'))
        obs_state_callback.assert_next_change_event(ObsState.ABORTED)

        # command_progress_callback.assert_not_called()
        command_status_callback.assert_not_called()
        command_result_callback.assert_not_called()

        # Reset from aborted state
        [[result_code], [reset_command_id]] = device_under_test.ObsReset()
        assert result_code == ResultCode.QUEUED
        command_status_callback.assert_next_change_event((reset_command_id, "QUEUED"))
        command_status_callback.assert_next_change_event(
            (reset_command_id, "IN_PROGRESS")
        )

        obs_state_callback.assert_next_change_event(ObsState.RESETTING)

        # command_progress_callback.assert_next_change_event((reset_command_id, '33'))
        # command_progress_callback.assert_next_change_event((reset_command_id, '66'))

        command_status_callback.assert_next_change_event(
            (reset_command_id, "COMPLETED")
        )

        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        command_result_callback.assert_next_change_event(
            (
                reset_command_id,
                json.dumps([int(ResultCode.OK), "Obs reset completed OK"]),
            )
        )

        assert device_under_test.obsState == ObsState.IDLE

        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_Abort

    # PROTECTED REGION ID(CspSubelementObsDevice.test_ObsReset_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ObsReset_when_in_wrong_state_decorators
    def test_ObsReset_when_in_wrong_state(self, device_under_test):
        """Test for ObsReset when the device is in wrong state."""
        # PROTECTED REGION ID(CspSubelementObsDevice.test_ObsReset_when_in_wrong_state) ENABLED START #
        # Set the device in ON/IDLE state
        device_under_test.On()
        with pytest.raises(
            DevFailed, match="ObsReset command not permitted in observation state IDLE"
        ):
            device_under_test.ObsReset()
        # PROTECTED REGION END #    //  CspSubelementObsDevice.test_ObsReset_when_in_wrong_state


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

        time.sleep(0.15)  # required because of PushChanges segfault workaround
        assert proxy1.state() == DevState.DISABLE
        assert proxy2.state() == DevState.DISABLE
