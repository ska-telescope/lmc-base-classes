# -*- coding: utf-8 -*-
#
# This file is part of the Rack project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" Rack

Ref (Reference Elt) Rack device
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
# PROTECTED REGION ID(Rack.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  Rack.additionnal_import

__all__ = ["Rack", "main"]


class Rack(SKABaseDevice):
    """
    Ref (Reference Elt) Rack device
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(Rack.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  Rack.class_variable

    # -----------------
    # Device Properties
    # -----------------

    pdus = device_property(
        dtype=('str',)
    )

    switches = device_property(
        dtype=('str',)
    )

    servers = device_property(
        dtype=('str',)
    )











    # ----------
    # Attributes
    # ----------











    # ---------------
    # Refral methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(Rack.init_device) ENABLED START #
        # PROTECTED REGION END #    //  Rack.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(Rack.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Rack.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(Rack.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Rack.delete_device

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
        # PROTECTED REGION ID(Rack.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Rack.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(Rack.main) ENABLED START #
    return run((Rack,), args=args, **kwargs)
    # PROTECTED REGION END #    //  Rack.main

if __name__ == '__main__':
    main()
