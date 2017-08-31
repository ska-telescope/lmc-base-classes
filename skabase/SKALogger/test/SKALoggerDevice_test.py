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
    properties = {
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


# Main execution
if __name__ == "__main__":
    main()
