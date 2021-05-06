"""
This module specifies CSP SubElement Observing state machine. It
comprises:

* an underlying state machine:
  :py:class:`._CspSubElementObsStateMachine`

* a :py:class:`.CspSubElementObsStateModel` that maps the underlying
  state machine state to a value of the
  :py:class:`ska_tango_base.control_model.ObsState` enum.
"""
from transitions import State
from transitions.extensions import LockedMachine as Machine

from ska_tango_base.control_model import ObsState
from ska_tango_base.state import ObsStateModel

__all__ = ["CspSubElementObsStateModel"]


class _CspSubElementObsStateMachine(Machine):
    """
    The observation state machine used by a generic CSP sub-element
    ObsDevice (derived from SKAObsDevice).

    Compared to the SKA Observation State Machine, it implements a
    smaller number of states, number that can be further decreased
    depending on the necessities of the different sub-elements.

    The implemented states are:

    * **IDLE**: the device is unconfigured.

    * **CONFIGURING_IDLE**: the device in unconfigured, but
      configuration is in progress.

    * **CONFIGURING_READY**: the device in configured, and configuration
      is in progress.

    * **READY**: the device is configured and is ready to perform
      observations

    * **SCANNING**: the device is performing the observation.

    * **ABORTING**: the device is processing an abort.

      TODO: Need to understand if this state is really required by the
      observing devices of any CSP sub-element.

    * **ABORTED**: the device has completed the abort request.

    * **FAULT**: the device component has experienced an error from
      which it can be recovered only via manual intervention invoking a
      reset command that force the device to the base state (IDLE).

    The actions supported divide into command-oriented actions and
    component monitoring actions.

    The command-oriented actions are:

    * **configure_invoked** and **configure_completed**: bookending the
      Configure() command, and hence the CONFIGURING state
    * **abort_invoked** and **abort_completed**: bookending the Abort()
      command, and hence the ABORTING state
    * **obsreset_invoked** and **obsreset_completed**: bookending the
      ObsReset() command, and hence the OBSRESETTING state
    * **end_invoked**, **scan_invoked**, **end_scan_invoked**: these
      result in reflexive transitions, and are purely there to indicate
      states in which the End(), Scan() and EndScan() commands are
      permitted to be run

    The component-oriented actions are:

    * **component_obsfault**: the monitored component has experienced an
      observation fault
    * **component_unconfigured**: the monitored component has become
      unconfigured
    * **component_configured**: the monitored component has become
      configured
    * **component_scanning**: the monitored component has started
      scanning
    * **component_not_scanning**: the monitored component has stopped
      scanning

    A diagram of the state machine is shown below. Reflexive transitions
    and transitions to FAULT obs state are omitted to simplify the
    diagram.

    .. uml:: diagrams/csp_subelement_obs_state_machine.uml
       :caption: Diagram of the CSP subelement obs state machine

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
            "CONFIGURING_IDLE",  # device CONFIGURING but component is unconfigured
            "CONFIGURING_READY",  # device CONFIGURING and component is configured
            "READY",
            "SCANNING",
            "ABORTING",
            "ABORTED",
            "RESETTING",
            "FAULT",
        ]
        transitions = [
            {
                "source": "*",
                "trigger": "component_obsfault",
                "dest": "FAULT",
            },
            {
                "source": "IDLE",
                "trigger": "configure_invoked",
                "dest": "CONFIGURING_IDLE",
            },
            {
                "source": "CONFIGURING_IDLE",
                "trigger": "configure_completed",
                "dest": "IDLE",
            },
            {
                "source": "READY",
                "trigger": "configure_invoked",
                "dest": "CONFIGURING_READY",
            },
            {
                "source": "CONFIGURING_IDLE",
                "trigger": "component_configured",
                "dest": "CONFIGURING_READY",
            },
            {
                "source": "CONFIGURING_READY",
                "trigger": "configure_completed",
                "dest": "READY",
            },
            {
                "source": "READY",
                "trigger": "end_invoked",
                "dest": "READY",
            },
            {
                "source": "READY",
                "trigger": "component_unconfigured",
                "dest": "IDLE",
            },
            {
                "source": "READY",
                "trigger": "scan_invoked",
                "dest": "READY",
            },
            {
                "source": "READY",
                "trigger": "component_scanning",
                "dest": "SCANNING",
            },
            {
                "source": "SCANNING",
                "trigger": "end_scan_invoked",
                "dest": "SCANNING",
            },
            {
                "source": "SCANNING",
                "trigger": "component_not_scanning",
                "dest": "READY",
            },
            {
                "source": [
                    "IDLE",
                    "CONFIGURING_IDLE",
                    "CONFIGURING_READY",
                    "READY",
                    "SCANNING",
                    "RESETTING",
                ],
                "trigger": "abort_invoked",
                "dest": "ABORTING",
            },
            # Aborting implies trying to stop the monitored component
            # while it is doing something. Thus the monitored component
            # may send some events while in aborting state.
            {
                "source": "ABORTING",
                "trigger": "component_unconfigured",  # Abort() invoked on ObsReset()
                "dest": "ABORTING",
            },
            {
                "source": "ABORTING",
                "trigger": "component_configured",  # Configure() was just finishing
                "dest": "ABORTING",
            },
            {
                "source": ["ABORTING"],
                "trigger": "component_not_scanning",  # Aborting implies stopping scan
                "dest": "ABORTING",
            },
            {
                "source": ["ABORTING"],
                "trigger": "component_scanning",  # Abort() invoked as scan is starting
                "dest": "ABORTING",
            },
            {
                "source": "ABORTING",
                "trigger": "abort_completed",
                "dest": "ABORTED",
            },
            {
                "source": ["ABORTED", "FAULT"],
                "trigger": "obsreset_invoked",
                "dest": "RESETTING",
            },
            {
                "source": "RESETTING",
                "trigger": "component_unconfigured",  # Resetting implies deconfiguring
                "dest": "RESETTING",
            },
            {
                "source": "RESETTING",
                "trigger": "obsreset_completed",
                "dest": "IDLE",
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


class CspSubElementObsStateModel(ObsStateModel):
    """
    Implements the observation state model for a generic CSP sub-element
    ObsDevice (derived from SKAObsDevice).

    Compared to the SKA observation state model, it implements a
    smaller number of states, number that can be further decreased
    depending on the necessities of the different sub-elements.

    The implemented states are:

    * **IDLE**: the device is unconfigured.

    * **CONFIGURING**: transitional state to report device configuration
      is in progress.
      
      TODO: Need to understand if this state is really required by the
      observing devices of any CSP sub-element.

    * **READY**: the device is configured and is ready to perform
      observations

    * **SCANNING**: the device is performing the observation.

    * **ABORTING**: the device is processing an abort.

      TODO: Need to understand if this state is really required by the
      observing devices of any CSP sub-element.

    * **ABORTED**: the device has completed the abort request.

    * **FAULT**: the device component has experienced an error from
      which it can be recovered only via manual intervention invoking a
      reset command that force the device to the base state (IDLE).

    A diagram of the CSP subelement observation state model is shown
    below. This model is non-deterministic as diagrammed, but the
    underlying state machine has extra state and transitions that render
    it deterministic. This model class simply maps those extra classes
    onto valid ObsState values

    .. uml:: diagrams/csp_subelement_obs_state_model.uml
       :caption: Diagram of the subarray observation state model
    """

    def __init__(self, logger, callback=None):
        """
        Initialise the model.

        :param logger: the logger to be used by this state model.
        :type logger: a logger that implements the standard library
            logger interface
        :param callback: A callback to be called when a transition
            causes a change to device obs_state
        :type callback: callable
        """
        super().__init__(_CspSubElementObsStateMachine, logger, callback=callback)

    _obs_state_mapping = {
        "IDLE": ObsState.IDLE,
        "CONFIGURING_IDLE": ObsState.CONFIGURING,
        "CONFIGURING_READY": ObsState.CONFIGURING,
        "READY": ObsState.READY,
        "SCANNING": ObsState.SCANNING,
        "ABORTING": ObsState.ABORTING,
        "ABORTED": ObsState.ABORTED,
        "RESETTING": ObsState.RESETTING,
        "FAULT": ObsState.FAULT,
    }

    def _obs_state_changed(self, machine_state):
        """
        Helper method that updates admin_mode whenever the admin_mode
        state machine reports a change of state, ensuring that the
        callback is called if one exists.

        :param machine_state: the new state of the adminMode state
            machine
        :type machine_state: str
        """
        obs_state = self._obs_state_mapping[machine_state]
        if self._obs_state != obs_state:
            self._obs_state = obs_state
            if self._callback is not None:
                self._callback(obs_state)
