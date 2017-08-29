# -*- coding: utf-8 -*-
#
# This file is part of the SKACapability project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SKACapability

Subarray handling device
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
# PROTECTED REGION ID(SKACapability.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SKACapability.additionnal_import

__all__ = ["SKACapability", "main"]


class SKACapability(SKAObsDevice):
    """
    Subarray handling device
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKACapability.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.class_variable

    # -----------------
    # Device Properties
    # -----------------










    CapType = device_property(
        dtype='str',
        mandatory=True
    )

    CapID = device_property(
        dtype='str',
        mandatory=True
    )

    subID = device_property(
        dtype='str',
    )

    # ----------
    # Attributes
    # ----------

    activationTime = attribute(
        dtype='uint64',
        unit="s",
        standard_unit="s",
        display_unit="s",
        doc="Unix time of activation.",
    )















    usedCapabilities = attribute(
        dtype=('str',),
        max_dim_x=100,
        doc="Number of instances of this Capability Type currently in use on this subarray.",
    )

    usedComponents = attribute(
        dtype=('str',),
        max_dim_x=100,
        doc="A list of components used by the Capability.",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKAObsDevice.init_device(self)
        # PROTECTED REGION ID(SKACapability.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKACapability.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKACapability.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKACapability.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKACapability.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKACapability.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_activationTime(self):
        # PROTECTED REGION ID(SKACapability.activationTime_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKACapability.activationTime_read

    def read_usedCapabilities(self):
        # PROTECTED REGION ID(SKACapability.usedCapabilities_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKACapability.usedCapabilities_read

    def read_usedComponents(self):
        # PROTECTED REGION ID(SKACapability.usedComponents_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  SKACapability.usedComponents_read


    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKACapability.main) ENABLED START #
    return run((SKACapability,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKACapability.main

if __name__ == '__main__':
    main()
