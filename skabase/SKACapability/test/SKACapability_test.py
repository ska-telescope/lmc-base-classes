#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKACapability project
#
#
#
#########################################################################################
"""Contain the tests for the SKACapability."""

# Standard imports
import sys
import os

# Imports
import re
import pytest
from tango import DevState

# Path
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# PROTECTED REGION ID(SKACapability.test_additional_imports) ENABLED START #
# PROTECTED REGION END #    //  SKACapability.test_additional_imports
# Device test case
# PROTECTED REGION ID(SKACapability.test_SKACapability_decorators) ENABLED START #
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION END #    //  SKACapability.test_SKACapability_decorators
class TestSKACapability(object):
    """Test case for packet generation."""

    properties = {
        'SkaLevel': '4',
        'CentralLoggingTarget': '',
        'ElementLoggingTarget': '',
        'StorageLoggingTarget': 'localhost',
        'GroupDefinitions': '',
        'CapType': '',
        'CapID': '',
        'subID': '',
        }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKACapability.numpy = MagicMock()
        # PROTECTED REGION ID(SKACapability.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKACapability.test_mocking

    def test_properties(self, tango_context):
        """Test device properties"""
        # Test the properties
        # PROTECTED REGION ID(SKACapability.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKACapability.test_properties

    # PROTECTED REGION ID(SKACapability.test_ObsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_ObsState_decorators

    def test_ConfigureInstances(self, tango_context):
        """Test for ConfigureInstances"""
        # PROTECTED REGION ID(SKACapability.test_ConfigureInstances) ENABLED START #
        tango_context.device.ConfigureInstances(1)
        assert tango_context.device.configuredInstances == 1
        # PROTECTED REGION END #    //  SKACapability.test_ConfigureInstances

    # # PROTECTED REGION ID(SKACapability.test_Reset_decorators) ENABLED START #
    # # PROTECTED REGION END #    //  SKACapability.test_Reset_decorators
    # def test_Reset(self, tango_context):
    #     """Test for Reset"""
    #     # PROTECTED REGION ID(SKACapability.test_Reset) ENABLED START #
    #     assert tango_context.device.Reset() == None
    #     # PROTECTED REGION END #    //  SKACapability.test_Reset

    # PROTECTED REGION ID(SKACapability.test_activationTime_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_activationTime_decorators
    def test_activationTime(self, tango_context):
        """Test for activationTime"""
        # PROTECTED REGION ID(SKACapability.test_activationTime) ENABLED START #
        assert tango_context.device.activationTime == 0.0
        # PROTECTED REGION END #    //  SKACapability.test_activationTime

    # PROTECTED REGION ID(SKACapability.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_configurationProgress_decorators
    # def test_configurationProgress(self, tango_context):
    #     """Test for configurationProgress"""
    #     # PROTECTED REGION ID(SKACapability.test_configurationProgress) ENABLED START #
    #     assert tango_context.device.configurationProgress == 0
    #     # PROTECTED REGION END #    //  SKACapability.test_configurationProgress

    # PROTECTED REGION ID(SKACapability.test_configurationDelayExpected_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_configurationDelayExpected_decorators
    # def test_configurationDelayExpected(self, tango_context):
    #     """Test for configurationDelayExpected"""
    #     # PROTECTED REGION ID(SKACapability.test_configurationDelayExpected) ENABLED START #
    #     assert tango_context.device.configurationDelayExpected == 0
    #     # PROTECTED REGION END #    //  SKACapability.test_configurationDelayExpected

    # PROTECTED REGION ID(SKACapability.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKACapability.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  SKACapability.test_buildState

    # PROTECTED REGION ID(SKACapability.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKACapability.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  SKACapability.test_versionId

    # PROTECTED REGION ID(SKACapability.test_configuredInstances_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_configuredInstances_decorators
    def test_configuredInstances(self, tango_context):
        """Test for configuredInstances"""
        # PROTECTED REGION ID(SKACapability.test_configuredInstances) ENABLED START #
        assert tango_context.device.configuredInstances == 0
        # PROTECTED REGION END #    //  SKACapability.test_configuredInstances

    # PROTECTED REGION ID(SKACapability.test_usedComponents_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_usedComponents_decorators
    def test_usedComponents(self, tango_context):
        """Test for usedComponents"""
        # PROTECTED REGION ID(SKACapability.test_usedComponents) ENABLED START #
        assert tango_context.device.usedComponents == ('',)
        # PROTECTED REGION END #    //  SKACapability.test_usedComponents
