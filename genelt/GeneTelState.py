# -*- coding: utf-8 -*-
#
# This file is part of the GeneTelState project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" GeneTelState

Gene (Gen Element) Telstate device.
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
# PROTECTED REGION ID(GeneTelState.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  GeneTelState.additionnal_import

__all__ = ["GeneTelState", "main"]


class GeneTelState(SKABaseDevice):
    """
    Gene (Gen Element) Telstate device.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(GeneTelState.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  GeneTelState.class_variable

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
        # PROTECTED REGION ID(GeneTelState.init_device) ENABLED START #
        # PROTECTED REGION END #    //  GeneTelState.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(GeneTelState.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneTelState.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(GeneTelState.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneTelState.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_attr1(self):
        # PROTECTED REGION ID(GeneTelState.attr1_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  GeneTelState.attr1_read

    def read_attr2(self):
        # PROTECTED REGION ID(GeneTelState.attr2_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  GeneTelState.attr2_read

    def read_importantState(self):
        # PROTECTED REGION ID(GeneTelState.importantState_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  GeneTelState.importantState_read

    def write_importantState(self, value):
        # PROTECTED REGION ID(GeneTelState.importantState_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneTelState.importantState_write


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def Reset(self):
        # PROTECTED REGION ID(GeneTelState.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneTelState.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(GeneTelState.main) ENABLED START #
    return run((GeneTelState,), args=args, **kwargs)
    # PROTECTED REGION END #    //  GeneTelState.main

if __name__ == '__main__':
    main()
