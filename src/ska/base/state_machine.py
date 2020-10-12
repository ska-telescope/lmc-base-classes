"""
This module contains specifications of SKA state machines.
"""
from transitions import Machine, State


__all__ = ["OperationStateMachine", "AdminModeStateMachine", "ObservationStateMachine"]


class OperationStateMachine(Machine):
    """
    State machine for operational state ("opState").

    The states supported are "UNINITIALISED", "INIT", "FAULT",
    "DISABLE", "STANDBY", "OFF" and "ON".

    The states "INIT", "FAULT" and "DISABLE" also have "INIT_ADMIN",
    "FAULT_ADMIN" and "DISABLE_ADMIN" flavours to represent these states
    in situations where the device being modelled has been
    administratively disabled.
    """

    def __init__(self, callback=None, **extra_kwargs):
        """
        Initialises the state model.

        :param callback: A callback to be called when a transition
            implies a change to op state
        :type callback: callable
        :param extra_kwargs: Additional keywords arguments to pass to super class
            initialiser (useful for graphing)
        """
        self._callback = callback

        states = [
            "UNINITIALISED",
            "INIT",
            "INIT_ADMIN",
            "FAULT",
            "FAULT_ADMIN",
            "DISABLE",
            "DISABLE_ADMIN",
            "STANDBY",
            "OFF",
            "ON",
        ]

        transitions = [
            {
                "source": "UNINITIALISED",
                "trigger": "init_started",
                "dest": "INIT",
            },
            {
                "source": ["INIT", "FAULT", "DISABLE", "STANDBY", "OFF", "ON"],
                "trigger": "fatal_error",
                "dest": "FAULT",
            },
            {
                "source": ["INIT_ADMIN", "FAULT_ADMIN", "DISABLE_ADMIN"],
                "trigger": "fatal_error",
                "dest": "FAULT_ADMIN",
            },
            {
                "source": "INIT",
                "trigger": "init_succeeded_disable",
                "dest": "DISABLE",
            },
            {
                "source": "INIT_ADMIN",
                "trigger": "init_succeeded_disable",
                "dest": "DISABLE_ADMIN",
            },
            {
                "source": "INIT",
                "trigger": "init_succeeded_standby",
                "dest": "STANDBY",
            },
            {
                "source": "INIT",
                "trigger": "init_succeeded_off",
                "dest": "OFF",
            },
            {
                "source": "INIT",
                "trigger": "init_failed",
                "dest": "FAULT",
            },
            {
                "source": "INIT_ADMIN",
                "trigger": "init_failed",
                "dest": "FAULT_ADMIN",
            },
            {
                "source": ["INIT", "INIT_ADMIN"],
                "trigger": "admin_on",
                "dest": "INIT_ADMIN",
            },
            {
                "source": ["INIT", "INIT_ADMIN"],
                "trigger": "admin_off",
                "dest": "INIT",
            },
            {
                "source": "FAULT",
                "trigger": "reset_succeeded_disable",
                "dest": "DISABLE",
            },
            {
                "source": "FAULT_ADMIN",
                "trigger": "reset_succeeded_disable",
                "dest": "DISABLE_ADMIN",
            },
            {
                "source": "FAULT",
                "trigger": "reset_succeeded_standby",
                "dest": "STANDBY",
            },
            {
                "source": "FAULT",
                "trigger": "reset_succeeded_off",
                "dest": "OFF",
            },
            {
                "source": "FAULT",
                "trigger": "reset_failed",
                "dest": "FAULT",
            },
            {
                "source": "FAULT_ADMIN",
                "trigger": "reset_failed",
                "dest": "FAULT_ADMIN",
            },
            {
                "source": ["FAULT", "FAULT_ADMIN"],
                "trigger": "admin_on",
                "dest": "FAULT_ADMIN",
            },
            {
                "source": ["FAULT", "FAULT_ADMIN"],
                "trigger": "admin_off",
                "dest": "FAULT",
            },
            {
                "source": ["DISABLE", "DISABLE_ADMIN"],
                "trigger": "admin_on",
                "dest": "DISABLE_ADMIN",
            },
            {
                "source": ["DISABLE", "DISABLE_ADMIN"],
                "trigger": "admin_off",
                "dest": "DISABLE",
            },
            {
                "source": "DISABLE_ADMIN",
                "trigger": "disable_succeeded",
                "dest": "DISABLE_ADMIN",
            },
            {
                "source": "DISABLE_ADMIN",
                "trigger": "disable_failed",
                "dest": "FAULT_ADMIN",
            },
            {
                "source": ["DISABLE", "STANDBY", "OFF"],
                "trigger": "disable_succeeded",
                "dest": "DISABLE",
            },
            {
                "source": ["DISABLE", "STANDBY", "OFF"],
                "trigger": "disable_failed",
                "dest": "FAULT",
            },
            {
                "source": ["DISABLE", "STANDBY", "OFF"],
                "trigger": "standby_succeeded",
                "dest": "STANDBY",
            },
            {
                "source": ["DISABLE", "STANDBY", "OFF"],
                "trigger": "standby_failed",
                "dest": "FAULT",
            },
            {
                "source": ["DISABLE", "STANDBY", "OFF", "ON"],
                "trigger": "off_succeeded",
                "dest": "OFF",
            },
            {
                "source": ["DISABLE", "STANDBY", "OFF", "ON"],
                "trigger": "off_failed",
                "dest": "FAULT",
            },
            {
                "source": ["OFF", "ON"],
                "trigger": "on_succeeded",
                "dest": "ON",
            },
            {
                "source": ["OFF", "ON"],
                "trigger": "on_failed",
                "dest": "FAULT",
            },
        ]

        super().__init__(
            states=states,
            initial="UNINITIALISED",
            transitions=transitions,
            after_state_change=self._state_changed,
            **extra_kwargs,
        )

    def _state_changed(self):
        """
        State machine callback that is called every time the op_state
        changes. Responsible for ensuring that callbacks are called.
        """
        if self._callback is not None:
            self._callback(self.state)


