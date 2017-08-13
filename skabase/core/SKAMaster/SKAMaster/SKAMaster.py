# -*- coding: utf-8 -*-
#
# This file is part of the SKAMaster project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SKAMaster

A master test
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
from SKAObsDevice import SKAObsDevice
# Additional import
# PROTECTED REGION ID(SKAMaster.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SKAMaster.additionnal_import

__all__ = ["SKAMaster", "main"]


class SKAMaster(SKAObsDevice):
    """
    A master test
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKAMaster.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.class_variable

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
        SKAObsDevice.init_device(self)
        # PROTECTED REGION ID(SKAMaster.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKAMaster.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKAMaster.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAMaster.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKAMaster.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAMaster.delete_device

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
    # PROTECTED REGION ID(SKAMaster.main) ENABLED START #
    return run((SKAMaster,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKAMaster.main

if __name__ == '__main__':
    main()
