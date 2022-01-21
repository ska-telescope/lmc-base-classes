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

from ska_tango_base.testing.reference import (
    ReferenceBaseComponentManager,
)
from ska_tango_base.control_model import AdminMode


# PROTECTED REGION ID(SKACapability.test_additional_imports) ENABLED START #
# PROTECTED REGION END #    //  SKACapability.test_additional_imports
# Device test case
# PROTECTED REGION ID(SKACapability.test_SKACapability_decorators) ENABLED START #
# PROTECTED REGION END #    //  SKACapability.test_SKACapability_decorators
class TestSKACapability(object):
    """Test case for packet generation."""

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Specification of the device under test.

        The specification includes the device's properties and memorized
        attributes.

        :param device_properties: fixture that returns device properties
            of the device under test

        :return: specification of how the device under test should be
            configured
        """
        return {
            "device": SKACapability,
            "component_manager_patch": lambda self: ReferenceBaseComponentManager(
                self.logger,
                self._communication_state_changed,
                self._component_state_changed,
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip("Not implemented")
    def test_properties(self, device_under_test):
        """
        Test device properties.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKACapability.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKACapability.test_properties

    def test_ConfigureInstances(self, device_under_test):
        """
        Test for ConfigureInstances.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKACapability.test_ConfigureInstances) ENABLED START #
        device_under_test.ConfigureInstances(1)
        assert device_under_test.configuredInstances == 1
        # PROTECTED REGION END #    //  SKACapability.test_ConfigureInstances

    # # PROTECTED REGION ID(SKACapability.test_Reset_decorators) ENABLED START #
    # # PROTECTED REGION END #    //  SKACapability.test_Reset_decorators
    # def test_Reset(self, device_under_test):
    #     """
    #     Test for Reset

    #     :param device_under_test: a proxy to the device under test
    #     """
    #     # PROTECTED REGION ID(SKACapability.test_Reset) ENABLED START #
    #     assert device_under_test.Reset() == None
    #     # PROTECTED REGION END #    //  SKACapability.test_Reset

    # PROTECTED REGION ID(SKACapability.test_activationTime_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_activationTime_decorators
    def test_activationTime(self, device_under_test):
        """
        Test for activationTime.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKACapability.test_activationTime) ENABLED START #
        assert device_under_test.activationTime == 0.0
        # PROTECTED REGION END #    //  SKACapability.test_activationTime

    # PROTECTED REGION ID(SKACapability.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_configurationProgress_decorators
    # def test_configurationProgress(self, device_under_test):
    #     """
    #     Test for configurationProgress
    #
    #     :param device_under_test: a proxy to the device under test
    #     """
    #     # PROTECTED REGION ID(SKACapability.test_configurationProgress) ENABLED START #
    #     assert device_under_test.configurationProgress == 0
    #     # PROTECTED REGION END #    //  SKACapability.test_configurationProgress

    # PROTECTED REGION ID(SKACapability.test_configurationDelayExpected_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_configurationDelayExpected_decorators
    # def test_configurationDelayExpected(self, device_under_test):
    #     """
    #     Test for configurationDelayExpected

    #     :param device_under_test: a proxy to the device under test
    #     """
    #     # PROTECTED REGION ID(SKACapability.test_configurationDelayExpected) ENABLED START #
    #     assert device_under_test.configurationDelayExpected == 0
    #     # PROTECTED REGION END #    //  SKACapability.test_configurationDelayExpected

    # PROTECTED REGION ID(SKACapability.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_buildState_decorators
    def test_buildState(self, device_under_test):
        """
        Test for buildState.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKACapability.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, device_under_test.buildState)) is not None
        # PROTECTED REGION END #    //  SKACapability.test_buildState

    # PROTECTED REGION ID(SKACapability.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_versionId_decorators
    def test_versionId(self, device_under_test):
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKACapability.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  SKACapability.test_versionId

    # PROTECTED REGION ID(SKACapability.test_configuredInstances_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_configuredInstances_decorators
    def test_configuredInstances(self, device_under_test):
        """
        Test for configuredInstances.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKACapability.test_configuredInstances) ENABLED START #
        assert device_under_test.configuredInstances == 0
        # PROTECTED REGION END #    //  SKACapability.test_configuredInstances

    # PROTECTED REGION ID(SKACapability.test_usedComponents_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKACapability.test_usedComponents_decorators
    def test_usedComponents(self, device_under_test):
        """
        Test for usedComponents.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKACapability.test_usedComponents) ENABLED START #
        assert device_under_test.usedComponents == ("",)
        # PROTECTED REGION END #    //  SKACapability.test_usedComponents
