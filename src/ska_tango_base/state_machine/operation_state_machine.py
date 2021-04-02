"""
This module contains a specification of the SKA operation state machine.
"""
from transitions import State
from transitions.extensions import LockedMachine as Machine


__all__ = ["OperationStateMachine"]


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


