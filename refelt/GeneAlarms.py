# -*- coding: utf-8 -*-
#
# This file is part of the GeneEltAlarms project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" GeneEltAlarms

Gene (Gen Element) EltAlarms device.
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
# PROTECTED REGION ID(GeneEltAlarms.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  GeneEltAlarms.additionnal_import

__all__ = ["GeneEltAlarms", "main"]


class GeneEltAlarms(SKABaseDevice):
    """
    Gene (Gen Element) EltAlarms device.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(GeneEltAlarms.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  GeneEltAlarms.class_variable

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
        # PROTECTED REGION ID(GeneEltAlarms.init_device) ENABLED START #
        # PROTECTED REGION END #    //  GeneEltAlarms.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(GeneEltAlarms.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneEltAlarms.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(GeneEltAlarms.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneEltAlarms.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_attr1(self):
        # PROTECTED REGION ID(GeneEltAlarms.attr1_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  GeneEltAlarms.attr1_read

    def read_attr2(self):
        # PROTECTED REGION ID(GeneEltAlarms.attr2_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  GeneEltAlarms.attr2_read

    def read_importantState(self):
        # PROTECTED REGION ID(GeneEltAlarms.importantState_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  GeneEltAlarms.importantState_read

    def write_importantState(self, value):
        # PROTECTED REGION ID(GeneEltAlarms.importantState_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneEltAlarms.importantState_write


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def Reset(self):
        # PROTECTED REGION ID(GeneEltAlarms.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneEltAlarms.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(GeneEltAlarms.main) ENABLED START #
    return run((GeneEltAlarms,), args=args, **kwargs)
    # PROTECTED REGION END #    //  GeneEltAlarms.main

if __name__ == '__main__':
    main()
