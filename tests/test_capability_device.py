#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKACapability project
#
#
#
#########################################################################################
"""Contain the tests for the SKACapability."""
import re
import pytest

from ska_tango_base import SKACapability
from ska_tango_base.base import ReferenceBaseComponentManager
from ska_tango_base.control_model import AdminMode


# PROTECTED REGION ID(SKACapability.test_additional_imports) ENABLED START #
# PROTECTED REGION END #    //  SKACapability.test_additional_imports
# Device test case
# PROTECTED REGION ID(SKACapability.test_SKACapability_decorators) ENABLED START #
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION END #    //  SKACapability.test_SKACapability_decorators
class TestSKACapability(object):
    """Test case for packet generation."""

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Specification of the device under test.

        The specification includes the device's properties and memorized
        attributes.
        """
        return {
            "device": SKACapability,
            "component_manager_patch": lambda self: ReferenceBaseComponentManager(
                self.op_state_model, logger=self.logger
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip("Not implemented")
    def test_properties(self, tango_context):
        """Test device properties."""
        # PROTECTED REGION ID(SKACapability.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKACapability.test_properties

    def test_ConfigureInstances(self, tango_context):
        """Test for ConfigureInstances."""
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
        """Test for activationTime."""
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
        """Test for buildState."""
        # PROTECTED REGION ID(SKACapability.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  SKACapability.test_buildState

    # PROTECTED REGION ID(SKACapability.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId."""
        # PROTECTED REGION ID(SKACapability.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  SKACapability.test_versionId

    # PROTECTED REGION ID(SKACapability.test_configuredInstances_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_configuredInstances_decorators
    def test_configuredInstances(self, tango_context):
        """Test for configuredInstances."""
        # PROTECTED REGION ID(SKACapability.test_configuredInstances) ENABLED START #
        assert tango_context.device.configuredInstances == 0
        # PROTECTED REGION END #    //  SKACapability.test_configuredInstances

    # PROTECTED REGION ID(SKACapability.test_usedComponents_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_usedComponents_decorators
    def test_usedComponents(self, tango_context):
        """Test for usedComponents."""
        # PROTECTED REGION ID(SKACapability.test_usedComponents) ENABLED START #
        assert tango_context.device.usedComponents == ("",)
        # PROTECTED REGION END #    //  SKACapability.test_usedComponents
