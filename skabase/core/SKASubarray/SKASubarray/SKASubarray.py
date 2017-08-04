# -*- coding: utf-8 -*-
#
# This file is part of the SKASubarray project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

SubArray handling device
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
# PROTECTED REGION ID(SKASubarray.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SKASubarray.additionnal_import

__all__ = ["SKASubarray", "main"]


class SKASubarray(SKAObsDevice):
    """
    SubArray handling device
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKASubarray.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.class_variable

    # -----------------
    # Device Properties
    # -----------------










    # ----------
    # Attributes
    # ----------

    subID = attribute(
        dtype='uint16',
        format="%02d",
        max_value=16,
        min_value=1,
        doc="The actual subarray ID of this instance.",
    )

    resources = attribute(
        dtype='str',
        doc="The list of resources assigned to the subarray",
    )















    activationTime = attribute(
        dtype=('uint',),
        max_dim_x=256,
        doc="Unix time of subarray activation.",
    )

    maxCapabilities = attribute(
        dtype=('uint16',),
        max_dim_x=10,
        doc="Maximum instances of each capability type, in the same order as the CapabilityTypes",
    )

    availableCapabilities = attribute(
        dtype=('uint16',),
        max_dim_x=10,
        doc="Available instances of each capability type, in the same order as the CapabilityTypes",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKAObsDevice.init_device(self)
        # PROTECTED REGION ID(SKASubarray.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKASubarray.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKASubarray.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKASubarray.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKASubarray.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKASubarray.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_subID(self):
        # PROTECTED REGION ID(SKASubarray.subID_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKASubarray.subID_read

    def read_resources(self):
        # PROTECTED REGION ID(SKASubarray.resources_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  SKASubarray.resources_read

    def read_activationTime(self):
        # PROTECTED REGION ID(SKASubarray.activationTime_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  SKASubarray.activationTime_read

    def read_maxCapabilities(self):
        # PROTECTED REGION ID(SKASubarray.maxCapabilities_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  SKASubarray.maxCapabilities_read

    def read_availableCapabilities(self):
        # PROTECTED REGION ID(SKASubarray.availableCapabilities_read) ENABLED START #
        return [0]
        # PROTECTED REGION END #    //  SKASubarray.availableCapabilities_read


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    doc_in="List of resources to initialise subarray with", 
    dtype_out=('str',), 
    doc_out="List of resources assigned to subarray", 
    )
    @DebugIt()
    def AssignResources(self, argin):
        # PROTECTED REGION ID(SKASubarray.AssignResources) ENABLED START #
        return [""]
        # PROTECTED REGION END #    //  SKASubarray.AssignResources

    @command(
    dtype_in='str', 
    doc_in="List of resources to add to subarray", 
    dtype_out=('str',), 
    )
    @DebugIt()
    def AddResources(self, argin):
        # PROTECTED REGION ID(SKASubarray.AddResources) ENABLED START #
        return [""]
        # PROTECTED REGION END #    //  SKASubarray.AddResources

    @command(
    dtype_in='str', 
    doc_in="List of resources to remove from subarray", 
    dtype_out=('str',), 
    doc_out="List of resources removed", 
    )
    @DebugIt()
    def RemoveResources(self, argin):
        # PROTECTED REGION ID(SKASubarray.RemoveResources) ENABLED START #
        return [""]
        # PROTECTED REGION END #    //  SKASubarray.RemoveResources

    @command(
    dtype_out=('str',), 
    doc_out="List of resources removed", 
    )
    @DebugIt()
    def RemoveAllResources(self):
        # PROTECTED REGION ID(SKASubarray.RemoveAllResources) ENABLED START #
        return [""]
        # PROTECTED REGION END #    //  SKASubarray.RemoveAllResources

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKASubarray.main) ENABLED START #
    return run((SKASubarray,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKASubarray.main

if __name__ == '__main__':
    main()
