# -*- coding: utf-8 -*-
#
# This file is part of the GeneBchild project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" GeneBchild

 Gene (Gen Element) device of type Bchild.
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
# PROTECTED REGION ID(GeneBchild.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  GeneBchild.additionnal_import

__all__ = ["GeneBchild", "main"]


class GeneBchild(SKABaseDevice):
    """
     Gene (Gen Element) device of type Bchild.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(GeneBchild.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  GeneBchild.class_variable

    # -----------------
    # Device Properties
    # -----------------










    # ----------
    # Attributes
    # ----------













    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(GeneBchild.init_device) ENABLED START #
        # PROTECTED REGION END #    //  GeneBchild.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(GeneBchild.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneBchild.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(GeneBchild.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneBchild.delete_device

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
        # PROTECTED REGION ID(GeneBchild.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneBchild.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(GeneBchild.main) ENABLED START #
    return run((GeneBchild,), args=args, **kwargs)
    # PROTECTED REGION END #    //  GeneBchild.main

if __name__ == '__main__':
    main()
