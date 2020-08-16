"""
This module contains specifications of SKA state machines.
"""
from transitions import Machine, State
from tango import DevState

from ska.base.control_model import AdminMode, ObsState


class BaseDeviceStateMachine(Machine):
    """
    State machine for an SKA base device. Supports ON and OFF states,
    states, plus initialisation and fault states, and
    also the basic admin modes.
    """

    def __init__(self, op_state_callback=None, admin_mode_callback=None):
        """
        Initialises the state model.

        :param op_state_callback: A callback to be called when a
            transition implies a change to op state
        :type op_state_callback: callable
        :param admin_mode_callback: A callback to be called when a
            transition causes a change to device admin_mode
        :type admin_mode_callback: callable
        """
        self._admin_mode = None
        self._admin_mode_callback = admin_mode_callback
        self._op_state = None
        self._op_state_callback = op_state_callback

        states = [
            State("UNINITIALISED"),
            State("INIT_ENABLED", on_enter="_init_entered"),
            State("INIT_DISABLED", on_enter="_init_entered"),
            State("FAULT_ENABLED", on_enter="_fault_entered"),
            State("FAULT_DISABLED", on_enter="_fault_entered"),
            State("DISABLED", on_enter="_disabled_entered"),
            State("OFF", on_enter="_off_entered"),
            State("ON", on_enter="_on_entered"),
        ]

        transitions = [
            {
                "source": "UNINITIALISED",
                "trigger": "init_started",
                "dest": "INIT_ENABLED",
                "after": self._maintenance_callback,
            },
            {
                "source": ["INIT_ENABLED", "OFF", "FAULT_ENABLED", "ON"],
                "trigger": "fatal_error",
                "dest": "FAULT_ENABLED",
            },
            {
                "source": ["INIT_DISABLED", "DISABLED", "FAULT_DISABLED"],
                "trigger": "fatal_error",
                "dest": "FAULT_DISABLED",
            },
            {
                "source": "INIT_ENABLED",
                "trigger": "init_succeeded",
                "dest": "OFF",
            },
            {
                "source": "INIT_DISABLED",
                "trigger": "init_succeeded",
                "dest": "DISABLED",
            },
            {
                "source": "INIT_ENABLED",
                "trigger": "init_failed",
                "dest": "FAULT_ENABLED",
            },
            {
                "source": "INIT_DISABLED",
                "trigger": "init_failed",
                "dest": "FAULT_DISABLED",
            },
            {
                "source": ["INIT_ENABLED", "INIT_DISABLED"],
                "trigger": "to_notfitted",
                "dest": "INIT_DISABLED",
                "after": self._not_fitted_callback
            },
            {
                "source": ["INIT_ENABLED", "INIT_DISABLED"],
                "trigger": "to_offline",
                "dest": "INIT_DISABLED",
                "after": self._offline_callback
            },
            {
                "source": ["INIT_ENABLED", "INIT_DISABLED"],
                "trigger": "to_maintenance",
                "dest": "INIT_ENABLED",
                "after": self._maintenance_callback
            },
            {
                "source": ["INIT_ENABLED", "INIT_DISABLED"],
                "trigger": "to_online",
                "dest": "INIT_ENABLED",
                "after": self._online_callback
            },
            {
                "source": "FAULT_DISABLED",
                "trigger": "reset_succeeded",
                "dest": "DISABLED",
            },
            {
                "source": "FAULT_ENABLED",
                "trigger": "reset_succeeded",
                "dest": "OFF",
            },
            {
                "source": ["FAULT_DISABLED", "FAULT_ENABLED"],
                "trigger": "reset_failed",
                "dest": None,
            },
            {
                "source": ["FAULT_DISABLED", "FAULT_ENABLED"],
                "trigger": "to_notfitted",
                "dest": "FAULT_DISABLED",
                "after": self._not_fitted_callback
            },
            {
                "source": ["FAULT_DISABLED", "FAULT_ENABLED"],
                "trigger": "to_offline",
                "dest": "FAULT_DISABLED",
                "after": self._offline_callback
            },
            {
                "source": ["FAULT_DISABLED", "FAULT_ENABLED"],
                "trigger": "to_maintenance",
                "dest": "FAULT_ENABLED",
                "after": self._maintenance_callback
            },
            {
                "source": ["FAULT_DISABLED", "FAULT_ENABLED"],
                "trigger": "to_online",
                "dest": "FAULT_ENABLED",
                "after": self._online_callback
            },
            {
                "source": "DISABLED",
                "trigger": "to_notfitted",
                "dest": "DISABLED",
                "after": self._not_fitted_callback
            },
            {
                "source": "DISABLED",
                "trigger": "to_offline",
                "dest": "DISABLED",
                "after": self._offline_callback
            },
            {
                "source": "DISABLED",
                "trigger": "to_maintenance",
                "dest": "OFF",
                "after": self._maintenance_callback
            },
            {
                "source": "DISABLED",
                "trigger": "to_online",
                "dest": "OFF",
                "after": self._online_callback
            },
            {
                "source": "OFF",
                "trigger": "to_notfitted",
                "dest": "DISABLED",
                "after": self._not_fitted_callback
            },
            {
                "source": "OFF",
                "trigger": "to_offline",
                "dest": "DISABLED",
                "after": self._offline_callback
            },
            {
                "source": "OFF",
                "trigger": "to_maintenance",
                "dest": "OFF",
                "after": self._maintenance_callback
            },
            {
                "source": "OFF",
                "trigger": "to_online",
                "dest": "OFF",
                "after": self._online_callback
            },
            {
                "source": "OFF",
                "trigger": "on_succeeded",
                "dest": "ON",
            },
            {
                "source": "OFF",
                "trigger": "on_failed",
                "dest": "FAULT_ENABLED",
            },
            {
                "source": "ON",
                "trigger": "off_succeeded",
                "dest": "OFF",
            },
            {
                "source": "ON",
                "trigger": "off_failed",
                "dest": "FAULT_ENABLED",
            },
        ]

        super().__init__(
            states=states,
            initial="UNINITIALISED",
            transitions=transitions,
        )

    def _init_entered(self):
        """
        called when the state machine enters the "" state.
        """
        self._update_op_state(DevState.INIT)

    def _fault_entered(self):
        """
        called when the state machine enters the "" state.
        """
        self._update_op_state(DevState.FAULT)

    def _disabled_entered(self):
        """
        called when the state machine enters the "" state.
        """
        self._update_op_state(DevState.DISABLE)

    def _off_entered(self):
        """
        called when the state machine enters the "" state.
        """
        self._update_op_state(DevState.OFF)

    def _on_entered(self):
        """
        called when the state machine enters the "" state.
        """
        self._update_op_state(DevState.ON)

    def _not_fitted_callback(self):
        """
        callback called when the state machine is set to admin mode
        NOT FITTED
        """
        self._update_admin_mode(AdminMode.NOT_FITTED)

    def _offline_callback(self):
        """
        callback called when the state machine is set to admin mode
        OFFLINE
        """
        self._update_admin_mode(AdminMode.OFFLINE)

    def _maintenance_callback(self):
        """
        callback called when the state machine is set to admin mode
        MAINTENANCE
        """
        self._update_admin_mode(AdminMode.MAINTENANCE)

    def _online_callback(self):
        """
        callback called when the state machine is set to admin mode
        online
        """
        self._update_admin_mode(AdminMode.ONLINE)

    def _update_admin_mode(self, admin_mode):
        """
        Helper method: calls the admin_mode callback if one exists

        :param admin_mode: the new admin_mode value
        :type admin_mode: AdminMode
        """
        if self._admin_mode != admin_mode:
            self._admin_mode = admin_mode
            if self._admin_mode_callback is not None:
                self._admin_mode_callback(self._admin_mode)

    def _update_op_state(self, op_state):
        """
        Helper method: sets this state models op_state, and calls the
        op_state callback if one exists

        :param op_state: the new op state value
        :type op_state: DevState
        """
        if self._op_state != op_state:
            self._op_state = op_state
            if self._op_state_callback is not None:
                self._op_state_callback(self._op_state)


