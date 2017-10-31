# -*- coding: utf-8 -*-
#
# This file is part of the RefA project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" RefA

An Ref (Reference Elt) device of type A
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
# PROTECTED REGION ID(RefA.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  RefA.additionnal_import

__all__ = ["RefA", "main"]


class RefA(SKABaseDevice):
    """
    An Ref (Reference Elt) device of type A
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(RefA.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  RefA.class_variable

    # -----------------
    # Device Properties
    # -----------------










    # ----------
    # Attributes
    # ----------



    attrR1 = attribute(
        dtype='str',
        doc="Attribute 1 for DevA",
    )

    attrRW2 = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        doc="Attribute 2 for DevA",
    )









    attrImportant1 = attribute(
        dtype='double',
        access=AttrWriteType.READ_WRITE,
        max_value=100,
        min_value=0,
        max_alarm=90,
        min_alarm=10,
        max_warning=80,
        min_warning=20,
        doc="An important attribute",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(RefA.init_device) ENABLED START #
        # PROTECTED REGION END #    //  RefA.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(RefA.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefA.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(RefA.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefA.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_attrR1(self):
        # PROTECTED REGION ID(RefA.attrR1_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  RefA.attrR1_read

    def read_attrRW2(self):
        # PROTECTED REGION ID(RefA.attrRW2_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  RefA.attrRW2_read

    def write_attrRW2(self, value):
        # PROTECTED REGION ID(RefA.attrRW2_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefA.attrRW2_write

    def read_attrImportant1(self):
        # PROTECTED REGION ID(RefA.attrImportant1_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  RefA.attrImportant1_read

    def write_attrImportant1(self, value):
        # PROTECTED REGION ID(RefA.attrImportant1_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefA.attrImportant1_write


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def Reset(self):
        # PROTECTED REGION ID(RefA.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefA.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(RefA.main) ENABLED START #
    return run((RefA,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefA.main

if __name__ == '__main__':
    main()
