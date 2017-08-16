# -*- coding: utf-8 -*-
#
# This file is part of the Switch project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" Switch

Ref (Reference Elt) Swtich device
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
# PROTECTED REGION ID(Switch.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  Switch.additionnal_import

__all__ = ["Switch", "main"]


class Switch(SKABaseDevice):
    """
    Ref (Reference Elt) Swtich device
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(Switch.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  Switch.class_variable

    # -----------------
    # Device Properties
    # -----------------










    # ----------
    # Attributes
    # ----------











    # ---------------
    # Refral methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(Switch.init_device) ENABLED START #
        # PROTECTED REGION END #    //  Switch.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(Switch.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Switch.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(Switch.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Switch.delete_device

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
        # PROTECTED REGION ID(Switch.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Switch.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(Switch.main) ENABLED START #
    return run((Switch,), args=args, **kwargs)
    # PROTECTED REGION END #    //  Switch.main

if __name__ == '__main__':
    main()
