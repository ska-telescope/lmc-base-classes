"""
This module defines a basic state model for SKA LMC devices that manage observations.

It consists of a single :py:class:`.ObsStateModel` class, which drives a
state machine to manage device "obs state", represented by the
:py:class:`ska_tango_base.control_model.ObsState` enum, and published by
Tango devices via the ``obsState`` attribute.
"""
from __future__ import annotations

import logging
from typing import Callable, Optional, cast

from ska_tango_base.control_model import ObsState
from ska_tango_base.faults import StateModelError
from ska_tango_base.utils import for_testing_only

__all__ = ["ObsStateModel"]


class ObsStateModel:
    """
    This class implements the state model for observation state ("obsState").

    The model supports states that are values of the
    :py:class:`ska_tango_base.control_model.ObsState` enum. Rather than
    specifying a state machine, it allows a state machine to be
    provided. Thus, the precise states supported, and the transitions,
    are not determined in advance.
    """

    def __init__(
        self: ObsStateModel,
        state_machine_factory: Callable,
        logger: logging.Logger,
        callback: Optional[Callable] = None,
    ) -> None:
        """
        Initialise the model.

        :param state_machine_factory: a callable that returns a
            state machine for this model to use
        :param logger: the logger to be used by this state model.
        :param callback: A callback to be called when a state machine
            transitions state
        """
        self.logger = logger

        self._obs_state = cast(ObsState, None)
        self._callback = callback

        self._obs_state_machine = state_machine_factory(
            callback=self._obs_state_changed
        )

    @property
    def obs_state(self: ObsStateModel) -> ObsState:
        """
        Return the obs_state.

        :returns: obs_state of this state model
        """
        return self._obs_state

    def _obs_state_changed(self: ObsStateModel, machine_state: str) -> None:
        """
        Handle notification that the observation state machine has changed state.

        This is a helper method that updates obs_state, ensuring that
        the callback is called if one exists.

        :param machine_state: the new state of the observation state
            machine
        """
        obs_state = ObsState[machine_state]
        if self._obs_state != obs_state:
            self._obs_state = obs_state
            if self._callback is not None:
                self._callback(obs_state)

    def is_action_allowed(
        self: ObsStateModel, action: str, raise_if_disallowed: bool = False
    ) -> bool:
        """
        Return whether a given action is allowed in the current state.

        :param action: an action, as given in the transitions table
        :param raise_if_disallowed: whether to raise an exception if the
            action is disallowed, or merely return False (optional,
            defaults to False)

        :raises StateModelError: if the action is unknown to the state
            machine

        :return: whether the action is allowed in the current state
        """
        if action in self._obs_state_machine.get_triggers(
            self._obs_state_machine.state
        ):
            return True

        if raise_if_disallowed:
            raise StateModelError(
                f"Action {action} is not allowed in obs state {self.obs_state.name}."
            )
        return False

    def perform_action(self: ObsStateModel, action: str) -> None:
        """
        Perform an action on the state model.

        :param action: an action, as given in the transitions table
        """
        _ = self.is_action_allowed(action, raise_if_disallowed=True)
        self._obs_state_machine.trigger(action)

    @for_testing_only
    def _straight_to_state(self: ObsStateModel, obs_state_name: ObsState) -> None:
        """
        Take this model straight to the specified state.

        This method exists to simplify testing; for example, if testing
        that a command may be run in a given ObsState, one can push this
        state model straight to that ObsState, rather than having to
        drive it to that state through a sequence of actions. It is not
        intended that this method would be called outside of test
        setups. A warning will be raised if it is.

        For example, to test that a device transitions from SCANNING to
        ABORTING when the Abort() command is called:

        .. code-block:: py

            model = ObservationStateModel(logger)
            model._straight_to_state("SCANNING")
            assert model.obs_state == ObsState.SCANNING
            model.perform_action("abort_invoked")
            assert model.obs_state == ObsState.ABORTING

        :param obs_state_name: the target obs_state
        """
        getattr(self._obs_state_machine, f"to_{obs_state_name}")()
