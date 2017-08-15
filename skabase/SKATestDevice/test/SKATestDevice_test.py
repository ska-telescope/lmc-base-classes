#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SKATestDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKATestDevice."""

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
from SKATestDevice import SKATestDevice

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
class SKATestDeviceDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SKATestDevice.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_additionnal_import
    device = SKATestDevice
    properties = {'SkaLevel': '4', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'CentralLoggingLevelDefault': '', 'ElementLoggingLevelDefault': '', 'StorageLoggingLevelStorage': '', 'MetricList': 'healthState,adminMode,controlMode', 'GroupDefinitions': '', 'StorageLoggingLevelDefault': '', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKATestDevice.numpy = MagicMock()
        # PROTECTED REGION ID(SKATestDevice.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKATestDevice.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(SKATestDevice.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKATestDevice.test_properties
        pass

    def test_ObsState(self):
        """Test for ObsState"""
        # PROTECTED REGION ID(SKATestDevice.test_ObsState) ENABLED START #
        self.device.ObsState()
        # PROTECTED REGION END #    //  SKATestDevice.test_ObsState

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(SKATestDevice.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  SKATestDevice.test_Reset

    def test_GetMetrics(self):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(SKATestDevice.test_GetMetrics) ENABLED START #
        self.device.GetMetrics()
        # PROTECTED REGION END #    //  SKATestDevice.test_GetMetrics

    def test_ToJson(self):
        """Test for ToJson"""
        # PROTECTED REGION ID(SKATestDevice.test_ToJson) ENABLED START #
        self.device.ToJson("")
        # PROTECTED REGION END #    //  SKATestDevice.test_ToJson

    def test_GetVersionInfo(self):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKATestDevice.test_GetVersionInfo) ENABLED START #
        self.device.GetVersionInfo()
        # PROTECTED REGION END #    //  SKATestDevice.test_GetVersionInfo

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(SKATestDevice.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  SKATestDevice.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(SKATestDevice.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  SKATestDevice.test_Status

    def test_obsState(self):
        """Test for obsState"""
        # PROTECTED REGION ID(SKATestDevice.test_obsState) ENABLED START #
        self.device.obsState
        # PROTECTED REGION END #    //  SKATestDevice.test_obsState

    def test_obsMode(self):
        """Test for obsMode"""
        # PROTECTED REGION ID(SKATestDevice.test_obsMode) ENABLED START #
        self.device.obsMode
        # PROTECTED REGION END #    //  SKATestDevice.test_obsMode

    def test_configurationProgress(self):
        """Test for configurationProgress"""
        # PROTECTED REGION ID(SKATestDevice.test_configurationProgress) ENABLED START #
        self.device.configurationProgress
        # PROTECTED REGION END #    //  SKATestDevice.test_configurationProgress

    def test_configurationDelayExpected(self):
        """Test for configurationDelayExpected"""
        # PROTECTED REGION ID(SKATestDevice.test_configurationDelayExpected) ENABLED START #
        self.device.configurationDelayExpected
        # PROTECTED REGION END #    //  SKATestDevice.test_configurationDelayExpected

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(SKATestDevice.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  SKATestDevice.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(SKATestDevice.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  SKATestDevice.test_versionId

    def test_centralLoggingLevel(self):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKATestDevice.test_centralLoggingLevel) ENABLED START #
        self.device.centralLoggingLevel
        # PROTECTED REGION END #    //  SKATestDevice.test_centralLoggingLevel

    def test_elementLoggingLevel(self):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKATestDevice.test_elementLoggingLevel) ENABLED START #
        self.device.elementLoggingLevel
        # PROTECTED REGION END #    //  SKATestDevice.test_elementLoggingLevel

    def test_storageLoggingLevel(self):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKATestDevice.test_storageLoggingLevel) ENABLED START #
        self.device.storageLoggingLevel
        # PROTECTED REGION END #    //  SKATestDevice.test_storageLoggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(SKATestDevice.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  SKATestDevice.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKATestDevice.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  SKATestDevice.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKATestDevice.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  SKATestDevice.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKATestDevice.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  SKATestDevice.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(SKATestDevice.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  SKATestDevice.test_testMode


# Main execution
if __name__ == "__main__":
    main()
