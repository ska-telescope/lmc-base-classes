# pylint: skip-file  # TODO: Incrementally lint this repo
"""
This module specifies the operational state ("opState") model for SKA LMC Tango devices.

It consists of:

* an underlying state machine: :py:class:`._OpStateMachine`
* an :py:class:`.OpStateModel` that maps state machine state to device
  "op state". This "op state" is currently represented as a
  :py:class:`tango.DevState` enum value, and reported using the tango
  device's special ``state()`` method.
"""
from tango import DevState
from transitions.extensions import LockedMachine as Machine

from ska_tango_base.faults import StateModelError
from ska_tango_base.utils import for_testing_only

__all__ = ["OpStateModel"]


class _OpStateMachine(Machine):
    """
    State machine representing the operational state of the device.

    The operational state of a device is either the state of the system
    component that the device monitors, or a state that indicates why
    the device is not monitoring the system component.

    The post-init states supported are:

    * **DISABLE**: the device has been told not to monitor its telescope
      component
    * **UNKNOWN**: the device is monitoring (or at least trying to
      monitor) its telescope component but is unable to determine the
      component's state
    * **OFF**: the device is monitoring its telescope component and the
      component is powered off
    * **STANDBY**: the device is monitoring its telescope component and
      the component is in low-power standby mode
    * **ON**: the device is monitoring its telescope component and the
      component is turned on
    * **FAULT_STANDBY**: the device is monitoring its telescope
      component and the component is in low-power standby mode and has
      experienced a fault.
    * **FAULT_ON**: the device is monitoring its telescope component and
      the component is turned on and has experienced a fault.

    There are also corresponding initialising states: **INIT_DISABLE**,
    **INIT_UNKNOWN**, **INIT_OFF**, **INIT_STANDBY**, **INIT_ON**,
    **INIT_FAULT_STANDBY** and **INIT_FAULT_ON**. These states allow for
    the underlying system component to change its state during
    long-running initialisation, and for a device to transition to an
    appropriate state at the end of initialisation.

    Finally, there is an **_UNINITIALISED** starting state, representing
    a device that hasn't started initialising yet.

    The actions supported are:

    * **init_invoked**: the device has started initialising
    * **init_completed**: the device has finished initialising
    * **component_disconnected**: the device his disconnected from the
      telescope component that it is supposed to manage (for example
      because its admin mode was set to OFFLINE). Note, this action
      indicates a device-initiated, deliberate disconnect; a lost
      connection would be indicated by a "component_fault" or
      "component_unknown** action, depending on circumstances.
    * **component_unknown**: the device is unable to determine the state
      of its component.
    * **component_off**: the component has been switched off
    * **component_standby**: the component has switched to low-power
      standby mode
    * **component_on**: the component has been switched on
    * **component_fault**: the component has experienced a fault
    * **component_no_fault**: the component has stopped experiencing a
      fault

    A diagram of the state machine is shown below. Essentially, the
    machine has three "super-states", representing a device before,
    during and after initialisation. Transition between these
    "super-states" is triggered by the "init_invoked" and
    "init_completed" actions. In the last two "super-states", the device
    monitors the component and updates its state accordingly.

    .. uml:: op_state_machine.uml
       :caption: Diagram of the op state machine

    The following is a diagram of the state machine, automatically
    generated from the code. Its equivalence to the diagram above
    demonstrates that the implementation is faithful to the design.

    .. figure:: _OpStateMachine_autogenerated.png
      :alt: Diagram of the op state machine, as implemented
    """

    def __init__(self, callback=None, **extra_kwargs):
        """
        Initialise the state model.

        :param callback: A callback to be called when a transition
            implies a change to op state
        :type callback: callable
        :param extra_kwargs: Additional keywords arguments to pass to
            superclass initialiser (useful for graphing)
        """
        self._callback = callback

        states = [
            "_UNINITIALISED",
            "INIT_DISABLE",
            "INIT_UNKNOWN",
            "INIT_OFF",
            "INIT_STANDBY",
            "INIT_ON",
            "INIT_FAULT_STANDBY",
            "INIT_FAULT_ON",
            "DISABLE",
            "UNKNOWN",
            "OFF",
            "STANDBY",
            "ON",
            "FAULT_STANDBY",
            "FAULT_ON",
        ]

        transitions = [
            # Initial transition on the device starting initialisation
            {
                "source": "_UNINITIALISED",
                "trigger": "init_invoked",
                "dest": "INIT_DISABLE",
            },
            # Changes in the state of the monitored component
            # while the device is initialising
            {
                "source": [
                    "INIT_DISABLE",
                    "INIT_UNKNOWN",
                    "INIT_OFF",
                    "INIT_STANDBY",
                    "INIT_ON",
                    "INIT_FAULT_STANDBY",
                    "INIT_FAULT_ON",
                ],
                "trigger": "component_disconnected",
                "dest": "INIT_DISABLE",
            },
            {
                "source": [
                    "INIT_DISABLE",
                    "INIT_UNKNOWN",
                    "INIT_OFF",
                    "INIT_STANDBY",
                    "INIT_ON",
                    "INIT_FAULT_STANDBY",
                    "INIT_FAULT_ON",
                ],
                "trigger": "component_unknown",
                "dest": "INIT_UNKNOWN",
            },
            {
                "source": [
                    "INIT_DISABLE",
                    "INIT_UNKNOWN",
                    "INIT_OFF",
                    "INIT_STANDBY",
                    "INIT_ON",
                    "INIT_FAULT_STANDBY",
                    "INIT_FAULT_ON",
                ],
                "trigger": "component_off",
                "dest": "INIT_OFF",
            },
            {
                "source": [
                    "INIT_DISABLE",
                    "INIT_UNKNOWN",
                    "INIT_OFF",
                    "INIT_STANDBY",
                    "INIT_ON",
                ],
                "trigger": "component_standby",
                "dest": "INIT_STANDBY",
            },
            {
                "source": [
                    "INIT_FAULT_STANDBY",
                    "INIT_FAULT_ON",
                ],
                "trigger": "component_standby",
                "dest": "INIT_FAULT_STANDBY",
            },
            {
                "source": [
                    "INIT_DISABLE",
                    "INIT_UNKNOWN",
                    "INIT_OFF",
                    "INIT_STANDBY",
                    "INIT_ON",
                ],
                "trigger": "component_on",
                "dest": "INIT_ON",
            },
            {
                "source": [
                    "INIT_FAULT_STANDBY",
                    "INIT_FAULT_ON",
                ],
                "trigger": "component_on",
                "dest": "INIT_FAULT_ON",
            },
            {
                "source": ["INIT_STANDBY", "INIT_FAULT_STANDBY"],
                "trigger": "component_fault",
                "dest": "INIT_FAULT_STANDBY",
            },
            {
                "source": ["INIT_ON", "INIT_FAULT_ON"],
                "trigger": "component_fault",
                "dest": "INIT_FAULT_ON",
            },
            {
                "source": ["INIT_STANDBY", "INIT_FAULT_STANDBY"],
                "trigger": "component_no_fault",
                "dest": "INIT_STANDBY",
            },
            {
                "source": ["INIT_ON", "INIT_FAULT_ON"],
                "trigger": "component_no_fault",
                "dest": "INIT_ON",
            },
            # Completion of initialisation
            {
                "source": "INIT_DISABLE",
                "trigger": "init_completed",
                "dest": "DISABLE",
            },
            {
                "source": "INIT_UNKNOWN",
                "trigger": "init_completed",
                "dest": "UNKNOWN",
            },
            {
                "source": "INIT_OFF",
                "trigger": "init_completed",
                "dest": "OFF",
            },
            {
                "source": "INIT_STANDBY",
                "trigger": "init_completed",
                "dest": "STANDBY",
            },
            {
                "source": "INIT_ON",
                "trigger": "init_completed",
                "dest": "ON",
            },
            {
                "source": "INIT_FAULT_STANDBY",
                "trigger": "init_completed",
                "dest": "FAULT_STANDBY",
            },
            {
                "source": "INIT_FAULT_ON",
                "trigger": "init_completed",
                "dest": "FAULT_ON",
            },
            # Changes in the state of the monitored component post-initialisation
            {
                "source": [
                    "DISABLE",
                    "UNKNOWN",
                    "OFF",
                    "STANDBY",
                    "ON",
                    "FAULT_STANDBY",
                    "FAULT_ON",
                ],
                "trigger": "component_disconnected",
                "dest": "DISABLE",
            },
            {
                "source": [
                    "DISABLE",
                    "UNKNOWN",
                    "OFF",
                    "STANDBY",
                    "ON",
                    "FAULT_STANDBY",
                    "FAULT_ON",
                ],
                "trigger": "component_unknown",
                "dest": "UNKNOWN",
            },
            {
                "source": [
                    "DISABLE",
                    "UNKNOWN",
                    "OFF",
                    "STANDBY",
                    "ON",
                    "FAULT",
                    "FAULT_STANDBY",
                    "FAULT_ON",
                ],
                "trigger": "component_off",
                "dest": "OFF",
            },
            {
                "source": ["DISABLE", "UNKNOWN", "OFF", "STANDBY", "ON"],
                "trigger": "component_standby",
                "dest": "STANDBY",
            },
            {
                "source": ["FAULT_STANDBY", "FAULT_ON"],
                "trigger": "component_standby",
                "dest": "FAULT_STANDBY",
            },
            {
                "source": ["DISABLE", "UNKNOWN", "OFF", "STANDBY", "ON"],
                "trigger": "component_on",
                "dest": "ON",
            },
            {
                "source": ["FAULT_STANDBY", "FAULT_ON"],
                "trigger": "component_on",
                "dest": "FAULT_ON",
            },
            {
                "source": ["STANDBY", "FAULT_STANDBY"],
                "trigger": "component_fault",
                "dest": "FAULT_STANDBY",
            },
            {
                "source": ["ON", "FAULT_ON"],
                "trigger": "component_fault",
                "dest": "FAULT_ON",
            },
            {
                "source": ["STANDBY", "FAULT_STANDBY"],
                "trigger": "component_no_fault",
                "dest": "STANDBY",
            },
            {
                "source": ["ON", "FAULT_ON"],
                "trigger": "component_no_fault",
                "dest": "ON",
            },
        ]

        super().__init__(
            states=states,
            initial="_UNINITIALISED",
            transitions=transitions,
            after_state_change=self._state_changed,
            **extra_kwargs,
        )
        self._state_changed()

    def _state_changed(self):
        """
        State machine callback that is called every time the op_state changes.

        Responsible for ensuring that callbacks are called.
        """
        if self._callback is not None:
            self._callback(self.state)