class AdminModeStateMachine(Machine):
    """
    The state machine governing admin modes
    """

    def __init__(self, callback=None, **extra_kwargs):
        """
        Initialises the admin mode state machine model.

        :param callback: A callback to be called whenever there is a transition
            to a new admin mode value
        :type callback: callable
        :param extra_kwargs: Additional keywords arguments to pass to super class
            initialiser (useful for graphing)
        """
        self._callback = callback

        states = ["RESERVED", "NOT_FITTED", "OFFLINE", "MAINTENANCE", "ONLINE"]
        transitions = [
            {
                "source": ["NOT_FITTED", "RESERVED", "OFFLINE"],
                "trigger": "to_reserved",
                "dest": "RESERVED",
            },
            {
                "source": ["RESERVED", "NOT_FITTED", "OFFLINE"],
                "trigger": "to_notfitted",
                "dest": "NOT_FITTED",
            },
            {
                "source": ["RESERVED", "NOT_FITTED", "OFFLINE", "MAINTENANCE", "ONLINE"],
                "trigger": "to_offline",
                "dest": "OFFLINE",
            },
            {
                "source": ["OFFLINE", "MAINTENANCE", "ONLINE"],
                "trigger": "to_maintenance",
                "dest": "MAINTENANCE",
            },
            {
                "source": ["OFFLINE", "MAINTENANCE", "ONLINE"],
                "trigger": "to_online",
                "dest": "ONLINE",
            },
        ]

        super().__init__(
            states=states,
            initial="MAINTENANCE",
            transitions=transitions,
            after_state_change=self._state_changed,
            **extra_kwargs,
        )
        self._state_changed()

    def _state_changed(self):
        """
        State machine callback that is called every time the admin mode
        changes. Responsible for ensuring that callbacks are called.
        """
        if self._callback is not None:
            self._callback(self.state)


