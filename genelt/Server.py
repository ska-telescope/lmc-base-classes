# -*- coding: utf-8 -*-
#
# This file is part of the Server project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" Server

Gene (Gen Elt) Server device
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
# PROTECTED REGION ID(Server.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  Server.additionnal_import

__all__ = ["Server", "main"]


class Server(SKABaseDevice):
    """
    Gene (Gen Elt) Server device
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(Server.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  Server.class_variable

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
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(Server.init_device) ENABLED START #
        # PROTECTED REGION END #    //  Server.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(Server.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Server.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(Server.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Server.delete_device

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
        # PROTECTED REGION ID(Server.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Server.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(Server.main) ENABLED START #
    return run((Server,), args=args, **kwargs)
    # PROTECTED REGION END #    //  Server.main

if __name__ == '__main__':
    main()
