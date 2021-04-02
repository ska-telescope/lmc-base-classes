"""
This module contains a specifications of the SKA admin mode state machine.
"""
from transitions import State
from transitions.extensions import LockedMachine as Machine


__all__ = ["AdminModeStateMachine"]


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


