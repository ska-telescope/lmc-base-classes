# -*- coding: utf-8 -*-
#
# This file is part of the SKATestDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SKATestDevice

A generic Test device for testing SKA base class functionalites.
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
# PROTECTED REGION ID(SKATestDevice.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SKATestDevice.additionnal_import

__all__ = ["SKATestDevice", "main"]


class SKATestDevice(SKABaseDevice):
    """
    A generic Test device for testing SKA base class functionalites.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKATestDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.class_variable

    # -----------------
    # Device Properties
    # -----------------











    # ----------
    # Attributes
    # ----------

    obsState = attribute(
        dtype='DevEnum',
        doc="Observing State",
        enum_labels=["IDLE", "CONFIGURING", "READY", "SCANNING", "PAUSED", "ABORTED", "FAULT", ],
    )

    obsMode = attribute(
        dtype='DevEnum',
        doc="Observing Mode",
        enum_labels=["IDLE", "IMG_CONTINUUM", "IMG_SPECTRAL_LINE", "IMG_ZOOM", "PULSAR_SEARCH", "TRANSIENT_SEARCH_FAST", "TRANSIENT_SEARCH_SLOW", "PULSAR_TIMING", "VLBI", ],
    )

    configurationProgress = attribute(
        dtype='uint16',
        unit="%",
        max_value=100,
        min_value=0,
        doc="Percentage configuration progress",
    )

    configurationDelayExpected = attribute(
        dtype='uint16',
        unit="seconds",
        doc="Configuration delay expected in seconds",
    )











    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SKATestDevice.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKATestDevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKATestDevice.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKATestDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKATestDevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKATestDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_obsState(self):
        # PROTECTED REGION ID(SKATestDevice.obsState_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKATestDevice.obsState_read

    def read_obsMode(self):
        # PROTECTED REGION ID(SKATestDevice.obsMode_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKATestDevice.obsMode_read

    def read_configurationProgress(self):
        # PROTECTED REGION ID(SKATestDevice.configurationProgress_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKATestDevice.configurationProgress_read

    def read_configurationDelayExpected(self):
        # PROTECTED REGION ID(SKATestDevice.configurationDelayExpected_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKATestDevice.configurationDelayExpected_read


    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKATestDevice.main) ENABLED START #
    return run((SKATestDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKATestDevice.main

if __name__ == '__main__':
    main()
