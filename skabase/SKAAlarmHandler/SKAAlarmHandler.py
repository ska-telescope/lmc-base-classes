# -*- coding: utf-8 -*-
#
# This file is part of the SKAAlarmHandler project
#
#
#

""" SKAAlarmHandler

A generic base device for Alarms for SKA. It exposes SKA alarms and SKA alerts as TANGO attributes.
SKA Alarms and SKA/Element Alerts are rules-based configurable conditions that can be defined over multiple
attribute values and quality factors, and are separate from the "built-in" TANGO attribute alarms.
"""

# tango imports
from tango import DebugIt
from tango.server import run, DeviceMeta, attribute, command, device_property

# Additional import
# PROTECTED REGION ID(SKAAlarmHandler.additionnal_import) ENABLED START #
#standard import
import os
import sys
from future.utils import with_metaclass

# SKA specific imports\
from skabase import release

file_path = os.path.dirname(os.path.abspath(__file__))
basedevice_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/SKABaseDevice"
sys.path.insert(0, basedevice_path)
from SKABaseDevice import SKABaseDevice
# PROTECTED REGION END #    //  SKAAlarmHandler.additionnal_import

__all__ = ["SKAAlarmHandler", "main"]


class SKAAlarmHandler(with_metaclass(DeviceMeta, SKABaseDevice)):
    """
    A generic base device for Alarms for SKA.
    """
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
        doc="Number of active Alerts",
    )

    statsNrAlarms = attribute(
        dtype='int',
        doc="Number of active Alarms",
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
        self._build_state = '{}, {}, {}'.format(release.name, release.version,
                                                release.description)
        self._version_id = release.version
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
        """
        Reads number of active alerts.
        :return: Number of active alerts
        """
        return 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.statsNrAlerts_read

    def read_statsNrAlarms(self):
        # PROTECTED REGION ID(SKAAlarmHandler.statsNrAlarms_read) ENABLED START #
        """
        Reads number of active alarms.
        :return: Number of active alarms
        """
        return 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.statsNrAlarms_read

    def read_statsNrNewAlarms(self):
        # PROTECTED REGION ID(SKAAlarmHandler.statsNrNewAlarms_read) ENABLED START #
        """
        Reads number of new active alarms.
        :return: Number of new active alarms
        """
        return 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.statsNrNewAlarms_read

    def read_statsNrUnackAlarms(self):
        # PROTECTED REGION ID(SKAAlarmHandler.statsNrUnackAlarms_read) ENABLED START #
        """
        Reads number of unacknowledged alarms.
        :return: Number of unacknowledged alarms.
        """
        return 0.0
        # PROTECTED REGION END #    //  SKAAlarmHandler.statsNrUnackAlarms_read

    def read_statsNrRtnAlarms(self):
        # PROTECTED REGION ID(SKAAlarmHandler.statsNrRtnAlarms_read) ENABLED START #
        """
        Reads number of returned alarms.
        :return: Number of returned alarms
        """
        return 0.0
        # PROTECTED REGION END #    //  SKAAlarmHandler.statsNrRtnAlarms_read

    def read_activeAlerts(self):
        # PROTECTED REGION ID(SKAAlarmHandler.activeAlerts_read) ENABLED START #
        """
        Reads list of active alerts.
        :return: List of active alerts
        """
        return ['']
        # PROTECTED REGION END #    //  SKAAlarmHandler.activeAlerts_read

    def read_activeAlarms(self):
        # PROTECTED REGION ID(SKAAlarmHandler.activeAlarms_read) ENABLED START #
        """
        Reads list of active alarms.
        :return: List of active alarms
        """
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
        """
        Get all configuration info of the alarm, e.g. rule, defined action, etc.
        :param argin: Name of the alarm
        :return: JSON string containing configuration information of the alarm
        """
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
        """
        Get list of current value, quality factor and status of
        all attributes participating in the alarm rule.
        :param argin: Name of the alarm
        :return: JSON string containing alarm data
        """
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
        """
        Get additional alarm information.
        :param argin: Name of the alarm
        :return: JSON string containing additional alarm information
        """
        return ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.GetAlarmAdditionalInfo

    @command(
    dtype_out='str',
    doc_out="JSON string",
    )
    @DebugIt()
    def GetAlarmStats(self):
        # PROTECTED REGION ID(SKAAlarmHandler.GetAlarmStats) ENABLED START #
        """
        Get current alarm stats.
        :return: JSON string containing alarm statistics
        """
        return ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.GetAlarmStats

    @command(
    dtype_out='str',
    doc_out="JSON string",
    )
    @DebugIt()
    def GetAlertStats(self):
        # PROTECTED REGION ID(SKAAlarmHandler.GetAlertStats) ENABLED START #
        """
        Get current alert stats.
        :return: JSON string containing alert statistics
        """
        return ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.GetAlertStats

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKAAlarmHandler.main) ENABLED START #
    """
    Main function of the SKAAlarmHandler module.
    :param args:
    :param kwargs:
    :return:
    """
    return run((SKAAlarmHandler,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKAAlarmHandler.main

if __name__ == '__main__':
    main()
