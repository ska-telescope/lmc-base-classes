# -*- coding: utf-8 -*-
#
# This file is part of the RefBchild project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" RefBchild

 Ref (Reference Element) device of type Bchild.
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
# PROTECTED REGION ID(RefBchild.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  RefBchild.additionnal_import

__all__ = ["RefBchild", "main"]


class RefBchild(SKABaseDevice):
    """
     Ref (Reference Element) device of type Bchild.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(RefBchild.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  RefBchild.class_variable

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
        # PROTECTED REGION ID(RefBchild.init_device) ENABLED START #
        # PROTECTED REGION END #    //  RefBchild.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(RefBchild.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefBchild.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(RefBchild.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefBchild.delete_device

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
        # PROTECTED REGION ID(RefBchild.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefBchild.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(RefBchild.main) ENABLED START #
    return run((RefBchild,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefBchild.main

if __name__ == '__main__':
    main()
