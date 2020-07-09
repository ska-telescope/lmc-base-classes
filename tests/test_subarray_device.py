#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKASubarray project
#
#
#
#########################################################################################
"""Contain the tests for the SKASubarray."""

import itertools
import re
import pytest

from tango import DevState, DevFailed

# PROTECTED REGION ID(SKASubarray.test_additional_imports) ENABLED START #
from ska.base import SKASubarray, SKASubarrayResourceManager, SKASubarrayStateModel
from ska.base.commands import ResultCode
from ska.base.control_model import (
    AdminMode, ControlMode, HealthState, ObsMode, ObsState, SimulationMode, TestMode
)
from ska.base.faults import CommandError
# PROTECTED REGION END #    //  SKASubarray.test_additional_imports


@pytest.mark.usefixtures("tango_context", "initialize_device")
class TestSKASubarray(object):
    """Test case for packet generation."""

    properties = {
        'CapabilityTypes': '',
        'GroupDefinitions': '',
        'SkaLevel': '4',
        'LoggingTargetsDefault': '',
        'SubID': '',
        }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKASubarray.numpy = MagicMock()
        # PROTECTED REGION ID(SKASubarray.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKASubarray.test_mocking

    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(SKASubarray.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKASubarray.test_properties
        pass

    # PROTECTED REGION ID(SKASubarray.test_Abort_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Abort_decorators
    def test_Abort(self, tango_context, tango_change_event_helper):
        """Test for Abort"""
        # PROTECTED REGION ID(SKASubarray.test_Abort) ENABLED START #

        tango_context.device.On()
        tango_context.device.AssignResources('{"example": ["BAND1"]}')
        tango_context.device.Configure('{"BAND1": 2}')

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.READY)

        assert tango_context.device.Abort() == [
            [ResultCode.OK], ["Abort command completed OK"]
        ]
        obs_state_callback.assert_calls(
            [ObsState.ABORTING, ObsState.ABORTED]
        )
        # PROTECTED REGION END #    //  SKASubarray.test_Abort

    # PROTECTED REGION ID(SKASubarray.test_Configure_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Configure_decorators
    def test_Configure(self, tango_context, tango_change_event_helper):
        """Test for Configure"""
        # PROTECTED REGION ID(SKASubarray.test_Configure) ENABLED START #
        tango_context.device.On()
        tango_context.device.AssignResources('{"example": ["BAND1"]}')

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.IDLE)

        tango_context.device.Configure('{"BAND1": 2}')

        obs_state_callback.assert_calls(
            [ObsState.CONFIGURING, ObsState.READY]
        )
        assert tango_context.device.obsState == ObsState.READY
        assert tango_context.device.configuredCapabilities == ("BAND1:2", "BAND2:0")
        # PROTECTED REGION END #    //  SKASubarray.test_Configure

    # PROTECTED REGION ID(SKASubarray.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKASubarray.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'SKASubarray, lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  SKASubarray.test_GetVersionInfo

    # PROTECTED REGION ID(SKASubarray.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKASubarray.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKASubarray.test_Status

    # PROTECTED REGION ID(SKASubarray.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKASubarray.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.OFF
        # PROTECTED REGION END #    //  SKASubarray.test_State

    # PROTECTED REGION ID(SKASubarray.test_AssignResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_AssignResources_decorators
    def test_AssignResources(self, tango_context, tango_change_event_helper):
        """Test for AssignResources"""
        # PROTECTED REGION ID(SKASubarray.test_AssignResources) ENABLED START #
        tango_context.device.On()

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.EMPTY)

        tango_context.device.AssignResources('{"example": ["BAND1", "BAND2"]}')

        obs_state_callback.assert_calls(
            [ObsState.RESOURCING, ObsState.IDLE]
        )
        assert tango_context.device.ObsState == ObsState.IDLE
        assert tango_context.device.assignedResources == ('BAND1', 'BAND2')

        tango_context.device.ReleaseAllResources()
        obs_state_callback.assert_calls(
            [ObsState.RESOURCING, ObsState.EMPTY]
        )
        assert tango_context.device.ObsState == ObsState.EMPTY

        with pytest.raises(DevFailed):
            tango_context.device.AssignResources('Invalid JSON')
        # PROTECTED REGION END #    //  SKASubarray.test_AssignResources

    # PROTECTED REGION ID(SKASubarray.test_EndSB_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_EndSB_decorators
    def test_End(self, tango_context, tango_change_event_helper):
        """Test for EndSB"""
        # PROTECTED REGION ID(SKASubarray.test_EndSB) ENABLED START #
        tango_context.device.On()
        tango_context.device.AssignResources('{"example": ["BAND1"]}')
        tango_context.device.Configure('{"BAND1": 2}')

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.READY)

        assert tango_context.device.End() == [
            [ResultCode.OK], ["End command completed OK"]
        ]
        obs_state_callback.assert_call(ObsState.IDLE)

        # PROTECTED REGION END #    //  SKASubarray.test_EndSB

    # PROTECTED REGION ID(SKASubarray.test_EndScan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_EndScan_decorators
    def test_EndScan(self, tango_context, tango_change_event_helper):
        """Test for EndScan"""
        # PROTECTED REGION ID(SKASubarray.test_EndScan) ENABLED START #
        tango_context.device.On()
        tango_context.device.AssignResources('{"example": ["BAND1"]}')
        tango_context.device.Configure('{"BAND1": 2}')
        tango_context.device.Scan('{"id": 123}')

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.SCANNING)

        assert tango_context.device.EndScan() == [
            [ResultCode.OK], ["EndScan command completed OK"]
        ]

        obs_state_callback.assert_call(ObsState.READY)

        # PROTECTED REGION END #    //  SKASubarray.test_EndScan

    # PROTECTED REGION ID(SKASubarray.test_ReleaseAllResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_ReleaseAllResources_decorators
    def test_ReleaseAllResources(self, tango_context, tango_change_event_helper):
        """Test for ReleaseAllResources"""
        # PROTECTED REGION ID(SKASubarray.test_ReleaseAllResources) ENABLED START #
        # assert tango_context.device.ReleaseAllResources() == [""]
        tango_context.device.On()
        tango_context.device.AssignResources('{"example": ["BAND1", "BAND2"]}')

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.IDLE)

        tango_context.device.ReleaseAllResources()

        obs_state_callback.assert_calls(
            [ObsState.RESOURCING, ObsState.EMPTY]
        )
        assert tango_context.device.assignedResources is None
        # PROTECTED REGION END #    //  SKASubarray.test_ReleaseAllResources

    # PROTECTED REGION ID(SKASubarray.test_ReleaseResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_ReleaseResources_decorators
    def test_ReleaseResources(self, tango_context, tango_change_event_helper):
        """Test for ReleaseResources"""
        # PROTECTED REGION ID(SKASubarray.test_ReleaseResources) ENABLED START #
        tango_context.device.On()
        tango_context.device.AssignResources('{"example": ["BAND1", "BAND2"]}')

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.IDLE)

        tango_context.device.ReleaseResources('{"example": ["BAND1"]}')

        obs_state_callback.assert_calls(
            [ObsState.RESOURCING, ObsState.IDLE]
        )
        assert tango_context.device.ObsState == ObsState.IDLE
        assert tango_context.device.assignedResources == ('BAND2',)
        # PROTECTED REGION END #    //  SKASubarray.test_ReleaseResources

    # PROTECTED REGION ID(SKASubarray.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Reset_decorators
    def test_ObsReset(self, tango_context, tango_change_event_helper):
        """Test for Reset"""
        # PROTECTED REGION ID(SKASubarray.test_Reset) ENABLED START #
        tango_context.device.On()
        tango_context.device.AssignResources('{"example": ["BAND1"]}')
        tango_context.device.Configure('{"BAND1": 2}')
        tango_context.device.Abort()

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.ABORTED)

        assert tango_context.device.ObsReset() == [
            [ResultCode.OK], ["ObsReset command completed OK"]
        ]

        obs_state_callback.assert_calls(
            [ObsState.RESETTING, ObsState.IDLE]
        )
        assert tango_context.device.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  SKASubarray.test_Reset

    # PROTECTED REGION ID(SKASubarray.test_Scan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Scan_decorators
    def test_Scan(self, tango_context, tango_change_event_helper):
        """Test for Scan"""
        # PROTECTED REGION ID(SKASubarray.test_Scan) ENABLED START #
        tango_context.device.On()
        tango_context.device.AssignResources('{"example": ["BAND1"]}')
        tango_context.device.Configure('{"BAND1": 2}')

        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_call(ObsState.READY)

        assert tango_context.device.Scan('{"id": 123}') == [
            [ResultCode.STARTED], ["Scan command STARTED - config {'id': 123}"]
        ]

        obs_state_callback.assert_call(ObsState.SCANNING)
        assert tango_context.device.obsState == ObsState.SCANNING

        tango_context.device.EndScan()
        with pytest.raises(DevFailed):
            tango_context.device.Scan('Invalid JSON')
        # PROTECTED REGION END #    //  SKASubarray.test_Scan

    # PROTECTED REGION ID(SKASubarray.test_activationTime_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_activationTime_decorators
    def test_activationTime(self, tango_context):
        """Test for activationTime"""
        # PROTECTED REGION ID(SKASubarray.test_activationTime) ENABLED START #
        assert tango_context.device.activationTime == 0.0
        # PROTECTED REGION END #    //  SKASubarray.test_activationTime

    # PROTECTED REGION ID(SKASubarray.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_adminMode_decorators
    def test_adminMode(self, tango_context, tango_change_event_helper):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKASubarray.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.MAINTENANCE
        assert tango_context.device.state() == DevState.OFF

        admin_mode_callback = tango_change_event_helper.subscribe("adminMode")
        dev_state_callback = tango_change_event_helper.subscribe("state")
        admin_mode_callback.assert_call(AdminMode.MAINTENANCE)
        dev_state_callback.assert_call(DevState.OFF)

        tango_context.device.adminMode = AdminMode.OFFLINE
        assert tango_context.device.adminMode == AdminMode.OFFLINE
        assert tango_context.device.state() == DevState.DISABLE
        admin_mode_callback.assert_call(AdminMode.OFFLINE)
        dev_state_callback.assert_call(DevState.DISABLE)

        # PROTECTED REGION END #    //  SKASubarray.test_adminMode

    # PROTECTED REGION ID(SKASubarray.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKASubarray.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  SKASubarray.test_buildState

    # PROTECTED REGION ID(SKASubarray.test_configurationDelayExpected_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_configurationDelayExpected_decorators
    def test_configurationDelayExpected(self, tango_context):
        """Test for configurationDelayExpected"""
        # PROTECTED REGION ID(SKASubarray.test_configurationDelayExpected) ENABLED START #
        assert tango_context.device.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SKASubarray.test_configurationDelayExpected

    # PROTECTED REGION ID(SKASubarray.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_configurationProgress_decorators
    def test_configurationProgress(self, tango_context):
        """Test for configurationProgress"""
        # PROTECTED REGION ID(SKASubarray.test_configurationProgress) ENABLED START #
        assert tango_context.device.configurationProgress == 0
        # PROTECTED REGION END #    //  SKASubarray.test_configurationProgress

    # PROTECTED REGION ID(SKASubarray.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKASubarray.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKASubarray.test_controlMode

    # PROTECTED REGION ID(SKASubarray.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKASubarray.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SKASubarray.test_healthState

    # PROTECTED REGION ID(SKASubarray.test_obsMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_obsMode_decorators
    def test_obsMode(self, tango_context):
        """Test for obsMode"""
        # PROTECTED REGION ID(SKASubarray.test_obsMode) ENABLED START #
        assert tango_context.device.obsMode == ObsMode.IDLE
        # PROTECTED REGION END #    //  SKASubarray.test_obsMode

    # PROTECTED REGION ID(SKASubarray.test_obsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_obsState_decorators
    def test_obsState(self, tango_context):
        """Test for obsState"""
        # PROTECTED REGION ID(SKASubarray.test_obsState) ENABLED START #
        assert tango_context.device.obsState == ObsState.EMPTY
        # PROTECTED REGION END #    //  SKASubarray.test_obsState

    # PROTECTED REGION ID(SKASubarray.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKASubarray.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKASubarray.test_simulationMode

    # PROTECTED REGION ID(SKASubarray.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKASubarray.test_testMode) ENABLED START #
        assert tango_context.device.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKASubarray.test_testMode

    # PROTECTED REGION ID(SKASubarray.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKASubarray.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  SKASubarray.test_versionId

    # PROTECTED REGION ID(SKASubarray.test_assignedResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_assignedResources_decorators
    def test_assignedResources(self, tango_context):
        """Test for assignedResources"""
        # PROTECTED REGION ID(SKASubarray.test_assignedResources) ENABLED START #
        assert tango_context.device.assignedResources is None
        # PROTECTED REGION END #    //  SKASubarray.test_assignedResources

    # PROTECTED REGION ID(SKASubarray.test_configuredCapabilities_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_configuredCapabilities_decorators
    def test_configuredCapabilities(self, tango_context):
        """Test for configuredCapabilities"""
        # PROTECTED REGION ID(SKASubarray.test_configuredCapabilities) ENABLED START #
        assert tango_context.device.configuredCapabilities == ("BAND1:0", "BAND2:0")
        # PROTECTED REGION END #    //  SKASubarray.test_configuredCapabilities

    @pytest.mark.parametrize(
        'state_under_test, action_under_test',
        itertools.product(
            [
                # not testing FAULT or OBSFAULT states because in the current
                # implementation the interface cannot be used to get the device
                # into these states
                "DISABLED", "OFF", "EMPTY", "IDLE", "READY", "SCANNING",
                "ABORTED",
            ],
            [
                # not testing 'reset' action because in the current
                # implementation the interface cannot be used to get the device
                # into a state from which 'reset' is a valid action
                "notfitted", "offline", "online", "maintenance", "on", "off",
                "assign", "release", "release (all)", "releaseall",
                "configure", "scan", "endscan", "end", "abort", "obsreset",
                "restart"]
        )
    )
    def test_state_machine(self, tango_context, state_under_test, action_under_test):
        """
        Test the subarray state machine: for a given initial state and
        an action, does execution of that action, from that initial
        state, yield the expected results? If the action was not allowed
        from that initial state, does the device raise a DevFailed
        exception? If the action was allowed, does it result in the
        correct state transition?
        """
        states = {
            "DISABLED":
                ([AdminMode.NOT_FITTED, AdminMode.OFFLINE], DevState.DISABLE, ObsState.EMPTY),
            "FAULT":  # not tested
                ([AdminMode.NOT_FITTED, AdminMode.OFFLINE, AdminMode.ONLINE, AdminMode.MAINTENANCE],
                 DevState.FAULT, ObsState.EMPTY),
            "OFF":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.OFF, ObsState.EMPTY),
            "EMPTY":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.EMPTY),
            "IDLE":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.IDLE),
            "READY":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.READY),
            "SCANNING":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.SCANNING),
            "ABORTED":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.ABORTED),
            "OBSFAULT":  # not tested
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.FAULT),
        }

        def assert_state(state):
            """
            Check that the device is in the state we think it should be in
            """
            (admin_modes, dev_state, obs_state) = states[state]
            assert tango_context.device.adminMode in admin_modes
            assert tango_context.device.state() == dev_state
            assert tango_context.device.obsState == obs_state

        actions = {
            "notfitted":
                lambda d: d.write_attribute("adminMode", AdminMode.NOT_FITTED),
            "offline":
                lambda d: d.write_attribute("adminMode", AdminMode.OFFLINE),
            "online":
                lambda d: d.write_attribute("adminMode", AdminMode.ONLINE),
            "maintenance":
                lambda d: d.write_attribute("adminMode", AdminMode.MAINTENANCE),
            "on":
                lambda d: d.On(),
            "off":
                lambda d: d.Off(),
            "reset":
                lambda d: d.Reset(),  # not tested
            "assign":
                lambda d: d.AssignResources('{"example": ["BAND1", "BAND2"]}'),
            "release":
                lambda d: d.ReleaseResources('{"example": ["BAND1"]}'),
            "release (all)":
                lambda d: d.ReleaseResources('{"example": ["BAND1", "BAND2"]}'),
            "releaseall":
                lambda d: d.ReleaseAllResources(),
            "configure":
                lambda d: d.Configure('{"BAND1": 2, "BAND2": 2}'),
            "scan":
                lambda d: d.Scan('{"id": 123}'),
            "endscan":
                lambda d: d.EndScan(),
            "end":
                lambda d: d.End(),
            "abort":
                lambda d: d.Abort(),
            "obsreset":
                lambda d: d.ObsReset(),
            "restart":
                lambda d: d.Restart(),
        }

        def perform_action(action):
            actions[action](tango_context.device)

        transitions = {
            ("DISABLED", "notfitted"): "DISABLED",
            ("DISABLED", "offline"): "DISABLED",
            ("DISABLED", "online"): "OFF",
            ("DISABLED", "maintenance"): "OFF",
            ("OFF", "notfitted"): "DISABLED",
            ("OFF", "offline"): "DISABLED",
            ("OFF", "online"): "OFF",
            ("OFF", "maintenance"): "OFF",
            ("OFF", "on"): "EMPTY",
            ("EMPTY", "off"): "OFF",
            ("EMPTY", "assign"): "IDLE",
            ("IDLE", "assign"): "IDLE",
            ("IDLE", "release"): "IDLE",
            ("IDLE", "release (all)"): "EMPTY",
            ("IDLE", "releaseall"): "EMPTY",
            ("IDLE", "configure"): "READY",
            ("IDLE", "abort"): "ABORTED",
            ("READY", "configure"): "READY",
            ("READY", "end"): "IDLE",
            ("READY", "abort"): "ABORTED",
            ("READY", "scan"): "SCANNING",
            ("SCANNING", "endscan"): "READY",
            ("SCANNING", "abort"): "ABORTED",
            ("ABORTED", "obsreset"): "IDLE",
            ("ABORTED", "restart"): "EMPTY",
        }

        setups = {
            "DISABLED":
                ['offline'],
            "OFF":
                [],
            "EMPTY":
                ['on'],
            "IDLE":
                ['on', 'assign'],
            "READY":
                ['on', 'assign', 'configure'],
            "SCANNING":
                ['on', 'assign', 'configure', 'scan'],
            "ABORTED":
                ['on', 'assign', 'abort'],
        }

        # state = "OFF"  # debugging only
        # assert_state(state)  # debugging only

        # Put the device into the state under test
        for action in setups[state_under_test]:
            perform_action(action)
            # state = transitions[state, action]  # debugging only
            # assert_state(state)  # debugging only

        # Check that we are in the state under test
        assert_state(state_under_test)

        # Test that the action under test does what we expect it to
        if (state_under_test, action_under_test) in transitions:
            # Action should succeed
            perform_action(action_under_test)
            assert_state(transitions[(state_under_test, action_under_test)])
        else:
            # Action should fail and the state should not change
            with pytest.raises(DevFailed):
                perform_action(action_under_test)
            assert_state(state_under_test)


