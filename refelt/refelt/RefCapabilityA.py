# -*- coding: utf-8 -*-
#
# This file is part of the RefCapabilityA project
#
#
#

""" RefCapabilityA

Ref (Reference Element) device of Type Capability A
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
from SKACapability import SKACapability
# Additional import
# PROTECTED REGION ID(RefCapabilityA.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  RefCapabilityA.additionnal_import

__all__ = ["RefCapabilityA", "main"]


class RefCapabilityA(SKACapability):
    """
    Ref (Reference Element) device of Type Capability A
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(RefCapabilityA.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  RefCapabilityA.class_variable

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
        SKACapability.init_device(self)
        # PROTECTED REGION ID(RefCapabilityA.init_device) ENABLED START #
        # PROTECTED REGION END #    //  RefCapabilityA.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(RefCapabilityA.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefCapabilityA.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(RefCapabilityA.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefCapabilityA.delete_device

    # ------------------
    # Attributes methods
    # ------------------


    # --------
    # Commands
    # --------

    @command(
    dtype_out='str', 
    doc_out="Observation state", 
    )
    @DebugIt()
    def ObsState(self):
        # PROTECTED REGION ID(RefCapabilityA.ObsState) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  RefCapabilityA.ObsState

    @command(
    )
    @DebugIt()
    def Reset(self):
        # PROTECTED REGION ID(RefCapabilityA.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefCapabilityA.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(RefCapabilityA.main) ENABLED START #
    return run((RefCapabilityA,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefCapabilityA.main

if __name__ == '__main__':
    main()
