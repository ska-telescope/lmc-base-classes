#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SKAAlarmHandler project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKAAlarmHandler."""

# Path
import sys
import os
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from time import sleep
from mock import MagicMock
from PyTango import DevFailed, DevState
from devicetest import DeviceTestCase, main
from SKAAlarmHandler import SKAAlarmHandler

# Note:
#
# Since the device uses an inner thread, it is necessary to
# wait during the tests in order the let the device update itself.
# Hence, the sleep calls have to be secured enough not to produce
# any inconsistent behavior. However, the unittests need to run fast.
# Here, we use a factor 3 between the read period and the sleep calls.
#
# Look at devicetest examples for more advanced testing


# Device test case
class SKAAlarmHandlerDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SKAAlarmHandler.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_additionnal_import
    device = SKAAlarmHandler
    properties = {'SubAlarmHandlers': '', 'AlarmConfigFile': '', 'SkaLevel': '4', 'MetricList': 'healthState,adminMode,controlMode', 'GroupDefinitions': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'CentralLoggingLevelDefault': '2', 'ElementLoggingLevelDefault': '3', 'StorageLoggingLevelDefault': '4', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKAAlarmHandler.numpy = MagicMock()
        # PROTECTED REGION ID(SKAAlarmHandler.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(SKAAlarmHandler.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_properties
        pass

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_Status

    def test_GetAlarmRule(self):
        """Test for GetAlarmRule"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmRule) ENABLED START #
        self.device.GetAlarmRule("")
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmRule

    def test_GetAlarmData(self):
        """Test for GetAlarmData"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmData) ENABLED START #
        self.device.GetAlarmData("")
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmData

    def test_GetAlarmAdditionalInfo(self):
        """Test for GetAlarmAdditionalInfo"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmAdditionalInfo) ENABLED START #
        self.device.GetAlarmAdditionalInfo("")
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmAdditionalInfo

    def test_GetAlarmStats(self):
        """Test for GetAlarmStats"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmStats) ENABLED START #
        self.device.GetAlarmStats()
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmStats

    def test_GetAlertStats(self):
        """Test for GetAlertStats"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlertStats) ENABLED START #
        self.device.GetAlertStats()
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlertStats

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_Reset

    def test_GetMetrics(self):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetMetrics) ENABLED START #
        self.device.GetMetrics()
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetMetrics

    def test_ToJson(self):
        """Test for ToJson"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_ToJson) ENABLED START #
        self.device.ToJson("")
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_ToJson

    def test_GetVersionInfo(self):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetVersionInfo) ENABLED START #
        self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetVersionInfo

    def test_statsNrAlerts(self):
        """Test for statsNrAlerts"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrAlerts) ENABLED START #
        self.device.statsNrAlerts
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrAlerts

    def test_statsNrAlarms(self):
        """Test for statsNrAlarms"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrAlarms) ENABLED START #
        self.device.statsNrAlarms
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrAlarms

    def test_statsNrNewAlarms(self):
        """Test for statsNrNewAlarms"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrNewAlarms) ENABLED START #
        self.device.statsNrNewAlarms
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrNewAlarms

    def test_statsNrUnackAlarms(self):
        """Test for statsNrUnackAlarms"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrUnackAlarms) ENABLED START #
        self.device.statsNrUnackAlarms
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrUnackAlarms

    def test_statsNrRtnAlarms(self):
        """Test for statsNrRtnAlarms"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrRtnAlarms) ENABLED START #
        self.device.statsNrRtnAlarms
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrRtnAlarms

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_versionId

    def test_centralLoggingLevel(self):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_centralLoggingLevel) ENABLED START #
        self.device.centralLoggingLevel
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_centralLoggingLevel

    def test_elementLoggingLevel(self):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_elementLoggingLevel) ENABLED START #
        self.device.elementLoggingLevel
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_elementLoggingLevel

    def test_storageLoggingLevel(self):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_storageLoggingLevel) ENABLED START #
        self.device.storageLoggingLevel
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_storageLoggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_testMode

    def test_activeAlerts(self):
        """Test for activeAlerts"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_activeAlerts) ENABLED START #
        self.device.activeAlerts
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_activeAlerts

    def test_activeAlarms(self):
        """Test for activeAlarms"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_activeAlarms) ENABLED START #
        self.device.activeAlarms
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_activeAlarms


# Main execution
if __name__ == "__main__":
    main()
