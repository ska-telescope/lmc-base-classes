#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SKATelStateDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKATelStateDevice."""

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
from SKATelStateDevice import SKATelStateDevice

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
class SKATelStateDeviceDeviceTestCase(DeviceTestCase):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SKATelStateDevice.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SKATelStateDevice.test_additionnal_import
    device = SKATelStateDevice
    properties = {
                  }
    empty = None  # Should be []

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKATelStateDevice.numpy = MagicMock()
        # PROTECTED REGION ID(SKATelStateDevice.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKATelStateDevice.test_mocking

    def test_properties(self):
        # test the properties
        # PROTECTED REGION ID(SKATelStateDevice.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKATelStateDevice.test_properties
        pass

    def test_State(self):
        """Test for State"""
        # PROTECTED REGION ID(SKATelStateDevice.test_State) ENABLED START #
        self.device.State()
        # PROTECTED REGION END #    //  SKATelStateDevice.test_State

    def test_Status(self):
        """Test for Status"""
        # PROTECTED REGION ID(SKATelStateDevice.test_Status) ENABLED START #
        self.device.Status()
        # PROTECTED REGION END #    //  SKATelStateDevice.test_Status


# Main execution
if __name__ == "__main__":
    main()
