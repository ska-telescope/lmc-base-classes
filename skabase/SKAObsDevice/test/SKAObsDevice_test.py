#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKAObsDevice project
#
#
#
#########################################################################################
"""Contain the tests for the SKAObsDevice."""

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

# PROTECTED REGION ID(SKAObsDevice.test_additional_imports) ENABLED START #
# PROTECTED REGION END #    //  SKAObsDevice.test_additional_imports
# Device test case
# PROTECTED REGION ID(SKAObsDevice.test_SKAObsDevice_decorators) ENABLED START #
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION END #    //  SKAObsDevice.test_SKAObsDevice_decorators
class TestSKAObsDevice(object):
    """Test case for packet generation."""

    properties = {
        'SkaLevel': '4',
        'LoggingTargetsDefault': ['console::cout'],
        'GroupDefinitions': '',
        }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKAObsDevice.numpy = MagicMock()
        # PROTECTED REGION ID(SKAObsDevice.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKAObsDevice.test_mocking

    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(SKAObsDevice.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKAObsDevice.test_properties
        pass

    # PROTECTED REGION ID(SKAObsDevice.test_ObsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_ObsState_decorators
    def test_ObsState(self, tango_context):
        """Test for ObsState"""
        # PROTECTED REGION ID(SKAObsDevice.test_ObsState) ENABLED START #
        assert tango_context.device.ObsState == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_ObsState

    # PROTECTED REGION ID(SKAObsDevice.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKAObsDevice.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.UNKNOWN
        # PROTECTED REGION END #    //  SKAObsDevice.test_State

    # PROTECTED REGION ID(SKAObsDevice.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKAObsDevice.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in UNKNOWN state."
        # PROTECTED REGION END #    //  SKAObsDevice.test_Status

    # PROTECTED REGION ID(SKAObsDevice.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKAObsDevice.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'SKAObsDevice, lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  SKAObsDevice.test_GetVersionInfo

    # PROTECTED REGION ID(SKAObsDevice.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_Reset_decorators
    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SKAObsDevice.test_Reset) ENABLED START #
        assert tango_context.device.Reset() is None
        # PROTECTED REGION END #    //  SKAObsDevice.test_Reset

    # PROTECTED REGION ID(SKAObsDevice.test_obsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_obsState_decorators
    def test_obsState(self, tango_context):
        """Test for obsState"""
        # PROTECTED REGION ID(SKAObsDevice.test_obsState) ENABLED START #
        assert tango_context.device.obsState == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_obsState

    # PROTECTED REGION ID(SKAObsDevice.test_obsMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_obsMode_decorators
    def test_obsMode(self, tango_context):
        """Test for obsMode"""
        # PROTECTED REGION ID(SKAObsDevice.test_obsMode) ENABLED START #
        assert tango_context.device.obsMode == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_obsMode

    # PROTECTED REGION ID(SKAObsDevice.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_configurationProgress_decorators
    def test_configurationProgress(self, tango_context):
        """Test for configurationProgress"""
        # PROTECTED REGION ID(SKAObsDevice.test_configurationProgress) ENABLED START #
        assert tango_context.device.configurationProgress == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_configurationProgress

    # PROTECTED REGION ID(SKAObsDevice.test_configurationDelayExpected_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_configurationDelayExpected_decorators
    def test_configurationDelayExpected(self, tango_context):
        """Test for configurationDelayExpected"""
        # PROTECTED REGION ID(SKAObsDevice.test_configurationDelayExpected) ENABLED START #
        assert tango_context.device.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_configurationDelayExpected

    # PROTECTED REGION ID(SKAObsDevice.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKAObsDevice.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) != None
        # PROTECTED REGION END #    //  SKAObsDevice.test_buildState

    # PROTECTED REGION ID(SKAObsDevice.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKAObsDevice.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) != None
        # PROTECTED REGION END #    //  SKAObsDevice.test_versionId

    # PROTECTED REGION ID(SKABaseDevice.test_loggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_loggingLevel_decorators
    def test_loggingLevel(self, tango_context):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(SKABaseDevice.test_loggingLevel) ENABLED START #
        assert tango_context.device.loggingLevel == TangoLoggingLevel.INFO

        for level in TangoLoggingLevel:
            tango_context.device.loggingLevel = level
            assert tango_context.device.loggingLevel == level

        with pytest.raises(DevFailed):
            tango_context.device.loggingLevel = TangoLoggingLevel.FATAL + 100
        # PROTECTED REGION END #    //  SKABaseDevice.test_loggingLevel

    # PROTECTED REGION ID(SKABaseDevice.test_loggingTargets_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_loggingTargets_decorators
    def test_loggingTargets(self, tango_context):
        """Test for loggingTargets"""
        # PROTECTED REGION ID(SKABaseDevice.test_loggingTargets) ENABLED START #
        assert tango_context.device.loggingTargets == ("console::cout",)

        with mock.patch("SKABaseDevice._create_logging_handler") as mocked_creator:
            mocked_creator.return_value = logging.NullHandler()
            device_fqdn = tango_context.get_device_access()
            tango_context.device.loggingTargets = [
                "console::cout", "file::/tmp/dummy", "syslog::some/address"]
            assert tango_context.device.loggingTargets == (
                "console::cout", "file::/tmp/dummy", "syslog::some/address")
            # the console handler was already present, so only the new targets
            # are expected
            mocked_creator.call_count == 2
            mocked_creator.assert_has_calls(
                [mock.call("file::/tmp/dummy", device_fqdn),
                 mock.call("syslog::some/address", device_fqdn)],
                any_order=True)

            # test console still works without name, defaulting to "cout"
            mocked_creator.reset_mock()
            tango_context.device.loggingTargets = ["console"]
            assert tango_context.device.loggingTargets == ("console::cout", )
            mocked_creator.assert_not_called()

            # test file still works without name, defaulting to <device name>.log
            mocked_creator.reset_mock()
            tango_context.device.loggingTargets = ["file"]
            expected_file = "file::{}.log".format(device_fqdn.replace('/', '_'))
            assert tango_context.device.loggingTargets == (expected_file, )
            mocked_creator.assert_called_with(expected_file, device_fqdn)

            mocked_creator.reset_mock()
            with pytest.raises(DevFailed):
                tango_context.device.loggingTargets = ["invalid::type"]
            mocked_creator.assert_not_called()
            # test missing target name for syslog fails
            with pytest.raises(DevFailed):
                tango_context.device.loggingTargets = ["syslog"]
            mocked_creator.assert_not_called()
        # PROTECTED REGION END #    //  SKABaseDevice.test_loggingTargets

    # PROTECTED REGION ID(SKAObsDevice.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKAObsDevice.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_healthState

    # PROTECTED REGION ID(SKAObsDevice.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKAObsDevice.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_adminMode

    # PROTECTED REGION ID(SKAObsDevice.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKAObsDevice.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == 0
        # PROTECTED REGION END #    //  SKAObsDevice.test_controlMode

    # PROTECTED REGION ID(SKAObsDevice.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKAObsDevice.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode is False
        # PROTECTED REGION END #    //  SKAObsDevice.test_simulationMode

    # PROTECTED REGION ID(SKAObsDevice.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKAObsDevice.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKAObsDevice.test_testMode) ENABLED START #
        assert tango_context.device.testMode == ''
        # PROTECTED REGION END #    //  SKAObsDevice.test_testMode
