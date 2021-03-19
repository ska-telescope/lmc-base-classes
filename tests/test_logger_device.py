#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKALogger project
#
#
#
#########################################################################################
"""Contain the tests for the SKALogger."""

import re
import pytest
from tango import DevState
from tango.test_context import MultiDeviceTestContext
from ska_tango_base.logger_device import SKALogger
from ska_tango_base.subarray_device import SKASubarray
import tango

# PROTECTED REGION ID(SKALogger.test_additional_imports) ENABLED START #
from ska_tango_base.control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    LoggingLevel,
    SimulationMode,
    TestMode,
)

# PROTECTED REGION END #    //  SKALogger.test_additional_imports


# PROTECTED REGION ID(SKALogger.test_SKALogger_decorators) ENABLED START #
@pytest.mark.usefixtures("tango_context", "initialize_device")
# PROTECTED REGION END #    //  SKALogger.test_SKALogger_decorators
class TestSKALogger(object):
    """Test case for packet generation."""

    properties = {
        "SkaLevel": "1",
        "GroupDefinitions": "",
    }

    @classmethod
    def mocking(cls):
        """Mock external libraries."""
        # Example : Mock numpy
        # cls.numpy = SKALogger.numpy = MagicMock()
        # PROTECTED REGION ID(SKALogger.test_mocking) ENABLED START #
        # PROTECTED REGION END #    //  SKALogger.test_mocking

    def test_properties(self, tango_context):
        # test the properties
        # PROTECTED REGION ID(SKALogger.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKALogger.test_properties
        pass

    # PROTECTED REGION ID(SKALogger.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_State_decorators
    def test_State(self, tango_context):
        """Test for State"""
        # PROTECTED REGION ID(SKALogger.test_State) ENABLED START #
        assert tango_context.device.State() == DevState.OFF
        # PROTECTED REGION END #    //  SKALogger.test_State

    # PROTECTED REGION ID(SKALogger.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_Status_decorators
    def test_Status(self, tango_context):
        """Test for Status"""
        # PROTECTED REGION ID(SKALogger.test_Status) ENABLED START #
        assert tango_context.device.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKALogger.test_Status

    # PROTECTED REGION ID(SKALogger.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, tango_context):
        """Test for GetVersionInfo"""
        # PROTECTED REGION ID(SKALogger.test_GetVersionInfo) ENABLED START #
        versionPattern = re.compile(
            r"SKALogger, ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope."
        )
        versionInfo = tango_context.device.GetVersionInfo()
        assert (re.match(versionPattern, versionInfo[0])) is not None
        # PROTECTED REGION END #    //  SKALogger.test_GetVersionInfo

    # PROTECTED REGION ID(SKALogger.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_buildState_decorators
    def test_buildState(self, tango_context):
        """Test for buildState"""
        # PROTECTED REGION ID(SKALogger.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, tango_context.device.buildState)) is not None
        # PROTECTED REGION END #    //  SKALogger.test_buildState

    # PROTECTED REGION ID(SKALogger.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_versionId_decorators
    def test_versionId(self, tango_context):
        """Test for versionId"""
        # PROTECTED REGION ID(SKALogger.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, tango_context.device.versionId)) is not None
        # PROTECTED REGION END #    //  SKALogger.test_versionId

    # PROTECTED REGION ID(SKALogger.test_loggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_loggingLevel_decorators
    def test_loggingLevel(self, tango_context):
        """Test for loggingLevel"""
        # PROTECTED REGION ID(SKALogger.test_loggingLevel) ENABLED START #
        assert tango_context.device.loggingLevel == LoggingLevel.INFO
        # PROTECTED REGION END #    //  SKALogger.test_loggingLevel

    # PROTECTED REGION ID(SKALogger.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_healthState_decorators
    def test_healthState(self, tango_context):
        """Test for healthState"""
        # PROTECTED REGION ID(SKALogger.test_healthState) ENABLED START #
        assert tango_context.device.healthState == HealthState.OK
        # PROTECTED REGION END #    //  SKALogger.test_healthState

    # PROTECTED REGION ID(SKALogger.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_adminMode_decorators
    def test_adminMode(self, tango_context):
        """Test for adminMode"""
        # PROTECTED REGION ID(SKALogger.test_adminMode) ENABLED START #
        assert tango_context.device.adminMode == AdminMode.MAINTENANCE
        # PROTECTED REGION END #    //  SKALogger.test_adminMode

    # PROTECTED REGION ID(SKALogger.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_controlMode_decorators
    def test_controlMode(self, tango_context):
        """Test for controlMode"""
        # PROTECTED REGION ID(SKALogger.test_controlMode) ENABLED START #
        assert tango_context.device.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKALogger.test_controlMode

    # PROTECTED REGION ID(SKALogger.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_simulationMode_decorators
    def test_simulationMode(self, tango_context):
        """Test for simulationMode"""
        # PROTECTED REGION ID(SKALogger.test_simulationMode) ENABLED START #
        assert tango_context.device.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKALogger.test_simulationMode

    # PROTECTED REGION ID(SKALogger.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_testMode_decorators
    def test_testMode(self, tango_context):
        """Test for testMode"""
        # PROTECTED REGION ID(SKALogger.test_testMode) ENABLED START #
        assert tango_context.device.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKALogger.test_testMode


def test_SetLoggingLevel():
    """Test for SetLoggingLevel"""
    logging_level = int(tango.LogLevel.LOG_ERROR)
    logging_target = "logger/target/1"
    logger_device = "logger/device/1"
    devices_info = (
        {"class": SKALogger, "devices": [{"name": logger_device}]},
        {"class": SKASubarray, "devices": [{"name": logging_target}]},
    )

    with MultiDeviceTestContext(devices_info, process=False) as multi_context:
        dev_proxy = multi_context.get_device(logging_target)
        dev_proxy.Init()
        dev_proxy.loggingLevel = int(tango.LogLevel.LOG_FATAL)
        assert dev_proxy.loggingLevel != logging_level

        levels = []
        levels.append(logging_level)
        targets = []
        targets.append(multi_context.get_device_access(logging_target))
        device_details = []
        device_details.append(levels)
        device_details.append(targets)
        multi_context.get_device(logger_device).SetLoggingLevel(device_details)
        assert dev_proxy.loggingLevel == logging_level
