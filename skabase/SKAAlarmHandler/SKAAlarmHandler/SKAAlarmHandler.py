# -*- coding: utf-8 -*-
#
# This file is part of the SKAAlarmDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SKAAlarmDevice

A generic base device for Alarms for SKA.
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
# PROTECTED REGION ID(SKAAlarmDevice.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SKAAlarmDevice.additionnal_import

__all__ = ["SKAAlarmDevice", "main"]


class SKAAlarmDevice(SKABaseDevice):
    """
    A generic base device for Alarms for SKA.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKAAlarmDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmDevice.class_variable

    # -----------------
    # Device Properties
    # -----------------

    SubAlarmHandlers = device_property(
        dtype=('str',),
    )

    AlarmConfigFile = device_property(
        dtype='str',
    )

    FormulaConfDevice = device_property(
        dtype='str',
    )










    # ----------
    # Attributes
    # ----------

    statsNrAlerts = attribute(
        dtype='int',
        doc="Number of Alarm alerts",
    )

    statsNrAlarms = attribute(
        dtype='int',
        doc="Number of Alarms active",
    )

    statsNrNewAlarms = attribute(
        dtype='int',
        doc="Number of New active alarms",
    )

    statsNrUnackAlarms = attribute(
        dtype='double',
        doc="Number of unacknowledged alarms",
    )

    statsNrRtnAlarms = attribute(
        dtype='double',
        doc="Number of returned alarms",
    )











    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SKAAlarmDevice.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKAAlarmDevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKAAlarmDevice.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAAlarmDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKAAlarmDevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAAlarmDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_statsNrAlerts(self):
        # PROTECTED REGION ID(SKAAlarmDevice.statsNrAlerts_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKAAlarmDevice.statsNrAlerts_read

    def read_statsNrAlarms(self):
        # PROTECTED REGION ID(SKAAlarmDevice.statsNrAlarms_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKAAlarmDevice.statsNrAlarms_read

    def read_statsNrNewAlarms(self):
        # PROTECTED REGION ID(SKAAlarmDevice.statsNrNewAlarms_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKAAlarmDevice.statsNrNewAlarms_read

    def read_statsNrUnackAlarms(self):
        # PROTECTED REGION ID(SKAAlarmDevice.statsNrUnackAlarms_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  SKAAlarmDevice.statsNrUnackAlarms_read

    def read_statsNrRtnAlarms(self):
        # PROTECTED REGION ID(SKAAlarmDevice.statsNrRtnAlarms_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  SKAAlarmDevice.statsNrRtnAlarms_read

    def initialize_dynamic_attributes(self):
        self.debug_stream("In initialize_dynamic_attributes()")
        # PROTECTED REGION ID(SKAAlarmDevice.initialize_dynamic_attributes) ENABLED START #
        # PROTECTED REGION END #    //  SKAAlarmDevice.initialize_dynamic_attributes

        """   Example to add dynamic attributes
           Copy inside the folowing protected area to instanciate at startup."""
        """    For Attribute activeAlerts
        myactiveAlerts = PyTango.SpectrumAttr('MyactiveAlerts', PyTango.DevString, PyTango.READ, 10000)
        self.add_attribute(myactiveAlerts,SKAAlarmDevice.read_activeAlerts, None, None)
        self.attr_activeAlerts_read = [""]
        """
        """    For Attribute alarmsActive
        myalarmsActive = PyTango.SpectrumAttr('MyalarmsActive', PyTango.DevString, PyTango.READ, 10000)
        self.add_attribute(myalarmsActive,SKAAlarmDevice.read_alarmsActive, None, None)
        self.attr_alarmsActive_read = [""]
        """

    def read_activeAlerts(self):
        # PROTECTED REGION ID(SKAAlarmDevice.activeAlerts_read) ENABLED START #
        return ['']
        # PROTECTED REGION END #    //  SKAAlarmDevice.activeAlerts_read

    def read_alarmsActive(self):
        # PROTECTED REGION ID(SKAAlarmDevice.alarmsActive_read) ENABLED START #
        return ['']
        # PROTECTED REGION END #    //  SKAAlarmDevice.alarmsActive_read

    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def GetAlarmRule(self):
        # PROTECTED REGION ID(SKAAlarmDevice.GetAlarmRule) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAAlarmDevice.GetAlarmRule

    @command(
    )
    @DebugIt()
    def GetAlarmData(self):
        # PROTECTED REGION ID(SKAAlarmDevice.GetAlarmData) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAAlarmDevice.GetAlarmData

    @command(
    dtype_in='str', 
    doc_in="Alarm name", 
    )
    @DebugIt()
    def GetAlarmAdditionalInfo(self, argin):
        # PROTECTED REGION ID(SKAAlarmDevice.GetAlarmAdditionalInfo) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAAlarmDevice.GetAlarmAdditionalInfo

    @command(
    )
    @DebugIt()
    def GetAlarmStats(self):
        # PROTECTED REGION ID(SKAAlarmDevice.GetAlarmStats) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAAlarmDevice.GetAlarmStats

    @command(
    dtype_out='str', 
    doc_out="JSON string", 
    )
    @DebugIt()
    def GetAlertStats(self):
        # PROTECTED REGION ID(SKAAlarmDevice.GetAlertStats) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  SKAAlarmDevice.GetAlertStats

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKAAlarmDevice.main) ENABLED START #
    return run((SKAAlarmDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKAAlarmDevice.main

if __name__ == '__main__':
    main()
