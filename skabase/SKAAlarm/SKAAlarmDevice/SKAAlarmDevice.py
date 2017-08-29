# -*- coding: utf-8 -*-
#
# This file is part of the SKAAlarmDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SKAAlarmDevice

A generic base device for Alarms for SKA.
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
# PROTECTED REGION ID(SKAAlarmDevice.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SKAAlarmDevice.additionnal_import

__all__ = ["SKAAlarmDevice", "main"]


class SKAAlarmDevice(Device):
    """
    A generic base device for Alarms for SKA.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKAAlarmDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmDevice.class_variable

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # PROTECTED REGION ID(SKAAlarmDevice.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKAAlarmDevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKAAlarmDevice.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAAlarmDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKAAlarmDevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAAlarmDevice.delete_device


    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKAAlarmDevice.main) ENABLED START #
    return run((SKAAlarmDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKAAlarmDevice.main

if __name__ == '__main__':
    main()
