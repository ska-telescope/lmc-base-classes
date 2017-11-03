# -*- coding: utf-8 -*-
#
# This file is part of the SKASubarray project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SKASubarray

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
from PyTango import DeviceProxy, Except, ErrSeverity
# PROTECTED REGION END #    //  SKASubarray.additionnal_import

__all__ = ["SKASubarray", "main"]


class SKASubarray(SKAObsDevice):
    """
    SubArray handling device
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKASubarray.class_variable) ENABLED START #
    def __init__(self, *args, **kwargs):
        super(SKASubarray, self).__init__(*args, **kwargs)

        # Initialize attribute values.
        self._activation_time = 0.0
        self._assigned_resources = [""]
        self._configured_capabilites = [""]


    def _is_command_allowed(self, command_name):
        """Determine whether the command specified by the command_name parameter should
        be allowed to execute or not.

        Parameters
        ==========
        command_name: str
            The name of the command which is to be executed.

        Returns
        =======
        True or False: boolean
            A True is returned when the device is in the allowed states and modes to
            execute the command. Returns False if the command name is not in the list of
            commands with rules specified for them.

        Throws
        ======
        PyTango.DevFailed: If the device is not in the allowed states and/modes to to
            execute the command.
        """
        dp = DeviceProxy(self.get_name())

        obstate_labels = list(dp.attribute_query('obsState').enum_labels)
        obs_idle = obstate_labels.index('IDLE')

        admin_labels = list(dp.attribute_query('adminMode').enum_labels)
        admin_online = admin_labels.index('ON-LINE')
        admin_maintenance = admin_labels.index('MAINTENANCE')
        admin_offline = admin_labels.index('OFF-LINE')
        admin_not_fitted = admin_labels.index('NOT-FITTED')
        current_admin_mode = self.read_adminMode()

        if command_name in ["ReleaseResources", "AssignResources"]:
            if (current_admin_mode == admin_offline or
                   current_admin_mode == admin_not_fitted):
                Except.throw_exception("Command failed!", "Subarray adminMode is"
                                       " 'OFF-LINE' or 'NOT-FITTED'.",
                                       command_name, ErrSeverity.ERR)

            if self.read_obsState() == obs_idle:
                if (current_admin_mode == admin_online or
                        current_admin_mode == admin_maintenance):
                    return True
                else:
                    Except.throw_exception("Command failed!", "Subarray adminMode not"
                                           "'ON-LINE' or not in 'MAINTENANCE'.",
                                           command_name, ErrSeverity.ERR)

            else:
                Except.throw_exception("Command failed!", "Subarray obsState not 'IDLE'.",
                                       command_name, ErrSeverity.ERR)

        return False


    def is_AssignResources_allowed(self):
        return self._is_command_allowed("AssignResources")


    def is_ReleaseResources_allowed(self):
        return self._is_command_allowed("ReleaseResources")


    def is_ReleaseAllResources_allowed(self):
        return self._is_command_allowed("ReleaseResources")
    # PROTECTED REGION END #    //  SKASubarray.class_variable

    # -----------------
    # Device Properties
    # -----------------







    SubID = device_property(
        dtype='str',
    )

    CapabililtyTypes = device_property(
        dtype=('str',),
    )

    # ----------
    # Attributes
    # ----------

    activationTime = attribute(
        dtype='double',
        unit="s",
        standard_unit="s",
        display_unit="s",
        doc="Time of activation in seconds since Unix epoch.",
    )















    assignedResources = attribute(
        dtype=('str',),
        max_dim_x=100,
        doc="The list of resources assigned to the subarray.",
    )

    configuredCapabilities = attribute(
        dtype=('str',),
        max_dim_x=10,
        doc="A list of capability types with no. of instances in use on this subarray; e.g.\nCorrelators:512, PssBeams:4, PstBeams:4, VlbiBeams:0.",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKAObsDevice.init_device(self)
        # PROTECTED REGION ID(SKASubarray.init_device) ENABLED START #

        # When Subarray in not in use it reports:
        self.set_state(DevState.DISABLE)

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

    def read_activationTime(self):
        # PROTECTED REGION ID(SKASubarray.activationTime_read) ENABLED START #
        return self._activation_time
        # PROTECTED REGION END #    //  SKASubarray.activationTime_read

    def read_assignedResources(self):
        # PROTECTED REGION ID(SKASubarray.assignedResources_read) ENABLED START #
        return self._assigned_resources
        # PROTECTED REGION END #    //  SKASubarray.assignedResources_read

    def read_configuredCapabilities(self):
        # PROTECTED REGION ID(SKASubarray.configuredCapabilities_read) ENABLED START #
        return self._configured_capabilities
        # PROTECTED REGION END #    //  SKASubarray.configuredCapabilities_read


    # --------
    # Commands
    # --------

    @command(
    dtype_in=('str',),
    doc_in="List of Resources to add to subarray.",
    dtype_out=('str',),
    doc_out="A list of Resources added to the subarray.",
    )
    @DebugIt()
    def AssignResources(self, argin):
        # PROTECTED REGION ID(SKASubarray.AssignResources) ENABLED START #
        argout = []
        resources = self._assigned_resources[:]
        for resource in argin:
            if resource not in resources:
                self._assigned_resources.append(resource)
            argout.append(resource)
        return argout

    @command(
    dtype_in=('str',),
    doc_in="List of resources to remove from the subarray.",
    dtype_out=('str',),
    doc_out="List of resources removed from the subarray.",
    )
    @DebugIt()
    def ReleaseResources(self, argin):
        # PROTECTED REGION ID(SKASubarray.ReleaseResources) ENABLED START #
        argout = []
        # Release resources...
        resources = self._assigned_resources[:]
        for resource in argin:
            if resource in resources:
                self._assigned_resources.remove(resource)
            argout.append(resource)
        return argout
        # PROTECTED REGION END #    //  SKASubarray.ReleaseResources

    @command(
    dtype_out=('str',),
    doc_out="List of resources removed from the subarray.",
    )
    @DebugIt()
    def ReleaseAllResources(self):
        # PROTECTED REGION ID(SKASubarray.ReleaseAllResources) ENABLED START #
        resources = self._assigned_resources[:]
        released_resources = self.ReleaseResources(resources)
        return released_resources
        # PROTECTED REGION END #    //  SKASubarray.ReleaseAllResources

    @command(
    dtype_in=('str',),
    doc_in="Capability type, nrInstances.",
    )
    @DebugIt()
    def ConfigureCapability(self, argin):
        # PROTECTED REGION ID(SKASubarray.ConfigureCapability) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKASubarray.ConfigureCapability

    @command(
    )
    @DebugIt()
    def Abort(self):
        # PROTECTED REGION ID(SKASubarray.Abort) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKASubarray.Abort

    @command(
    )
    @DebugIt()
    def EndSB(self):
        # PROTECTED REGION ID(SKASubarray.EndSB) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKASubarray.EndSB

    @command(
    dtype_in=('str',),
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(SKASubarray.Scan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKASubarray.Scan

    @command(
    )
    @DebugIt()
    def EndScan(self):
        # PROTECTED REGION ID(SKASubarray.EndScan) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKASubarray.EndScan

    @command(
    )
    @DebugIt()
    def Pause(self):
        # PROTECTED REGION ID(SKASubarray.Pause) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKASubarray.Pause

    @command(
    )
    @DebugIt()
    def Resume(self):
        # PROTECTED REGION ID(SKASubarray.Resume) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKASubarray.Resume

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKASubarray.main) ENABLED START #
    return run((SKASubarray,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKASubarray.main

if __name__ == '__main__':
    main()
