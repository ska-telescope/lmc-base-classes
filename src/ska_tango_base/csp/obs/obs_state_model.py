"""
This module specifies CSP SubElement Observing state machine.

It comprises:

* an underlying state machine:
  :py:class:`.CspSubElementObsStateMachine`

* a :py:class:`.CspSubElementObsStateModel` that maps the underlying
  state machine state to a value of the
  :py:class:`ska_control_model.obs_state.ObsState` enum.
"""
import logging
from typing import Any, Callable, Optional

from transitions.extensions import LockedMachine as Machine

from ska_tango_base.obs import ObsStateModel

__all__ = ["CspSubElementObsStateMachine", "CspSubElementObsStateModel"]


class CspSubElementObsStateMachine(Machine):
    """
    The observation state machine used by a generic CSP sub-element ObsDevice.

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

    .. uml:: obs_state_machine.uml
       :caption: Diagram of the CSP subelement obs state machine
    """

    def __init__(
        self, callback: Optional[Callable] = None, **extra_kwargs: Any
    ) -> None:
        """
        Initialise the model.

        :param callback: A callback to be called when the state changes
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

    def _state_changed(self) -> None:
        """
        State machine callback that is called every time the obs_state changes.

        Responsible for ensuring that callbacks are called.
        """
        if self._callback is not None:
            self._callback(self.state)


class CspSubElementObsStateModel(ObsStateModel):
    """
    Implements the observation state model for a generic CSP sub-element ObsDevice.

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

    * **RESETTING**: the device is resetting from an ABORTED or FAULT
      state back to IDLE

    * **FAULT**: the device component has experienced an error from
      which it can be recovered only via manual intervention invoking a
      reset command that force the device to the base state (IDLE).
    """

    def __init__(
        self, logger: logging.Logger, callback: Optional[Callable] = None
    ) -> None:
        """
        Initialise the model.

        :param logger: the logger to be used by this state model.
        :param callback: A callback to be called when a transition
            causes a change to device obs_state
        """
        super().__init__(
            logger,
            callback=callback,
            state_machine_factory=CspSubElementObsStateMachine,
        )
