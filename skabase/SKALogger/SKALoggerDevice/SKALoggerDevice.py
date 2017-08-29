# -*- coding: utf-8 -*-
#
# This file is part of the SKALoggerDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SKALoggerDevice

A generic base device for Logging for SKA.
"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import command
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
# Additional import
# PROTECTED REGION ID(SKALoggerDevice.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SKALoggerDevice.additionnal_import

__all__ = ["SKALoggerDevice", "main"]


class SKALoggerDevice(Device):
    """
    A generic base device for Logging for SKA.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKALoggerDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKALoggerDevice.class_variable

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # PROTECTED REGION ID(SKALoggerDevice.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKALoggerDevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKALoggerDevice.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKALoggerDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKALoggerDevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKALoggerDevice.delete_device


    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKALoggerDevice.main) ENABLED START #
    return run((SKALoggerDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKALoggerDevice.main

if __name__ == '__main__':
    main()