class ObservationStateMachine(Machine):
    """
    The observation state machine used by an observing subarray, per
    ADR-8.
    """

    def __init__(self, obs_state_callback=None):
        """
        Initialises the model.

        :param obs_state_callback: A callback to be called when a
            transition causes a change to device obs_state
        :type obs_state_callback: callable
        """
        self._obs_state = ObsState.EMPTY
        self._obs_state_callback = obs_state_callback

        states = [obs_state.name for obs_state in ObsState]
        transitions = [
            {
                "source": "*",
                "trigger": "fatal_error",
                "dest": ObsState.FAULT.name,
            },
            {
                "source": [ObsState.EMPTY.name, ObsState.IDLE.name],
                "trigger": "assign_started",
                "dest": ObsState.RESOURCING.name,
            },
            {
                "source": ObsState.IDLE.name,
                "trigger": "release_started",
                "dest": ObsState.RESOURCING.name,
            },
            {
                "source": ObsState.RESOURCING.name,
                "trigger": "resourcing_succeeded_some_resources",
                "dest": ObsState.IDLE.name,
            },
            {
                "source": ObsState.RESOURCING.name,
                "trigger": "resourcing_succeeded_no_resources",
                "dest": ObsState.EMPTY.name,
            },
            {
                "source": ObsState.RESOURCING.name,
                "trigger": "resourcing_failed",
                "dest": ObsState.FAULT.name,
            },
            {
                "source": [ObsState.IDLE.name, ObsState.READY.name],
                "trigger": "configure_started",
                "dest": ObsState.CONFIGURING.name,
            },
            {
                "source": ObsState.CONFIGURING.name,
                "trigger": "configure_succeeded",
                "dest": ObsState.READY.name,
            },
            {
                "source": ObsState.CONFIGURING.name,
                "trigger": "configure_failed",
                "dest": ObsState.FAULT.name,
            },
            {
                "source": ObsState.READY.name,
                "trigger": "end_succeeded",
                "dest": ObsState.IDLE.name,
            },
            {
                "source": ObsState.READY.name,
                "trigger": "end_failed",
                "dest": ObsState.FAULT.name,
            },
            {
                "source": ObsState.READY.name,
                "trigger": "scan_started",
                "dest": ObsState.SCANNING.name,
            },
            {
                "source": ObsState.SCANNING.name,
                "trigger": "scan_succeeded",
                "dest": ObsState.READY.name,
            },
            {
                "source": ObsState.SCANNING.name,
                "trigger": "scan_failed",
                "dest": ObsState.FAULT.name,
            },
            {
                "source": ObsState.SCANNING.name,
                "trigger": "end_scan_succeeded",
                "dest": ObsState.READY.name,
            },
            {
                "source": ObsState.SCANNING.name,
                "trigger": "end_scan_failed",
                "dest": ObsState.FAULT.name,
            },
            {
                "source": [
                    ObsState.IDLE.name, ObsState.CONFIGURING.name,
                    ObsState.READY.name, ObsState.SCANNING.name,
                    ObsState.RESETTING.name,
                ],
                "trigger": "abort_started",
                "dest": ObsState.ABORTING.name,
            },
            {
                "source": ObsState.ABORTING.name,
                "trigger": "abort_succeeded",
                "dest": ObsState.ABORTED.name,
            },
            {
                "source": ObsState.ABORTING.name,
                "trigger": "abort_failed",
                "dest": ObsState.FAULT.name,
            },
            {
                "source": [ObsState.ABORTED.name, ObsState.FAULT.name],
                "trigger": "obs_reset_started",
                "dest": ObsState.RESETTING.name,
            },
            {
                "source": ObsState.RESETTING.name,
                "trigger": "obs_reset_succeeded",
                "dest": ObsState.IDLE.name,
            },
            {
                "source": ObsState.RESETTING.name,
                "trigger": "obs_reset_failed",
                "dest": ObsState.FAULT.name,
            },
            {
                "source": [ObsState.ABORTED.name, ObsState.FAULT.name],
                "trigger": "restart_started",
                "dest": ObsState.RESTARTING.name,
            },
            {
                "source": ObsState.RESTARTING.name,
                "trigger": "restart_succeeded",
                "dest": ObsState.EMPTY.name,
            },
            {
                "source": ObsState.RESTARTING.name,
                "trigger": "restart_failed",
                "dest": ObsState.FAULT.name,
            },
        ]

        super().__init__(
            states=states,
            initial=ObsState.EMPTY.name,
            transitions=transitions,
            after_state_change=self._obs_state_changed
        )

    def _obs_state_changed(self):
        """
        State machine callback that is called every time the obs_state
        changes. Responsible for ensuring that callbacks are called.
        """
        obs_state = ObsState[self.state]
        if self._obs_state != obs_state:
            self._obs_state = obs_state
            if self._obs_state_callback is not None:
                self._obs_state_callback(self._obs_state)
