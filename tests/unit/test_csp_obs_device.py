# type: ignore
# pylint: skip-file  # TODO: Incrementally lint this repo
########################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubelementObsDevice project
#
########################################################################
"""This module contains the tests for the CspSubelementObsDevice."""
import json
import re

import pytest
import tango
from ska_control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    ObsState,
    ResultCode,
    SimulationMode,
    TestMode,
)
from tango.test_context import MultiDeviceTestContext

from ska_tango_base import CspSubElementObsDevice, SKAObsDevice
from ska_tango_base.csp import CspSubElementObsStateModel
from ska_tango_base.testing.reference import (
    FakeBaseComponent,
    ReferenceCspObsComponentManager,
)


@pytest.fixture
def csp_subelement_obsdevice_state_model(logger):
    """
    Return a new CspSubElementObsDevice StateModel for testing.

    :param logger: fixture that returns a logger

    :return: a new CspSubElementObsDevice StateModel for testing.
    """
    return CspSubElementObsStateModel(logger)


class TestCspSubElementObsDevice:
    """Test case for CSP SubElement ObsDevice class."""

    @pytest.fixture(scope="class")
    def device_properties(self):
        """
        Fixture that returns properties of the device under test.

        :return: properties of the device under test
        """
        return {"DeviceID": "11"}

    @pytest.fixture(scope="class")
    def device_test_config(self, device_properties):
        """
        Specify device configuration, including properties and memorized attributes.

        This implementation provides a concrete subclass of the device
        class under test, some properties, and a memorized value for
        adminMode.

        :param device_properties: fixture that returns device properties
            of the device under test

        :return: specification of how the device under test should be
            configured
        """
        return {
            "device": CspSubElementObsDevice,
            "component_manager_patch": lambda self: ReferenceCspObsComponentManager(
                self.logger,
                self._communication_state_changed,
                self._component_state_changed,
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

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

    def test_deviceID(self, device_under_test, device_properties):
        """
        Test for deviceID.

        :param device_under_test: a proxy to the device under test
        :param device_properties: fixture that returns device properties
            of the device under test
        """
        assert device_under_test.deviceID == int(device_properties["DeviceID"])

    def test_sdpDestinationAddresses(self, device_under_test):
        """
        Test for sdpDestinationAddresses.

        :param device_under_test: a proxy to the device under test
        """
        addresses_dict = {"outputHost": [], "outputMac": [], "outputPort": []}
        assert device_under_test.sdpDestinationAddresses == json.dumps(addresses_dict)

    def test_sdpLinkActivity(self, device_under_test):
        """
        Test for sdpLinkActive.

        :param device_under_test: a proxy to the device under test
        """
        actual = device_under_test.sdpLinkActive
        n_links = len(actual)
        expected = [False for i in range(0, n_links)]
        assert all([a == b for a, b in zip(actual, expected)])

    def test_sdpLinkCapacity(self, device_under_test):
        """
        Test for sdpLinkCapacity.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.sdpLinkCapacity == 0

    def test_healthFailureMessage(self, device_under_test):
        """
        Test for healthFailureMessage.

        :param device_under_test: a proxy to the device under test
        """
        assert device_under_test.healthFailureMessage == ""

    def test_ConfigureScan_and_GoToIdle(
        self, device_under_test, change_event_callbacks
    ):
        """
        Test for ConfigureScan.

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
        for progress_point in FakeBaseComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (on_command_id, progress_point)
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
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        # TODO: Everything above here is just to turn on the device and clear the queue
        # attributes. We need a better way to handle this.

        assert device_under_test.configurationId == ""

        config_id = "sbi-mvp01-20200325-00002"

        [[result_code], [config_command_id]] = device_under_test.ConfigureScan(
            json.dumps({"id": config_id})
        )
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.CONFIGURING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", config_command_id, "QUEUED"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", config_command_id, "IN_PROGRESS"),
        )
        for progress_point in FakeBaseComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (config_command_id, progress_point)
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
            (on_command_id, "COMPLETED", config_command_id, "COMPLETED"),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.READY)

        assert device_under_test.configurationId == config_id

        # test deconfigure
        [[result_code], [gotoidle_command_id]] = device_under_test.GoToIdle()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
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
                config_command_id,
                "COMPLETED",
                gotoidle_command_id,
                "IN_PROGRESS",
            ),
        )
        for progress_point in FakeBaseComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (gotoidle_command_id, progress_point)
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
                config_command_id,
                "COMPLETED",
                gotoidle_command_id,
                "COMPLETED",
            ),
        )

        assert device_under_test.configurationId == ""

    def test_ConfigureScan_when_in_wrong_state(self, device_under_test):
        """
        Test for ConfigureScan when the device is in wrong state.

        :param device_under_test: a proxy to the device under test
        """
        # The device in in OFF/IDLE state, not valid to invoke ConfigureScan.

        with pytest.raises(tango.DevFailed, match="Component is not powered ON"):
            device_under_test.ConfigureScan(
                '{"id":"sbi-mvp01-20200325-00002"}'  # noqa: FS003
            )

    def test_ConfigureScan_with_wrong_input_args(self, device_under_test):
        """
        Test ConfigureScan's handling of wrong input arguments.

        Specifically, test when input argument specifies a wrong json
        configuration and the device is in IDLE state.

        :param device_under_test: a proxy to the device under test
        """
        device_under_test.On()
        # wrong configurationID key
        assert device_under_test.obsState == ObsState.IDLE

        wrong_configuration = '{"subid":"sbi-mvp01-20200325-00002"}'  # noqa: FS003
        (result_code, _) = device_under_test.ConfigureScan(wrong_configuration)
        assert result_code == ResultCode.FAILED
        assert device_under_test.obsState == ObsState.IDLE

    def test_ConfigureScan_with_json_syntax_error(self, device_under_test):
        """
        Test for ConfigureScan when syntax error in json configuration.

        :param device_under_test: a proxy to the device under test
        """
        device_under_test.On()
        assert device_under_test.obsState == ObsState.IDLE

        (result_code, _) = device_under_test.ConfigureScan('{"foo": 1,}')  # noqa: FS003
        assert result_code == ResultCode.FAILED
        assert device_under_test.obsState == ObsState.IDLE

    def test_GoToIdle_when_in_wrong_state(self, device_under_test):
        """
        Test for GoToIdle when the device is in wrong state.

        :param device_under_test: a proxy to the device under test
        """
        # The device in in OFF/IDLE state, not valid to invoke GoToIdle.
        with pytest.raises(
            tango.DevFailed,
            match="GoToIdle command not permitted in observation state IDLE",
        ):
            device_under_test.GoToIdle()

    def test_Scan_and_EndScan(self, device_under_test, change_event_callbacks):
        """
        Test for Scan.

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
        for progress_point in FakeBaseComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (on_command_id, progress_point)
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
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        assert device_under_test.scanId == 0

        config_id = "sbi-mvp01-20200325-00002"

        [[result_code], [config_command_id]] = device_under_test.ConfigureScan(
            json.dumps({"id": config_id})
        )
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.CONFIGURING)

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", config_command_id, "QUEUED"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", config_command_id, "IN_PROGRESS"),
        )
        for progress_point in FakeBaseComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (config_command_id, progress_point)
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
            (on_command_id, "COMPLETED", config_command_id, "COMPLETED"),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.READY)

        assert device_under_test.configurationId == config_id

        # TODO: Everything above here is just to turn on the device, configure it, and
        # clear the queue attributes. We need a better way to handle this.

        scan_id = 1
        [[result_code], [scan_command_id]] = device_under_test.Scan(str(scan_id))
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                scan_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                scan_command_id,
                "IN_PROGRESS",
            ),
        )

        for progress_point in FakeBaseComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (scan_command_id, progress_point)
            )
        change_event_callbacks.assert_change_event("obsState", ObsState.SCANNING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                scan_command_id,
                json.dumps([int(ResultCode.OK), "Scan commencement completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                scan_command_id,
                "COMPLETED",
            ),
        )

        assert device_under_test.scanId == scan_id

        # test end_scan
        [[result_code], [endscan_command_id]] = device_under_test.EndScan()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                scan_command_id,
                "COMPLETED",
                endscan_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                scan_command_id,
                "COMPLETED",
                endscan_command_id,
                "IN_PROGRESS",
            ),
        )
        for progress_point in FakeBaseComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (endscan_command_id, progress_point)
            )
        change_event_callbacks.assert_change_event("obsState", ObsState.READY)
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                endscan_command_id,
                json.dumps([int(ResultCode.OK), "End scan completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                config_command_id,
                "COMPLETED",
                scan_command_id,
                "COMPLETED",
                endscan_command_id,
                "COMPLETED",
            ),
        )

        assert device_under_test.scanId == 0

    def test_Scan_when_in_wrong_state(self, device_under_test, change_event_callbacks):
        """
        Test for Scan when the device is in wrong state.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        # Set the device in ON/IDLE state
        assert device_under_test.state() == tango.DevState.OFF

        device_under_test.subscribe_event(
            "state",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["state"],
        )
        change_event_callbacks.assert_change_event("state", tango.DevState.OFF)

        [[result_code], [_]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("state", tango.DevState.ON)

        with pytest.raises(
            tango.DevFailed,
            match="Scan command not permitted in observation state IDLE",
        ):
            device_under_test.Scan("32")

    def test_Scan_with_wrong_argument(self, device_under_test, change_event_callbacks):
        """
        Test for Scan when a wrong input argument is passed.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        # Set the device in ON/IDLE state
        assert device_under_test.state() == tango.DevState.OFF

        device_under_test.subscribe_event(
            "state",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["state"],
        )
        change_event_callbacks.assert_change_event("state", tango.DevState.OFF)

        [[result_code], [_]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("state", tango.DevState.ON)

        device_under_test.subscribe_event(
            "obsState",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["obsState"],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        config_id = "sbi-mvp01-20200325-00002"

        [[result_code], [_]] = device_under_test.ConfigureScan(
            json.dumps({"id": config_id})
        )
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.CONFIGURING)
        change_event_callbacks.assert_change_event("obsState", ObsState.READY)

        assert device_under_test.configurationId == config_id

        (result_code, _) = device_under_test.Scan("abc")
        assert result_code == ResultCode.FAILED

        change_event_callbacks.assert_not_called()
        assert device_under_test.obsState == ObsState.READY

    def test_EndScan_when_in_wrong_state(
        self, device_under_test, change_event_callbacks
    ):
        """
        Test for EndScan when the device is in wrong state.

        :param device_under_test: a proxy to the device under test
        :param change_event_callbacks: dictionary of mock change event
            callbacks with asynchrony support
        """
        # Set the device in ON/READY state
        assert device_under_test.state() == tango.DevState.OFF

        device_under_test.subscribe_event(
            "state",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["state"],
        )
        change_event_callbacks.assert_change_event("state", tango.DevState.OFF)

        [[result_code], [_]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("state", tango.DevState.ON)

        device_under_test.subscribe_event(
            "obsState",
            tango.EventType.CHANGE_EVENT,
            change_event_callbacks["obsState"],
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        config_id = "sbi-mvp01-20200325-00002"

        [[result_code], [_]] = device_under_test.ConfigureScan(
            json.dumps({"id": config_id})
        )
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.CONFIGURING)
        change_event_callbacks.assert_change_event("obsState", ObsState.READY)

        assert device_under_test.configurationId == config_id

        with pytest.raises(
            tango.DevFailed,
            match="EndScan command not permitted in observation state READY",
        ):
            device_under_test.EndScan()

    def test_abort_and_obsreset(self, device_under_test, change_event_callbacks):
        """
        Test for Abort.

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
        for progress_point in FakeBaseComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (on_command_id, progress_point)
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
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        # TODO: Everything above here is just to turn on the device and clear the queue
        # attributes. We need a better way to handle this.

        # Start configuring but then abort
        [[result_code], [configure_command_id]] = device_under_test.ConfigureScan(
            json.dumps({"id": "sbi-mvp01-20200325-00002"})
        )
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.CONFIGURING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", configure_command_id, "QUEUED"),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (on_command_id, "COMPLETED", configure_command_id, "IN_PROGRESS"),
        )

        [[result_code], [abort_command_id]] = device_under_test.Abort()
        assert result_code == ResultCode.STARTED

        change_event_callbacks.assert_change_event("obsState", ObsState.ABORTING)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                configure_command_id,
                "IN_PROGRESS",
                abort_command_id,
                "IN_PROGRESS",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                configure_command_id,
                "IN_PROGRESS",
                abort_command_id,
                "COMPLETED",
            ),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.ABORTED)
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                configure_command_id,
                "ABORTED",
                abort_command_id,
                "COMPLETED",
            ),
        )
        change_event_callbacks.assert_not_called()

        # Reset from aborted state
        [[result_code], [reset_command_id]] = device_under_test.ObsReset()
        assert result_code == ResultCode.QUEUED

        change_event_callbacks.assert_change_event("obsState", ObsState.RESETTING)

        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                configure_command_id,
                "ABORTED",
                abort_command_id,
                "COMPLETED",
                reset_command_id,
                "QUEUED",
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                configure_command_id,
                "ABORTED",
                abort_command_id,
                "COMPLETED",
                reset_command_id,
                "IN_PROGRESS",
            ),
        )
        for progress_point in FakeBaseComponent.PROGRESS_REPORTING_POINTS:
            change_event_callbacks.assert_change_event(
                "longRunningCommandProgress", (reset_command_id, progress_point)
            )
        change_event_callbacks.assert_change_event(
            "longRunningCommandResult",
            (
                reset_command_id,
                json.dumps([int(ResultCode.OK), "Obs reset completed OK"]),
            ),
        )
        change_event_callbacks.assert_change_event(
            "longRunningCommandStatus",
            (
                on_command_id,
                "COMPLETED",
                configure_command_id,
                "ABORTED",
                abort_command_id,
                "COMPLETED",
                reset_command_id,
                "COMPLETED",
            ),
        )
        change_event_callbacks.assert_change_event("obsState", ObsState.IDLE)

        assert device_under_test.obsState == ObsState.IDLE

    def test_ObsReset_when_in_wrong_state(self, device_under_test):
        """
        Test for ObsReset when the device is in wrong state.

        :param device_under_test: a proxy to the device under test
        """
        # Set the device in ON/IDLE state
        device_under_test.On()

        import time

        time.sleep(3)
        with pytest.raises(
            tango.DevFailed,
            match="ObsReset command not permitted in observation state IDLE",
        ):
            device_under_test.ObsReset()


@pytest.mark.forked
def test_multiple_devices_in_same_process(mocker):
    """
    Test that we can run this device with other devices in a single process.

    :param mocker: pytest fixture that wraps :py:mod:`unittest.mock`.
    """
    # Patch abstract method/s; it doesn't matter what we patch them with, so long as
    # they don't raise NotImplementedError.
    mocker.patch.object(SKAObsDevice, "create_component_manager")
    mocker.patch.object(CspSubElementObsDevice, "create_component_manager")

    devices_info = (
        {"class": CspSubElementObsDevice, "devices": [{"name": "test/se/1"}]},
        {"class": SKAObsDevice, "devices": [{"name": "test/obsdevice/1"}]},
    )

    with MultiDeviceTestContext(devices_info, process=False) as context:
        proxy1 = context.get_device("test/se/1")
        proxy2 = context.get_device("test/obsdevice/1")
        assert proxy1.state() == tango.DevState.DISABLE
        assert proxy2.state() == tango.DevState.DISABLE
