# -*- coding: utf-8 -*-
#
# This file is part of the SKAObsDevice project
#
#
#
""" SKAObsDevice

A generic base device for Observations for SKA. It inherits SKABaseDevice
class. Any device implementing an obsMode will inherit from SKAObsDevice
instead of just SKABaseDevice.
"""

# Additional import
# PROTECTED REGION ID(SKAObsDevice.additionnal_import) ENABLED START #
import warnings

# Tango imports
from tango import DevState
from tango.server import run, attribute

# SKA specific imports
from ska_tango_base import SKABaseDevice, DeviceStateModel
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsMode, ObsState
from ska_tango_base.faults import StateModelError
from ska_tango_base.utils import for_testing_only
# PROTECTED REGION END #    //  SKAObsDevice.additionnal_imports

__all__ = ["SKAObsDevice", "ObsDeviceStateModel", "main"]


class ObsDeviceStateModel(DeviceStateModel):
    """
    Base class for ObsDevice state models
    """

    def __init__(
        self,
        action_breakdown,
        obs_machine_class,
        logger,
        op_state_callback=None,
        admin_mode_callback=None,
        obs_state_callback=None,
    ):
        """
        Initialises the model.

        :param action_breakdown: the action breakdown associated with the observing
           state machine class
        :type action_breakdown: dictionary defining actions to be performed
            on the observation state machine and,as needed, on the device state machine.
        :param obs_machine_class
        :type obs_machine_class: state machine for the observing state of a
            SKAObsDevice class device.
        :param logger: the logger to be used by this state model.
        :type logger: a logger that implements the standard library
            logger interface
        :param op_state_callback: A callback to be called when a
            transition implies a change to op state
        :type op_state_callback: callable
        :param admin_mode_callback: A callback to be called when a
            transition causes a change to device admin_mode
        :type admin_mode_callback: callable
        :param obs_state_callback: A callback to be called when a
            transition causes a change to device obs_state
        :type obs_state_callback: callable
        """
        super().__init__(
            logger,
            op_state_callback=op_state_callback,
            admin_mode_callback=admin_mode_callback,
        )

        self._obs_state = None
        self._obs_state_callback = obs_state_callback

        self._observation_state_machine = obs_machine_class(
            self._update_obs_state
        )
        self._action_breakdown = dict(action_breakdown)

    @property
    def obs_state(self):
        """
        Returns the obs_state

        :returns: obs_state of this state model
        :rtype: ObsState
        """
        return self._obs_state

    def _update_obs_state(self, machine_state):
        """
        Helper method that updates obs_state whenever the observation
        state machine reports a change of state, ensuring that the
        callback is called if one exists.

        :param machine_state: the new state of the observation state
            machine
        :type machine_state: str
        """
        obs_state = ObsState[machine_state]
        if self._obs_state != obs_state:
            self._obs_state = obs_state
            if self._obs_state_callback is not None:
                self._obs_state_callback(obs_state)

    def _is_obs_action_allowed(self, action):
        if action not in self._action_breakdown:
            return None

        if self.op_state != DevState.ON:
            return False

        (obs_action, super_action) = self._action_breakdown[action]

        if obs_action not in self._observation_state_machine.get_triggers(
            self._observation_state_machine.state
        ):
            return False
        return super_action is None or super().is_action_allowed(super_action)

    def is_action_allowed(self, action):
        """
        Whether a given action is allowed in the current state.

        :param action: an action, as given in the transitions table
        :type action: ANY

        :returns: where the action is allowed in the current state:
        :rtype: bool: True if the action is allowed, False if it is
            not allowed
        :raises StateModelError: for an unrecognised action
        """
        obs_allowed = self._is_obs_action_allowed(action)
        if obs_allowed is None:
            return super().is_action_allowed(action)
        if obs_allowed:
            return True
        try:
            return super().is_action_allowed(action)
        except StateModelError:
            return False

    def try_action(self, action):
        """
        Checks whether a given action is allowed in the current state,
        and raises a StateModelError if it is not.

        :param action: an action, as given in the transitions table
        :type action: str

        :raises StateModelError: if the action is not allowed in the
            current state

        :returns: True if the action is allowed
        :rtype: boolean
        """
        if not self.is_action_allowed(action):
            raise StateModelError(
                f"Action {action} is not allowed in operational state "
                f"{self.op_state}, admin mode {self.admin_mode}, "
                f"observation state {self.obs_state}."
            )
        return True

    def perform_action(self, action):
        """
        Performs an action on the state model

        :param action: an action, as given in the transitions table
        :type action: ANY

        :raises StateModelError: if the action is not allowed in the
            current state

        """
        self.try_action(action)

        if self._is_obs_action_allowed(action):
            (obs_action, super_action) = self._action_breakdown[action]

            if obs_action.startswith("to_"):
                message = (
                    f"Forcing device state of an observing device "
                    f"should only be done as an emergency measure and may be "
                    f"disallowed in future (action: {obs_action})."
                )
                self.logger.warning(message)
                warnings.warn(message, PendingDeprecationWarning)

            self._observation_state_machine.trigger(obs_action)
            if super_action is not None:
                super().perform_action(super_action)
        else:
            super().perform_action(action)

    @for_testing_only
    def _straight_to_state(self, op_state=None, admin_mode=None, obs_state=None):
        """
        Takes the ObsDeviceStateModel straight to the specified states.
        This method exists to simplify testing; for example, if testing
        that a command may be run in a given state, one can push the
        state model straight to that state, rather than having to drive
        it to that state through a sequence of actions. It is not
        intended that this method would be called outside of test
        setups. A warning will be raised if it is.

        Note that this method will allow you to put the device into an
        incoherent combination of states and modes (e.g. adminMode
        OFFLINE, opState STANDBY, and obsState SCANNING).

        :param op_state: the target operational state (optional)
        :type op_state: :py:class:`tango.DevState`
        :param admin_mode: the target admin mode (optional)
        :type admin_mode: :py:class:`~ska_tango_base.control_model.AdminMode`
        :param obs_state: the target observation state (optional)
        :type obs_state: :py:class:`~ska_tango_base.control_model.ObsState`
        """
        if obs_state is not None:
            getattr(self._observation_state_machine, f"to_{obs_state.name}")()
        super()._straight_to_state(op_state=op_state, admin_mode=admin_mode)


