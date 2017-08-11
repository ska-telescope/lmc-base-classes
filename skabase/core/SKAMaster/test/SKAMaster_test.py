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
    properties = {'member_list': '', 
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

    def test_add_member(self):
        """Test for add_member"""
        # PROTECTED REGION ID(SKAMaster.test_add_member) ENABLED START #
        self.device.add_member("")
        # PROTECTED REGION END #    //  SKAMaster.test_add_member

    def test_remove_member(self):
        """Test for remove_member"""
        # PROTECTED REGION ID(SKAMaster.test_remove_member) ENABLED START #
        self.device.remove_member("")
        # PROTECTED REGION END #    //  SKAMaster.test_remove_member

    def test_run_command(self):
        """Test for run_command"""
        # PROTECTED REGION ID(SKAMaster.test_run_command) ENABLED START #
        self.device.run_command("")
        # PROTECTED REGION END #    //  SKAMaster.test_run_command

    def test_get_member_names(self):
        """Test for get_member_names"""
        # PROTECTED REGION ID(SKAMaster.test_get_member_names) ENABLED START #
        self.device.get_member_names("")
        # PROTECTED REGION END #    //  SKAMaster.test_get_member_names

    def test_get_attribute_list(self):
        """Test for get_attribute_list"""
        # PROTECTED REGION ID(SKAMaster.test_get_attribute_list) ENABLED START #
        self.device.get_attribute_list("")
        # PROTECTED REGION END #    //  SKAMaster.test_get_attribute_list

    def test_members_state(self):
        """Test for members_state"""
        # PROTECTED REGION ID(SKAMaster.test_members_state) ENABLED START #
        self.device.members_state
        # PROTECTED REGION END #    //  SKAMaster.test_members_state


# Main execution
if __name__ == "__main__":
    main()
