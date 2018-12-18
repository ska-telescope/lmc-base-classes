#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SKATestDevice project
#
#
#
# Distributed under the terms of the none license.
# See LICENSE.txt for more info.
"""Contain the tests for the SKATestDevice."""

# Path
import sys
import os
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# Imports
import pytest
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
@pytest.mark.usefixtures("tango_context", "initialize_device")
class TestSKATestDevice(object):
    """Test case for packet generation."""
    # PROTECTED REGION ID(SKATestDevice.test_additionnal_import) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_additionnal_import

    properties = {'SkaLevel': '4', 'CentralLoggingTarget': '', 'ElementLoggingTarget': '', 'StorageLoggingTarget': 'localhost', 'CentralLoggingLevelDefault': '', 'ElementLoggingLevelDefault': '', 'StorageLoggingLevelStorage': '', 'MetricList': 'healthState', 'GroupDefinitions': '', 'StorageLoggingLevelDefault': '', 
                  }


    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKATestDevice.numpy = MagicMock()
        # PROTECTED REGION ID(SKATestDevice.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKATestDevice.test_mocking

    def test_properties(self, tango_context):
        # test the properties
        # PROTECTED REGION ID(SKATestDevice.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKATestDevice.test_properties
        pass

    # PROTECTED REGION ID(SKATestDevice.test_GetMetrics_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_GetMetrics_decorators
    # def test_GetMetrics(self, tango_context):
    #    """Test for GetMetrics"""
    #    # PROTECTED REGION ID(SKATestDevice.test_GetMetrics) ENABLED START #
    #    assert tango_context.device.GetMetrics() == ""
    #    # PROTECTED REGION END #    //  SKATestDevice.test_GetMetrics

    # PROTECTED REGION ID(SKATestDevice.test_ToJson_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKATestDevice.test_ToJson_decorators
    # def test_ToJson(self, tango_context):
    #    """Test for ToJson"""
    #    # PROTECTED REGION ID(SKATestDevice.test_ToJson) ENABLED START #
    #    assert tango_context.device.ToJson("") == ""
    #    # PROTECTED REGION END #    //  SKATestDevice.test_ToJson

    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKATestDevice.test_GetVersionInfo) ENABLED START #
        assert tango_context.device.GetVersionInfo() == [""]
        # PROTECTED REGION END #    //  SKATestDevice.test_GetVersionInfo

    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKATestDevice.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.UNKNOWN
        # PROTECTED REGION END #    //  SKATestDevice.test_State

    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKATestDevice.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in UNKNOWN state."
        # PROTECTED REGION END #    //  SKATestDevice.test_Status

    def test_RunGroupCommand(self, tango_context):
        """Test for RunGroupCommand"""
        # PROTECTED REGION ID(SKATestDevice.test_RunGroupCommand) ENABLED START #
        assert tango_context.device.RunGroupCommand("") == ""
        # PROTECTED REGION END #    //  SKATestDevice.test_RunGroupCommand

    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SKATestDevice.test_Reset) ENABLED START #
        assert tango_context.device.Reset() == None
        # PROTECTED REGION END #    //  SKATestDevice.test_Reset

    def test_On(self):
        """Test for On"""
        # PROTECTED REGION ID(SKATestDevice.test_On) ENABLED START #
        self.device.On()
        # PROTECTED REGION END #    //  SKATestDevice.test_On

    def test_Stop(self):
        """Test for Stop"""
        # PROTECTED REGION ID(SKATestDevice.test_Stop) ENABLED START #
        self.device.Stop()
        # PROTECTED REGION END #    //  SKATestDevice.test_Stop

    def test_obsState(self, tango_context):
        """Test for obsState"""
        # PROTECTED REGION ID(SKATestDevice.test_obsState) ENABLED START #
        assert tango_context.device.obsState == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_obsState

    def test_obsMode(self, tango_context):
        """Test for obsMode"""
        # PROTECTED REGION ID(SKATestDevice.test_obsMode) ENABLED START #
        assert tango_context.device.obsMode == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_obsMode

    def test_configurationProgress(self, tango_context):
        """Test for configurationProgress"""
        # PROTECTED REGION ID(SKATestDevice.test_configurationProgress) ENABLED START #
        assert tango_context.device.configurationProgress == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_configurationProgress

    def test_configurationDelayExpected(self, tango_context):
        """Test for configurationDelayExpected"""
        # PROTECTED REGION ID(SKATestDevice.test_configurationDelayExpected) ENABLED START #
        assert tango_context.device.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_configurationDelayExpected

    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKATestDevice.test_buildState) ENABLED START #
        assert tango_context.device.buildState == ''
        # PROTECTED REGION END #    //  SKATestDevice.test_buildState

    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKATestDevice.test_versionId) ENABLED START #
        assert tango_context.device.versionId == ''
        # PROTECTED REGION END #    //  SKATestDevice.test_versionId

    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKATestDevice.test_centralLoggingLevel) ENABLED START #
        assert tango_context.device.centralLoggingLevel == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_centralLoggingLevel

    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKATestDevice.test_elementLoggingLevel) ENABLED START #
        assert tango_context.device.elementLoggingLevel == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_elementLoggingLevel

    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKATestDevice.test_storageLoggingLevel) ENABLED START #
        assert tango_context.device.storageLoggingLevel == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_storageLoggingLevel

    def test_healthState(self,tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKATestDevice.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_healthState

    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKATestDevice.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_adminMode

    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKATestDevice.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == 0
        # PROTECTED REGION END #    //  SKATestDevice.test_controlMode

    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKATestDevice.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == False
        # PROTECTED REGION END #    //  SKATestDevice.test_simulationMode

    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKATestDevice.test_testMode) ENABLED START #
        assert tango_context.device.testMode == ''
        # PROTECTED REGION END #    //  SKATestDevice.test_testMode
