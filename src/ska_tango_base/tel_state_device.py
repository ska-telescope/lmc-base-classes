# -*- coding: utf-8 -*-
#
# This file is part of the SKATelState project
#
#
#
"""
SKATelState.

A generic base device for Telescope State for SKA.
"""
# PROTECTED REGION ID(SKATelState.additionnal_import) ENABLED START #
# Tango imports
# from tango import DebugIt
from tango.server import run, device_property

# SKA specific imports
from ska_tango_base import SKABaseDevice

# PROTECTED REGION END #    //  SKATelState.additionnal_imports

__all__ = ["SKATelState", "main"]


class SKATelState(SKABaseDevice):
    """A generic base device for Telescope State for SKA."""

    # PROTECTED REGION ID(SKATelState.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.class_variable

    # -----------------
    # Device Properties
    # -----------------

    TelStateConfigFile = device_property(
        dtype="str",
    )

    # ----------
    # Attributes
    # ----------

    # ---------------
    # General methods
    # ---------------
    def always_executed_hook(self):
        # PROTECTED REGION ID(SKATelState.always_executed_hook) ENABLED START #
        """
        Perform actions that are executed before every device command.

        This is a Tango hook.
        """
        pass
        # PROTECTED REGION END #    //  SKATelState.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKATelState.delete_device) ENABLED START #
        """
        Clean up any resources prior to device deletion.

        This method is a Tango hook that is called by the device
        destructor and by the device Init command. It allows for any
        memory or other resources allocated in the init_device method to
        be released prior to device deletion.
        """
        pass
        # PROTECTED REGION END #    //  SKATelState.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    # --------
    # Commands
    # --------


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKATelState.main) ENABLED START #
    """Launch an SKATelState device."""
    return run((SKATelState,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKATelState.main


if __name__ == "__main__":
    main()
