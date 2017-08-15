# -*- coding: utf-8 -*-
#
# This file is part of the GeneMaster project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" GeneMaster

Gene (Gen Element) device of Type Master
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
# PROTECTED REGION ID(GeneMaster.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  GeneMaster.additionnal_import

__all__ = ["GeneMaster", "main"]


class GeneMaster(SKAMaster):
    """
    Gene (Gen Element) device of Type Master
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(GeneMaster.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  GeneMaster.class_variable

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
        # PROTECTED REGION ID(GeneMaster.init_device) ENABLED START #
        # PROTECTED REGION END #    //  GeneMaster.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(GeneMaster.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneMaster.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(GeneMaster.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneMaster.delete_device

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
        # PROTECTED REGION ID(GeneMaster.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  GeneMaster.Reset

    @command(
    dtype_out='str', 
    doc_out="Observation state", 
    )
    @DebugIt()
    def ObsState(self):
        # PROTECTED REGION ID(GeneMaster.ObsState) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  GeneMaster.ObsState

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(GeneMaster.main) ENABLED START #
    return run((GeneMaster,), args=args, **kwargs)
    # PROTECTED REGION END #    //  GeneMaster.main

if __name__ == '__main__':
    main()
