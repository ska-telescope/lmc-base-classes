#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKAAlarmHandler project
#
#
#
#########################################################################################
"""Contain the tests for the SKAAlarmHandler."""

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

# PROTECTED REGION ID(SKAAlarmHandler.test_additional_imports) ENABLED START #
# PROTECTED REGION END #    //  SKAAlarmHandler.test_additional_imports
# Device test case
# PROTECTED REGION ID(SKAAlarmHandler.test_SKAAlarmHandler_decorators) ENABLED START #
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION END #    //  SKAAlarmHandler.test_SKAAlarmHandler_decorators
class TestSKAAlarmHandler(object):
    """Test case for packet generation."""

    properties = {
        'SubAlarmHandlers': '',
        'AlarmConfigFile': '',
        'SkaLevel': '4',
        'GroupDefinitions': '',
        'CentralLoggingTarget': '',
        'ElementLoggingTarget': '',
        'StorageLoggingTarget': 'localhost',
        }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKAAlarmHandler.numpy = MagicMock()
        # PROTECTED REGION ID(SKAAlarmHandler.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_mocking

    def test_properties(self, tango_context):
        """Test the device properties"""
        # Test the properties
        # PROTECTED REGION ID(SKAAlarmHandler.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_properties

    # PROTECTED REGION ID(SKAAlarmHandler.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.UNKNOWN
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_State

    # PROTECTED REGION ID(SKAAlarmHandler.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in UNKNOWN state."
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_Status

    # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmRule_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmRule_decorators
    def test_GetAlarmRule(self, tango_context):
        """Test for GetAlarmRule"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmRule) ENABLED START #
        assert tango_context.device.GetAlarmRule("") == ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmRule

    # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmData_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmData_decorators
    def test_GetAlarmData(self, tango_context):
        """Test for GetAlarmData"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmData) ENABLED START #
        assert tango_context.device.GetAlarmData("") == ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmData

    # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmAdditionalInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmAdditionalInfo_decorators
    def test_GetAlarmAdditionalInfo(self, tango_context):
        """Test for GetAlarmAdditionalInfo"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmAdditionalInfo) ENABLED START #
        assert tango_context.device.GetAlarmAdditionalInfo("") == ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmAdditionalInfo

    # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmStats_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmStats_decorators
    def test_GetAlarmStats(self, tango_context):
        """Test for GetAlarmStats"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlarmStats) ENABLED START #
        assert tango_context.device.GetAlarmStats() == ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlarmStats

    # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlertStats_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlertStats_decorators
    def test_GetAlertStats(self, tango_context):
        """Test for GetAlertStats"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetAlertStats) ENABLED START #
        assert tango_context.device.GetAlertStats() == ""
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetAlertStats

    # PROTECTED REGION ID(SKAAlarmHandler.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_Reset_decorators
    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_Reset) ENABLED START #
        assert tango_context.device.Reset() is None
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_Reset

    # PROTECTED REGION ID(SKAAlarmHandler.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'SKAAlarmHandler, lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_GetVersionInfo


    # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrAlerts_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrAlerts_decorators
    def test_statsNrAlerts(self, tango_context):
        """Test for statsNrAlerts"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrAlerts) ENABLED START #
        assert tango_context.device.statsNrAlerts == 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrAlerts

    # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrAlarms_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrAlarms_decorators
    def test_statsNrAlarms(self, tango_context):
        """Test for statsNrAlarms"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrAlarms) ENABLED START #
        assert tango_context.device.statsNrAlarms == 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrAlarms

    # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrNewAlarms_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrNewAlarms_decorators
    def test_statsNrNewAlarms(self, tango_context):
        """Test for statsNrNewAlarms"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrNewAlarms) ENABLED START #
        assert tango_context.device.statsNrNewAlarms == 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrNewAlarms

    # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrUnackAlarms_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrUnackAlarms_decorators
    def test_statsNrUnackAlarms(self, tango_context):
        """Test for statsNrUnackAlarms"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrUnackAlarms) ENABLED START #
        assert tango_context.device.statsNrUnackAlarms == 0.0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrUnackAlarms

    # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrRtnAlarms_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrRtnAlarms_decorators
    def test_statsNrRtnAlarms(self, tango_context):
        """Test for statsNrRtnAlarms"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_statsNrRtnAlarms) ENABLED START #
        assert tango_context.device.statsNrRtnAlarms == 0.0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_statsNrRtnAlarms

    # PROTECTED REGION ID(SKAAlarmHandler.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_buildState

    # PROTECTED REGION ID(SKAAlarmHandler.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_versionId

    # PROTECTED REGION ID(SKAAlarmHandler.test_centralLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_centralLoggingLevel_decorators
    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_centralLoggingLevel) ENABLED START #
        assert tango_context.device.centralLoggingLevel == 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_centralLoggingLevel

    # PROTECTED REGION ID(SKAAlarmHandler.test_elementLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_elementLoggingLevel_decorators
    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_elementLoggingLevel) ENABLED START #
        assert tango_context.device.elementLoggingLevel == 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_elementLoggingLevel

    # PROTECTED REGION ID(SKAAlarmHandler.test_storageLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_storageLoggingLevel_decorators
    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_storageLoggingLevel) ENABLED START #
        assert tango_context.device.storageLoggingLevel == 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_storageLoggingLevel

    # PROTECTED REGION ID(SKAAlarmHandler.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_healthState

    # PROTECTED REGION ID(SKAAlarmHandler.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_adminMode

    # PROTECTED REGION ID(SKAAlarmHandler.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == 0
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_controlMode

    # PROTECTED REGION ID(SKAAlarmHandler.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode is False
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_simulationMode

    # PROTECTED REGION ID(SKAAlarmHandler.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_testMode) ENABLED START #
        assert tango_context.device.testMode == ''
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_testMode

    # PROTECTED REGION ID(SKAAlarmHandler.test_activeAlerts_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_activeAlerts_decorators
    def test_activeAlerts(self, tango_context):
        """Test for activeAlerts"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_activeAlerts) ENABLED START #
        assert tango_context.device.activeAlerts == ('',)
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_activeAlerts

    # PROTECTED REGION ID(SKAAlarmHandler.test_activeAlarms_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAAlarmHandler.test_activeAlarms_decorators
    def test_activeAlarms(self, tango_context):
        """Test for activeAlarms"""
        # PROTECTED REGION ID(SKAAlarmHandler.test_activeAlarms) ENABLED START #
        assert tango_context.device.activeAlarms == ('',)
        # PROTECTED REGION END #    //  SKAAlarmHandler.test_activeAlarms
