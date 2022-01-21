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

from ska_tango_base.testing.reference import (
    ReferenceBaseComponentManager,
)
from ska_tango_base.logger_device import SKALogger
from ska_tango_base.subarray import SKASubarray
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
# PROTECTED REGION END #    //  SKALogger.test_SKALogger_decorators
class TestSKALogger(object):
    """Test class for tests of the SKALogger device class."""

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Specification of the device under test.

        The specification includes the device's properties and memorized
        attributes.
        """
        return {
            "device": SKALogger,
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
        """Test device properties."""
        # PROTECTED REGION ID(SKALogger.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKALogger.test_properties
        pass

    # PROTECTED REGION ID(SKALogger.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_State_decorators
    def test_State(self, device_under_test):
        """Test for State."""
        # PROTECTED REGION ID(SKALogger.test_State) ENABLED START #
        assert device_under_test.state() == DevState.OFF
        # PROTECTED REGION END #    //  SKALogger.test_State

    # PROTECTED REGION ID(SKALogger.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_Status_decorators
    def test_Status(self, device_under_test):
        """Test for Status."""
        # PROTECTED REGION ID(SKALogger.test_Status) ENABLED START #
        assert device_under_test.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKALogger.test_Status

    # PROTECTED REGION ID(SKALogger.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test):
        """Test for GetVersionInfo."""
        # PROTECTED REGION ID(SKALogger.test_GetVersionInfo) ENABLED START #
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])
        # PROTECTED REGION END #    //  SKALogger.test_GetVersionInfo

    # PROTECTED REGION ID(SKALogger.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_buildState_decorators
    def test_buildState(self, device_under_test):
        """Test for buildState."""
        # PROTECTED REGION ID(SKALogger.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, device_under_test.buildState)) is not None
        # PROTECTED REGION END #    //  SKALogger.test_buildState

    # PROTECTED REGION ID(SKALogger.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_versionId_decorators
    def test_versionId(self, device_under_test):
        """Test for versionId."""
        # PROTECTED REGION ID(SKALogger.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  SKALogger.test_versionId

    # PROTECTED REGION ID(SKALogger.test_loggingLevel_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_loggingLevel_decorators
    def test_loggingLevel(self, device_under_test):
        """Test for loggingLevel."""
        # PROTECTED REGION ID(SKALogger.test_loggingLevel) ENABLED START #
        assert device_under_test.loggingLevel == LoggingLevel.INFO
        # PROTECTED REGION END #    //  SKALogger.test_loggingLevel

    # PROTECTED REGION ID(SKALogger.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_healthState_decorators
    def test_healthState(self, device_under_test):
        """Test for healthState."""
        # PROTECTED REGION ID(SKALogger.test_healthState) ENABLED START #
        assert device_under_test.healthState == HealthState.UNKNOWN
        # PROTECTED REGION END #    //  SKALogger.test_healthState

    # PROTECTED REGION ID(SKALogger.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_adminMode_decorators
    def test_adminMode(self, device_under_test):
        """Test for adminMode."""
        # PROTECTED REGION ID(SKALogger.test_adminMode) ENABLED START #
        assert device_under_test.adminMode == AdminMode.ONLINE
        # PROTECTED REGION END #    //  SKALogger.test_adminMode

    # PROTECTED REGION ID(SKALogger.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_controlMode_decorators
    def test_controlMode(self, device_under_test):
        """Test for controlMode."""
        # PROTECTED REGION ID(SKALogger.test_controlMode) ENABLED START #
        assert device_under_test.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKALogger.test_controlMode

    # PROTECTED REGION ID(SKALogger.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_simulationMode_decorators
    def test_simulationMode(self, device_under_test):
        """Test for simulationMode."""
        # PROTECTED REGION ID(SKALogger.test_simulationMode) ENABLED START #
        assert device_under_test.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKALogger.test_simulationMode

    # PROTECTED REGION ID(SKALogger.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKALogger.test_testMode_decorators
    def test_testMode(self, device_under_test):
        """Test for testMode."""
        # PROTECTED REGION ID(SKALogger.test_testMode) ENABLED START #
        assert device_under_test.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKALogger.test_testMode


@pytest.mark.forked
def test_SetLoggingLevel():
    """Test for SetLoggingLevel."""
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
