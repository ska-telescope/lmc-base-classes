# -*- coding: utf-8 -*-
#
# This file is part of the SKASubarray project
#
#
#

""" SKASubarray

A SubArray handling device. It allows the assigning/releasing of resources into/from Subarray, configuring
capabilities, and exposes the related information like assigned resources, configured capabilities, etc.
"""
# tango imports
from tango import DebugIt
from tango.server import run, DeviceMeta, attribute, command
from tango.server import device_property
from tango import DeviceProxy, Except, ErrSeverity, DevState

# Additional import
# PROTECTED REGION ID(SKASubarray.additionnal_import) ENABLED START #
# standard imports
from builtins import zip
import os
import sys
from future.utils import with_metaclass
from itertools import zip_longest as zip

# SKA specific imports
from skabase import release

file_path = os.path.dirname(os.path.abspath(__file__))
obs_device_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SKAObsDevice"
sys.path.insert(0, obs_device_path)
from SKAObsDevice import SKAObsDevice
# PROTECTED REGION END #    //  SKASubarray.additionnal_import

__all__ = ["SKASubarray", "main"]


class SKASubarray(with_metaclass(DeviceMeta, SKAObsDevice)):
    """
    SubArray handling device
    """
    # PROTECTED REGION ID(SKASubarray.class_variable) ENABLED START #
    def _is_command_allowed(self, command_name):
        """Determine whether the command specified by the command_name parameter should
        be allowed to execute or not.

        Parameters
        ----------
        command_name: str
            The name of the command which is to be executed.

        Returns
        -------
        True or False: boolean
            A True is returned when the device is in the allowed states and modes to
            execute the command. Returns False if the command name is not in the list of
            commands with rules specified for them.

        Raises
        ------
        tango.DevFailed: If the device is not in the allowed states and/modes to
            execute the command.
        """
        dp = DeviceProxy(self.get_name())

        obstate_labels = list(dp.attribute_query('obsState').enum_labels)
        obs_idle = obstate_labels.index('IDLE')
        obs_ready = obstate_labels.index('READY')

        admin_labels = list(dp.attribute_query('adminMode').enum_labels)
        admin_online = admin_labels.index('ON-LINE')
        admin_maintenance = admin_labels.index('MAINTENANCE')
        admin_offline = admin_labels.index('OFF-LINE')
        admin_not_fitted = admin_labels.index('NOT-FITTED')
        current_admin_mode = self.read_adminMode()

        if command_name in ["ReleaseResources", "AssignResources"]:
            if current_admin_mode in [admin_offline, admin_not_fitted]:
                Except.throw_exception("Command failed!", "Subarray adminMode is"
                                       " 'OFF-LINE' or 'NOT-FITTED'.",
                                       command_name, ErrSeverity.ERR)

            if self.read_obsState() == obs_idle:
                if current_admin_mode in [admin_online, admin_maintenance]:
                    return True
                else:
                    Except.throw_exception("Command failed!", "Subarray adminMode not"
                                           "'ON-LINE' or not in 'MAINTENANCE'.",
                                           command_name, ErrSeverity.ERR)

            else:
                Except.throw_exception("Command failed!", "Subarray obsState not 'IDLE'.",
                                       command_name, ErrSeverity.ERR)

        elif command_name in ['ConfigureCapability', 'DeconfigureCapability',
                              'DeconfigureAllCapabilities']:
            if self.get_state() == DevState.ON and self.read_adminMode() == admin_online:
                if self.read_obsState() in [obs_idle, obs_ready]:
                    return True
                else:
                    Except.throw_exception(
                        "Command failed!", "Subarray obsState not 'IDLE' or 'READY'.",
                        command_name, ErrSeverity.ERR)
            else:
                Except.throw_exception(
                    "Command failed!", "Subarray State not 'ON' and/or adminMode not"
                    " 'ON-LINE'.", command_name, ErrSeverity.ERR)

        return False


    def _validate_capability_types(self, command_name, capability_types):
        """Check the validity of the input parameter passed on to the command specified
        by the command_name parameter.

        Parameters
        ----------
        command_name: str
            The name of the command which is to be executed.
        capability_types: list
            A list strings representing capability types.

        Raises
        ------
        tango.DevFailed: If any of the capabilities requested are not valid.
        """
        invalid_capabilities = list(
            set(capability_types) - set(self._configured_capabilities))

        if invalid_capabilities:
            Except.throw_exception(
                "Command failed!", "Invalid capability types requested {}".format(
                    invalid_capabilities), command_name, ErrSeverity.ERR)


    def _validate_input_sizes(self, command_name, argin):
        """Check the validity of the input parameters passed on to the command specified
        by the command_name parameter.

        Parameters
        ----------
        command_name: str
            The name of the command which is to be executed.
        argin: tango.DevVarLongStringArray
            A tuple of two lists representing [number of instances][capability types]

        Raises
        ------
        tango.DevFailed: If the two lists are not equal in length.
        """
        capabilities_instances, capability_types = argin
        if len(capabilities_instances) != len(capability_types):
            Except.throw_exception("Command failed!", "Argin value lists size mismatch.",
                                   command_name, ErrSeverity.ERR)


    def is_AssignResources_allowed(self):
        return self._is_command_allowed("AssignResources")

    def is_ReleaseResources_allowed(self):
        return self._is_command_allowed("ReleaseResources")

    def is_ReleaseAllResources_allowed(self):
        return self._is_command_allowed("ReleaseResources")

    def is_ConfigureCapability_allowed(self):
        return self._is_command_allowed('ConfigureCapability')

    def is_DeconfigureCapability_allowed(self):
        return self._is_command_allowed('DeconfigureCapability')

    def is_DeconfigureAllCapabilities_allowed(self):
        return self._is_command_allowed('DeconfigureAllCapabilities')
    # PROTECTED REGION END #    //  SKASubarray.class_variable

    # -----------------
    # Device Properties
    # -----------------

    CapabilityTypes = device_property(
        dtype=('str',),
    )

    SubID = device_property(
        dtype='str',
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
        doc="A list of capability types with no. of instances "
            "in use on this subarray; "
            "e.g.\nCorrelators:512, PssBeams:4, "
            "PstBeams:4, VlbiBeams:0.",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKAObsDevice.init_device(self)
        # PROTECTED REGION ID(SKASubarray.init_device) ENABLED START #
        self._build_state = '{}, {}, {}'.format(release.name, release.version,
                                                release.description)
        self._version_id = release.version

        # Initialize attribute values.
        self._activation_time = 0.0
        self._assigned_resources = [""]
        # self._configured_capabilities is gonna be kept as a dictionary internally. The
        # keys and value will represent the capability type name and the number of
        # instances, respectively.
        try:
            self._configured_capabilities = dict.fromkeys(self.CapabilityTypes, 0)
        except TypeError:
            # Might need to have the device property be mandatory in the database.
            self._configured_capabilities = {}

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
        """
        Reads the time since device is activated.
        :return: Time of activation in seconds since Unix epoch.
        """
        return self._activation_time
        # PROTECTED REGION END #    //  SKASubarray.activationTime_read

    def read_assignedResources(self):
        # PROTECTED REGION ID(SKASubarray.assignedResources_read) ENABLED START #
        """
        Reads the resources assigned to the device.
        :return: Resources assigned to the device.
        """
        return self._assigned_resources
        # PROTECTED REGION END #    //  SKASubarray.assignedResources_read

    def read_configuredCapabilities(self):
        # PROTECTED REGION ID(SKASubarray.configuredCapabilities_read) ENABLED START #
        """
        Reads capabilities configured in the Subarray.
        :return: A list of capability types with no. of instances
        used in the Subarray
        """
        configured_capabilities = []
        for capability_type, capability_instances in (
                list(self._configured_capabilities.items())):
            configured_capabilities.append(
                "{}:{}".format(capability_type, capability_instances))
        return sorted(configured_capabilities)
        # PROTECTED REGION END #    //  SKASubarray.configuredCapabilities_read

    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def Abort(self):
        # PROTECTED REGION ID(SKASubarray.Abort) ENABLED START #
        """Change obsState to ABORTED."""
        pass
        # PROTECTED REGION END #    //  SKASubarray.Abort

    @command(
    dtype_in='DevVarLongStringArray',
    doc_in="[Number of instances to add][Capability types]",
    )
    @DebugIt()
    def ConfigureCapability(self, argin):
        # PROTECTED REGION ID(SKASubarray.ConfigureCapability) ENABLED START #
        """Configures number of instances for each capability. If the capability exists,
        it increments the configured instances by the number of instances requested,
        otherwise an exception will be raised.
        Note: The two lists arguments must be of equal length or an exception will be raised."""
        command_name = 'ConfigureCapability'
        dp = DeviceProxy(self.get_name())
        obstate_labels = list(dp.attribute_query('obsState').enum_labels)
        obs_configuring = obstate_labels.index('CONFIGURING')

        capabilities_instances, capability_types = argin
        self._validate_capability_types(command_name, capability_types)
        self._validate_input_sizes(command_name, argin)

        # Set obsState to 'CONFIGURING'.
        self._obs_state = obs_configuring

        # Perform the configuration.
        for capability_instances, capability_type in zip(
                capabilities_instances, capability_types):
            self._configured_capabilities[capability_type] += capability_instances

        # Change the obsState to 'READY'.
        obs_ready = obstate_labels.index('READY')
        self._obs_state = obs_ready
        # PROTECTED REGION END #    //  SKASubarray.ConfigureCapability

    @command(
    dtype_in='str',
    doc_in="Capability type",
    )
    @DebugIt()
    def DeconfigureAllCapabilities(self, argin):
        # PROTECTED REGION ID(SKASubarray.DeconfigureAllCapabilities) ENABLED START #i
        """Deconfigure all instances of the given Capability type. If the capability
        type does not exist an exception will be raised, otherwise it sets the
        configured instances for that capability type to zero."""
        self._validate_capability_types('DeconfigureAllCapabilities', [argin])
        self._configured_capabilities[argin] = 0
        # PROTECTED REGION END #    //  SKASubarray.DeconfigureAllCapabilities

    @command(
    dtype_in='DevVarLongStringArray',
    doc_in="[Number of instances to remove][Capability types]",
    )
    @DebugIt()
    def DeconfigureCapability(self, argin):
        # PROTECTED REGION ID(SKASubarray.DeconfigureCapability) ENABLED START #
        """Deconfigures a given number of instances for each capability.
        If the capability exists, it decrements the configured instances by the
        number of instances requested, otherwise an exceptioin will be raised.
        Note: The two lists arguments must be of equal length or an exception
        will be raised"""
        command_name = 'DeconfigureCapability'
        capabilities_instances, capability_types = argin

        self._validate_capability_types(command_name, capability_types)
        self._validate_input_sizes(command_name, argin)


        # Perform the deconfiguration
        for capability_instances, capability_type in zip(
                capabilities_instances, capability_types):
            if self._configured_capabilities[capability_type] < int(capability_instances):
                self._configured_capabilities[capability_type] = 0
            else:
                self._configured_capabilities[capability_type] -= (
                    int(capability_instances))
        # PROTECTED REGION END #    //  SKASubarray.DeconfigureCapability

    @command(
    dtype_in=('str',),
    doc_in="List of Resources to add to subarray.",
    dtype_out=('str',),
    doc_out="A list of Resources added to the subarray.",
    )
    @DebugIt()
    def AssignResources(self, argin):
        # PROTECTED REGION ID(SKASubarray.AssignResources) ENABLED START #
        """Assign resources to a Subarray"""
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
        """Delta removal of assigned resources."""
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
    )
    @DebugIt()
    def EndSB(self):
        # PROTECTED REGION ID(SKASubarray.EndSB) ENABLED START #
        """Change obsState to IDLE."""
        pass
        # PROTECTED REGION END #    //  SKASubarray.EndSB

    @command(
    )
    @DebugIt()
    def EndScan(self):
        # PROTECTED REGION ID(SKASubarray.EndScan) ENABLED START #
        """Ends the scan"""
        pass
        # PROTECTED REGION END #    //  SKASubarray.EndScan

    @command(
    )
    @DebugIt()
    def Pause(self):
        # PROTECTED REGION ID(SKASubarray.Pause) ENABLED START #
        """Pauses the scan"""
        pass
        # PROTECTED REGION END #    //  SKASubarray.Pause

    @command(
    dtype_out=('str',),
    doc_out="List of resources removed from the subarray.",
    )
    @DebugIt()
    def ReleaseAllResources(self):
        # PROTECTED REGION ID(SKASubarray.ReleaseAllResources) ENABLED START #
        """Remove all resources to tear down to an empty subarray."""
        resources = self._assigned_resources[:]
        released_resources = self.ReleaseResources(resources)
        return released_resources
        # PROTECTED REGION END #    //  SKASubarray.ReleaseAllResources

    @command(
    )
    @DebugIt()
    def Resume(self):
        # PROTECTED REGION ID(SKASubarray.Resume) ENABLED START #
        """Resumes the scan"""
        pass
        # PROTECTED REGION END #    //  SKASubarray.Resume

    @command(
    dtype_in=('str',),
    )
    @DebugIt()
    def Scan(self, argin):
        # PROTECTED REGION ID(SKASubarray.Scan) ENABLED START #
        """Starts the scan"""
        pass
        # PROTECTED REGION END #    //  SKASubarray.Scan

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKASubarray.main) ENABLED START #
    """
    Main entry point of the module.
    """
    return run((SKASubarray,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKASubarray.main

if __name__ == '__main__':
    main()
