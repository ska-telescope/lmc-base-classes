# -*- coding: utf-8 -*-
#
# This file is part of the SKACapability project
#
#
#

""" SKACapability

Capability handling device
"""
from __future__ import print_function
from __future__ import absolute_import

# tango imports
from tango import DebugIt
from tango.server import run, DeviceMeta, attribute, command, device_property

# Additional import
# PROTECTED REGION ID(SKACapability.additionnal_import) ENABLED START #
# standard import
import os
import sys
from future.utils import with_metaclass

# SKA specific imports
import release # DO NOT import after modifying system path

file_path = os.path.dirname(os.path.abspath(__file__))
obs_device_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SKAObsDevice"
sys.path.insert(0, obs_device_path)
from SKAObsDevice import SKAObsDevice
# PROTECTED REGION END #    //  SKACapability.additionnal_import

__all__ = ["SKACapability", "main"]


class SKACapability(with_metaclass(DeviceMeta, SKAObsDevice)):
    """
    A Subarray handling device. It exposes the instances of configured capabilities.
    """
    # PROTECTED REGION ID(SKACapability.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.class_variable

    # -----------------
    # Device Properties
    # -----------------

    CapType = device_property(
        dtype='str',
    )

    CapID = device_property(
        dtype='str',
    )

    subID = device_property(
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

    configuredInstances = attribute(
        dtype='uint16',
        doc="Number of instances of this Capability Type currently in use on this subarray.",
    )

    usedComponents = attribute(
        dtype=('str',),
        max_dim_x=100,
        doc="A list of components with no. of instances in use on this Capability.",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKAObsDevice.init_device(self)
        self._build_state = '{}, {}, {}'.format(release.name, release.version,
                                                release.description)
        self._version_id = release.version
        # PROTECTED REGION ID(SKACapability.init_device) ENABLED START #
        self._activation_time = 0.0
        self._configured_instances = 0
        self._used_components = [""]
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
        """
        Reads time of activation since Unix epoch.
        :return: Activation time in seconds
        """
        return self._activation_time
        # PROTECTED REGION END #    //  SKACapability.activationTime_read

    def read_configuredInstances(self):
        # PROTECTED REGION ID(SKACapability.configuredInstances_read) ENABLED START #
        """
        Reads the number of instances of a capability in the subarray
        :return: The number of configured instances of a capability in a subarray
        """
        return self._configured_instances
        # PROTECTED REGION END #    //  SKACapability.configuredInstances_read

    def read_usedComponents(self):
        # PROTECTED REGION ID(SKACapability.usedComponents_read) ENABLED START #
        """
        Reads the list of components with no. of instances in use on this Capability
        :return: The number of components currently in use.
        """
        return self._used_components
        # PROTECTED REGION END #    //  SKACapability.usedComponents_read


    # --------
    # Commands
    # --------

    @command(
    dtype_in='uint16',
    doc_in="The number of instances to configure for this Capability.",
    )
    @DebugIt()
    def ConfigureInstances(self, argin):
        # PROTECTED REGION ID(SKACapability.ConfigureInstances) ENABLED START #
        """
        This function indicates how many number of instances of the current capacity
        should to be configured.
        :param argin: Number of instances to configure
        :return: None.
        """
        self._configured_instances = argin
        # PROTECTED REGION END #    //  SKACapability.ConfigureInstances

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKACapability.main) ENABLED START #
    """Main function of the SKACapability module."""
    return run((SKACapability,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKACapability.main

if __name__ == '__main__':
    main()