@pytest.fixture
def resource_manager():
    yield SKASubarrayResourceManager()


@pytest.fixture
def state_model():
    yield SKASubarrayStateModel()


class TestSKASubarrayResourceManager:
    def test_ResourceManager_assign(self, resource_manager):
        # create a resource manager and check that it is empty
        assert not len(resource_manager)
        assert resource_manager.get() == set()

        resource_manager.assign('{"example": ["A"]}')
        assert len(resource_manager) == 1
        assert resource_manager.get() == set(["A"])

        resource_manager.assign('{"example": ["A"]}')
        assert len(resource_manager) == 1
        assert resource_manager.get() == set(["A"])

        resource_manager.assign('{"example": ["A", "B"]}')
        assert len(resource_manager) == 2
        assert resource_manager.get() == set(["A", "B"])

        resource_manager.assign('{"example": ["A"]}')
        assert len(resource_manager) == 2
        assert resource_manager.get() == set(["A", "B"])

        resource_manager.assign('{"example": ["A", "C"]}')
        assert len(resource_manager) == 3
        assert resource_manager.get() == set(["A", "B", "C"])

        resource_manager.assign('{"example": ["D"]}')
        assert len(resource_manager) == 4
        assert resource_manager.get() == set(["A", "B", "C", "D"])

    def test_ResourceManager_release(self, resource_manager):
        resource_manager = SKASubarrayResourceManager()
        resource_manager.assign('{"example": ["A", "B", "C", "D"]}')

        # okay to release resources not assigned; does nothing
        resource_manager.release('{"example": ["E"]}')
        assert len(resource_manager) == 4
        assert resource_manager.get() == set(["A", "B", "C", "D"])

        # check release does what it should
        resource_manager.release('{"example": ["D"]}')
        assert len(resource_manager) == 3
        assert resource_manager.get() == set(["A", "B", "C"])

        # okay to release resources both assigned and not assigned
        resource_manager.release('{"example": ["C", "D"]}')
        assert len(resource_manager) == 2
        assert resource_manager.get() == set(["A", "B"])

        # check release all does what it should
        resource_manager.release_all()
        assert len(resource_manager) == 0
        assert resource_manager.get() == set()

        # okay to call release_all when already empty
        resource_manager.release_all()
        assert len(resource_manager) == 0
        assert resource_manager.get() == set()


class TestSKASubarray_commands:
    """
    This class contains tests of SKASubarray commands
    """

    def test_AssignCommand(self, resource_manager, state_model):
        """
        Test for SKASubarray.AssignResourcesCommand
        """
        assign_resources = SKASubarray.AssignResourcesCommand(
            resource_manager,
            state_model
        )

        # until the state_model is in the right state for it, the
        # command's is_allowed() method will return False, and an
        # attempt to call the command will raise a CommandError, and
        # there will be no side-effect on the resource manager
        for action in ["init_started", "init_succeeded", "on_succeeded"]:
            assert not assign_resources.is_allowed()
            with pytest.raises(CommandError):
                assign_resources('{"example": ["foo"]}')
            assert not len(resource_manager)
            assert resource_manager.get() == set()

            state_model.perform_action(action)

        # now that the state_model is in the right state, is_allowed()
        # should return True, and the command should succeed, and we
        # should see the result in the resource manager
        assert assign_resources.is_allowed()
        assert assign_resources('{"example": ["foo"]}') == (
            ResultCode.OK, "AssignResources command completed OK"
        )
        assert len(resource_manager) == 1
        assert resource_manager.get() == set(["foo"])
