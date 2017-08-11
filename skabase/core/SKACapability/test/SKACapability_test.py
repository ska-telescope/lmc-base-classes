#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SKACapability project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKACapability."""

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
from SKACapability import SKACapability

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
class SKACapabilityDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SKACapability.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_additionnal_import
    device = SKACapability
    properties = {'SkaLevel': '4', 'ManagedDevices': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'CentralLoggingLevelDefault': '', 'ElementLoggingLevelDefault': '', 'StorageLoggingLevelStorage': '', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKACapability.numpy = MagicMock()
        # PROTECTED REGION ID(SKACapability.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKACapability.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(SKACapability.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKACapability.test_properties
        pass

    def test_ObsState(self):
        """Test for ObsState"""
        # PROTECTED REGION ID(SKACapability.test_ObsState) ENABLED START #
        self.device.ObsState()
        # PROTECTED REGION END #    //  SKACapability.test_ObsState

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(SKACapability.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  SKACapability.test_Reset

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(SKACapability.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  SKACapability.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(SKACapability.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  SKACapability.test_Status

    def test_subID(self):
        """Test for subID"""
        # PROTECTED REGION ID(SKACapability.test_subID) ENABLED START #
        self.device.subID
        # PROTECTED REGION END #    //  SKACapability.test_subID

    def test_capID(self):
        """Test for capID"""
        # PROTECTED REGION ID(SKACapability.test_capID) ENABLED START #
        self.device.capID
        # PROTECTED REGION END #    //  SKACapability.test_capID

    def test_maxInstances(self):
        """Test for maxInstances"""
        # PROTECTED REGION ID(SKACapability.test_maxInstances) ENABLED START #
        self.device.maxInstances
        # PROTECTED REGION END #    //  SKACapability.test_maxInstances

    def test_availableInstances(self):
        """Test for availableInstances"""
        # PROTECTED REGION ID(SKACapability.test_availableInstances) ENABLED START #
        self.device.availableInstances
        # PROTECTED REGION END #    //  SKACapability.test_availableInstances

    def test_activationTime(self):
        """Test for activationTime"""
        # PROTECTED REGION ID(SKACapability.test_activationTime) ENABLED START #
        self.device.activationTime
        # PROTECTED REGION END #    //  SKACapability.test_activationTime

    def test_obsState(self):
        """Test for obsState"""
        # PROTECTED REGION ID(SKACapability.test_obsState) ENABLED START #
        self.device.obsState
        # PROTECTED REGION END #    //  SKACapability.test_obsState

    def test_obsMode(self):
        """Test for obsMode"""
        # PROTECTED REGION ID(SKACapability.test_obsMode) ENABLED START #
        self.device.obsMode
        # PROTECTED REGION END #    //  SKACapability.test_obsMode

    def test_configurationProgress(self):
        """Test for configurationProgress"""
        # PROTECTED REGION ID(SKACapability.test_configurationProgress) ENABLED START #
        self.device.configurationProgress
        # PROTECTED REGION END #    //  SKACapability.test_configurationProgress

    def test_configurationDelayExpected(self):
        """Test for configurationDelayExpected"""
        # PROTECTED REGION ID(SKACapability.test_configurationDelayExpected) ENABLED START #
        self.device.configurationDelayExpected
        # PROTECTED REGION END #    //  SKACapability.test_configurationDelayExpected

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(SKACapability.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  SKACapability.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(SKACapability.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  SKACapability.test_versionId

    def test_centralLoggingLevel(self):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKACapability.test_centralLoggingLevel) ENABLED START #
        self.device.centralLoggingLevel
        # PROTECTED REGION END #    //  SKACapability.test_centralLoggingLevel

    def test_elementLoggingLevel(self):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKACapability.test_elementLoggingLevel) ENABLED START #
        self.device.elementLoggingLevel
        # PROTECTED REGION END #    //  SKACapability.test_elementLoggingLevel

    def test_storageLoggingLevel(self):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKACapability.test_storageLoggingLevel) ENABLED START #
        self.device.storageLoggingLevel
        # PROTECTED REGION END #    //  SKACapability.test_storageLoggingLevel

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(SKACapability.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  SKACapability.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKACapability.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  SKACapability.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKACapability.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  SKACapability.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKACapability.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  SKACapability.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(SKACapability.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  SKACapability.test_testMode


# Main execution
if __name__ == "__main__":
    main()
