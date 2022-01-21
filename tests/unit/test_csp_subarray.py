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
import json
import re

import pytest
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
from ska_tango_base.csp import CspSubElementSubarray
from ska_tango_base.testing.reference import ReferenceCspSubarrayComponentManager

# PROTECTED REGION END #    //  CspSubElementSubarray.test_additional_imports


# Device test case
# PROTECTED REGION ID(CspSubElementSubarray.test_CspSubelementSubarray_decorators) ENABLED START #
# PROTECTED REGION END #    // CspSubelementSubarray.test_CspSubelementSubarray_decorators


class TestCspSubElementSubarray(object):
    """Test case for CSP SubElement Subarray class."""

    @pytest.fixture(scope="class")
    def device_properties(self):
        """
        Fixture that returns device properties of the device under test.

        :return: properties of the device under test
        """
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

        :param device_properties: fixture that returns device properties
            of the device under test

        :return: specification of how the device under test should be
            configured
        """
        return {
            "device": CspSubElementSubarray,
            "component_manager_patch": lambda self: ReferenceCspSubarrayComponentManager(
                self.logger,
                self._communication_state_changed,
                self._component_state_changed,
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip(reason="Not implemented")
    def test_properties(self, device_under_test):
        """
        Test the device properties.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_properties
        pass

    # PROTECTED REGION ID(CspSubelementSubarray.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_State_decorators
    def test_State(self, device_under_test):
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_State) ENABLED START #
        assert device_under_test.state() == DevState.OFF
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_State

    # PROTECTED REGION ID(CspSubelementSubarray.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_Status_decorators
    def test_Status(self, device_under_test):
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_Status) ENABLED START #
        assert device_under_test.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_Status

    # PROTECTED REGION ID(CspSubelementSubarray.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test):
        """
        Test for GetVersionInfo.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_GetVersionInfo) ENABLED START #
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_GetVersionInfo

    # PROTECTED REGION ID(CspSubelementSubarray.test_configurationProgress_decorators) ENABLED START #
    def test_buildState(self, device_under_test):
        """
        Test for buildState.

        :param device_under_test: a proxy to the device under test
        """
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
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_versionId

    # PROTECTED REGION ID(CspSubelementSubarray.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_healthState_decorators
    def test_healthState(self, device_under_test):
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_healthState) ENABLED START #
        assert device_under_test.healthState == HealthState.UNKNOWN
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_healthState

    # PROTECTED REGION ID(CspSubelementSubarray.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_adminMode_decorators
    def test_adminMode(self, device_under_test):
        """
        Test for adminMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_adminMode) ENABLED START #
        assert device_under_test.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_adminMode

    # PROTECTED REGION ID(CspSubelementSubarray.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_controlMode_decorators
    def test_controlMode(self, device_under_test):
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_controlMode) ENABLED START #
        assert device_under_test.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_controlMode

    # PROTECTED REGION ID(CspSubelementSubarray.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_simulationMode_decorators
    def test_simulationMode(self, device_under_test):
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_simulationMode) ENABLED START #
        assert device_under_test.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_simulationMode

    # PROTECTED REGION ID(CspSubelementSubarray.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_testMode_decorators
    def test_testMode(self, device_under_test):
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_testMode) ENABLED START #
        assert device_under_test.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_testMode

    def test_scanID(self, device_under_test, tango_change_event_helper):
        """
        Test for scanID.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        device_under_test.On()

        device_state_callback.assert_next_change_event(DevState.ON)
        assert device_under_test.state() == DevState.ON

        assert device_under_test.scanID == 0

    # PROTECTED REGION ID(CspSubelementSubarray.test_sdpDestinationAddresses_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_sdpDestinationAddresses_decorators
    def test_sdpDestinationAddresses(self, device_under_test):
        """
        Test for sdpDestinationAddresses.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_sdpDestinationAddresses) ENABLED START #
        addresses_dict = {"outputHost": [], "outputMac": [], "outputPort": []}
        device_under_test.sdpDestinationAddresses = json.dumps(addresses_dict)
        assert device_under_test.sdpDestinationAddresses == json.dumps(addresses_dict)
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_sdpDestinationAddresses

    # PROTECTED REGION ID(CspSubelementSubarray.test_sdpLinkActive_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_sdpLinkActive_decorators
    def test_sdpLinkActivity(self, device_under_test):
        """
        Test for sdpLinkActive.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_sdpLinkActive) ENABLED START #
        actual = device_under_test.sdpLinkActive
        n_links = len(actual)
        expected = [False for i in range(0, n_links)]
        assert all([a == b for a, b in zip(actual, expected)])
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_sdpLinkActive

    # PROTECTED REGION ID(CspSubelementSubarray.test_outputDataRateToSdp_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_outputDataRateToSdp_decorators
    def test_outputDataRateToSdp(self, device_under_test):
        """
        Test for outputDataRateToSdp.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_outputDataRateToSdp) ENABLED START #
        assert device_under_test.outputDataRateToSdp == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_outputDataRateToSdp

    # PROTECTED REGION ID(CspSubelementSubarray.test_listOfDevicesCompletedTasks_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_listOfDevicesCompletedTasks_decorators
    def test_listOfDevicesCompletedTasks(self, device_under_test):
        """
        Test for listOfDevicesCompletedTasks.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_listOfDevicesCompletedTasks) ENABLED START #
        attr_value_as_dict = json.loads(device_under_test.listOfDevicesCompletedTasks)
        assert not bool(attr_value_as_dict)
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_listOfDevicesCompletedTasks

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_decorators

    # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesMaximumDuration_decorators
    def test_assignResourcesMaximumDuration(self, device_under_test):
        """
        Test for assignResourcesMaximumDuration.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesMaximumDuration) ENABLED START #
        device_under_test.assignResourcesMaximumDuration = 5
        assert device_under_test.assignResourcesMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesMaximumDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_configureScanMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_configureScanMeasuredDuration_decorators
    def test_configureScanMeasuredDuration(self, device_under_test):
        """
        Test for configureScanMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_configureScanMeasuredDuration) ENABLED START #
        assert device_under_test.configureScanMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_configureScanMeasuredDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_configurationProgress_decorators
    def test_configurationProgress(self, device_under_test):
        """
        Test for configurationProgress.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_configurationProgress) ENABLED START #
        assert device_under_test.configurationProgress == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_configurationProgress

    # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesMeasuredDuration_decorators
    def test_assignResourcesMeasuredDuration(self, device_under_test):
        """
        Test for assignResourcesMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesMeasuredDuration) ENABLED START #
        assert device_under_test.assignResourcesMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesMeasuredDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesProgress_decorators
    def test_assignResourcesProgress(self, device_under_test):
        """
        Test for assignResourcesProgress.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_assignResourcesProgress) ENABLED START #
        assert device_under_test.assignResourcesProgress == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_assignResourcesProgress

    # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesMaximumDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesMaximumDuration_decorators
    def test_releaseResourcesMaximumDuration(self, device_under_test):
        """
        Test for releaseResourcesMaximumDuration.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesMaximumDuration) ENABLED START #
        device_under_test.releaseResourcesMaximumDuration = 5
        assert device_under_test.releaseResourcesMaximumDuration == 5
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesMaximumDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesMeasuredDuration_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesMeasuredDuration_decorators
    def test_releaseResourcesMeasuredDuration(self, device_under_test):
        """
        Test for releaseResourcesMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesMeasuredDuration) ENABLED START #
        assert device_under_test.releaseResourcesMeasuredDuration == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesMeasuredDuration

    # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesProgress_decorators
    def test_releaseResourcesProgress(self, device_under_test):
        """
        Test for releaseResourcesProgress.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_releaseResourcesProgress) ENABLED START #
        assert device_under_test.releaseResourcesProgress == 0
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_releaseResourcesProgress

    # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag_decorators
    def test_configureScanTimeoutExpiredFlag(self, device_under_test):
        """
        Test for timeoutExpiredFlag.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag) ENABLED START #
        assert not device_under_test.configureScanTimeoutExpiredFlag
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag

    # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag_decorators
    def test_assignResourcesTimeoutExpiredFlag(self, device_under_test):
        """
        Test for timeoutExpiredFlag.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag) ENABLED START #
        assert not device_under_test.assignResourcesTimeoutExpiredFlag
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag

    # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag_decorators
    def test_releaseResourcesTimeoutExpiredFlag(self, device_under_test):
        """
        Test for timeoutExpiredFlag.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_timeoutExpiredFlag) ENABLED START #
        assert not device_under_test.releaseResourcesTimeoutExpiredFlag
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_timeoutExpiredFlag

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_decorators
    @pytest.mark.parametrize("command_alias", ["Configure", "ConfigureScan"])
    def test_ConfigureScan_and_GoToIdle(
        self, device_under_test, tango_change_event_helper, command_alias
    ):
        """
        Test for ConfigureScan.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        :param command_alias: name of the specific command being tested.
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan) ENABLED START #
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
        obs_state_callback.assert_next_change_event(ObsState.EMPTY)

        [[result_code], [command_id]] = device_under_test.AssignResources(
            json.dumps([1, 2, 3])
        )

        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.RESOURCING)

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        command_result_callback.assert_next_change_event(
            (
                command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            )
        )

        # TODO: Everything above here is just to turn on the device, assign it some
        # resources, and clear the queue attributes. We need a better way to handle
        # this.
        assert device_under_test.configurationId == ""

        configuration_id = "sbi-mvp01-20200325-00002"
        [[result_code], [command_id]] = device_under_test.command_inout(
            command_alias, json.dumps({"id": configuration_id})
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

        assert device_under_test.configurationId == configuration_id
        assert device_under_test.lastScanConfiguration == json.dumps(
            {"id": configuration_id}
        )

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

        assert device_under_test.configurationID == ""
        assert device_under_test.lastScanConfiguration == ""
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state_decorators
    def test_ConfigureScan_when_in_wrong_state(self, device_under_test):
        """
        Test for ConfigureScan when the device is in wrong state.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state) ENABLED START #
        # The device in in OFF/EMPTY state, not valid to invoke ConfigureScan.
        with pytest.raises(
            DevFailed,
            match="ConfigureScan command not permitted in observation state EMPTY",
        ):
            device_under_test.ConfigureScan('{"id":"sbi-mvp01-20200325-00002"}')
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_when_in_wrong_state

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key_decorators) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key_decorators
    def test_ConfigureScan_with_wrong_configId_key(
        self, device_under_test, tango_change_event_helper
    ):
        """
        Test that ConfigureScan handles a wrong configuration id key.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key) ENABLED START #

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
        obs_state_callback.assert_next_change_event(ObsState.EMPTY)

        [[result_code], [command_id]] = device_under_test.AssignResources(
            json.dumps([1, 2, 3])
        )

        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.RESOURCING)

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        command_result_callback.assert_next_change_event(
            (
                command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            )
        )

        wrong_configuration = '{"subid":"sbi-mvp01-20200325-00002"}'
        result_code, _ = device_under_test.ConfigureScan(wrong_configuration)
        assert result_code == ResultCode.FAILED
        assert device_under_test.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_wrong_configId_key

    # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error) ENABLED START #
    # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error_decorators
    def test_ConfigureScan_with_json_syntax_error(
        self, device_under_test, tango_change_event_helper
    ):
        """
        Test for ConfigureScan when syntax error in json configuration.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        # PROTECTED REGION ID(CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error) ENABLED START #
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
        obs_state_callback.assert_next_change_event(ObsState.EMPTY)

        [[result_code], [command_id]] = device_under_test.AssignResources(
            json.dumps([1, 2, 3])
        )

        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.RESOURCING)

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        command_result_callback.assert_next_change_event(
            (
                command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            )
        )

        result_code, _ = device_under_test.ConfigureScan('{"foo": 1,}')
        assert result_code == ResultCode.FAILED
        assert device_under_test.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  CspSubelementSubarray.test_ConfigureScan_with_json_syntax_error