class OpStateModel:
    """
    This class implements the state model for device operational state ("opState").

    The model supports the following states, represented as values of
    the :py:class:`tango.DevState` enum.

    * **INIT**: the device is initialising.
    * **DISABLE**: the device has been told not to monitor its telescope
      component
    * **UNKNOWN**: the device is monitoring (or at least trying to
      monitor) its telescope component but is unable to determine the
      component's state
    * **OFF**: the device is monitoring its telescope component and the
      component is powered off
    * **STANDBY**: the device is monitoring its telescope component and
      the component is in low-power standby mode
    * **ON**: the device is monitoring its telescope component and the
      component is turned on
    * **FAULT**: the device is monitoring its telescope component and
      the component has failed or is in an inconsistent state.

    These are essentially the same states as the underlying
    :py:class:`._OpStateMachine`, except that all initialisation states
    are mapped to the INIT DevState.

    The actions supported are:

    * **init_invoked**: the device has started initialising
    * **init_completed**: the device has finished initialising
    * **component_disconnected**: the device his disconnected from the
      telescope component that it is supposed to manage (for example
      because its admin mode was set to OFFLINE). Note, this action
      indicates a device-initiated, deliberate disconnect; a lost
      connection would be indicated by a "component_unknown" action.
    * **component_unknown**: the device is unable to determine the state
      of its component.
    * **component_off**: the component has been switched off
    * **component_standby**: the component has switched to low-power
      standby mode
    * **component_on**: the component has been switched on
    * **component_fault**: the component has experienced a fault
    * **component_no_fault**: the component has stopped experiencing a fault

    A diagram of the operational state model, as implemented, is shown
    below.

    .. uml:: op_state_model.uml
       :caption: Diagram of the operational state model

    The following hierarchical diagram is more explanatory; however note
    that the implementation does *not* use a hierarchical state machine.

    .. uml:: op_state_model_hierarchical.uml
       :caption: Diagram of the operational state model
    """

    def __init__(self, logger, callback=None):
        """
        Initialise the operational state model.

        :param logger: the logger to be used by this state model.
        :type logger: a logger that implements the standard library
            logger interface
        :param callback: A callback to be called when the state machine
            for op_state reports a change of state
        :type callback: callable
        """
        self.logger = logger

        self._op_state = None
        self._callback = callback

        self._op_state_machine = _OpStateMachine(
            callback=self._op_state_changed
        )

    @property
    def op_state(self):
        """
        Return the op state.

        :returns: the op state of this state model
        :rtype: :py:class:`tango.DevState`
        """
        return self._op_state

    _op_state_mapping = {
        "_UNINITIALISED": None,
        "INIT_DISABLE": DevState.INIT,
        "INIT_UNKNOWN": DevState.INIT,
        "INIT_OFF": DevState.INIT,
        "INIT_STANDBY": DevState.INIT,
        "INIT_ON": DevState.INIT,
        "INIT_FAULT_STANDBY": DevState.INIT,
        "INIT_FAULT_ON": DevState.INIT,
        "DISABLE": DevState.DISABLE,
        "UNKNOWN": DevState.UNKNOWN,
        "OFF": DevState.OFF,
        "STANDBY": DevState.STANDBY,
        "ON": DevState.ON,
        "FAULT_STANDBY": DevState.FAULT,
        "FAULT_ON": DevState.FAULT,
    }

    def _op_state_changed(self, machine_state):
        """
        Handle notification that the operational state machine has changed state.

        This is a helper method that updates op_state, ensuring that the
        callback is called if one exists.

        :param machine_state: the new state of the operation state
            machine
        :type machine_state: str
        """
        op_state = self._op_state_mapping[machine_state]
        if self._op_state != op_state:
            self._op_state = op_state
            if self._callback is not None:
                self._callback(op_state)

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
        if action in self._op_state_machine.get_triggers(
            self._op_state_machine.state
        ):
            return True

        if raise_if_disallowed:
            raise StateModelError(
                f"Action {action} is not allowed in op_state {self.op_state}."
            )
        return False

    def perform_action(self, action):
        """
        Perform an action on the state model.

        :param action: an action, as given in the transitions table
        :type action: str
        """
        _ = self.is_action_allowed(action, raise_if_disallowed=True)
        self._op_state_machine.trigger(action)

    @for_testing_only
    def _straight_to_state(self, op_state_name):
        """
        Take this op state model straight to the specified underlying op state.

        This method exists to simplify testing; for example, if testing
        that a command may be run in a given op state, you can push
        this state model straight to that op state, rather than having
        to drive it to that state through a sequence of actions. It is
        not intended that this method would be called outside of test
        setups. A warning will be raised if it is.

        The state must be provided as the string name of a state in the
        underlying :py:class:`._OpStateMachine`. This machine has more
        specific states, allowing for more flexibility in test setup.
        Specifically, there are "DISABLE", "UNKNOWN", "OFF", "STANDBY",
        "ON" and "FAULT" states, representing states of an initialised
        device. But instead of a single "INIT" state, there are
        "INIT_DISABLE", "INIT_UNKNOWN", "INIT_OFF", "INIT_STANDBY",
        "INIT_ON" and "INIT_FAULT" states, representing an initialised
        device with the monitored component in a given state.

        For example, to test that a device transitions out of INIT into
        STANDBY when the component that it monitors is in low-power
        standby mode:

        .. code-block:: py

          model = OpStateModel(logger)
          model._straight_to_state("INIT_STANDBY")
          assert model.op_state == DevState.INIT
          model.perform_action("init_completed")
          assert model.op_state == DevState.STANDBY

        :param op_state_name: the name of a target op state, as used by
            the underlying :py:class:`._OpStateMachine`.
        :type op_state_name: str
        """
        getattr(self._op_state_machine, f"to_{op_state_name}")()
