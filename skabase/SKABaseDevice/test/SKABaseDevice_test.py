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
import pytest
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
from time import sleep
from mock import MagicMock
from PyTango import DevFailed, DevState

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
@pytest.mark.usefixtures("tango_device_proxy")
class TestSKABaseDevice(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SKABaseDevice.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_additionnal_import
    properties = {'SkaLevel': '4', 'MetricList': 'healthState', 'GroupDefinitions': '', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 
                  }

    def test_properties(self, tango_device_proxy):
        # test the properties
        # PROTECTED REGION ID(SKABaseDevice.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKABaseDevice.test_properties
        pass

    def test_State(self, tango_device_proxy):
        """Test for State"""
        # PROTECTED REGION ID(SKABaseDevice.test_State) ENABLED START #
        tango_device_proxy.State()
        # PROTECTED REGION END #    //  SKABaseDevice.test_State

    def test_Status(self, tango_device_proxy):
        """Test for Status"""
        # PROTECTED REGION ID(SKABaseDevice.test_Status) ENABLED START #
        tango_device_proxy.Status()
        # PROTECTED REGION END #    //  SKABaseDevice.test_Status

    def test_Reset(self, tango_device_proxy):
        """Test for Reset"""
        # PROTECTED REGION ID(SKABaseDevice.test_Reset) ENABLED START #
        tango_device_proxy.Reset()
        # PROTECTED REGION END #    //  SKABaseDevice.test_Reset

    def test_GetMetrics(self, tango_device_proxy):
        """Test for GetMetrics"""
        # PROTECTED REGION ID(SKABaseDevice.test_GetMetrics) ENABLED START #
        tango_device_proxy.GetMetrics()
        # PROTECTED REGION END #    //  SKABaseDevice.test_GetMetrics

    def test_ToJson(self, tango_device_proxy):
        """Test for ToJson"""
        # PROTECTED REGION ID(SKABaseDevice.test_ToJson) ENABLED START #
        tango_device_proxy.ToJson("")
        # PROTECTED REGION END #    //  SKABaseDevice.test_ToJson

    def test_GetVersionInfo(self, tango_device_proxy):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKABaseDevice.test_GetVersionInfo) ENABLED START #
        tango_device_proxy.GetVersionInfo()
        # PROTECTED REGION END #    //  SKABaseDevice.test_GetVersionInfo

    def test_buildState(self, tango_device_proxy):
        """Test for buildState"""
        # PROTECTED REGION ID(SKABaseDevice.test_buildState) ENABLED START #
        tango_device_proxy.buildState
        # PROTECTED REGION END #    //  SKABaseDevice.test_buildState

    def test_versionId(self, tango_device_proxy):
        """Test for versionId"""
        # PROTECTED REGION ID(SKABaseDevice.test_versionId) ENABLED START #
        tango_device_proxy.versionId
        # PROTECTED REGION END #    //  SKABaseDevice.test_versionId

    def test_centralLoggingLevel(self, tango_device_proxy):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKABaseDevice.test_centralLoggingLevel) ENABLED START #
        tango_device_proxy.centralLoggingLevel
        # PROTECTED REGION END #    //  SKABaseDevice.test_centralLoggingLevel

    def test_elementLoggingLevel(self, tango_device_proxy):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKABaseDevice.test_elementLoggingLevel) ENABLED START #
        tango_device_proxy.elementLoggingLevel
        # PROTECTED REGION END #    //  SKABaseDevice.test_elementLoggingLevel

    def test_storageLoggingLevel(self, tango_device_proxy):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKABaseDevice.test_storageLoggingLevel) ENABLED START #
        tango_device_proxy.storageLoggingLevel
        # PROTECTED REGION END #    //  SKABaseDevice.test_storageLoggingLevel

    def test_healthState(self, tango_device_proxy):
        """Test for healthState"""
        # PROTECTED REGION ID(SKABaseDevice.test_healthState) ENABLED START #
        tango_device_proxy.healthState
        # PROTECTED REGION END #    //  SKABaseDevice.test_healthState

    def test_adminMode(self, tango_device_proxy):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_adminMode) ENABLED START #
        tango_device_proxy.adminMode
        # PROTECTED REGION END #    //  SKABaseDevice.test_adminMode

    def test_controlMode(self, tango_device_proxy):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_controlMode) ENABLED START #
        tango_device_proxy.controlMode
        # PROTECTED REGION END #    //  SKABaseDevice.test_controlMode

    def test_simulationMode(self, tango_device_proxy):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_simulationMode) ENABLED START #
        tango_device_proxy.simulationMode
        # PROTECTED REGION END #    //  SKABaseDevice.test_simulationMode

    def test_testMode(self, tango_device_proxy):
        """Test for testMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_testMode) ENABLED START #
        tango_device_proxy.testMode
        # PROTECTED REGION END #    //  SKABaseDevice.test_testMode


# Main execution
if __name__ == "__main__":
    main()
