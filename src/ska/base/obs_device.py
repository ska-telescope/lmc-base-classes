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
# Tango imports
from tango import DevState
from tango.server import run, attribute

# SKA specific imports
from ska.base import SKABaseDevice, SKABaseDeviceStateModel
from ska.base.commands import ResultCode
from ska.base.control_model import AdminMode, ObsMode, ObsState
# PROTECTED REGION END #    //  SKAObsDevice.additionnal_imports

__all__ = ["SKAObsDevice", "SKAObsDeviceStateModel", "main"]


class SKAObsDeviceStateModel(SKABaseDeviceStateModel):
    """
    Implements the state model for the SKABaseDevice
    """
    def __init__(self, dev_state_callback=None):
        """
        Initialises the model. Note that this does not imply moving to
        INIT state. The INIT state is managed by the model itself.
        """
        super().__init__(
            dev_state_callback=dev_state_callback
        )
        self.update_transitions(
            {
                ('UNINITIALISED', 'init_started'): (
                    "INIT (ENABLED)",
                    lambda self: (
                        self._set_admin_mode(AdminMode.MAINTENANCE),
                        self._set_dev_state(DevState.INIT),
                        self._set_obs_state(ObsState.EMPTY)
                    )
                )
            }
        )
        self._obs_state = None

    def _set_obs_state(self, obs_state):
        """
        Helper method: set the value of obs_state value

        :param obs_state: the new obs_state value
        :type obs_state: ObsState
        """
        self._obs_state = obs_state

    @property
    def obs_state(self):
        return self._obs_state


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
        polling_period=1000,
        doc="Observing State",
    )

    obsMode = attribute(
        dtype=ObsMode,
        polling_period=1000,
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
    def _init_state_model(self):
        """
        Sets up the state model for the device
        """
        self.state_model = SKAObsDeviceStateModel(
            dev_state_callback=self._update_state,
        )

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKAObsDevice.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAObsDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKAObsDevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAObsDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_obsState(self):
        # PROTECTED REGION ID(SKAObsDevice.obsState_read) ENABLED START #
        """Reads Observation State of the device"""
        return self.state_model.obs_state
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
