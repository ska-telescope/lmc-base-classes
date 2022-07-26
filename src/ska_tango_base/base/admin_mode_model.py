# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
This module specifies the admin mode model for SKA LMC Tango devices.

It consists of a single public class: :py:class:`.AdminModeModel`. This
uses a state machine to device device adminMode, represented as a
:py:class:`ska_tango_base.control_model.AdminMode` enum value, and
reported by Tango devices through the ``AdminMode`` attribute.
"""
from __future__ import annotations

import logging
from typing import Callable, Optional

from transitions.extensions import LockedMachine as Machine

from ska_tango_base.control_model import AdminMode
from ska_tango_base.faults import StateModelError
from ska_tango_base.utils import for_testing_only

__all__ = ["AdminModeModel"]


class _AdminModeMachine(Machine):
    """
    The state machine governing admin modes.

    For documentation of states and transitions, see the documentation
    of the public :py:class:`.AdminModeModel` class.
    """

    def __init__(
        self: _AdminModeMachine,
        callback: Optional[Callable[[AdminMode], None]] = None,
        **extra_kwargs: dict,
    ) -> None:
        """
        Initialise the admin mode state machine model.

        :param callback: A callback to be called whenever there is a
            transition to a new admin mode value
        :param extra_kwargs: Additional keywords arguments to pass to
            super class initialiser (useful for graphing)
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
                "source": [
                    "RESERVED",
                    "NOT_FITTED",
                    "OFFLINE",
                    "MAINTENANCE",
                    "ONLINE",
                ],
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
            initial="OFFLINE",
            transitions=transitions,
            after_state_change=self._state_changed,
            **extra_kwargs,
        )
        self._state_changed()

    def _state_changed(self: _AdminModeMachine) -> None:
        """
        State machine callback that is called every time the admin mode changes.

        Responsible for ensuring that callbacks are called.
        """
        if self._callback is not None:
            self._callback(self.state)


class AdminModeModel:
    """
    This class implements the state model for device adminMode.

    The model supports the five admin modes defined by the values of the
    :py:class:`ska_tango_base.control_model.AdminMode` enum.

    * **NOT_FITTED**: the component that the device is supposed to
      monitor is not fitted.
    * **RESERVED**: the component that the device is monitoring is not
      in use because it is redundant to other devices. It is ready to
      take over should other devices fail.
    * **OFFLINE**: the component that the device is monitoring device
      has been declared by SKA operations not to be used
    * **MAINTENANCE**: the component that the device is monitoring
      cannot be used for science purposes but can be for engineering /
      maintenance purposes, such as testing, debugging, etc.
    * **ONLINE**: the component that the device is monitoring can be
      used for science purposes.

    The admin mode state machine allows for:

    * any transition between the modes NOT_FITTED, RESERVED and OFFLINE
      (e.g. an unfitted device being fitted as a redundant or
      non-redundant device, a redundant device taking over when another
      device fails, etc.)
    * any transition between the modes OFFLINE, MAINTENANCE and ONLINE
      (e.g. an online device being taken offline or put into maintenance
      mode to diagnose a fault, a faulty device moving between
      maintenance and offline mode as it undergoes sporadic periods of
      diagnosis.)

    The actions supported are:

    * **to_not_fitted**
    * **to_reserved**
    * **to_offline**
    * **to_maintenance**
    * **to_online**

    A diagram of the admin mode model, as designed, is shown below

    .. uml:: admin_mode_model.uml
       :caption: Diagram of the admin mode model

    The following is an diagram of the underlying state machine,
    automatically generated from the code. Its equivalence to the
    diagram above demonstrates that the implementation is faithful to
    the design.

    .. figure:: _AdminModeMachine_autogenerated.png
      :alt: Diagram of the admin mode state machine, as implemented
    """

    def __init__(
        self: AdminModeModel,
        logger: logging.Logger,
        callback: Optional[Callable[[AdminMode], None]] = None,
    ) -> None:
        """
        Initialise the state model.

        :param logger: the logger to be used by this state model.
        :param callback: A callback to be called when the state machine
            for admin_mode reports a change of state
        """
        self.logger = logger

        self._admin_mode = AdminMode.OFFLINE
        self._callback = callback

        # This type-hint needs investigation !!!
        self._admin_mode_machine = _AdminModeMachine(
            callback=self._admin_mode_changed  # type: ignore[arg-type]
        )

    @property
    def admin_mode(self: AdminModeModel) -> AdminMode:
        """
        Return the admin_mode.

        :returns: admin_mode of this state model
        """
        return self._admin_mode

    def _admin_mode_changed(self: AdminModeModel, machine_state: str) -> None:
        """
        Handle notification that the admin mode state machine has changed state.

        This is a helper method that updates admin mode, ensuring that
        the callback is called if one exists.

        :param machine_state: the new state of the admin mode machine
        """
        admin_mode = AdminMode[machine_state]
        if self._admin_mode != admin_mode:
            self._admin_mode = admin_mode
            if self._callback is not None:
                self._callback(admin_mode)

    def is_action_allowed(
        self: AdminModeModel, action: str, raise_if_disallowed: bool = False
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
        if action in self._admin_mode_machine.get_triggers(
            self._admin_mode_machine.state
        ):
            return True

        if raise_if_disallowed:
            raise StateModelError(
                f"Action {action} is not allowed in admin mode {self.admin_mode}."
            )
        return False

    def perform_action(self: AdminModeModel, action: str) -> None:
        """
        Perform an action on the state model.

        :param action: an action, as given in the transitions table
        """
        _ = self.is_action_allowed(action, raise_if_disallowed=True)
        self._admin_mode_machine.trigger(action)

    @for_testing_only
    def _straight_to_state(self: AdminModeModel, *, admin_mode: AdminMode) -> None:
        """
        Take this AdminMode state model straight to the specified AdminMode.

        This method exists to simplify testing; for example, if testing
        that a command may be run in a given AdminMode, you can push
        this state model straight to that AdminMode, rather than having
        to drive it to that state through a sequence of actions. It is
        not intended that this method would be called outside of test
        setups. A warning will be raised if it is.

        :param admin_mode: the target
        """
        getattr(self._admin_mode_machine, f"to_{admin_mode.name}")()
