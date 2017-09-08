# -*- coding: utf-8 -*-
#
# This file is part of the SKATelStateDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SKATelStateDevice

A generic base device for Telescope State for SKA.
"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango.server import device_property
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
from SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(SKATelStateDevice.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SKATelStateDevice.additionnal_import

__all__ = ["SKATelStateDevice", "main"]


class SKATelStateDevice(SKABaseDevice):
    """
    A generic base device for Telescope State for SKA.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKATelStateDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKATelStateDevice.class_variable

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
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SKATelStateDevice.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKATelStateDevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKATelStateDevice.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKATelStateDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKATelStateDevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKATelStateDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def Reset(self):
        # PROTECTED REGION ID(SKATelStateDevice.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKATelStateDevice.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKATelStateDevice.main) ENABLED START #
    return run((SKATelStateDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKATelStateDevice.main

if __name__ == '__main__':
    main()
