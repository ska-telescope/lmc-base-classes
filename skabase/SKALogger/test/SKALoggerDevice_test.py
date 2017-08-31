#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SKALoggerDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKALoggerDevice."""

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
from SKALoggerDevice import SKALoggerDevice

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
class SKALoggerDeviceDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SKALoggerDevice.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SKALoggerDevice.test_additionnal_import
    device = SKALoggerDevice
    properties = {'SkaLevel': '4', 'MetricList': 'healthState,adminMode,controlMode', 'GroupDefinitions': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'CentralLoggingLevelDefault': '2', 'ElementLoggingLevelDefault': '3', 'StorageLoggingLevelDefault': '4', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKALoggerDevice.numpy = MagicMock()
        # PROTECTED REGION ID(SKALoggerDevice.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKALoggerDevice.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(SKALoggerDevice.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKALoggerDevice.test_properties
        pass

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(SKALoggerDevice.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  SKALoggerDevice.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(SKALoggerDevice.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  SKALoggerDevice.test_Status

    def test_SetCentralLoggingLevel(self):
        """Test for SetCentralLoggingLevel"""
        # PROTECTED REGION ID(SKALoggerDevice.test_SetCentralLoggingLevel) ENABLED START #
        self.device.SetCentralLoggingLevel(0)
        # PROTECTED REGION END #    //  SKALoggerDevice.test_SetCentralLoggingLevel

    def test_SetElementLoggingLevel(self):
        """Test for SetElementLoggingLevel"""
        # PROTECTED REGION ID(SKALoggerDevice.test_SetElementLoggingLevel) ENABLED START #
        self.device.SetElementLoggingLevel(0)
        # PROTECTED REGION END #    //  SKALoggerDevice.test_SetElementLoggingLevel

    def test_SetStorageLoggingLevel(self):
        """Test for SetStorageLoggingLevel"""
        # PROTECTED REGION ID(SKALoggerDevice.test_SetStorageLoggingLevel) ENABLED START #
        self.device.SetStorageLoggingLevel(0)
        # PROTECTED REGION END #    //  SKALoggerDevice.test_SetStorageLoggingLevel

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(SKALoggerDevice.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  SKALoggerDevice.test_Reset

    def test_GetMetrics(self):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(SKALoggerDevice.test_GetMetrics) ENABLED START #
        self.device.GetMetrics()
        # PROTECTED REGION END #    //  SKALoggerDevice.test_GetMetrics

    def test_ToJson(self):
        """Test for ToJson"""
        # PROTECTED REGION ID(SKALoggerDevice.test_ToJson) ENABLED START #
        self.device.ToJson("")
        # PROTECTED REGION END #    //  SKALoggerDevice.test_ToJson

    def test_GetVersionInfo(self):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKALoggerDevice.test_GetVersionInfo) ENABLED START #
        self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  SKALoggerDevice.test_GetVersionInfo

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(SKALoggerDevice.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  SKALoggerDevice.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(SKALoggerDevice.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  SKALoggerDevice.test_versionId

    def test_centralLoggingLevel(self):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKALoggerDevice.test_centralLoggingLevel) ENABLED START #
        self.device.centralLoggingLevel
        # PROTECTED REGION END #    //  SKALoggerDevice.test_centralLoggingLevel

    def test_elementLoggingLevel(self):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKALoggerDevice.test_elementLoggingLevel) ENABLED START #
        self.device.elementLoggingLevel
        # PROTECTED REGION END #    //  SKALoggerDevice.test_elementLoggingLevel

    def test_storageLoggingLevel(self):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKALoggerDevice.test_storageLoggingLevel) ENABLED START #
        self.device.storageLoggingLevel
        # PROTECTED REGION END #    //  SKALoggerDevice.test_storageLoggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(SKALoggerDevice.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  SKALoggerDevice.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKALoggerDevice.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  SKALoggerDevice.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKALoggerDevice.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  SKALoggerDevice.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKALoggerDevice.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  SKALoggerDevice.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(SKALoggerDevice.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  SKALoggerDevice.test_testMode


# Main execution
if __name__ == "__main__":
    main()
