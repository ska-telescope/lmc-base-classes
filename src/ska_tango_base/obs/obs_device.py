# -*- coding: utf-8 -*-
#
# This file is part of the SKAObsDevice project
#
#
#
"""
SKAObsDevice.

A generic base device for Observations for SKA. It inherits
SKABaseDevice class. Any device implementing an obsMode will inherit
from SKAObsDevice instead of just SKABaseDevice.
"""

# Additional import
# PROTECTED REGION ID(SKAObsDevice.additionnal_import) ENABLED START #
# Tango imports
from tango.server import run, attribute

# SKA specific imports
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import DeviceInitCommand, ResultCode
from ska_tango_base.control_model import ObsMode, ObsState

# PROTECTED REGION END #    //  SKAObsDevice.additionnal_imports

__all__ = ["SKAObsDevice", "main"]


class SKAObsDevice(SKABaseDevice):
    """A generic base device for Observations for SKA."""

    class InitCommand(DeviceInitCommand):
        """A class for the SKAObsDevice's init_device() "command"."""

        def do(self):
            """
            Stateless hook for device initialisation.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            self._device._obs_state = ObsState.EMPTY
            self._device._obs_mode = ObsMode.IDLE
            self._device._config_progress = 0
            self._device._config_delay_expected = 0

            for attribute_name in [
                "obsState",
                "obsMode",
                "configurationProgress",
                "configurationDelayExpected",
            ]:
                self._device.set_change_event(attribute_name, True)
                self._device.set_archive_event(attribute_name, True)

            message = "SKAObsDevice Init command completed OK"
            self.logger.info(message)
            self._completed()
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
    """Device attribute."""

    obsMode = attribute(
        dtype=ObsMode,
        doc="Observing Mode",
    )
    """Device attribute."""

    configurationProgress = attribute(
        dtype="uint16",
        unit="%",
        max_value=100,
        min_value=0,
        doc="Percentage configuration progress",
    )
    """Device attribute."""

    configurationDelayExpected = attribute(
        dtype="uint16",
        unit="seconds",
        doc="Configuration delay expected in seconds",
    )
    """Device attribute."""

    # ---------------
    # General methods
    # ---------------
    def _update_obs_state(self, obs_state):
        """
        Perform Tango operations in response to a change in obsState.

        This helper method is passed to the observation state model as a
        callback, so that the model can trigger actions in the Tango
        device.

        :param obs_state: the new obs_state value
        :type obs_state: :py:class:`~ska_tango_base.control_model.ObsState`
        """
        self._obs_state = obs_state
        self.push_change_event("obsState", obs_state)
        self.push_archive_event("obsState", obs_state)

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKAObsDevice.always_executed_hook) ENABLED START #
        """
        Perform actions that are executed before every device command.

        This is a Tango hook.
        """
        pass
        # PROTECTED REGION END #    //  SKAObsDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKAObsDevice.delete_device) ENABLED START #
        """
        Clean up any resources prior to device deletion.

        This method is a Tango hook that is called by the device
        destructor and by the device Init command. It allows for any
        memory or other resources allocated in the init_device method to
        be released prior to device deletion.
        """
        pass
        # PROTECTED REGION END #    //  SKAObsDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_obsState(self):
        # PROTECTED REGION ID(SKAObsDevice.obsState_read) ENABLED START #
        """Read the Observation State of the device."""
        return self._obs_state
        # PROTECTED REGION END #    //  SKAObsDevice.obsState_read

    def read_obsMode(self):
        # PROTECTED REGION ID(SKAObsDevice.obsMode_read) ENABLED START #
        """Read the Observation Mode of the device."""
        return self._obs_mode
        # PROTECTED REGION END #    //  SKAObsDevice.obsMode_read

    def read_configurationProgress(self):
        # PROTECTED REGION ID(SKAObsDevice.configurationProgress_read) ENABLED START #
        """Read the percentage configuration progress of the device."""
        return self._config_progress
        # PROTECTED REGION END #    //  SKAObsDevice.configurationProgress_read

    def read_configurationDelayExpected(self):
        # PROTECTED REGION ID(SKAObsDevice.configurationDelayExpected_read) ENABLED START #
        """Read the expected Configuration Delay in seconds."""
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
    Launch an SKAObsDevice.

    :param args: positional arguments
    :param kwargs: keyword arguments
    """
    return run((SKAObsDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKAObsDevice.main


if __name__ == "__main__":
    main()
