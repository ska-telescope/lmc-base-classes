#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKASubarray project
#
#
#
#########################################################################################
"""Contain the tests for the SKASubarray."""

import json
import re
import pytest

from tango import DevState, DevFailed

# PROTECTED REGION ID(SKASubarray.test_additional_imports) ENABLED START #
from ska_tango_base import SKASubarray
from ska_tango_base.base import OpStateModel
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    ObsMode,
    ObsState,
    SimulationMode,
    TestMode,
)
from ska_tango_base.faults import CommandError
from ska_tango_base.subarray import (
    ReferenceSubarrayComponentManager,
    SubarrayObsStateModel,
)

# PROTECTED REGION END #    //  SKASubarray.test_additional_imports


class TestSKASubarray:
    """Test cases for SKASubarray device."""

    @pytest.fixture(scope="class")
    def device_properties(self):
        """Fixture that returns properties of the device under test."""
        return {
            "CapabilityTypes": ["BAND1", "BAND2"],
            "LoggingTargetsDefault": "",
            "GroupDefinitions": "",
            "SkaLevel": "4",
            "SubID": "1",
        }

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Specify device configuration, including properties and memorized attributes.

        This implementation provides a concrete subclass of the device
        class under test, some properties, and a memorized value for
        adminMode.
        """
        return {
            "device": SKASubarray,
            "component_manager_patch": lambda self: ReferenceSubarrayComponentManager(
                self.op_state_model,
                self.obs_state_model,
                self.CapabilityTypes,
                logger=self.logger,
                num_workers=3,
                max_queue_size=5,
                push_change_event=self.push_change_event,
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip(reason="Not implemented")
    def test_properties(self, device_under_test):
        """Test device properties."""
        # PROTECTED REGION ID(SKASubarray.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKASubarray.test_properties
        """Test the Tango device properties of this subarray device."""

    # PROTECTED REGION ID(SKASubarray.test_Abort_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Abort_decorators
    def test_Abort(self, device_under_test, tango_change_event_helper):
        """Test for Abort."""
        # PROTECTED REGION ID(SKASubarray.test_Abort) ENABLED START #

        result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )

        on_tr = device_under_test.On()
        result_callback.wait_for_lrc_id(on_tr.unique_id)

        assign_tr = device_under_test.AssignResources(json.dumps(["BAND1"]))
        result_callback.wait_for_lrc_id(assign_tr.unique_id)

        device_under_test.Configure('{"BAND1": 2}')

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.READY)

        assert device_under_test.Abort() == [
            [ResultCode.OK],
            ["Abort command completed OK"],
        ]
        obs_state_callback.assert_calls([ObsState.ABORTING, ObsState.ABORTED])
        # PROTECTED REGION END #    //  SKASubarray.test_Abort

    # PROTECTED REGION ID(SKASubarray.test_Configure_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Configure_decorators
    def test_Configure(self, device_under_test, tango_change_event_helper):
        """Test for Configure."""
        # PROTECTED REGION ID(SKASubarray.test_Configure) ENABLED START #
        result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )

        on_tr = device_under_test.On()
        result_callback.wait_for_lrc_id(on_tr.unique_id)
        assign_tr = device_under_test.AssignResources(json.dumps(["BAND1"]))
        result_callback.wait_for_lrc_id(assign_tr.unique_id)

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.IDLE)

        device_under_test.Configure('{"BAND1": 2}')

        obs_state_callback.assert_calls([ObsState.CONFIGURING, ObsState.READY])
        assert device_under_test.obsState == ObsState.READY
        assert device_under_test.configuredCapabilities == ("BAND1:2", "BAND2:0")
        # PROTECTED REGION END #    //  SKASubarray.test_Configure

    # PROTECTED REGION ID(SKASubarray.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test, tango_change_event_helper):
        """Test for GetVersionInfo."""
        # PROTECTED REGION ID(SKASubarray.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            f"['{device_under_test.info().dev_class}, ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            "A set of generic base devices for SKA Telescope.']"
        )
        result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )

        ver_info_tr = device_under_test.GetVersionInfo()
        result_callback.wait_for_lrc_id(ver_info_tr.unique_id)

        versionInfo = device_under_test.longRunningCommandResult[2]
        assert (re.match(versionPattern, versionInfo)) is not None
        # PROTECTED REGION END #    //  SKASubarray.test_GetVersionInfo

    # PROTECTED REGION ID(SKASubarray.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Status_decorators
    def test_Status(self, device_under_test):
        """Test for Status."""
        # PROTECTED REGION ID(SKASubarray.test_Status) ENABLED START #
        assert device_under_test.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKASubarray.test_Status

    # PROTECTED REGION ID(SKASubarray.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_State_decorators
    def test_State(self, device_under_test):
        """Test for State."""
        # PROTECTED REGION ID(SKASubarray.test_State) ENABLED START #
        assert device_under_test.State() == DevState.OFF
        # PROTECTED REGION END #    //  SKASubarray.test_State

    # PROTECTED REGION ID(SKASubarray.test_AssignResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_AssignResources_decorators
    def test_AssignResources(self, device_under_test, tango_change_event_helper):
        """Test for AssignResources."""
        # PROTECTED REGION ID(SKASubarray.test_AssignResources) ENABLED START #

        result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )

        on_tr = device_under_test.On()
        result_callback.wait_for_lrc_id(on_tr.unique_id)

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.EMPTY)

        resources_to_assign = ["BAND1", "BAND2"]
        assign_tr = device_under_test.AssignResources(json.dumps(resources_to_assign))
        result_callback.wait_for_lrc_id(assign_tr.unique_id)

        obs_state_callback.assert_calls([ObsState.RESOURCING, ObsState.IDLE])
        assert device_under_test.ObsState == ObsState.IDLE
        assert list(device_under_test.assignedResources) == resources_to_assign

        device_under_test.ReleaseAllResources()
        obs_state_callback.assert_calls([ObsState.RESOURCING, ObsState.EMPTY])
        assert device_under_test.ObsState == ObsState.EMPTY

        with pytest.raises(DevFailed):
            device_under_test.AssignResources("Invalid JSON")
        # PROTECTED REGION END #    //  SKASubarray.test_AssignResources

    # PROTECTED REGION ID(SKASubarray.test_EndSB_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_EndSB_decorators
    def test_End(self, device_under_test, tango_change_event_helper):
        """Test for EndSB."""
        # PROTECTED REGION ID(SKASubarray.test_EndSB) ENABLED START #
        result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )

        on_tr = device_under_test.On()
        result_callback.wait_for_lrc_id(on_tr.unique_id)

        assign_tr = device_under_test.AssignResources(json.dumps(["BAND1"]))
        result_callback.wait_for_lrc_id(assign_tr.unique_id)

        device_under_test.Configure('{"BAND1": 2}')

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.READY)

        assert device_under_test.End() == [
            [ResultCode.OK],
            ["End command completed OK"],
        ]
        obs_state_callback.assert_call(ObsState.IDLE)

        # PROTECTED REGION END #    //  SKASubarray.test_EndSB

    # PROTECTED REGION ID(SKASubarray.test_EndScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_EndScan_decorators
    def test_EndScan(self, device_under_test, tango_change_event_helper):
        """Test for EndScan."""
        # PROTECTED REGION ID(SKASubarray.test_EndScan) ENABLED START #
        result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )

        on_tr = device_under_test.On()
        result_callback.wait_for_lrc_id(on_tr.unique_id)

        assign_tr = device_under_test.AssignResources(json.dumps(["BAND1"]))
        result_callback.wait_for_lrc_id(assign_tr.unique_id)

        device_under_test.Configure('{"BAND1": 2}')
        device_under_test.Scan('{"id": 123}')

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.SCANNING)

        assert device_under_test.EndScan() == [
            [ResultCode.OK],
            ["EndScan command completed OK"],
        ]

        obs_state_callback.assert_call(ObsState.READY)

        # PROTECTED REGION END #    //  SKASubarray.test_EndScan

    # PROTECTED REGION ID(SKASubarray.test_ReleaseAllResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_ReleaseAllResources_decorators
    def test_ReleaseAllResources(self, device_under_test, tango_change_event_helper):
        """Test for ReleaseAllResources."""
        # PROTECTED REGION ID(SKASubarray.test_ReleaseAllResources) ENABLED START #
        # assert device_under_test.ReleaseAllResources() == [""]
        result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )

        on_tr = device_under_test.On()
        result_callback.wait_for_lrc_id(on_tr.unique_id)

        assign_tr = device_under_test.AssignResources(json.dumps(["BAND1", "BAND2"]))
        result_callback.wait_for_lrc_id(assign_tr.unique_id)

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.IDLE)

        device_under_test.ReleaseAllResources()

        obs_state_callback.assert_calls([ObsState.RESOURCING, ObsState.EMPTY])
        assert device_under_test.assignedResources is None
        # PROTECTED REGION END #    //  SKASubarray.test_ReleaseAllResources

    # PROTECTED REGION ID(SKASubarray.test_ReleaseResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_ReleaseResources_decorators
    def test_ReleaseResources(self, device_under_test, tango_change_event_helper):
        """Test for ReleaseResources."""
        # PROTECTED REGION ID(SKASubarray.test_ReleaseResources) ENABLED START #
        result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )

        on_tr = device_under_test.On()
        result_callback.wait_for_lrc_id(on_tr.unique_id)

        assign_tr = device_under_test.AssignResources(json.dumps(["BAND1", "BAND2"]))
        result_callback.wait_for_lrc_id(assign_tr.unique_id)

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.IDLE)

        device_under_test.ReleaseResources(json.dumps(["BAND1"]))

        obs_state_callback.assert_calls([ObsState.RESOURCING, ObsState.IDLE])
        assert device_under_test.ObsState == ObsState.IDLE
        assert device_under_test.assignedResources == ("BAND2",)
        # PROTECTED REGION END #    //  SKASubarray.test_ReleaseResources

    # PROTECTED REGION ID(SKASubarray.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Reset_decorators
    def test_ObsReset(self, device_under_test, tango_change_event_helper):
        """Test for Reset."""
        # PROTECTED REGION ID(SKASubarray.test_Reset) ENABLED START #
        result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )

        on_tr = device_under_test.On()
        result_callback.wait_for_lrc_id(on_tr.unique_id)

        assign_tr = device_under_test.AssignResources(json.dumps(["BAND1"]))
        result_callback.wait_for_lrc_id(assign_tr.unique_id)

        device_under_test.Configure('{"BAND1": 2}')
        device_under_test.Abort()

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.ABORTED)

        assert device_under_test.ObsReset() == [
            [ResultCode.OK],
            ["ObsReset command completed OK"],
        ]

        obs_state_callback.assert_calls([ObsState.RESETTING, ObsState.IDLE])
        assert device_under_test.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  SKASubarray.test_Reset

    # PROTECTED REGION ID(SKASubarray.test_Scan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Scan_decorators
    def test_Scan(self, device_under_test, tango_change_event_helper):
        """Test for Scan."""
        # PROTECTED REGION ID(SKASubarray.test_Scan) ENABLED START #
        result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )

        on_tr = device_under_test.On()
        result_callback.wait_for_lrc_id(on_tr.unique_id)

        assign_tr = device_under_test.AssignResources(json.dumps(["BAND1"]))
        result_callback.wait_for_lrc_id(assign_tr.unique_id)

        device_under_test.Configure('{"BAND1": 2}')

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.READY)

        assert device_under_test.Scan('{"id": 123}') == [
            [ResultCode.STARTED],
            ["Scan command started"],
        ]

        obs_state_callback.assert_call(ObsState.SCANNING)
        assert device_under_test.obsState == ObsState.SCANNING

        device_under_test.EndScan()
        with pytest.raises(DevFailed):
            device_under_test.Scan("Invalid JSON")
        # PROTECTED REGION END #    //  SKASubarray.test_Scan

    # PROTECTED REGION ID(SKASubarray.test_activationTime_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_activationTime_decorators
    def test_activationTime(self, device_under_test):
        """Test for activationTime."""
        # PROTECTED REGION ID(SKASubarray.test_activationTime) ENABLED START #
        assert device_under_test.activationTime == 0.0
        # PROTECTED REGION END #    //  SKASubarray.test_activationTime

    # PROTECTED REGION ID(SKASubarray.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_adminMode_decorators
    def test_adminMode(self, device_under_test, tango_change_event_helper):
        """Test for adminMode."""
        # PROTECTED REGION ID(SKASubarray.test_adminMode) ENABLED START #
        assert device_under_test.state() == DevState.OFF
        assert device_under_test.adminMode == AdminMode.ONLINE

        admin_mode_callback = tango_change_event_helper.subscribe("adminMode")
        op_state_callback = tango_change_event_helper.subscribe("state")
        admin_mode_callback.assert_call(AdminMode.ONLINE)
        op_state_callback.assert_call(DevState.OFF)

        device_under_test.adminMode = AdminMode.OFFLINE
        assert device_under_test.state() == DevState.DISABLE
        assert device_under_test.adminMode == AdminMode.OFFLINE
        admin_mode_callback.assert_call(AdminMode.OFFLINE)
        op_state_callback.assert_call(DevState.DISABLE)

        device_under_test.adminMode = AdminMode.MAINTENANCE
        assert device_under_test.state() == DevState.OFF
        assert device_under_test.adminMode == AdminMode.MAINTENANCE
        admin_mode_callback.assert_call(AdminMode.MAINTENANCE)
        op_state_callback.assert_calls([DevState.UNKNOWN, DevState.OFF])
        # PROTECTED REGION END #    //  SKASubarray.test_adminMode

    # PROTECTED REGION ID(SKASubarray.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_buildState_decorators
    def test_buildState(self, device_under_test):
        """Test for buildState."""
        # PROTECTED REGION ID(SKASubarray.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, device_under_test.buildState)) is not None
        # PROTECTED REGION END #    //  SKASubarray.test_buildState

    # PROTECTED REGION ID(SKASubarray.test_configurationDelayExpected_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_configurationDelayExpected_decorators
    def test_configurationDelayExpected(self, device_under_test):
        """Test for configurationDelayExpected."""
        # PROTECTED REGION ID(SKASubarray.test_configurationDelayExpected) ENABLED START #
        assert device_under_test.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SKASubarray.test_configurationDelayExpected

    # PROTECTED REGION ID(SKASubarray.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_configurationProgress_decorators
    def test_configurationProgress(self, device_under_test):
        """Test for configurationProgress."""
        # PROTECTED REGION ID(SKASubarray.test_configurationProgress) ENABLED START #
        assert device_under_test.configurationProgress == 0
        # PROTECTED REGION END #    //  SKASubarray.test_configurationProgress

    # PROTECTED REGION ID(SKASubarray.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_controlMode_decorators
    def test_controlMode(self, device_under_test):
        """Test for controlMode."""
        # PROTECTED REGION ID(SKASubarray.test_controlMode) ENABLED START #
        assert device_under_test.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKASubarray.test_controlMode

    # PROTECTED REGION ID(SKASubarray.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_healthState_decorators
    def test_healthState(self, device_under_test):
        """Test for healthState."""
        # PROTECTED REGION ID(SKASubarray.test_healthState) ENABLED START #
        assert device_under_test.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SKASubarray.test_healthState

    # PROTECTED REGION ID(SKASubarray.test_obsMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_obsMode_decorators
    def test_obsMode(self, device_under_test):
        """Test for obsMode."""
        # PROTECTED REGION ID(SKASubarray.test_obsMode) ENABLED START #
        assert device_under_test.obsMode == ObsMode.IDLE
        # PROTECTED REGION END #    //  SKASubarray.test_obsMode

    # PROTECTED REGION ID(SKASubarray.test_obsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_obsState_decorators
    def test_obsState(self, device_under_test):
        """Test for obsState."""
        # PROTECTED REGION ID(SKASubarray.test_obsState) ENABLED START #
        assert device_under_test.obsState == ObsState.EMPTY
        # PROTECTED REGION END #    //  SKASubarray.test_obsState

    # PROTECTED REGION ID(SKASubarray.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_simulationMode_decorators
    def test_simulationMode(self, device_under_test):
        """Test for simulationMode."""
        # PROTECTED REGION ID(SKASubarray.test_simulationMode) ENABLED START #
        assert device_under_test.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKASubarray.test_simulationMode

    # PROTECTED REGION ID(SKASubarray.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_testMode_decorators
    def test_testMode(self, device_under_test):
        """Test for testMode."""
        # PROTECTED REGION ID(SKASubarray.test_testMode) ENABLED START #
        assert device_under_test.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKASubarray.test_testMode

    # PROTECTED REGION ID(SKASubarray.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_versionId_decorators
    def test_versionId(self, device_under_test):
        """Test for versionId."""
        # PROTECTED REGION ID(SKASubarray.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  SKASubarray.test_versionId

    # PROTECTED REGION ID(SKASubarray.test_assignedResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_assignedResources_decorators
    def test_assignedResources(self, device_under_test, tango_change_event_helper):
        """Test for assignedResources."""
        # PROTECTED REGION ID(SKASubarray.test_assignedResources) ENABLED START #
        result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )

        on_tr = device_under_test.On()
        result_callback.wait_for_lrc_id(on_tr.unique_id)

        assert device_under_test.assignedResources is None
        # PROTECTED REGION END #    //  SKASubarray.test_assignedResources

    # PROTECTED REGION ID(SKASubarray.test_configuredCapabilities_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_configuredCapabilities_decorators
    def test_configuredCapabilities(self, device_under_test, tango_change_event_helper):
        """Test for configuredCapabilities."""
        # PROTECTED REGION ID(SKASubarray.test_configuredCapabilities) ENABLED START #
        result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )

        on_tr = device_under_test.On()
        result_callback.wait_for_lrc_id(on_tr.unique_id)

        assert device_under_test.configuredCapabilities == ("BAND1:0", "BAND2:0")
        # PROTECTED REGION END #    //  SKASubarray.test_configuredCapabilities


class TestSKASubarray_commands:
    """This class contains tests of SKASubarray commands."""

    @pytest.fixture
    def op_state_model(self, logger):
        """Yield a new OpStateModel for testing."""
        yield OpStateModel(logger)

    @pytest.fixture
    def subarray_state_model(self, logger):
        """Yield a new SubarrayObsStateModel for testing."""
        yield SubarrayObsStateModel(logger)

    @pytest.fixture()
    def component_manager(self, op_state_model, subarray_state_model, logger, mocker):
        """
        Fixture that returns the component manager under test.

        :param mock_op_state_model: a mock state model for testing
        :param logger: a logger for the component manager

        :return: the component manager under test
        """
        mock_capability_types = ["foo", "bah"]
        return ReferenceSubarrayComponentManager(
            op_state_model, subarray_state_model, mock_capability_types, logger=logger
        )

    def test_AssignCommand(
        self, component_manager, op_state_model, subarray_state_model
    ):
        """Test for SKASubarray.AssignResourcesCommand."""
        op_state_model._straight_to_state("DISABLE")
        component_manager.start_communicating()
        component_manager.on()

        assign_resources = SKASubarray.AssignResourcesCommand(
            component_manager,
            op_state_model,
            subarray_state_model,
        )
        for obs_state_name in [
            "RESOURCING_EMPTY",
            "RESOURCING_IDLE",
            "CONFIGURING_IDLE",
            "CONFIGURING_READY",
            "READY",
            "SCANNING",
            "ABORTING",
            "ABORTED",
            "RESETTING",
            "RESTARTING",
            "FAULT",
        ]:
            subarray_state_model._straight_to_state(obs_state_name)
            prior_obs_state = subarray_state_model.obs_state
            assert not assign_resources.is_allowed()
            with pytest.raises(CommandError):
                assign_resources(["foo"])
            assert component_manager.assigned_resources == []
            assert subarray_state_model.obs_state == prior_obs_state

        # now push to empty, a state in which the command IS allowed
        subarray_state_model._straight_to_state("EMPTY")
        assert assign_resources.is_allowed(True)
        assert assign_resources(["foo"]) == (
            ResultCode.OK,
            "AssignResources command completed OK",
        )
        assert component_manager.assigned_resources == ["foo"]
        assert subarray_state_model.obs_state == ObsState.IDLE

        # AssignResources is still allowed in IDLE
        assert assign_resources.is_allowed()
        assert assign_resources(["bar"]) == (
            ResultCode.OK,
            "AssignResources command completed OK",
        )
        assert component_manager.assigned_resources == ["bar", "foo"]
        assert subarray_state_model.obs_state == ObsState.IDLE
