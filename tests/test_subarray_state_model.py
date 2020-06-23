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
import pytest

from tango import DevState

from ska.base.control_model import AdminMode, ObsState
from ska.base.faults import StateModelError


class TestSKASubarrayStateModel():
    """
    Test cases for SKASubarrayStateModel.
    """

    @pytest.mark.parametrize(
        'state_under_test, action_under_test',
        itertools.product(
            ["UNINITIALISED", "INIT_ENABLED", "INIT_DISABLED", "FAULT_ENABLED",
             "FAULT_DISABLED", "DISABLED", "OFF", "EMPTY",
             "RESOURCING", "IDLE", "CONFIGURING", "READY", "SCANNING",
             "ABORTING", "ABORTED", "OBSFAULT"],
            ["init_started", "init_succeeded", "init_failed", "fatal_error",
             "reset_succeeded", "reset_failed", "to_notfitted",
             "to_offline", "to_online", "to_maintenance", "on_succeeded",
             "on_failed", "off_succeeded", "off_failed", "assign_started",
             "resourcing_succeeded_no_resources", "resourcing_succeeded_some_resources",
             "resourcing_failed", "release_started", "configure_started",
             "configure_succeeded", "configure_failed", "scan_started",
             "scan_succeeded", "scan_failed", "end_scan_succeeded",
             "end_scan_failed", "abort_started", "abort_succeeded",
             "abort_failed", "obs_reset_started", "obs_reset_succeeded",
             "obs_reset_failed", "restart_started", "restart_succeeded",
             "restart_failed"]
        )
    )
    def test_state_machine(self, state_model,
                           state_under_test, action_under_test):
        """
        Test the subarray state machine: for a given initial state and
        an action, does execution of that action, from that initial
        state, yield the expected results? If the action was not allowed
        from that initial state, does the device raise a DevFailed
        exception? If the action was allowed, does it result in the
        correct state transition?

        :todo: support starting in different memorised adminModes
        """

        states = {
            "UNINITIALISED":
                (None, None, None),
            "FAULT_ENABLED":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.FAULT, None),
            "FAULT_DISABLED":
                ([AdminMode.NOT_FITTED, AdminMode.OFFLINE], DevState.FAULT, None),
            "INIT_ENABLED":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.INIT, ObsState.EMPTY),
            "INIT_DISABLED":
                ([AdminMode.NOT_FITTED, AdminMode.OFFLINE], DevState.INIT, ObsState.EMPTY),
            "DISABLED":
                ([AdminMode.NOT_FITTED, AdminMode.OFFLINE], DevState.DISABLE, ObsState.EMPTY),
            "OFF":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.OFF, ObsState.EMPTY),
            "EMPTY":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.EMPTY),
            "RESOURCING":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.RESOURCING),
            "IDLE":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.IDLE),
            "CONFIGURING":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.CONFIGURING),
            "READY":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.READY),
            "SCANNING":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.SCANNING),
            "ABORTING":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.ABORTING),
            "ABORTED":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.ABORTED),
            "RESETTING":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.RESETTING),
            "RESTARTING":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.RESTARTING),
            "OBSFAULT":
                ([AdminMode.ONLINE, AdminMode.MAINTENANCE], DevState.ON, ObsState.FAULT),
        }

        def assert_state(state):
            (admin_modes, state, obs_state) = states[state]
            if admin_modes is not None:
                assert state_model.admin_mode in admin_modes
            if state is not None:
                assert state_model.dev_state == state
            if obs_state is not None:
                assert state_model.obs_state == obs_state

        transitions = {
            ('UNINITIALISED', 'init_started'): "INIT_ENABLED",
            ('INIT_ENABLED', 'to_notfitted'): "INIT_DISABLED",
            ('INIT_ENABLED', 'to_offline'): "INIT_DISABLED",
            ('INIT_ENABLED', 'to_online'): "INIT_ENABLED",
            ('INIT_ENABLED', 'to_maintenance'): "INIT_ENABLED",
            ('INIT_ENABLED', 'init_succeeded'): 'OFF',
            ('INIT_ENABLED', 'init_failed'): 'FAULT_ENABLED',
            ('INIT_ENABLED', 'fatal_error'): "FAULT_ENABLED",
            ('INIT_DISABLED', 'to_notfitted'): "INIT_DISABLED",
            ('INIT_DISABLED', 'to_offline'): "INIT_DISABLED",
            ('INIT_DISABLED', 'to_online'): "INIT_ENABLED",
            ('INIT_DISABLED', 'to_maintenance'): "INIT_ENABLED",
            ('INIT_DISABLED', 'init_succeeded'): 'DISABLED',
            ('INIT_DISABLED', 'init_failed'): 'FAULT_DISABLED',
            ('INIT_DISABLED', 'fatal_error'): "FAULT_DISABLED",
            ('FAULT_DISABLED', 'to_notfitted'): "FAULT_DISABLED",
            ('FAULT_DISABLED', 'to_offline'): "FAULT_DISABLED",
            ('FAULT_DISABLED', 'to_online'): "FAULT_ENABLED",
            ('FAULT_DISABLED', 'to_maintenance'): "FAULT_ENABLED",
            ('FAULT_DISABLED', 'reset_succeeded'): "DISABLED",
            ('FAULT_DISABLED', 'reset_failed'): "FAULT_DISABLED",
            ('FAULT_DISABLED', 'fatal_error'): "FAULT_DISABLED",
            ('FAULT_ENABLED', 'to_notfitted'): "FAULT_DISABLED",
            ('FAULT_ENABLED', 'to_offline'): "FAULT_DISABLED",
            ('FAULT_ENABLED', 'to_online'): "FAULT_ENABLED",
            ('FAULT_ENABLED', 'to_maintenance'): "FAULT_ENABLED",
            ('FAULT_ENABLED', 'reset_succeeded'): "OFF",
            ('FAULT_ENABLED', 'reset_failed'): "FAULT_ENABLED",
            ('FAULT_ENABLED', 'fatal_error'): "FAULT_ENABLED",
            ('DISABLED', 'to_notfitted'): "DISABLED",
            ('DISABLED', 'to_offline'): "DISABLED",
            ('DISABLED', 'to_online'): "OFF",
            ('DISABLED', 'to_maintenance'): "OFF",
            ('DISABLED', 'fatal_error'): "FAULT_DISABLED",
            ('OFF', 'to_notfitted'): "DISABLED",
            ('OFF', 'to_offline'): "DISABLED",
            ('OFF', 'to_online'): "OFF",
            ('OFF', 'to_maintenance'): "OFF",
            ('OFF', 'on_succeeded'): "EMPTY",
            ('OFF', 'on_failed'): "FAULT_ENABLED",
            ('OFF', 'fatal_error'): "FAULT_ENABLED",
            ('EMPTY', 'off_succeeded'): "OFF",
            ('EMPTY', 'off_failed'): "FAULT_ENABLED",
            ('EMPTY', 'assign_started'): "RESOURCING",
            ('EMPTY', 'fatal_error'): "OBSFAULT",
            ('RESOURCING', 'resourcing_succeeded_some_resources'): "IDLE",
            ('RESOURCING', 'resourcing_succeeded_no_resources'): "EMPTY",
            ('RESOURCING', 'resourcing_failed'): "OBSFAULT",
            ('RESOURCING', 'fatal_error'): "OBSFAULT",
            ('IDLE', 'assign_started'): "RESOURCING",
            ('IDLE', 'release_started'): "RESOURCING",
            ('IDLE', 'configure_started'): "CONFIGURING",
            ('IDLE', 'abort_started'): "ABORTING",
            ('IDLE', 'fatal_error'): "OBSFAULT",
            ('CONFIGURING', 'configure_succeeded'): "READY",
            ('CONFIGURING', 'configure_failed'): "OBSFAULT",
            ('CONFIGURING', 'abort_started'): "ABORTING",
            ('CONFIGURING', 'fatal_error'): "OBSFAULT",
            ('READY', 'end_succeeded'): "IDLE",
            ('READY', 'end_failed'): "OBSFAULT",
            ('READY', 'configure_started'): "CONFIGURING",
            ('READY', 'abort_started'): "ABORTING",
            ('READY', 'scan_started'): "SCANNING",
            ('READY', 'fatal_error'): "OBSFAULT",
            ('SCANNING', 'scan_succeeded'): "READY",
            ('SCANNING', 'scan_failed'): "OBSFAULT",
            ('SCANNING', 'end_scan_succeeded'): "READY",
            ('SCANNING', 'end_scan_failed'): "OBSFAULT",
            ('SCANNING', 'abort_started'): "ABORTING",
            ('SCANNING', 'fatal_error'): "OBSFAULT",
            ('ABORTING', 'abort_succeeded'): "ABORTED",
            ('ABORTING', 'abort_failed'): "OBSFAULT",
            ('ABORTING', 'fatal_error'): "OBSFAULT",
            ('ABORTED', 'obs_reset_started'): "RESETTING",
            ('ABORTED', 'restart_started'): "RESTARTING",
            ('ABORTED', 'fatal_error'): "OBSFAULT",
            ('OBSFAULT', 'obs_reset_started'): "RESETTING",
            ('OBSFAULT', 'restart_started'): "RESTARTING",
            ('OBSFAULT', 'fatal_error'): "OBSFAULT",
            ('RESETTING', 'obs_reset_succeeded'): "IDLE",
            ('RESETTING', 'obs_reset_failed'): "OBSFAULT",
            ('RESETTING', 'fatal_error'): "OBSFAULT",
            ('RESTARTING', 'restart_succeeded'): "EMPTY",
            ('RESTARTING', 'restart_failed'): "OBSFAULT",
            ('RESTARTING', 'fatal_error'): "OBSFAULT",
        }

        setups = {
            "UNINITIALISED": [],
            "INIT_ENABLED": ['init_started'],
            "INIT_DISABLED": ['init_started', 'to_offline'],
            "FAULT_ENABLED": ['init_started', 'init_failed'],
            "FAULT_DISABLED": ['init_started', 'to_offline', 'init_failed'],
            "OFF": ['init_started', 'init_succeeded'],
            "DISABLED": ['init_started', 'init_succeeded', 'to_offline'],
            "EMPTY": ['init_started', 'init_succeeded', 'on_succeeded'],
            "RESOURCING": [
                'init_started', 'init_succeeded', 'on_succeeded',
                'assign_started'
            ],
            "IDLE": [
                'init_started', 'init_succeeded', 'on_succeeded',
                'assign_started', 'resourcing_succeeded_some_resources'],
            "CONFIGURING": [
                'init_started', 'init_succeeded', 'on_succeeded',
                'assign_started', 'resourcing_succeeded_some_resources',
                'configure_started'
            ],
            "READY": [
                'init_started', 'init_succeeded', 'on_succeeded',
                'assign_started', 'resourcing_succeeded_some_resources',
                'configure_started', 'configure_succeeded'
            ],
            "SCANNING": [
                'init_started', 'init_succeeded', 'on_succeeded',
                'assign_started', 'resourcing_succeeded_some_resources',
                'configure_started', 'configure_succeeded', 'scan_started'
            ],
            "ABORTING": [
                'init_started', 'init_succeeded', 'on_succeeded',
                'assign_started', 'resourcing_succeeded_some_resources',
                'abort_started'
            ],
            "ABORTED": [
                'init_started', 'init_succeeded', 'on_succeeded',
                'assign_started', 'resourcing_succeeded_some_resources',
                'abort_started', 'abort_succeeded'
            ],
            "OBSFAULT": [
                'init_started', 'init_succeeded', 'on_succeeded',
                'fatal_error'
            ],
            "RESETTING": [
                'init_started', 'init_succeeded', 'on_succeeded',
                'assign_started', 'resourcing_succeeded_some_resources',
                'abort_started', 'abort_succeeded', 'obs_reset_started'
            ],
            "RESTARTING": [
                'init_started', 'init_succeeded', 'on_succeeded',
                'assign_started', 'resourcing_succeeded_some_resources',
                'abort_started', 'abort_succeeded', 'restart_started'
            ],
        }

        # state = "UNINITIALISED"  # for test debugging only
        # assert_state(state)  # for test debugging only

        # Put the device into the state under test
        for action in setups[state_under_test]:
            state_model.perform_action(action)
            # state = transitions[state, action]  # for test debugging only
            # assert_state(state)  # for test debugging only

        # Check that we are in the state under test
        assert_state(state_under_test)

        # Test that the action under test does what we expect it to
        if (state_under_test, action_under_test) in transitions:
            # Action should succeed
            state_model.perform_action(action_under_test)
            assert_state(transitions[(state_under_test, action_under_test)])
        else:
            # Action should fail and the state should not change
            with pytest.raises(StateModelError):
                state_model.perform_action(action_under_test)
            assert_state(state_under_test)
