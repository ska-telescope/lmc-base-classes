# -*- coding: utf-8 -*-
#
# This file is part of the RefB project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" RefB

Ref (Reference Element) device of type B.
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
# PROTECTED REGION ID(RefB.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  RefB.additionnal_import

__all__ = ["RefB", "main"]


class RefB(SKABaseDevice):
    """
    Ref (Reference Element) device of type B.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(RefB.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  RefB.class_variable

    # -----------------
    # Device Properties
    # -----------------










    # ----------
    # Attributes
    # ----------



    attr1 = attribute(
        dtype='str',
        doc="Attribute 1 for DevB",
    )

    attr2 = attribute(
        dtype='str',
        doc="Attribute 2 for DevB",
    )









    importantState = attribute(
        dtype='DevEnum',
        access=AttrWriteType.READ_WRITE,
        enum_labels=["OK", "GOOD", "BAD", "VERY-BAD", ],
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(RefB.init_device) ENABLED START #
        # PROTECTED REGION END #    //  RefB.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(RefB.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefB.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(RefB.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefB.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_attr1(self):
        # PROTECTED REGION ID(RefB.attr1_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  RefB.attr1_read

    def read_attr2(self):
        # PROTECTED REGION ID(RefB.attr2_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  RefB.attr2_read

    def read_importantState(self):
        # PROTECTED REGION ID(RefB.importantState_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefB.importantState_read

    def write_importantState(self, value):
        # PROTECTED REGION ID(RefB.importantState_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefB.importantState_write


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def Reset(self):
        # PROTECTED REGION ID(RefB.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefB.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(RefB.main) ENABLED START #
    return run((RefB,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefB.main

if __name__ == '__main__':
    main()
