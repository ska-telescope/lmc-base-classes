# -*- coding: utf-8 -*-
#
# This file is part of the RefSubarray project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" RefSubarray

Ref (Reference Element) device of Type Subarray
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
from SKASubarray import SKASubarray
# Additional import
# PROTECTED REGION ID(RefSubarray.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  RefSubarray.additionnal_import

__all__ = ["RefSubarray", "main"]


class RefSubarray(SKASubarray):
    """
    Ref (Reference Element) device of Type Subarray
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(RefSubarray.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  RefSubarray.class_variable

    # -----------------
    # Device Properties
    # -----------------









    # ----------
    # Attributes
    # ----------

    obsState = attribute(
        dtype='DevEnum',
        doc="Observing State",
    )

    obsMode = attribute(
        dtype='DevEnum',
        doc="Observing Mode",
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
        SKASubarray.init_device(self)
        # PROTECTED REGION ID(RefSubarray.init_device) ENABLED START #
        # PROTECTED REGION END #    //  RefSubarray.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(RefSubarray.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefSubarray.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(RefSubarray.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefSubarray.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_obsState(self):
        # PROTECTED REGION ID(RefSubarray.obsState_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefSubarray.obsState_read

    def read_obsMode(self):
        # PROTECTED REGION ID(RefSubarray.obsMode_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefSubarray.obsMode_read

    def read_configurationProgress(self):
        # PROTECTED REGION ID(RefSubarray.configurationProgress_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefSubarray.configurationProgress_read

    def read_configurationDelayExpected(self):
        # PROTECTED REGION ID(RefSubarray.configurationDelayExpected_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefSubarray.configurationDelayExpected_read


    # --------
    # Commands
    # --------

    @command(
    dtype_out='str', 
    doc_out="Observation state", 
    )
    @DebugIt()
    def ObsState(self):
        # PROTECTED REGION ID(RefSubarray.ObsState) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  RefSubarray.ObsState

    @command(
    )
    @DebugIt()
    def Reset(self):
        # PROTECTED REGION ID(RefSubarray.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefSubarray.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(RefSubarray.main) ENABLED START #
    return run((RefSubarray,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefSubarray.main

if __name__ == '__main__':
    main()
