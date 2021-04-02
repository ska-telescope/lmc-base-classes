"""
This module contains a specification of the SKA observation state machine.
"""
from transitions import State
from transitions.extensions import LockedMachine as Machine


__all__ = ["ObservationStateMachine"]


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
