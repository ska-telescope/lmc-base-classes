"""
This module defines a basic state model for SKA LMC devices that manage observations.

It consists of a single :py:class:`.ObsStateModel` class, which drives a
state machine to manage device "obs state", represented by the
:py:class:`ska_tango_base.control_model.ObsState` enum, and published by
Tango devices via the ``obsState`` attribute.
"""
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
        self,
        state_machine_factory,
        logger,
        callback=None,
    ):
        """
        Initialise the model.

        :param state_machine_factory: a callable that returns a
            state machine for this model to use
        :type state_machine_factory: callable
        :param logger: the logger to be used by this state model.
        :type logger: a logger that implements the standard library
            logger interface
        :param callback: A callback to be called when a state machine
            transitions state
        :type callback: callable
        """
        self.logger = logger

        self._obs_state = None
        self._callback = callback

        self._obs_state_machine = state_machine_factory(
            callback=self._obs_state_changed
        )

    @property
    def obs_state(self):
        """
        Return the obs_state.

        :returns: obs_state of this state model
        :rtype: ObsState
        """
        return self._obs_state

    def _obs_state_changed(self, machine_state):
        """
        Handle notification that the observation state machine has changed state.

        This is a helper method that updates obs_state, ensuring that
        the callback is called if one exists.

        :param machine_state: the new state of the observation state
            machine
        :type machine_state: str
        """
        obs_state = ObsState[machine_state]
        if self._obs_state != obs_state:
            self._obs_state = obs_state
            if self._callback is not None:
                self._callback(obs_state)

    def is_action_allowed(self, action, raise_if_disallowed=False):
        """
        Return whether a given action is allowed in the current state.

        :param action: an action, as given in the transitions table
        :type action: str

        :param raise_if_disallowed: whether to raise an exception if the
            action is disallowed, or merely return False (optional,
            defaults to False)
        :type raise_if_disallowed: bool

        :raises StateModelError: if the action is unknown to the state
            machine

        :return: whether the action is allowed in the current state
        :rtype: bool
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

    def perform_action(self, action):
        """
        Perform an action on the state model.

        :param action: an action, as given in the transitions table
        :type action: ANY
        """
        _ = self.is_action_allowed(action, raise_if_disallowed=True)
        self._obs_state_machine.trigger(action)

    @for_testing_only
    def _straight_to_state(self, obs_state_name):
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
        :type obs_state_name:
            :py:class:`~ska_tango_base.control_model.ObsState`
        """
        getattr(self._obs_state_machine, f"to_{obs_state_name}")()
