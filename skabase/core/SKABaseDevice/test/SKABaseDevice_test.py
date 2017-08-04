#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKABASE."""

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
from SKABaseDevice import SKABaseDevice

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
class SKABaseDeviceDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SKABaseDevice.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_additionnal_import
    device = SKABaseDevice
    properties = {'SkaLevel': '4', 'ManagedDevices': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'CentralLoggingLevelDefault': '', 'ElementLoggingLevelDefault': '', 'StorageLoggingLevelStorage': '', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKABaseDevice.numpy = MagicMock()
        # PROTECTED REGION ID(SKABaseDevice.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKABaseDevice.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(SKABaseDevice.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKABaseDevice.test_properties
        pass

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(SKABaseDevice.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  SKABaseDevice.test_Reset

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(SKABaseDevice.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  SKABaseDevice.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(SKABaseDevice.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  SKABaseDevice.test_Status

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(SKABaseDevice.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  SKABaseDevice.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(SKABaseDevice.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  SKABaseDevice.test_versionId

    def test_centralLoggingLevel(self):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKABaseDevice.test_centralLoggingLevel) ENABLED START #
        self.device.centralLoggingLevel
        # PROTECTED REGION END #    //  SKABaseDevice.test_centralLoggingLevel

    def test_elementLoggingLevel(self):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKABaseDevice.test_elementLoggingLevel) ENABLED START #
        self.device.elementLoggingLevel
        # PROTECTED REGION END #    //  SKABaseDevice.test_elementLoggingLevel

    def test_storageLoggingLevel(self):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKABaseDevice.test_storageLoggingLevel) ENABLED START #
        self.device.storageLoggingLevel
        # PROTECTED REGION END #    //  SKABaseDevice.test_storageLoggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(SKABaseDevice.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  SKABaseDevice.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  SKABaseDevice.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  SKABaseDevice.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  SKABaseDevice.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  SKABaseDevice.test_testMode

    def test_testadd(self):
        """Test for testadd"""
        # PROTECTED REGION ID(SKABaseDevice.test_testadd) ENABLED START #
        self.device.testadd
        # PROTECTED REGION END #    //  SKABaseDevice.test_testadd


# Main execution
if __name__ == "__main__":
    main()