class ObservationStateMachine(Machine):
    """
    The observation state machine used by an observing subarray, per
    ADR-8.
    """

    def __init__(self, callback=None, **extra_kwargs):
        """
        Initialises the model.

        :param callback: A callback to be called when the state changes
        :type callback: callable
        :param extra_kwargs: Additional keywords arguments to pass to super class
            initialiser (useful for graphing)
        """
        self._callback = callback

        states = [
            "EMPTY",
            "RESOURCING",
            "IDLE",
            "CONFIGURING",
            "READY",
            "SCANNING",
            "ABORTING",
            "ABORTED",
            "RESETTING",
            "RESTARTING",
            "FAULT",
        ]
        transitions = [
            {
                "source": "*",
                "trigger": "fatal_error",
                "dest": "FAULT",
            },
            {
                "source": ["EMPTY", "IDLE"],
                "trigger": "assign_started",
                "dest": "RESOURCING",
            },
            {
                "source": "IDLE",
                "trigger": "release_started",
                "dest": "RESOURCING",
            },
            {
                "source": "RESOURCING",
                "trigger": "resourcing_succeeded_some_resources",
                "dest": "IDLE",
            },
            {
                "source": "RESOURCING",
                "trigger": "resourcing_succeeded_no_resources",
                "dest": "EMPTY",
            },
            {
                "source": "RESOURCING",
                "trigger": "resourcing_failed",
                "dest": "FAULT",
            },
            {
                "source": ["IDLE", "READY"],
                "trigger": "configure_started",
                "dest": "CONFIGURING",
            },
            {
                "source": "CONFIGURING",
                "trigger": "configure_succeeded",
                "dest": "READY",
            },
            {
                "source": "CONFIGURING",
                "trigger": "configure_failed",
                "dest": "FAULT",
            },
            {
                "source": "READY",
                "trigger": "end_succeeded",
                "dest": "IDLE",
            },
            {
                "source": "READY",
                "trigger": "end_failed",
                "dest": "FAULT",
            },
            {
                "source": "READY",
                "trigger": "scan_started",
                "dest": "SCANNING",
            },
            {
                "source": "SCANNING",
                "trigger": "scan_succeeded",
                "dest": "READY",
            },
            {
                "source": "SCANNING",
                "trigger": "scan_failed",
                "dest": "FAULT",
            },
            {
                "source": "SCANNING",
                "trigger": "end_scan_succeeded",
                "dest": "READY",
            },
            {
                "source": "SCANNING",
                "trigger": "end_scan_failed",
                "dest": "FAULT",
            },
            {
                "source": [
                    "IDLE",
                    "CONFIGURING",
                    "READY",
                    "SCANNING",
                    "RESETTING",
                ],
                "trigger": "abort_started",
                "dest": "ABORTING",
            },
            {
                "source": "ABORTING",
                "trigger": "abort_succeeded",
                "dest": "ABORTED",
            },
            {
                "source": "ABORTING",
                "trigger": "abort_failed",
                "dest": "FAULT",
            },
            {
                "source": ["ABORTED", "FAULT"],
                "trigger": "reset_started",
                "dest": "RESETTING",
            },
            {
                "source": "RESETTING",
                "trigger": "reset_succeeded",
                "dest": "IDLE",
            },
            {
                "source": "RESETTING",
                "trigger": "reset_failed",
                "dest": "FAULT",
            },
            {
                "source": ["ABORTED", "FAULT"],
                "trigger": "restart_started",
                "dest": "RESTARTING",
            },
            {
                "source": "RESTARTING",
                "trigger": "restart_succeeded",
                "dest": "EMPTY",
            },
            {
                "source": "RESTARTING",
                "trigger": "restart_failed",
                "dest": "FAULT",
            },
        ]

        super().__init__(
            states=states,
            initial="EMPTY",
            transitions=transitions,
            after_state_change=self._state_changed,
            **extra_kwargs,
        )
        self._state_changed()

    def _state_changed(self):
        """
        State machine callback that is called every time the obs_state
        changes. Responsible for ensuring that callbacks are called.
        """
        if self._callback is not None:
            self._callback(self.state)
