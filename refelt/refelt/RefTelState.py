# -*- coding: utf-8 -*-
#
# This file is part of the RefTelState project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" RefTelState

Ref (Reference Element) Telstate device.
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
# PROTECTED REGION ID(RefTelState.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  RefTelState.additionnal_import

__all__ = ["RefTelState", "main"]


class RefTelState(SKABaseDevice):
    """
    Ref (Reference Element) Telstate device.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(RefTelState.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  RefTelState.class_variable

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
    # Refral methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(RefTelState.init_device) ENABLED START #
        # PROTECTED REGION END #    //  RefTelState.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(RefTelState.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefTelState.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(RefTelState.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefTelState.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_attr1(self):
        # PROTECTED REGION ID(RefTelState.attr1_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  RefTelState.attr1_read

    def read_attr2(self):
        # PROTECTED REGION ID(RefTelState.attr2_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  RefTelState.attr2_read

    def read_importantState(self):
        # PROTECTED REGION ID(RefTelState.importantState_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefTelState.importantState_read

    def write_importantState(self, value):
        # PROTECTED REGION ID(RefTelState.importantState_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefTelState.importantState_write


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def Reset(self):
        # PROTECTED REGION ID(RefTelState.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefTelState.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(RefTelState.main) ENABLED START #
    return run((RefTelState,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefTelState.main

if __name__ == '__main__':
    main()
