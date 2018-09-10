# -*- coding: utf-8 -*-
#
# This file is part of the RefTelState project
#
#
#

""" RefTelState

Ref (Reference Element) device of Type TelState
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
from SKATelState import SKATelState
# Additional import
# PROTECTED REGION ID(RefTelState.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  RefTelState.additionnal_import

__all__ = ["RefTelState", "main"]


class RefTelState(SKATelState):
    """
    Ref (Reference Element) device of Type TelState
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











    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKATelState.init_device(self)
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


    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(RefTelState.main) ENABLED START #
    return run((RefTelState,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefTelState.main

if __name__ == '__main__':
    main()
