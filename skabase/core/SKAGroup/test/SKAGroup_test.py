#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SKAGroup project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the ."""

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
from SKAGroup import SKAGroup

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
class SKAGroupDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SKAGroup.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SKAGroup.test_additionnal_import
    device = SKAGroup
    properties = {'member_list': '', 'SkaLevel': '4', 'ManagedDevices': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'CentralLoggingLevelDefault': '', 'ElementLoggingLevelDefault': '', 'StorageLoggingLevelStorage': '', 'WillInheritFrom': 'SKABaseDevice', 
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKAGroup.numpy = MagicMock()
        # PROTECTED REGION ID(SKAGroup.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKAGroup.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(SKAGroup.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKAGroup.test_properties
        pass

    def test_add_member(self):
        """Test for add_member"""
        # PROTECTED REGION ID(SKAGroup.test_add_member) ENABLED START #
        self.device.add_member("")
        # PROTECTED REGION END #    //  SKAGroup.test_add_member

    def test_remove_member(self):
        """Test for remove_member"""
        # PROTECTED REGION ID(SKAGroup.test_remove_member) ENABLED START #
        self.device.remove_member("")
        # PROTECTED REGION END #    //  SKAGroup.test_remove_member

    def test_run_command(self):
        """Test for run_command"""
        # PROTECTED REGION ID(SKAGroup.test_run_command) ENABLED START #
        self.device.run_command("")
        # PROTECTED REGION END #    //  SKAGroup.test_run_command

    def test_get_member_names(self):
        """Test for get_member_names"""
        # PROTECTED REGION ID(SKAGroup.test_get_member_names) ENABLED START #
        self.device.get_member_names("")
        # PROTECTED REGION END #    //  SKAGroup.test_get_member_names

    def test_get_attribute_list(self):
        """Test for get_attribute_list"""
        # PROTECTED REGION ID(SKAGroup.test_get_attribute_list) ENABLED START #
        self.device.get_attribute_list("")
        # PROTECTED REGION END #    //  SKAGroup.test_get_attribute_list

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(SKAGroup.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  SKAGroup.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(SKAGroup.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  SKAGroup.test_Status

    def test_Reset(self):
        """Test for Reset"""
        # PROTECTED REGION ID(SKAGroup.test_Reset) ENABLED START #
        self.device.Reset()
        # PROTECTED REGION END #    //  SKAGroup.test_Reset

    def test_ObsState(self):
        """Test for ObsState"""
        # PROTECTED REGION ID(SKAGroup.test_ObsState) ENABLED START #
        self.device.ObsState()
        # PROTECTED REGION END #    //  SKAGroup.test_ObsState

    def test_members_state(self):
        """Test for members_state"""
        # PROTECTED REGION ID(SKAGroup.test_members_state) ENABLED START #
        self.device.members_state
        # PROTECTED REGION END #    //  SKAGroup.test_members_state

    def test_centralLoggingLevel(self):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKAGroup.test_centralLoggingLevel) ENABLED START #
        self.device.centralLoggingLevel
        # PROTECTED REGION END #    //  SKAGroup.test_centralLoggingLevel

    def test_elementLoggingLevel(self):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKAGroup.test_elementLoggingLevel) ENABLED START #
        self.device.elementLoggingLevel
        # PROTECTED REGION END #    //  SKAGroup.test_elementLoggingLevel

    def test_storageLoggingLevel(self):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKAGroup.test_storageLoggingLevel) ENABLED START #
        self.device.storageLoggingLevel
        # PROTECTED REGION END #    //  SKAGroup.test_storageLoggingLevel

    def test_buildState(self):
        """Test for buildState"""
        # PROTECTED REGION ID(SKAGroup.test_buildState) ENABLED START #
        self.device.buildState
        # PROTECTED REGION END #    //  SKAGroup.test_buildState

    def test_versionId(self):
        """Test for versionId"""
        # PROTECTED REGION ID(SKAGroup.test_versionId) ENABLED START #
        self.device.versionId
        # PROTECTED REGION END #    //  SKAGroup.test_versionId

    def test_healthState(self):
        """Test for healthState"""
        # PROTECTED REGION ID(SKAGroup.test_healthState) ENABLED START #
        self.device.healthState
        # PROTECTED REGION END #    //  SKAGroup.test_healthState

    def test_adminMode(self):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKAGroup.test_adminMode) ENABLED START #
        self.device.adminMode
        # PROTECTED REGION END #    //  SKAGroup.test_adminMode

    def test_controlMode(self):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKAGroup.test_controlMode) ENABLED START #
        self.device.controlMode
        # PROTECTED REGION END #    //  SKAGroup.test_controlMode

    def test_simulationMode(self):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKAGroup.test_simulationMode) ENABLED START #
        self.device.simulationMode
        # PROTECTED REGION END #    //  SKAGroup.test_simulationMode

    def test_testMode(self):
        """Test for testMode"""
        # PROTECTED REGION ID(SKAGroup.test_testMode) ENABLED START #
        self.device.testMode
        # PROTECTED REGION END #    //  SKAGroup.test_testMode

    def test_obsState(self):
        """Test for obsState"""
        # PROTECTED REGION ID(SKAGroup.test_obsState) ENABLED START #
        self.device.obsState
        # PROTECTED REGION END #    //  SKAGroup.test_obsState

    def test_obsMode(self):
        """Test for obsMode"""
        # PROTECTED REGION ID(SKAGroup.test_obsMode) ENABLED START #
        self.device.obsMode
        # PROTECTED REGION END #    //  SKAGroup.test_obsMode

    def test_configurationProgress(self):
        """Test for configurationProgress"""
        # PROTECTED REGION ID(SKAGroup.test_configurationProgress) ENABLED START #
        self.device.configurationProgress
        # PROTECTED REGION END #    //  SKAGroup.test_configurationProgress

    def test_configurationDelayExpected(self):
        """Test for configurationDelayExpected"""
        # PROTECTED REGION ID(SKAGroup.test_configurationDelayExpected) ENABLED START #
        self.device.configurationDelayExpected
        # PROTECTED REGION END #    //  SKAGroup.test_configurationDelayExpected


# Main execution
if __name__ == "__main__":
    main()
