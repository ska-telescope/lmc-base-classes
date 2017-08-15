# -*- coding: utf-8 -*-
#
# This file is part of the RefAchild project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" RefAchild

Ref (Reference Element) device of type Achild
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
# PROTECTED REGION ID(RefAchild.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  RefAchild.additionnal_import

__all__ = ["RefAchild", "main"]


class RefAchild(SKABaseDevice):
    """
    Ref (Reference Element) device of type Achild
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(RefAchild.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  RefAchild.class_variable

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
        # PROTECTED REGION ID(RefAchild.init_device) ENABLED START #
        # PROTECTED REGION END #    //  RefAchild.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(RefAchild.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefAchild.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(RefAchild.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefAchild.delete_device

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
        # PROTECTED REGION ID(RefAchild.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefAchild.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(RefAchild.main) ENABLED START #
    return run((RefAchild,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefAchild.main

if __name__ == '__main__':
    main()
