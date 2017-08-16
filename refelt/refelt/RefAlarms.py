# -*- coding: utf-8 -*-
#
# This file is part of the RefEltAlarms project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" RefEltAlarms

Ref (Reference Element) EltAlarms device.
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
# PROTECTED REGION ID(RefEltAlarms.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  RefEltAlarms.additionnal_import

__all__ = ["RefEltAlarms", "main"]


class RefEltAlarms(SKABaseDevice):
    """
    Ref (Reference Element) EltAlarms device.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(RefEltAlarms.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  RefEltAlarms.class_variable

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
        # PROTECTED REGION ID(RefEltAlarms.init_device) ENABLED START #
        # PROTECTED REGION END #    //  RefEltAlarms.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(RefEltAlarms.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefEltAlarms.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(RefEltAlarms.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefEltAlarms.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_attr1(self):
        # PROTECTED REGION ID(RefEltAlarms.attr1_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  RefEltAlarms.attr1_read

    def read_attr2(self):
        # PROTECTED REGION ID(RefEltAlarms.attr2_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  RefEltAlarms.attr2_read

    def read_importantState(self):
        # PROTECTED REGION ID(RefEltAlarms.importantState_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefEltAlarms.importantState_read

    def write_importantState(self, value):
        # PROTECTED REGION ID(RefEltAlarms.importantState_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefEltAlarms.importantState_write


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def Reset(self):
        # PROTECTED REGION ID(RefEltAlarms.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefEltAlarms.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(RefEltAlarms.main) ENABLED START #
    return run((RefEltAlarms,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefEltAlarms.main

if __name__ == '__main__':
    main()
