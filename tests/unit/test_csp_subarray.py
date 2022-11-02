# type: ignore
########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubelementSubarray project
#
#
#
########################################################################################
"""This module tests the :py:mod:``ska_tango_base.csp.subarray_device`` module."""
import json
import re

import pytest
import tango
from ska_control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    ObsState,
    SimulationMode,
    TestMode,
)

from ska_tango_base.commands import ResultCode
from ska_tango_base.csp import CspSubElementSubarray
from ska_tango_base.testing.reference import ReferenceCspSubarrayComponentManager

# Device test case


class TestCspSubElementSubarray:  # pylint: disable=too-many-public-methods
    """Test case for CSP SubElement Subarray class."""

    @pytest.fixture(scope="class")
    def device_properties(self):
        """
        Fixture that returns device properties of the device under test.

        :return: properties of the device under test
        """
        return {"CapabilityTypes": ["id"]}

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Return a specification of the device to be tested.

        The specification includes the device's properties and memorized
        attributes.

        This implementation provides a concrete subclass of the device
        class under test, some properties, and a memorized value for
        adminMode.

        :param device_properties: fixture that returns device properties
            of the device under test

        :return: specification of how the device under test should be
            configured
        """
        return {
            "device": CspSubElementSubarray,
            "component_manager_patch": (
                lambda self: ReferenceCspSubarrayComponentManager(
                    self.logger,
                    self._communication_state_changed,
                    self._component_state_changed,
                )
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip(reason="Not implemented")
    def test_properties(self, device_under_test):
        """
        Test the device properties.

        :param device_under_test: a proxy to the device under test
        """

    def test_State(self, device_under_test):
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.state() == tango.DevState.OFF

    def test_Status(self, device_under_test):
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.Status() == "The device is in OFF state."

    def test_GetVersionInfo(self, device_under_test):
        """
        Test for GetVersionInfo.

        :param device_under_test: a proxy to the device under test
        """
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])

    def test_buildState(self, device_under_test):
        """
        Test for buildState.

        :param device_under_test: a proxy to the device under test
        """
        build_pattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(build_pattern, device_under_test.buildState)) is not None

    def test_versionId(self, device_under_test):
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        version_id_pattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(version_id_pattern, device_under_test.versionId)) is not None

    def test_healthState(self, device_under_test):
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.healthState == HealthState.UNKNOWN

    def test_adminMode(self, device_under_test):
        """
        Test for adminMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.adminMode == AdminMode.ONLINE

    def test_controlMode(self, device_under_test):
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.controlMode == ControlMode.REMOTE

    def test_simulationMode(self, device_under_test):
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.simulationMode == SimulationMode.FALSE

    def test_testMode(self, device_under_test):
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.testMode == TestMode.NONE

    def test_scanID(self, device_under_test, change_event_callbacks):
        """
        Test for scanID.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        assert device_under_test.state() == tango.DevState.OFF

        device_under_test.subscribe_event(
            "state",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["state"],
        )
        change_event_callbacks.assert_change_event("state", tango.DevState.OFF)

        device_under_test.On()

        change_event_callbacks.assert_change_event("state", tango.DevState.ON)
        assert device_under_test.state() == tango.DevState.ON

        assert device_under_test.scanID == 0

    def test_sdpDestinationAddresses(self, device_under_test):
        """
        Test for sdpDestinationAddresses.

        :param device_under_test: a proxy to the device under test
        """
        addresses_dict = {"outputHost": [], "outputMac": [], "outputPort": []}
        device_under_test.sdpDestinationAddresses = json.dumps(addresses_dict)
        assert device_under_test.sdpDestinationAddresses == json.dumps(addresses_dict)

    def test_sdpLinkActivity(self, device_under_test):
        """
        Test for sdpLinkActive.

        :param device_under_test: a proxy to the device under test
        """
        actual = device_under_test.sdpLinkActive
        n_links = len(actual)
        expected = [False for i in range(0, n_links)]
        assert all(a == b for a, b in zip(actual, expected))

    def test_outputDataRateToSdp(self, device_under_test):
        """
        Test for outputDataRateToSdp.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.outputDataRateToSdp == 0

    def test_listOfDevicesCompletedTasks(self, device_under_test):
        """
        Test for listOfDevicesCompletedTasks.

        :param device_under_test: a proxy to the device under test
        """
        attr_value_as_dict = json.loads(device_under_test.listOfDevicesCompletedTasks)
        assert not bool(attr_value_as_dict)

    def test_assignResourcesMaximumDuration(self, device_under_test):
        """
        Test for assignResourcesMaximumDuration.

        :param device_under_test: a proxy to the device under test
        """
        device_under_test.assignResourcesMaximumDuration = 5
        assert device_under_test.assignResourcesMaximumDuration == 5

    def test_configureScanMeasuredDuration(self, device_under_test):
        """
        Test for configureScanMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.configureScanMeasuredDuration == 0

    def test_configurationProgress(self, device_under_test):
        """
        Test for configurationProgress.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.configurationProgress == 0

    def test_assignResourcesMeasuredDuration(self, device_under_test):
        """
        Test for assignResourcesMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.assignResourcesMeasuredDuration == 0

    def test_assignResourcesProgress(self, device_under_test):
        """
        Test for assignResourcesProgress.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.assignResourcesProgress == 0

    def test_releaseResourcesMaximumDuration(self, device_under_test):
        """
        Test for releaseResourcesMaximumDuration.

        :param device_under_test: a proxy to the device under test
        """
        device_under_test.releaseResourcesMaximumDuration = 5
        assert device_under_test.releaseResourcesMaximumDuration == 5

    def test_releaseResourcesMeasuredDuration(self, device_under_test):
        """
        Test for releaseResourcesMeasuredDuration.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.releaseResourcesMeasuredDuration == 0

    def test_releaseResourcesProgress(self, device_under_test):
        """
        Test for releaseResourcesProgress.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.releaseResourcesProgress == 0

    def test_configureScanTimeoutExpiredFlag(self, device_under_test):
        """
        Test for timeoutExpiredFlag.

        :param device_under_test: a proxy to the device under test
        """
        assert not device_under_test.configureScanTimeoutExpiredFlag

    def test_assignResourcesTimeoutExpiredFlag(self, device_under_test):
        """
        Test for timeoutExpiredFlag.

        :param device_under_test: a proxy to the device under test
        """
        assert not device_under_test.assignResourcesTimeoutExpiredFlag

    def test_releaseResourcesTimeoutExpiredFlag(self, device_under_test):
        """
        Test for timeoutExpiredFlag.

        :param device_under_test: a proxy to the device under test
        """
        assert not device_under_test.releaseResourcesTimeoutExpiredFlag

    # TODO: Pylint is right that this test is way too long.
    @pytest.mark.parametrize("command_alias", ["Configure", "ConfigureScan"])
    def test_ConfigureScan_and_GoToIdle(  # pylint: disable=too-many-statements
        self, device_under_test, change_event_callbacks, command_alias
    ):
        """
        Test for ConfigureScan.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        :param command_alias: name of the specific command being tested.
        """
        assert device_under_test.state() == tango.DevState.OFF

        for attribute in [
            "state",
            "status",
            "longRunningCommandProgress",
            "longRunningCommandStatus",
            "longRunningCommandResult",
        ]:
            device_under_test.subscribe_event(
                attribute,
                tango.EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(tango.DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandProgress"].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(None)
        change_event_callbacks["longRunningCommandResult"].assert_change_event(("", ""))

        [[result_code], [on_command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "QUEUED")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "IN_PROGRESS")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "66")
        )

        change_event_callbacks.assert_change_event("state", tango.DevState.ON)
        change_event_callbacks.assert_change_event(
            "status", "The device is in ON state."
        )

        assert device_under_test.state() == tango.DevState.ON

        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                on_command_id,
                json.dumps([int(ResultCode.OK), "On command completed OK"]),
            ),
        )

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "COMPLETED")
        )

        device_under_test.subscribe_event(
            "obsState",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["obsState"],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.EMPTY)

        [
            [result_code],
            [assign_command_id],
        ] = device_under_test.AssignResources(json.dumps([1, 2, 3]))

        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "QUEUED"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "IN_PROGRESS"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "66")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                assign_command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "COMPLETED"),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        # TODO: Everything above here is just to turn on the device, assign it some
        # resources, and clear the queue attributes. We need a better way to handle
        # this.
        assert device_under_test.configurationId == ""

        configuration_id = "sbi-mvp01-20200325-00002"
        [[result_code], [config_command_id]] = device_under_test.command_inout(
            command_alias, json.dumps({"id": configuration_id})
        )
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.CONFIGURING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "IN_PROGRESS",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (config_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (config_command_id, "66")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                config_command_id,
                json.dumps([int(ResultCode.OK), "Configure completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
            ),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.READY)

        assert device_under_test.configurationId == configuration_id
        assert device_under_test.lastScanConfiguration == json.dumps(
            {"id": configuration_id}
        )

        # test deconfigure
        [[result_code], [gotoidle_command_id]] = device_under_test.GoToIdle()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                gotoidle_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                gotoidle_command_id,
                "IN_PROGRESS",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (gotoidle_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (gotoidle_command_id, "66")
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                gotoidle_command_id,
                json.dumps([int(ResultCode.OK), "Deconfigure completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                assign_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                gotoidle_command_id,
                "COMPLETED",
            ),
        )

        assert device_under_test.configurationID == ""
        assert device_under_test.lastScanConfiguration == ""

    def test_ConfigureScan_when_in_wrong_state(self, device_under_test):
        """
        Test for ConfigureScan when the device is in wrong state.

        :param device_under_test: a proxy to the device under test
        """
        # The device in in OFF/EMPTY state, not valid to invoke ConfigureScan.
        with pytest.raises(
            tango.DevFailed,
            match="ConfigureScan command not permitted in observation state EMPTY",
        ):
            device_under_test.ConfigureScan(
                '{"id":"sbi-mvp01-20200325-00002"}'  # noqa: FS003
            )

    def test_ConfigureScan_with_wrong_configId_key(
        self, device_under_test, change_event_callbacks
    ):
        """
        Test that ConfigureScan handles a wrong configuration id key.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        assert device_under_test.state() == tango.DevState.OFF

        for attribute in [
            "state",
            "status",
            "longRunningCommandProgress",
            "longRunningCommandStatus",
            "longRunningCommandResult",
        ]:
            device_under_test.subscribe_event(
                attribute,
                tango.EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(tango.DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandProgress"].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(None)
        change_event_callbacks["longRunningCommandResult"].assert_change_event(("", ""))

        [[result_code], [on_command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "QUEUED")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "IN_PROGRESS")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "66")
        )

        change_event_callbacks.assert_change_event("state", tango.DevState.ON)
        change_event_callbacks.assert_change_event(
            "status", "The device is in ON state."
        )

        assert device_under_test.state() == tango.DevState.ON

        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                on_command_id,
                json.dumps([int(ResultCode.OK), "On command completed OK"]),
            ),
        )

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "COMPLETED")
        )

        device_under_test.subscribe_event(
            "obsState",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["obsState"],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.EMPTY)

        [
            [result_code],
            [assign_command_id],
        ] = device_under_test.AssignResources(json.dumps([1, 2, 3]))

        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "QUEUED"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "IN_PROGRESS"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "66")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                assign_command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "COMPLETED"),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        wrong_configuration = '{"subid":"sbi-mvp01-20200325-00002"}'  # noqa: FS003
        result_code, _ = device_under_test.ConfigureScan(wrong_configuration)
        assert result_code == ResultCode.FAILED
        assert device_under_test.obsState == ObsState.IDLE

    def test_ConfigureScan_with_json_syntax_error(
        self, device_under_test, change_event_callbacks
    ):
        """
        Test for ConfigureScan when syntax error in json configuration.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        assert device_under_test.state() == tango.DevState.OFF

        for attribute in [
            "state",
            "status",
            "longRunningCommandProgress",
            "longRunningCommandStatus",
            "longRunningCommandResult",
        ]:
            device_under_test.subscribe_event(
                attribute,
                tango.EventType.CHANGE_EVENT,
                change_event_callbacks[attribute],
            )

        change_event_callbacks["state"].assert_change_event(tango.DevState.OFF)
        change_event_callbacks["status"].assert_change_event(
            "The device is in OFF state."
        )
        change_event_callbacks["longRunningCommandProgress"].assert_change_event(None)
        change_event_callbacks["longRunningCommandStatus"].assert_change_event(None)
        change_event_callbacks["longRunningCommandResult"].assert_change_event(("", ""))

        [[result_code], [on_command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "QUEUED")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "IN_PROGRESS")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (on_command_id, "66")
        )

        change_event_callbacks.assert_change_event("state", tango.DevState.ON)
        change_event_callbacks.assert_change_event(
            "status", "The device is in ON state."
        )

        assert device_under_test.state() == tango.DevState.ON

        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                on_command_id,
                json.dumps([int(ResultCode.OK), "On command completed OK"]),
            ),
        )

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus", (on_command_id, "COMPLETED")
        )

        device_under_test.subscribe_event(
            "obsState",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["obsState"],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.EMPTY)

        [
            [result_code],
            [assign_command_id],
        ] = device_under_test.AssignResources(json.dumps([1, 2, 3]))

        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.RESOURCING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "QUEUED"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "IN_PROGRESS"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "33")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandProgress", (assign_command_id, "66")
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                assign_command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", assign_command_id, "COMPLETED"),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        result_code, _ = device_under_test.ConfigureScan('{"foo": 1,}')  # noqa: FS003
        assert result_code == ResultCode.FAILED
        assert device_under_test.obsState == ObsState.IDLE
