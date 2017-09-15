# -*- coding: utf-8 -*-
#
# This file is part of the SKAAlarmHandler project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SKAAlarmHandler

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
# PROTECTED REGION ID(SKAAlarmHandler.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SKAAlarmHandler.additionnal_import

__all__ = ["SKAAlarmHandler", "main"]


class SKAAlarmHandler(SKABaseDevice):
    """
    A generic base device for Alarms for SKA.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKAAlarmHandler.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.class_variable

    # -----------------
    # Device Properties
    # -----------------

    SubAlarmHandlers = device_property(
        dtype=('str',),
    )

    AlarmConfigFile = device_property(
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











    activeAlerts = attribute(
        dtype=('str',),
        max_dim_x=10000,
        doc="List of active alerts",
    )

    activeAlarms = attribute(
        dtype=('str',),
        max_dim_x=10000,
        doc="List of active alarms",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SKAAlarmHandler.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKAAlarmHandler.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKAAlarmHandler.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAAlarmHandler.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKAAlarmHandler.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAAlarmHandler.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_statsNrAlerts(self):
        # PROTECTED REGION ID(SKAAlarmHandler.statsNrAlerts_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.statsNrAlerts_read

    def read_statsNrAlarms(self):
        # PROTECTED REGION ID(SKAAlarmHandler.statsNrAlarms_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.statsNrAlarms_read

    def read_statsNrNewAlarms(self):
        # PROTECTED REGION ID(SKAAlarmHandler.statsNrNewAlarms_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.statsNrNewAlarms_read

    def read_statsNrUnackAlarms(self):
        # PROTECTED REGION ID(SKAAlarmHandler.statsNrUnackAlarms_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  SKAAlarmHandler.statsNrUnackAlarms_read

    def read_statsNrRtnAlarms(self):
        # PROTECTED REGION ID(SKAAlarmHandler.statsNrRtnAlarms_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  SKAAlarmHandler.statsNrRtnAlarms_read

    def read_activeAlerts(self):
        # PROTECTED REGION ID(SKAAlarmHandler.activeAlerts_read) ENABLED START #
        return ['']
        # PROTECTED REGION END #    //  SKAAlarmHandler.activeAlerts_read

    def read_activeAlarms(self):
        # PROTECTED REGION ID(SKAAlarmHandler.activeAlarms_read) ENABLED START #
        return ['']
        # PROTECTED REGION END #    //  SKAAlarmHandler.activeAlarms_read


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    doc_in="Alarm name", 
    dtype_out='str', 
    doc_out="JSON string", 
    )
    @DebugIt()
    def GetAlarmRule(self, argin):
        # PROTECTED REGION ID(SKAAlarmHandler.GetAlarmRule) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.GetAlarmRule

    @command(
    dtype_in='str', 
    doc_in="Alarm name", 
    dtype_out='str', 
    doc_out="JSON string", 
    )
    @DebugIt()
    def GetAlarmData(self, argin):
        # PROTECTED REGION ID(SKAAlarmHandler.GetAlarmData) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.GetAlarmData

    @command(
    dtype_in='str', 
    doc_in="Alarm name", 
    dtype_out='str', 
    doc_out="JSON string", 
    )
    @DebugIt()
    def GetAlarmAdditionalInfo(self, argin):
        # PROTECTED REGION ID(SKAAlarmHandler.GetAlarmAdditionalInfo) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.GetAlarmAdditionalInfo

    @command(
    dtype_out='str', 
    doc_out="JSON string", 
    )
    @DebugIt()
    def GetAlarmStats(self):
        # PROTECTED REGION ID(SKAAlarmHandler.GetAlarmStats) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.GetAlarmStats

    @command(
    dtype_out='str', 
    doc_out="JSON string", 
    )
    @DebugIt()
    def GetAlertStats(self):
        # PROTECTED REGION ID(SKAAlarmHandler.GetAlertStats) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.GetAlertStats

    @command(
    )
    @DebugIt()
    def Reset(self):
        # PROTECTED REGION ID(SKAAlarmHandler.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAAlarmHandler.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKAAlarmHandler.main) ENABLED START #
    return run((SKAAlarmHandler,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKAAlarmHandler.main

if __name__ == '__main__':
    main()
