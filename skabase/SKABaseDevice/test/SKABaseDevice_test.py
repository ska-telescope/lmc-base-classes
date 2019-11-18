#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#
#########################################################################################
"""Contain the tests for the SKABASE."""

# Standard imports
import sys
import os
import re
import pytest
from tango import DevState

# Imports
from skabase.SKABaseDevice import SKABaseDevice
# PROTECTED REGION ID(SKABaseDevice.test_additional_imports) ENABLED START #
# PROTECTED REGION END #    //  SKABaseDevice.test_additional_imports

# Path
path = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, os.path.abspath(path))

# PROTECTED REGION ID(SKABaseDevice.test_additional_imports) ENABLED START #
# PROTECTED REGION END #    //  SKABaseDevice.test_additional_imports
# Device test case
# PROTECTED REGION ID(SKABaseDevice.test_SKABaseDevice_decorators) ENABLED START #
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION END #    //  SKABaseDevice.test_SKABaseDevice_decorators
class TestSKABaseDevice(object):
    """Test case for packet generation."""

    properties = {
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
        # cls.numpy = SKABaseDevice.numpy = MagicMock()
        # PROTECTED REGION ID(SKABaseDevice.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKABaseDevice.test_mocking

    def test_properties(self, tango_context):
        # Test the properties
        # PROTECTED REGION ID(SKABaseDevice.test_properties) ENABLED START #
        """
        Test device properties.

        :param tango_context: Object
            Tango device object

        :return: None
        """
        # PROTECTED REGION END #    //  SKABaseDevice.test_properties
        # pass

    # PROTECTED REGION ID(SKABaseDevice.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKABaseDevice.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.UNKNOWN
        # PROTECTED REGION END #    //  SKABaseDevice.test_State

    # PROTECTED REGION ID(SKABaseDevice.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKABaseDevice.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in UNKNOWN state."
        # PROTECTED REGION END #    //  SKABaseDevice.test_Status

    # PROTECTED REGION ID(SKABaseDevice.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKABaseDevice.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r'SKABaseDevice, lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope.')
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  SKABaseDevice.test_GetVersionInfo

    # PROTECTED REGION ID(SKABaseDevice.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_Reset_decorators
    def test_Reset(self, tango_context):
        """Test for Reset"""
        # PROTECTED REGION ID(SKABaseDevice.test_Reset) ENABLED START #
        assert tango_context.device.Reset() is None
        # PROTECTED REGION END #    //  SKABaseDevice.test_Reset


    # PROTECTED REGION ID(SKABaseDevice.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKABaseDevice.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r'lmcbaseclasses, [0-9].[0-9].[0-9], '
            r'A set of generic base devices for SKA Telescope')
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  SKABaseDevice.test_buildState

    # PROTECTED REGION ID(SKABaseDevice.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKABaseDevice.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r'[0-9].[0-9].[0-9]')
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  SKABaseDevice.test_versionId

    # PROTECTED REGION ID(SKABaseDevice.test_centralLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_centralLoggingLevel_decorators
    def test_centralLoggingLevel(self, tango_context):
        """Test for centralLoggingLevel"""
        # PROTECTED REGION ID(SKABaseDevice.test_centralLoggingLevel) ENABLED START #
        assert tango_context.device.centralLoggingLevel == 0
        # PROTECTED REGION END #    //  SKABaseDevice.test_centralLoggingLevel

    # PROTECTED REGION ID(SKABaseDevice.test_elementLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_elementLoggingLevel_decorators
    def test_elementLoggingLevel(self, tango_context):
        """Test for elementLoggingLevel"""
        # PROTECTED REGION ID(SKABaseDevice.test_elementLoggingLevel) ENABLED START #
        assert tango_context.device.elementLoggingLevel == 0
        # PROTECTED REGION END #    //  SKABaseDevice.test_elementLoggingLevel

    # PROTECTED REGION ID(SKABaseDevice.test_storageLoggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_storageLoggingLevel_decorators
    def test_storageLoggingLevel(self, tango_context):
        """Test for storageLoggingLevel"""
        # PROTECTED REGION ID(SKABaseDevice.test_storageLoggingLevel) ENABLED START #
        assert tango_context.device.storageLoggingLevel == 0
        # PROTECTED REGION END #    //  SKABaseDevice.test_storageLoggingLevel

    # PROTECTED REGION ID(SKABaseDevice.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKABaseDevice.test_healthState) ENABLED START #
        assert tango_context.device.healthState == 0
        # PROTECTED REGION END #    //  SKABaseDevice.test_healthState

    # PROTECTED REGION ID(SKABaseDevice.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == 0
        # PROTECTED REGION END #    //  SKABaseDevice.test_adminMode

    # PROTECTED REGION ID(SKABaseDevice.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == 0
        # PROTECTED REGION END #    //  SKABaseDevice.test_controlMode

    # PROTECTED REGION ID(SKABaseDevice.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode is False
        # PROTECTED REGION END #    //  SKABaseDevice.test_simulationMode

    # PROTECTED REGION ID(SKABaseDevice.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKABaseDevice.test_testMode) ENABLED START #
        assert tango_context.device.testMode == ''
        # PROTECTED REGION END #    //  SKABaseDevice.test_testMode

    # TODO: Fix this test case when "Error in get_name() of tango.DeviceImpl while using pytest" is resolved.
    # def test_get_device_commands(self, tango_context):
        # Test the get_device_commands method
        # commands = SKABaseDevice.get_device_commands(SKABaseDevice)
        #assert commands == [{'parameters': [], 'name': 'GetVersionInfo', 'component_type': 'nodb', 'component_id': 'skabasedevice'}, {'parameters': [], 'name': 'Init', 'component_type': 'nodb', 'component_id': 'skabasedevice'}, {'parameters': [], 'name': 'Reset', 'component_type': 'nodb', 'component_id': 'skabasedevice'}, {'parameters': [], 'name': 'State', 'component_type': 'nodb', 'component_id': 'skabasedevice'}, {'parameters': [], 'name': 'Status', 'component_type': 'nodb', 'component_id': 'skabasedevice'}]

    # TODO: Fix this test case when "Error in get_name() of tango.DeviceImpl while using pytest" is resolved.
    # def test_get_device_attributes(self, tango_context):
    #     # Test the get_device_attributes method
    #     attributes = SKABaseDevice.get_device_attributes(SKABaseDevice)
    #     assert attributes == 1

    def test__parse_argin(self, tango_context):
        SKABaseDevice._init_logging(SKABaseDevice)
        result = SKABaseDevice._parse_argin(SKABaseDevice,'{"class":"SKABaseDevice"}')
        assert result == {'class': 'SKABaseDevice'}

    def test__parse_argin_with_required(self, tango_context):
        SKABaseDevice._init_logging(SKABaseDevice)
        with pytest.raises(Exception):
             SKABaseDevice._parse_argin(SKABaseDevice,'{"class":"SKABaseDevice"}', required='class')

    # TODO: Fix this test case when "__DeviceImpl__debug_stream() missing 'msg' argument" is resolved.
    # def test_dev_logging(self, tango_context):
    #     SKABaseDevice._central_logging_level = int(tango.LogLevel.LOG_DEBUG)
    #     SKABaseDevice._element_logging_level = int(tango.LogLevel.LOG_DEBUG)
    #     SKABaseDevice._storage_logging_level = int(tango.LogLevel.LOG_DEBUG)
    #     result = SKABaseDevice.dev_logging(SKABaseDevice, "test message", int(tango.LogLevel.LOG_DEBUG))
    #     result = []
    #     SKABaseDevice.error_stream(SKABaseDevice, "Syslog cannot be initialized")
    #     assert result == None