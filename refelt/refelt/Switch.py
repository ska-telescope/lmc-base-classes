# -*- coding: utf-8 -*-
#
# This file is part of the Switch project
#
#
#

""" Switch

Ref (Reference Elt) Swtich device
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

__all__ = ["Switch", "main"]


class Switch(SKABaseDevice):
    """
    Ref (Reference Elt) Swtich device
    """
    __metaclass__ = DeviceMeta

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

    def always_executed_hook(self):
        pass

    def delete_device(self):
        pass

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
        pass

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    return run((Switch,), args=args, **kwargs)

if __name__ == '__main__':
    main()
