# -*- coding: utf-8 -*-
#
# This file is part of the RefAlarmHandler project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" RefAlarmHandler

Ref (Reference Element) device of Type AlarmHandler
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
from SKAAlarmHandler import SKAAlarmHandler
# Additional import
# PROTECTED REGION ID(RefAlarmHandler.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  RefAlarmHandler.additionnal_import

__all__ = ["RefAlarmHandler", "main"]


class RefAlarmHandler(SKAAlarmHandler):
    """
    Ref (Reference Element) device of Type AlarmHandler
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(RefAlarmHandler.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  RefAlarmHandler.class_variable

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
        SKAAlarmHandler.init_device(self)
        # PROTECTED REGION ID(RefAlarmHandler.init_device) ENABLED START #
        # PROTECTED REGION END #    //  RefAlarmHandler.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(RefAlarmHandler.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefAlarmHandler.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(RefAlarmHandler.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefAlarmHandler.delete_device

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
    # PROTECTED REGION ID(RefAlarmHandler.main) ENABLED START #
    return run((RefAlarmHandler,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefAlarmHandler.main

if __name__ == '__main__':
    main()
