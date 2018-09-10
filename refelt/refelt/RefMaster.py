# -*- coding: utf-8 -*-
#
# This file is part of the RefMaster project
#
#
#

""" RefMaster

Ref (Reference Element) device of Type Master
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
from SKAMaster import SKAMaster
# Additional import
# PROTECTED REGION ID(RefMaster.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  RefMaster.additionnal_import

__all__ = ["RefMaster", "main"]


class RefMaster(SKAMaster):
    """
    Ref (Reference Element) device of Type Master
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(RefMaster.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  RefMaster.class_variable

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
        SKAMaster.init_device(self)
        # PROTECTED REGION ID(RefMaster.init_device) ENABLED START #
        # PROTECTED REGION END #    //  RefMaster.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(RefMaster.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefMaster.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(RefMaster.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefMaster.delete_device

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
        # PROTECTED REGION ID(RefMaster.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefMaster.Reset

    @command(
    dtype_out='str', 
    doc_out="Observation state", 
    )
    @DebugIt()
    def ObsState(self):
        # PROTECTED REGION ID(RefMaster.ObsState) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  RefMaster.ObsState

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(RefMaster.main) ENABLED START #
    return run((RefMaster,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefMaster.main

if __name__ == '__main__':
    main()
