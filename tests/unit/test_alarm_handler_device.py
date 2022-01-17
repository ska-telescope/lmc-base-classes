#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKAAlarmHandler project
#
#
#
#########################################################################################
"""Contain the tests for the SKAAlarmHandler."""

# Imports
import re

import pytest

from ska_tango_base import SKAAlarmHandler

from ska_tango_base.testing.reference import (
    ReferenceBaseComponentManager,
)
from ska_tango_base.control_model import AdminMode


# PROTECTED REGION ID(SKAAlarmHandler.test_additional_imports) ENABLED START #
# PROTECTED REGION END #    //  SKAAlarmHandler.test_additional_imports
# Device test case
# PROTECTED REGION ID(SKAAlarmHandler.test_SKAAlarmHandler_decorators) ENABLED START #
# PROTECTED REGION END #    //  SKAAlarmHandler.test_SKAAlarmHandler_decorators


class TestSKAAlarmHandler(object):
    """Test class for tests of the SKAAlarmHander device class."""

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Fixture that specifies the device to be tested.

        The specification includes device properties and memorized
        attributes.
        """
        return {
            "device": SKAAlarmHandler,
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
        """Test the device properties."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_properties

    # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmRule_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmRule_decorators
    def test_GetAlarmRule(self, device_under_test):
        """Test for GetAlarmRule."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmRule) ENABLED START #
        assert device_under_test.GetAlarmRule("") == ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmRule

    # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmData_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmData_decorators
    def test_GetAlarmData(self, device_under_test):
        """Test for GetAlarmData."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmData) ENABLED START #
        assert device_under_test.GetAlarmData("") == ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmData

    # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmAdditionalInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmAdditionalInfo_decorators
    def test_GetAlarmAdditionalInfo(self, device_under_test):
        """Test for GetAlarmAdditionalInfo."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmAdditionalInfo) ENABLED START #
        assert device_under_test.GetAlarmAdditionalInfo("") == ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmAdditionalInfo

    # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmStats_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmStats_decorators
    def test_GetAlarmStats(self, device_under_test):
        """Test for GetAlarmStats."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmStats) ENABLED START #
        assert device_under_test.GetAlarmStats() == ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmStats

    # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlertStats_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlertStats_decorators
    def test_GetAlertStats(self, device_under_test):
        """Test for GetAlertStats."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlertStats) ENABLED START #
        assert device_under_test.GetAlertStats() == ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlertStats

    # PROTECTED REGION ID(SKAAlarmHandler.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test):
        """Test for GetVersionInfo."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetVersionInfo) ENABLED START #
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])

        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetVersionInfo

    # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrAlerts_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrAlerts_decorators
    def test_statsNrAlerts(self, device_under_test):
        """Test for statsNrAlerts."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrAlerts) ENABLED START #
        assert device_under_test.statsNrAlerts == 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrAlerts

    # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrAlarms_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrAlarms_decorators
    def test_statsNrAlarms(self, device_under_test):
        """Test for statsNrAlarms."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrAlarms) ENABLED START #
        assert device_under_test.statsNrAlarms == 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrAlarms

    # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrNewAlarms_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrNewAlarms_decorators
    def test_statsNrNewAlarms(self, device_under_test):
        """Test for statsNrNewAlarms."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrNewAlarms) ENABLED START #
        assert device_under_test.statsNrNewAlarms == 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrNewAlarms

    # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrUnackAlarms_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrUnackAlarms_decorators
    def test_statsNrUnackAlarms(self, device_under_test):
        """Test for statsNrUnackAlarms."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrUnackAlarms) ENABLED START #
        assert device_under_test.statsNrUnackAlarms == 0.0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrUnackAlarms

    # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrRtnAlarms_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrRtnAlarms_decorators
    def test_statsNrRtnAlarms(self, device_under_test):
        """Test for statsNrRtnAlarms."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrRtnAlarms) ENABLED START #
        assert device_under_test.statsNrRtnAlarms == 0.0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrRtnAlarms

    # PROTECTED REGION ID(SKAAlarmHandler.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_buildState_decorators
    def test_buildState(self, device_under_test):
        """Test for buildState."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, device_under_test.buildState)) is not None
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_buildState

    # PROTECTED REGION ID(SKAAlarmHandler.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_versionId_decorators
    def test_versionId(self, device_under_test):
        """Test for versionId."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_versionId

    # PROTECTED REGION ID(SKAAlarmHandler.test_activeAlerts_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_activeAlerts_decorators
    def test_activeAlerts(self, device_under_test):
        """Test for activeAlerts."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_activeAlerts) ENABLED START #
        assert device_under_test.activeAlerts == ("",)
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_activeAlerts

    # PROTECTED REGION ID(SKAAlarmHandler.test_activeAlarms_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_activeAlarms_decorators
    def test_activeAlarms(self, device_under_test):
        """Test for activeAlarms."""
        # PROTECTED REGION ID(SKAAlarmHandler.test_activeAlarms) ENABLED START #
        assert device_under_test.activeAlarms == ("",)
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_activeAlarms
