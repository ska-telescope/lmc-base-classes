# -*- coding: utf-8 -*-
#
# This file is part of the SKAMaster project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SKAMaster

A master test
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
# PROTECTED REGION ID(SKAMaster.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SKAMaster.additionnal_import

__all__ = ["SKAMaster", "main"]


class SKAMaster(SKABaseDevice):
    """
    A master test
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKAMaster.class_variable) ENABLED START #
    def __init__(self, *args, **kwargs):
        super(SKAMaster, self).__init__(*args, **kwargs)

        # Initialize attribute values.
        self._element_logger_address = ""
        self._element_alarm_address = ""
        self._element_tel_state_address = ""
        self._element_database_address = ""
        self._max_capabilities = []
        self._available_capabilities = []

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
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SKAMaster.init_device) ENABLED START #
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
        return self._element_logger_address
        # PROTECTED REGION END #    //  SKAMaster.elementLoggerAddress_read

    def read_elementAlarmAddress(self):
        # PROTECTED REGION ID(SKAMaster.elementAlarmAddress_read) ENABLED START #
        return self._element_alarm_address
        # PROTECTED REGION END #    //  SKAMaster.elementAlarmAddress_read

    def read_elementTelStateAddress(self):
        # PROTECTED REGION ID(SKAMaster.elementTelStateAddress_read) ENABLED START #
        return self._element_tel_state_address
        # PROTECTED REGION END #    //  SKAMaster.elementTelStateAddress_read

    def read_elementDatabaseAddress(self):
        # PROTECTED REGION ID(SKAMaster.elementDatabaseAddress_read) ENABLED START #
        return self._element_database_address
        # PROTECTED REGION END #    //  SKAMaster.elementDatabaseAddress_read

    def read_maxCapabilities(self):
        # PROTECTED REGION ID(SKAMaster.maxCapabilities_read) ENABLED START #
        return self._max_capabilities
        # PROTECTED REGION END #    //  SKAMaster.maxCapabilities_read

    def read_availableCapabilities(self):
        # PROTECTED REGION ID(SKAMaster.availableCapabilities_read) ENABLED START #
        return self._available_capabilities
        # PROTECTED REGION END #    //  SKAMaster.availableCapabilities_read


    # --------
    # Commands
    # --------

    @command(
    dtype_in=('str',),
    doc_in="Capability type, nrInstances",
    dtype_out='bool',
    )
    @DebugIt()
    def isCapabilityAchievable(self, argin):
        # PROTECTED REGION ID(SKAMaster.isCapabilityAchievable) ENABLED START #
        return False
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
