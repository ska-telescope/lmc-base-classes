# -*- coding: utf-8 -*-
#
# This file is part of the GeneAchild project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" GeneAchild

Gene (Gen Element) device of type Achild
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
# PROTECTED REGION ID(GeneAchild.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  GeneAchild.additionnal_import

__all__ = ["GeneAchild", "main"]


class GeneAchild(SKABaseDevice):
    """
    Gene (Gen Element) device of type Achild
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(GeneAchild.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  GeneAchild.class_variable

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
        # PROTECTED REGION ID(GeneAchild.init_device) ENABLED START #
        # PROTECTED REGION END #    //  GeneAchild.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(GeneAchild.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneAchild.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(GeneAchild.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneAchild.delete_device

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
        # PROTECTED REGION ID(GeneAchild.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneAchild.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(GeneAchild.main) ENABLED START #
    return run((GeneAchild,), args=args, **kwargs)
    # PROTECTED REGION END #    //  GeneAchild.main

if __name__ == '__main__':
    main()
