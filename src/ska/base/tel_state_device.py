# -*- coding: utf-8 -*-
#
# This file is part of the SKATelState project
#
#
#
""" SKATelState

A generic base device for Telescope State for SKA.
"""
# PROTECTED REGION ID(SKATelState.additionnal_import) ENABLED START #
# Standard import
import os
import sys

# Tango imports
from tango.server import run, device_property

# SKA specific imports
from . import SKABaseDevice, release
# PROTECTED REGION END #    //  SKATelState.additionnal_imports

__all__ = ["SKATelState", "main"]


class SKATelState(SKABaseDevice):
    """
    A generic base device for Telescope State for SKA.
    """
    # PROTECTED REGION ID(SKATelState.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKATelState.class_variable

    # -----------------
    # Device Properties
    # -----------------

    TelStateConfigFile = device_property(
        dtype='str',
    )


    # ----------
    # Attributes
    # ----------

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """init_device
        Init device method of SKATelStateDevice
        """
        SKABaseDevice.init_device(self)
        self._build_state = '{}, {}, {}'.format(release.name, release.version,
                                                release.description)
        self._version_id = release.version
        # PROTECTED REGION ID(SKATelState.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKATelState.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKATelState.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKATelState.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKATelState.delete_device) ENABLED START #
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
    """
    Main function of the module

    :param args: None by default.

    :param kwargs:

    :return:
    """
    return run((SKATelState,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKATelState.main

if __name__ == '__main__':
    main()
