# -*- coding: utf-8 -*-
#
# This file is part of the SKAMaster project
#
#
#

""" SKAMaster

A master test
"""
# tango imports
from tango import DebugIt
from tango.server import run, DeviceMeta, attribute, command, device_property

# Additional import
# PROTECTED REGION ID(SKAMaster.additionnal_import) ENABLED START #
from builtins import zip
import os
import sys
from future.utils import with_metaclass
from itertools import zip_longest as zip

# SKA specific imports
from skabase import release

file_path = os.path.dirname(os.path.abspath(__file__))
basedevice_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SKABaseDevice"
sys.path.insert(0, basedevice_path)
from SKABaseDevice import SKABaseDevice

from utils import (validate_capability_types, validate_input_sizes,
                           convert_dict_to_list)

# PROTECTED REGION END #    //  SKAMaster.additionnal_import

__all__ = ["SKAMaster", "main"]


class SKAMaster(with_metaclass(DeviceMeta, SKABaseDevice)):
    """
    A master test
    """
    # PROTECTED REGION ID(SKAMaster.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.class_variable

    # -----------------
    # Device Properties
    # -----------------

    MaxCapabilities = device_property(
        dtype=('str',),
    )

    # ----------
    # Attributes
    # ----------

    elementLoggerAddress = attribute(
        dtype='str',
        doc="FQDN of Element Logger",
    )

    elementAlarmAddress = attribute(
        dtype='str',
        doc="FQDN of Element Alarm Handlers",
    )

    elementTelStateAddress = attribute(
        dtype='str',
        doc="FQDN of Element TelState device",
    )

    elementDatabaseAddress = attribute(
        dtype='str',
        doc="FQDN of Element Database device",
    )

    maxCapabilities = attribute(
        dtype=('str',),
        max_dim_x=20,
        doc="Maximum number of instances of each capability type, e.g. 'CORRELATOR:512', 'PSS-BEAMS:4'.",
    )

    availableCapabilities = attribute(
        dtype=('str',),
        max_dim_x=20,
        doc="A list of available number of instances of each capability type, "
            "e.g. 'CORRELATOR:512', 'PSS-BEAMS:4'.",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SKAMaster.init_device) ENABLED START #
        self._build_state = '{}, {}, {}'.format(release.name, release.version,
                                                release.description)
        self._version_id = release.version
        # Initialize attribute values.
        self._element_logger_address = ""
        self._element_alarm_address = ""
        self._element_tel_state_address = ""
        self._element_database_address = ""
        self._element_alarm_device = ""
        self._element_tel_state_device = ""
        self._element_database_device = ""

        self._max_capabilities = {}
        if self.MaxCapabilities:
            for max_capability in self.MaxCapabilities:
                capability_type, max_capability_instances = max_capability.split(":")
                self._max_capabilities[capability_type] = int(max_capability_instances)
        self._available_capabilities = self._max_capabilities.copy()
        # PROTECTED REGION END #    //  SKAMaster.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKAMaster.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAMaster.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKAMaster.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAMaster.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_elementLoggerAddress(self):
        # PROTECTED REGION ID(SKAMaster.elementLoggerAddress_read) ENABLED START #
        """Reads FQDN of Element Logger device"""
        return self._element_logger_address
        # PROTECTED REGION END #    //  SKAMaster.elementLoggerAddress_read

    def read_elementAlarmAddress(self):
        # PROTECTED REGION ID(SKAMaster.elementAlarmAddress_read) ENABLED START #
        """Reads FQDN of Element Alarm device"""
        return self._element_alarm_address
        # PROTECTED REGION END #    //  SKAMaster.elementAlarmAddress_read

    def read_elementTelStateAddress(self):
        # PROTECTED REGION ID(SKAMaster.elementTelStateAddress_read) ENABLED START #
        """Reads FQDN of Element TelState device"""
        return self._element_tel_state_address
        # PROTECTED REGION END #    //  SKAMaster.elementTelStateAddress_read

    def read_elementDatabaseAddress(self):
        # PROTECTED REGION ID(SKAMaster.elementDatabaseAddress_read) ENABLED START #
        """Reads FQDN of Element Database device"""
        return self._element_database_address
        # PROTECTED REGION END #    //  SKAMaster.elementDatabaseAddress_read

    def read_maxCapabilities(self):
        # PROTECTED REGION ID(SKAMaster.maxCapabilities_read) ENABLED START #
        """Reads maximum number of instances of each capability type"""
        return convert_dict_to_list(self._max_capabilities)
        # PROTECTED REGION END #    //  SKAMaster.maxCapabilities_read

    def read_availableCapabilities(self):
        # PROTECTED REGION ID(SKAMaster.availableCapabilities_read) ENABLED START #
        """Reads list of available number of instances of each capability type"""
        return convert_dict_to_list(self._available_capabilities)
        # PROTECTED REGION END #    //  SKAMaster.availableCapabilities_read

    # --------
    # Commands
    # --------

    @command(
    dtype_in='DevVarLongStringArray',
    doc_in="[nrInstances][Capability types]",
    dtype_out='bool',
    )
    @DebugIt()
    def isCapabilityAchievable(self, argin):
        # PROTECTED REGION ID(SKAMaster.isCapabilityAchievable) ENABLED START #
        command_name = 'isCapabilityAchievable'
        capabilities_instances, capability_types = argin
        validate_input_sizes(command_name, argin)
        validate_capability_types(command_name, capability_types,
                                  list(self._max_capabilities.keys()))

        for capability_type, capability_instances in zip(
                capability_types, capabilities_instances):
            if not self._available_capabilities[capability_type] >= capability_instances:
                return False

        return True
        # PROTECTED REGION END #    //  SKAMaster.isCapabilityAchievable

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKAMaster.main) ENABLED START #
    return run((SKAMaster,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKAMaster.main

if __name__ == '__main__':
    main()
