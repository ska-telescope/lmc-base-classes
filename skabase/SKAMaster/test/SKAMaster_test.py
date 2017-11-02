#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SKAMaster project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKAMaster."""

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
from SKAMaster import SKAMaster

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
class SKAMasterDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SKAMaster.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SKAMaster.test_additionnal_import
    device = SKAMaster
    properties = {'SkaLevel': '4', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'MetricList': 'healthState,adminMode,controlMode', 'GroupDefinitions': '', 'NrSubarrays': '16', 'CapabilityTypes': '', 'MaxCapabilities': '', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKAMaster.numpy = MagicMock()
        # PROTECTED REGION ID(SKAMaster.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKAMaster.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(SKAMaster.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKAMaster.test_properties
        pass

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(SKAMaster.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  SKAMaster.test_Reset

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(SKAMaster.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  SKAMaster.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(SKAMaster.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  SKAMaster.test_Status

    def test_GetMetrics(self):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(SKAMaster.test_GetMetrics) ENABLED START #
        self.device.GetMetrics()
        # PROTECTED REGION END #    //  SKAMaster.test_GetMetrics

    def test_ToJson(self):
        """Test for ToJson"""
        # PROTECTED REGION ID(SKAMaster.test_ToJson) ENABLED START #
        self.device.ToJson("")
        # PROTECTED REGION END #    //  SKAMaster.test_ToJson

    def test_GetVersionInfo(self):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKAMaster.test_GetVersionInfo) ENABLED START #
        self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  SKAMaster.test_GetVersionInfo

    def test_isCapabilityAchievable(self):
        """Test for isCapabilityAchievable"""
        # PROTECTED REGION ID(SKAMaster.test_isCapabilityAchievable) ENABLED START #
        self.device.isCapabilityAchievable([""])
        # PROTECTED REGION END #    //  SKAMaster.test_isCapabilityAchievable

    def test_elementLoggerAddress(self):
        """Test for elementLoggerAddress"""
        # PROTECTED REGION ID(SKAMaster.test_elementLoggerAddress) ENABLED START #
        self.device.elementLoggerAddress
        # PROTECTED REGION END #    //  SKAMaster.test_elementLoggerAddress

    def test_elementAlarmAddress(self):
        """Test for elementAlarmAddress"""
        # PROTECTED REGION ID(SKAMaster.test_elementAlarmAddress) ENABLED START #
        self.device.elementAlarmAddress
        # PROTECTED REGION END #    //  SKAMaster.test_elementAlarmAddress

    def test_elementTelStateAddress(self):
        """Test for elementTelStateAddress"""
        # PROTECTED REGION ID(SKAMaster.test_elementTelStateAddress) ENABLED START #
        self.device.elementTelStateAddress
        # PROTECTED REGION END #    //  SKAMaster.test_elementTelStateAddress

    def test_elementDatabaseAddress(self):
        """Test for elementDatabaseAddress"""
        # PROTECTED REGION ID(SKAMaster.test_elementDatabaseAddress) ENABLED START #
        self.device.elementDatabaseAddress
        # PROTECTED REGION END #    //  SKAMaster.test_elementDatabaseAddress

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(SKAMaster.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  SKAMaster.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(SKAMaster.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  SKAMaster.test_versionId

    def test_centralLoggingLevel(self):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKAMaster.test_centralLoggingLevel) ENABLED START #
        self.device.centralLoggingLevel
        # PROTECTED REGION END #    //  SKAMaster.test_centralLoggingLevel

    def test_elementLoggingLevel(self):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKAMaster.test_elementLoggingLevel) ENABLED START #
        self.device.elementLoggingLevel
        # PROTECTED REGION END #    //  SKAMaster.test_elementLoggingLevel

    def test_storageLoggingLevel(self):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKAMaster.test_storageLoggingLevel) ENABLED START #
        self.device.storageLoggingLevel
        # PROTECTED REGION END #    //  SKAMaster.test_storageLoggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(SKAMaster.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  SKAMaster.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKAMaster.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  SKAMaster.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKAMaster.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  SKAMaster.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKAMaster.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  SKAMaster.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(SKAMaster.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  SKAMaster.test_testMode

    def test_maxCapabilities(self):
        """Test for maxCapabilities"""
        # PROTECTED REGION ID(SKAMaster.test_maxCapabilities) ENABLED START #
        self.device.maxCapabilities
        # PROTECTED REGION END #    //  SKAMaster.test_maxCapabilities

    def test_availableCapabilities(self):
        """Test for availableCapabilities"""
        # PROTECTED REGION ID(SKAMaster.test_availableCapabilities) ENABLED START #
        self.device.availableCapabilities
        # PROTECTED REGION END #    //  SKAMaster.test_availableCapabilities


# Main execution
if __name__ == "__main__":
    main()
