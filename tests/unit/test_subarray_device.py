#########################################################################################
# -*- coding: utf-8 -*-
#
# This file is part of the SKASubarray project
#
#
#
#########################################################################################
"""Contain the tests for the SKASubarray."""

import json
import re

import pytest
from tango import DevState

# PROTECTED REGION ID(SKASubarray.test_additional_imports) ENABLED START #
from ska_tango_base import SKASubarray
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import (
    AdminMode,
    ControlMode,
    HealthState,
    ObsMode,
    ObsState,
    SimulationMode,
    TestMode,
)
from ska_tango_base.testing.reference import ReferenceSubarrayComponentManager

# PROTECTED REGION END #    //  SKASubarray.test_additional_imports


class TestSKASubarray:
    """Test cases for SKASubarray device."""

    @pytest.fixture(scope="class")
    def device_properties(self):
        """
        Fixture that returns properties of the device under test.

        :return: properties of the device under test
        """
        return {
            "CapabilityTypes": ["BAND1", "BAND2"],
            "LoggingTargetsDefault": "",
            "GroupDefinitions": "",
            "SkaLevel": "4",
            "SubID": "1",
        }

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
            "device": SKASubarray,
            "component_manager_patch": lambda self: ReferenceSubarrayComponentManager(
                self.CapabilityTypes,
                self.logger,
                self._communication_state_changed,
                self._component_state_changed,
            ),
            "properties": device_properties,
            "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
        }

    @pytest.mark.skip(reason="Not implemented")
    def test_properties(self, device_under_test):
        """
        Test device properties.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_properties) ENABLED START #
        # PROTECTED REGION END #    //  SKASubarray.test_properties
        """Test the Tango device properties of this subarray device."""

    # PROTECTED REGION ID(SKASubarray.test_GetVersionInfo_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_GetVersionInfo_decorators
    def test_GetVersionInfo(self, device_under_test, tango_change_event_helper):
        """
        Test for GetVersionInfo.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        # PROTECTED REGION ID(SKASubarray.test_GetVersionInfo) ENABLED START #
        version_pattern = (
            f"{device_under_test.info().dev_class}, ska_tango_base, "
            "[0-9]+.[0-9]+.[0-9]+, A set of generic base devices for SKA Telescope."
        )
        version_info = device_under_test.GetVersionInfo()
        assert len(version_info) == 1
        assert re.match(version_pattern, version_info[0])
        # PROTECTED REGION END #    //  SKASubarray.test_GetVersionInfo

    # PROTECTED REGION ID(SKASubarray.test_Status_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Status_decorators
    def test_Status(self, device_under_test):
        """
        Test for Status.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_Status) ENABLED START #
        assert device_under_test.Status() == "The device is in OFF state."
        # PROTECTED REGION END #    //  SKASubarray.test_Status

    # PROTECTED REGION ID(SKASubarray.test_State_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_State_decorators
    def test_State(self, device_under_test):
        """
        Test for State.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_State) ENABLED START #
        assert device_under_test.state() == DevState.OFF
        # PROTECTED REGION END #    //  SKASubarray.test_State

    # PROTECTED REGION ID(SKASubarray.test_AssignResources_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_AssignResources_decorators
    def test_assign_and_release_resources(
        self, device_under_test, tango_change_event_helper
    ):
        """
        Test for AssignResources.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        # PROTECTED REGION ID(SKASubarray.test_AssignResources) ENABLED START #
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        device_status_callback = tango_change_event_helper.subscribe("status")
        device_status_callback.assert_next_change_event("The device is in OFF state.")

        command_progress_callback = tango_change_event_helper.subscribe(
            "longRunningCommandProgress"
        )
        command_progress_callback.assert_next_change_event(None)

        command_status_callback = tango_change_event_helper.subscribe(
            "longRunningCommandStatus"
        )
        command_status_callback.assert_next_change_event(None)

        command_result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )
        command_result_callback.assert_next_change_event(("", ""))

        [[result_code], [command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED
        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        device_state_callback.assert_next_change_event(DevState.ON)
        device_status_callback.assert_next_change_event("The device is in ON state.")
        assert device_under_test.state() == DevState.ON

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "On command completed OK"]))
        )

        # TODO: Everything above here is just to turn on the device and clear the queue
        # attributes. We need a better way to handle this.

        # Test assignment of resources
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_next_change_event(ObsState.EMPTY)

        resources_to_assign = ["BAND1", "BAND2"]
        [[result_code], [command_id]] = device_under_test.AssignResources(
            json.dumps(resources_to_assign)
        )
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.RESOURCING)

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        command_result_callback.assert_next_change_event(
            (
                command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            )
        )

        assert list(device_under_test.assignedResources) == resources_to_assign

        # Test partial release of resources
        resources_to_release = ["BAND1"]
        [[result_code], [command_id]] = device_under_test.ReleaseResources(
            json.dumps(resources_to_release)
        )
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.RESOURCING)

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        command_result_callback.assert_next_change_event(
            (
                command_id,
                json.dumps([int(ResultCode.OK), "Resource release completed OK"]),
            )
        )

        assert list(device_under_test.assignedResources) == ["BAND2"]

        # Test release all
        [[result_code], [command_id]] = device_under_test.ReleaseAllResources()
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.RESOURCING)

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.EMPTY)

        command_result_callback.assert_next_change_event(
            (
                command_id,
                json.dumps([int(ResultCode.OK), "Resource release completed OK"]),
            )
        )

        assert not device_under_test.assignedResources
        # PROTECTED REGION END #    //  SKASubarray.test_AssignResources

    # PROTECTED REGION ID(SKASubarray.test_Configure_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Configure_decorators
    def test_configure_and_end(self, device_under_test, tango_change_event_helper):
        """
        Test for Configure.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        # PROTECTED REGION ID(SKASubarray.test_Configure) ENABLED START #
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        device_status_callback = tango_change_event_helper.subscribe("status")
        device_status_callback.assert_next_change_event("The device is in OFF state.")

        command_progress_callback = tango_change_event_helper.subscribe(
            "longRunningCommandProgress"
        )
        command_progress_callback.assert_next_change_event(None)

        command_status_callback = tango_change_event_helper.subscribe(
            "longRunningCommandStatus"
        )
        command_status_callback.assert_next_change_event(None)

        command_result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )
        command_result_callback.assert_next_change_event(("", ""))

        [[result_code], [command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED
        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        device_state_callback.assert_next_change_event(DevState.ON)
        device_status_callback.assert_next_change_event("The device is in ON state.")
        assert device_under_test.state() == DevState.ON

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "On command completed OK"]))
        )

        # assignment of resources
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_next_change_event(ObsState.EMPTY)

        resources_to_assign = ["BAND1"]
        [[result_code], [command_id]] = device_under_test.AssignResources(
            json.dumps(resources_to_assign)
        )
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.RESOURCING)

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        command_result_callback.assert_next_change_event(
            (
                command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            )
        )

        assert list(device_under_test.assignedResources) == resources_to_assign

        # TODO: Everything above here is just to turn on the device, assign it some
        # resources, and clear the queue attributes. We need a better way to handle
        # this.
        assert list(device_under_test.configuredCapabilities) == ["BAND1:0", "BAND2:0"]

        configuration_to_apply = {"BAND1": 2}
        [[result_code], [command_id]] = device_under_test.Configure(
            json.dumps(configuration_to_apply)
        )
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.CONFIGURING)

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.READY)

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "Configure completed OK"]))
        )

        assert list(device_under_test.configuredCapabilities) == ["BAND1:2", "BAND2:0"]

        # test deconfigure
        [[result_code], [command_id]] = device_under_test.End()
        assert result_code == ResultCode.QUEUED

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "Deconfigure completed OK"]))
        )

        assert list(device_under_test.configuredCapabilities) == ["BAND1:0", "BAND2:0"]
        # PROTECTED REGION END #    //  SKASubarray.test_Configure

    # PROTECTED REGION ID(SKASubarray.test_Scan_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Scan_decorators
    def test_scan_and_end_scan(self, device_under_test, tango_change_event_helper):
        """
        Test for Scan.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        # PROTECTED REGION ID(SKASubarray.test_Scan) ENABLED START #
        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        device_status_callback = tango_change_event_helper.subscribe("status")
        device_status_callback.assert_next_change_event("The device is in OFF state.")

        command_progress_callback = tango_change_event_helper.subscribe(
            "longRunningCommandProgress"
        )
        command_progress_callback.assert_next_change_event(None)

        command_status_callback = tango_change_event_helper.subscribe(
            "longRunningCommandStatus"
        )
        command_status_callback.assert_next_change_event(None)

        command_result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )
        command_result_callback.assert_next_change_event(("", ""))

        [[result_code], [command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED
        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        device_state_callback.assert_next_change_event(DevState.ON)
        device_status_callback.assert_next_change_event("The device is in ON state.")
        assert device_under_test.state() == DevState.ON

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "On command completed OK"]))
        )

        # assignment of resources
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_next_change_event(ObsState.EMPTY)

        resources_to_assign = ["BAND1"]
        [[result_code], [command_id]] = device_under_test.AssignResources(
            json.dumps(resources_to_assign)
        )
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.RESOURCING)

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        command_result_callback.assert_next_change_event(
            (
                command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            )
        )

        assert list(device_under_test.assignedResources) == resources_to_assign

        # configuration
        assert list(device_under_test.configuredCapabilities) == ["BAND1:0", "BAND2:0"]

        configuration_to_apply = {"BAND1": 2}
        [[result_code], [command_id]] = device_under_test.Configure(
            json.dumps(configuration_to_apply)
        )
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.CONFIGURING)

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.READY)

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "Configure completed OK"]))
        )

        assert list(device_under_test.configuredCapabilities) == ["BAND1:2", "BAND2:0"]

        # TODO: Everything above here is just to turn on the device, assign it some
        # resources, configure it, and clear the queue attributes. We need a better way
        # to handle this.

        dummy_scan_arg = 5
        [[result_code], [command_id]] = device_under_test.Scan(
            json.dumps(dummy_scan_arg)
        )
        assert result_code == ResultCode.QUEUED

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.SCANNING)

        command_result_callback.assert_next_change_event(
            (
                command_id,
                json.dumps([int(ResultCode.OK), "Scan commencement completed OK"]),
            )
        )

        # test end scan
        [[result_code], [command_id]] = device_under_test.EndScan()
        assert result_code == ResultCode.QUEUED

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.READY)

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "End scan completed OK"]))
        )

    # PROTECTED REGION ID(SKASubarray.test_Reset_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_Reset_decorators
    def test_abort_and_obsreset(self, device_under_test, tango_change_event_helper):
        """
        Test for Reset.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        # PROTECTED REGION ID(SKASubarray.test_Reset) ENABLED START #

        assert device_under_test.state() == DevState.OFF

        device_state_callback = tango_change_event_helper.subscribe("state")
        device_state_callback.assert_next_change_event(DevState.OFF)

        device_status_callback = tango_change_event_helper.subscribe("status")
        device_status_callback.assert_next_change_event("The device is in OFF state.")

        command_progress_callback = tango_change_event_helper.subscribe(
            "longRunningCommandProgress"
        )
        command_progress_callback.assert_next_change_event(None)

        command_status_callback = tango_change_event_helper.subscribe(
            "longRunningCommandStatus"
        )
        command_status_callback.assert_next_change_event(None)

        command_result_callback = tango_change_event_helper.subscribe(
            "longRunningCommandResult"
        )
        command_result_callback.assert_next_change_event(("", ""))

        [[result_code], [command_id]] = device_under_test.On()
        assert result_code == ResultCode.QUEUED
        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        device_state_callback.assert_next_change_event(DevState.ON)
        device_status_callback.assert_next_change_event("The device is in ON state.")
        assert device_under_test.state() == DevState.ON

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        command_result_callback.assert_next_change_event(
            (command_id, json.dumps([int(ResultCode.OK), "On command completed OK"]))
        )

        # assignment of resources
        obs_state_callback = tango_change_event_helper.subscribe("obsState")
        obs_state_callback.assert_next_change_event(ObsState.EMPTY)

        resources_to_assign = ["BAND1"]
        [[result_code], [command_id]] = device_under_test.AssignResources(
            json.dumps(resources_to_assign)
        )
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.RESOURCING)

        command_status_callback.assert_next_change_event((command_id, "QUEUED"))
        command_status_callback.assert_next_change_event((command_id, "IN_PROGRESS"))

        command_progress_callback.assert_next_change_event((command_id, "33"))
        command_progress_callback.assert_next_change_event((command_id, "66"))

        command_status_callback.assert_next_change_event((command_id, "COMPLETED"))

        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        command_result_callback.assert_next_change_event(
            (
                command_id,
                json.dumps([int(ResultCode.OK), "Resource assignment completed OK"]),
            )
        )

        assert list(device_under_test.assignedResources) == resources_to_assign

        # TODO: Everything above here is just to turn on the device, assign it some
        # resources, and clear the queue attributes. We need a better way to handle
        # this.

        # Start configuring but then abort
        assert list(device_under_test.configuredCapabilities) == ["BAND1:0", "BAND2:0"]

        configuration_to_apply = {"BAND1": 2}
        [[result_code], [configure_command_id]] = device_under_test.Configure(
            json.dumps(configuration_to_apply)
        )
        assert result_code == ResultCode.QUEUED

        obs_state_callback.assert_next_change_event(ObsState.CONFIGURING)

        command_status_callback.assert_next_change_event(
            (configure_command_id, "QUEUED")
        )
        command_status_callback.assert_next_change_event(
            (configure_command_id, "IN_PROGRESS")
        )

        [[result_code], [abort_command_id]] = device_under_test.Abort()
        assert result_code == ResultCode.STARTED

        obs_state_callback.assert_next_change_event(ObsState.ABORTING)

        command_status_callback.assert_next_change_event(
            (configure_command_id, "IN_PROGRESS", abort_command_id, "IN_PROGRESS")
        )

        status_call = command_status_callback.get_next_change_event()
        if status_call == (
            configure_command_id,
            "ABORTED",
            abort_command_id,
            "IN_PROGRESS",
        ):
            # event announcing abort of configure arrived first,
            # now we expect abort to completed
            command_status_callback.assert_next_change_event(
                (abort_command_id, "COMPLETED")
            )
        else:
            # event announcing completion of abort arrived first,
            # now we expect configure to abort.
            assert status_call == (
                configure_command_id,
                "IN_PROGRESS",
                abort_command_id,
                "COMPLETED",
            )
            command_status_callback.assert_next_change_event(
                (configure_command_id, "ABORTED")
            )

        obs_state_callback.assert_next_change_event(ObsState.ABORTED)

        # command_progress_callback.assert_not_called()
        command_status_callback.assert_not_called()
        command_result_callback.assert_not_called()

        # Reset from aborted state
        [[result_code], [reset_command_id]] = device_under_test.ObsReset()
        assert result_code == ResultCode.QUEUED
        command_status_callback.assert_next_change_event((reset_command_id, "QUEUED"))
        command_status_callback.assert_next_change_event(
            (reset_command_id, "IN_PROGRESS")
        )

        obs_state_callback.assert_next_change_event(ObsState.RESETTING)

        call = command_progress_callback.get_next_change_event()
        if call == (configure_command_id, "33"):
            call = command_progress_callback.get_next_change_event()
        assert call == (reset_command_id, "33")
        command_progress_callback.assert_next_change_event((reset_command_id, "66"))

        command_status_callback.assert_next_change_event(
            (reset_command_id, "COMPLETED")
        )

        obs_state_callback.assert_next_change_event(ObsState.IDLE)

        command_result_callback.assert_next_change_event(
            (
                reset_command_id,
                json.dumps([int(ResultCode.OK), "Obs reset completed OK"]),
            )
        )

        assert list(device_under_test.configuredCapabilities) == ["BAND1:0", "BAND2:0"]
        assert device_under_test.obsState == ObsState.IDLE
        # PROTECTED REGION END #    //  SKASubarray.test_Reset

    # PROTECTED REGION ID(SKASubarray.test_activationTime_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_activationTime_decorators
    def test_activationTime(self, device_under_test):
        """
        Test for activationTime.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_activationTime) ENABLED START #
        assert device_under_test.activationTime == 0.0
        # PROTECTED REGION END #    //  SKASubarray.test_activationTime

    # PROTECTED REGION ID(SKASubarray.test_adminMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_adminMode_decorators
    def test_adminMode(self, device_under_test, tango_change_event_helper):
        """
        Test for adminMode.

        :param device_under_test: a proxy to the device under test
        :param tango_change_event_helper: helper fixture that simplifies
            subscription to the device under test with a callback.
        """
        # PROTECTED REGION ID(SKASubarray.test_adminMode) ENABLED START #
        assert device_under_test.state() == DevState.OFF
        assert device_under_test.adminMode == AdminMode.ONLINE

        admin_mode_callback = tango_change_event_helper.subscribe("adminMode")
        op_state_callback = tango_change_event_helper.subscribe("state")
        admin_mode_callback.assert_next_change_event(AdminMode.ONLINE)
        op_state_callback.assert_next_change_event(DevState.OFF)

        device_under_test.adminMode = AdminMode.OFFLINE
        admin_mode_callback.assert_next_change_event(AdminMode.OFFLINE)
        op_state_callback.assert_next_change_event(DevState.DISABLE)
        assert device_under_test.state() == DevState.DISABLE
        assert device_under_test.adminMode == AdminMode.OFFLINE

        device_under_test.adminMode = AdminMode.MAINTENANCE
        admin_mode_callback.assert_next_change_event(AdminMode.MAINTENANCE)
        op_state_callback.assert_next_change_event(DevState.UNKNOWN)
        op_state_callback.assert_next_change_event(DevState.OFF)
        assert device_under_test.state() == DevState.OFF
        assert device_under_test.adminMode == AdminMode.MAINTENANCE
        # PROTECTED REGION END #    //  SKASubarray.test_adminMode

    # PROTECTED REGION ID(SKASubarray.test_buildState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_buildState_decorators
    def test_buildState(self, device_under_test):
        """
        Test for buildState.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_buildState) ENABLED START #
        buildPattern = re.compile(
            r"ska_tango_base, [0-9]+.[0-9]+.[0-9]+, "
            r"A set of generic base devices for SKA Telescope"
        )
        assert (re.match(buildPattern, device_under_test.buildState)) is not None
        # PROTECTED REGION END #    //  SKASubarray.test_buildState

    # PROTECTED REGION ID(SKASubarray.test_configurationDelayExpected_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_configurationDelayExpected_decorators
    def test_configurationDelayExpected(self, device_under_test):
        """
        Test for configurationDelayExpected.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_configurationDelayExpected) ENABLED START #
        assert device_under_test.configurationDelayExpected == 0
        # PROTECTED REGION END #    //  SKASubarray.test_configurationDelayExpected

    # PROTECTED REGION ID(SKASubarray.test_configurationProgress_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_configurationProgress_decorators
    def test_configurationProgress(self, device_under_test):
        """
        Test for configurationProgress.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_configurationProgress) ENABLED START #
        assert device_under_test.configurationProgress == 0
        # PROTECTED REGION END #    //  SKASubarray.test_configurationProgress

    # PROTECTED REGION ID(SKASubarray.test_controlMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_controlMode_decorators
    def test_controlMode(self, device_under_test):
        """
        Test for controlMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_controlMode) ENABLED START #
        assert device_under_test.controlMode == ControlMode.REMOTE
        # PROTECTED REGION END #    //  SKASubarray.test_controlMode

    # PROTECTED REGION ID(SKASubarray.test_healthState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_healthState_decorators
    def test_healthState(self, device_under_test):
        """
        Test for healthState.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_healthState) ENABLED START #
        assert device_under_test.healthState == HealthState.UNKNOWN
        # PROTECTED REGION END #    //  SKASubarray.test_healthState

    # PROTECTED REGION ID(SKASubarray.test_obsMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_obsMode_decorators
    def test_obsMode(self, device_under_test):
        """
        Test for obsMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_obsMode) ENABLED START #
        assert device_under_test.obsMode == ObsMode.IDLE
        # PROTECTED REGION END #    //  SKASubarray.test_obsMode

    # PROTECTED REGION ID(SKASubarray.test_obsState_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_obsState_decorators
    def test_obsState(self, device_under_test):
        """
        Test for obsState.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_obsState) ENABLED START #
        assert device_under_test.obsState == ObsState.EMPTY
        # PROTECTED REGION END #    //  SKASubarray.test_obsState

    # PROTECTED REGION ID(SKASubarray.test_simulationMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_simulationMode_decorators
    def test_simulationMode(self, device_under_test):
        """
        Test for simulationMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_simulationMode) ENABLED START #
        assert device_under_test.simulationMode == SimulationMode.FALSE
        # PROTECTED REGION END #    //  SKASubarray.test_simulationMode

    # PROTECTED REGION ID(SKASubarray.test_testMode_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_testMode_decorators
    def test_testMode(self, device_under_test):
        """
        Test for testMode.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_testMode) ENABLED START #
        assert device_under_test.testMode == TestMode.NONE
        # PROTECTED REGION END #    //  SKASubarray.test_testMode

    # PROTECTED REGION ID(SKASubarray.test_versionId_decorators) ENABLED START #
    # PROTECTED REGION END #    //  SKASubarray.test_versionId_decorators
    def test_versionId(self, device_under_test):
        """
        Test for versionId.

        :param device_under_test: a proxy to the device under test
        """
        # PROTECTED REGION ID(SKASubarray.test_versionId) ENABLED START #
        versionIdPattern = re.compile(r"[0-9]+.[0-9]+.[0-9]+")
        assert (re.match(versionIdPattern, device_under_test.versionId)) is not None
        # PROTECTED REGION END #    //  SKASubarray.test_versionId
