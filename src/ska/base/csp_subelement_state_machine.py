"""
This module contains specifications of the CSP SubElement Observing state machine.
"""
from transitions import State
from transitions.extensions import LockedMachine as Machine

__all__ = ["CspSubElementObsDeviceStateMachine"]


class CspSubElementObsDeviceStateMachine(Machine):
    """
    The observation state machine used by a generic CSP 
    Sub-element ObsDevice (derived from SKAObsDevice).
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
            "IDLE",
            "CONFIGURING",
            "READY",
            "SCANNING",
            "ABORTING",
            "ABORTED",
            "FAULT",
        ]
        transitions = [
            {
                "source": "*",
                "trigger": "fatal_error",
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
                "source": "IDLE",
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
                    "CONFIGURING",
                    "READY",
                    "SCANNING",
                    "IDLE",
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
                "trigger": "reset_succeeded",
                "dest": "IDLE",
            },
            {
                "source": ["ABORTED", "FAULT"],
                "trigger": "reset_failed",
                "dest": "FAULT",
            },
        ]

        super().__init__(
            states=states,
            initial="IDLE",
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