class SKAObsDevice(SKABaseDevice):
    """
    A generic base device for Observations for SKA.
    """
    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the SKAObsDevice's init_device() "command".
        """

        def do(self):
            """
            Stateless hook for device initialisation.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            super().do()

            device = self.target
            device.set_change_event("obsState", True, True)
            device.set_archive_event("obsState", True, True)

            device._obs_state = ObsState.EMPTY
            device._obs_mode = ObsMode.IDLE
            device._config_progress = 0
            device._config_delay_expected = 0

            message = "SKAObsDevice Init command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    # PROTECTED REGION ID(SKAObsDevice.class_variable) ENABLED START #

    # PROTECTED REGION END #    //  SKAObsDevice.class_variable

    # -----------------
    # Device Properties
    # -----------------

    # ----------
    # Attributes
    # ----------

    obsState = attribute(
        dtype=ObsState,
        doc="Observing State",
    )

    obsMode = attribute(
        dtype=ObsMode,
        doc="Observing Mode",
    )

    configurationProgress = attribute(
        dtype='uint16',
        unit="%",
        max_value=100,
        min_value=0,
        doc="Percentage configuration progress",
    )

    configurationDelayExpected = attribute(
        dtype='uint16',
        unit="seconds",
        doc="Configuration delay expected in seconds",
    )

    # ---------------
    # General methods
    # ---------------
    def _update_obs_state(self, obs_state):
        """
        Helper method for changing obs_state; passed to the state model as a
        callback

        :param obs_state: the new obs_state value
        :type admin_mode: :py:class:`~ska_tango_base.control_model.ObsState`
        """
        self._obs_state = obs_state
        self.push_change_event("obsState", obs_state)
        self.push_archive_event("obsState", obs_state)

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKAObsDevice.always_executed_hook) ENABLED START #
        """
        Method that is always executed before any device command gets executed.

        :return: None
        """
        pass
        # PROTECTED REGION END #    //  SKAObsDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKAObsDevice.delete_device) ENABLED START #
        """
        Method to cleanup when device is stopped.

        :return: None
        """
        pass
        # PROTECTED REGION END #    //  SKAObsDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_obsState(self):
        # PROTECTED REGION ID(SKAObsDevice.obsState_read) ENABLED START #
        """Reads Observation State of the device"""
        return self._obs_state
        # PROTECTED REGION END #    //  SKAObsDevice.obsState_read

    def read_obsMode(self):
        # PROTECTED REGION ID(SKAObsDevice.obsMode_read) ENABLED START #
        """Reads Observation Mode of the device"""
        return self._obs_mode
        # PROTECTED REGION END #    //  SKAObsDevice.obsMode_read

    def read_configurationProgress(self):
        # PROTECTED REGION ID(SKAObsDevice.configurationProgress_read) ENABLED START #
        """Reads percentage configuration progress of the device"""
        return self._config_progress
        # PROTECTED REGION END #    //  SKAObsDevice.configurationProgress_read

    def read_configurationDelayExpected(self):
        # PROTECTED REGION ID(SKAObsDevice.configurationDelayExpected_read) ENABLED START #
        """Reads expected Configuration Delay in seconds"""
        return self._config_delay_expected
        # PROTECTED REGION END #    //  SKAObsDevice.configurationDelayExpected_read

    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKAObsDevice.main) ENABLED START #
    """
    Main function of the SKAObsDevice module.

    :param args: None
    :param kwargs:
    """
    return run((SKAObsDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKAObsDevice.main


if __name__ == '__main__':
    main()
