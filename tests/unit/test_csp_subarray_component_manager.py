"""Tests for the ``csp_subelement_component_manager`` module."""
from __future__ import annotations

import itertools
import logging
import unittest.mock
from typing import Callable, Type

import pytest
from ska_control_model import CommunicationStatus, PowerState, ResultCode, TaskStatus
from ska_tango_testing.mock import MockCallableGroup

from ska_tango_base.testing.reference import (
    FakeCspSubarrayComponent,
    ReferenceCspSubarrayComponentManager,
)


class TestCspSubelementSubarrayComponentManager:
    """Tests of the ``SubarrayComponentManager`` class."""

    @pytest.fixture()
    def mock_resource_factory(
        self: TestCspSubelementSubarrayComponentManager,
    ) -> Type[unittest.mock.Mock]:
        """
        Return a factory that provides mock resources.

        :return: a factory that provides mock resources.
        """
        return unittest.mock.Mock

    @pytest.fixture()
    def mock_config_factory(
        self: TestCspSubelementSubarrayComponentManager,
    ) -> Callable[[], dict[str, str]]:
        """
        Return a factory that provides mock arguments to the configure() method.

        :return: a factory that provides mock arguments to the
            configure() method.
        """
        mock_config_generator = ({"id": f"mock_id_{i}"} for i in itertools.count(1))
        return lambda: next(mock_config_generator)

    @pytest.fixture()
    def mock_scan_args(
        self: TestCspSubelementSubarrayComponentManager,
    ) -> unittest.mock.Mock:
        """
        Return some mock arguments to the scan() method.

        :return: some mock arguments to the scan() method.
        """
        return unittest.mock.Mock()

    @pytest.fixture()
    def component(
        self: TestCspSubelementSubarrayComponentManager,
    ) -> FakeCspSubarrayComponent:
        """
        Return a component for testing.

        :return: a component for testing
        """
        return FakeCspSubarrayComponent()

    @pytest.fixture()
    def component_manager(
        self: TestCspSubelementSubarrayComponentManager,
        logger: logging.Logger,
        callbacks: MockCallableGroup,
        component: FakeCspSubarrayComponent,
    ) -> ReferenceCspSubarrayComponentManager:
        """
        Fixture that returns the component manager under test.

        :param logger: a logger for the component manager
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        :param component: a subarray component for testing purposes

        :return: the component manager under test
        """
        return ReferenceCspSubarrayComponentManager(
            logger,
            callbacks["communication_state"],
            callbacks["component_state"],
            component,
        )

    def test_state_changes_with_start_and_stop_communicating(
        self: TestCspSubelementSubarrayComponentManager,
        component_manager: ReferenceCspSubarrayComponentManager,
        callbacks: MockCallableGroup,
    ) -> None:
        """
        Test that state is updated when the component is connected / disconnected.

        :param component_manager: the component manager under test
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """
        assert component_manager.communication_state == CommunicationStatus.DISABLED
        callbacks.assert_not_called()

        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call("communication_state", CommunicationStatus.ESTABLISHED)
        assert component_manager.communication_state == CommunicationStatus.ESTABLISHED

        callbacks.assert_call("component_state", power=PowerState.OFF)

        component_manager.stop_communicating()
        callbacks.assert_call("component_state", power=PowerState.UNKNOWN)
        callbacks.assert_call("communication_state", CommunicationStatus.DISABLED)
        assert component_manager.communication_state == CommunicationStatus.DISABLED

    def test_simulate_communication_failure(
        self: TestCspSubelementSubarrayComponentManager,
        component_manager: ReferenceCspSubarrayComponentManager,
        callbacks: MockCallableGroup,
    ) -> None:
        """
        Test that we can simulate connection failure.

        :param component_manager: the component manager under test
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """
        assert component_manager.communication_state == CommunicationStatus.DISABLED
        callbacks.assert_not_called()

        component_manager.simulate_communication_failure(True)

        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        assert (
            component_manager.communication_state == CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_not_called()

        component_manager.simulate_communication_failure(False)
        callbacks.assert_call("communication_state", CommunicationStatus.ESTABLISHED)
        assert component_manager.communication_state == CommunicationStatus.ESTABLISHED

        callbacks.assert_call("component_state", power=PowerState.OFF)

        component_manager.simulate_communication_failure(True)
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        assert (
            component_manager.communication_state == CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_not_called()

        component_manager.stop_communicating()
        callbacks.assert_call("component_state", power=PowerState.UNKNOWN)
        callbacks.assert_call("communication_state", CommunicationStatus.DISABLED)
        assert component_manager.communication_state == CommunicationStatus.DISABLED

    @pytest.mark.parametrize("command", ["off", "standby", "on"])
    def test_command_fails_when_disconnected(
        self: TestCspSubelementSubarrayComponentManager,
        component_manager: ReferenceCspSubarrayComponentManager,
        callbacks: MockCallableGroup,
        command: str,
    ) -> None:
        """
        Test that commands fail when there is not connection to the component.

        :param component_manager: the component manager under test
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        :param command: the command under test
        """
        assert component_manager.communication_state == CommunicationStatus.DISABLED
        callbacks.assert_not_called()

        with pytest.raises(
            ConnectionError,
            match="Communication with component is not established.",
        ):
            getattr(component_manager, command)()

        component_manager.simulate_communication_failure(True)
        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        assert (
            component_manager.communication_state == CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_not_called()

        with pytest.raises(
            ConnectionError,
            match="Communication with component is not established.",
        ):
            getattr(component_manager, command)()

        component_manager.simulate_communication_failure(False)
        callbacks.assert_call("communication_state", CommunicationStatus.ESTABLISHED)
        assert component_manager.communication_state == CommunicationStatus.ESTABLISHED
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component_manager.simulate_communication_failure(True)
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        assert (
            component_manager.communication_state == CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_not_called()

        with pytest.raises(
            ConnectionError,
            match="Communication with component is not established.",
        ):
            getattr(component_manager, command)()

        component_manager.stop_communicating()
        callbacks.assert_call("component_state", power=PowerState.UNKNOWN)
        callbacks.assert_call("communication_state", CommunicationStatus.DISABLED)
        assert component_manager.communication_state == CommunicationStatus.DISABLED

        with pytest.raises(
            ConnectionError,
            match="Communication with component is not established.",
        ):
            getattr(component_manager, command)()

    def test_command_succeeds_when_connected(
        self: TestCspSubelementSubarrayComponentManager,
        component_manager: ReferenceCspSubarrayComponentManager,
        callbacks: MockCallableGroup,
    ) -> None:
        """
        Test that commands succeed when there is a connection to the component.

        :param component_manager: the component manager under test
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """
        assert component_manager.communication_state == CommunicationStatus.DISABLED
        callbacks.assert_not_called()

        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call("communication_state", CommunicationStatus.ESTABLISHED)
        assert component_manager.communication_state == CommunicationStatus.ESTABLISHED
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component_manager.standby(callbacks["standby_task"])
        callbacks.assert_call("standby_task", status=TaskStatus.QUEUED)
        callbacks.assert_call("standby_task", status=TaskStatus.IN_PROGRESS)
        for progress_point in FakeCspSubarrayComponent.PROGRESS_REPORTING_POINTS:
            callbacks.assert_call("standby_task", progress=progress_point)
        callbacks.assert_call("component_state", power=PowerState.STANDBY)
        callbacks.assert_call(
            "standby_task",
            status=TaskStatus.COMPLETED,
            result=(ResultCode.OK, "Standby command completed OK"),
        )

        callbacks.assert_not_called()

        # Let's use our test of on() to test the case of not providing a task callback.
        component_manager.on()
        callbacks.assert_call("component_state", power=PowerState.ON)

        component_manager.off(callbacks["off_task"])
        callbacks.assert_call("off_task", status=TaskStatus.QUEUED)
        callbacks.assert_call("off_task", status=TaskStatus.IN_PROGRESS)
        for progress_point in FakeCspSubarrayComponent.PROGRESS_REPORTING_POINTS:
            callbacks.assert_call("off_task", progress=progress_point)
        callbacks.assert_call("component_state", power=PowerState.OFF)
        callbacks.assert_call(
            "off_task",
            status=TaskStatus.COMPLETED,
            result=(ResultCode.OK, "Off command completed OK"),
        )

    @pytest.mark.parametrize(
        "power_state", [PowerState.OFF, PowerState.STANDBY, PowerState.ON]
    )
    def test_simulate_power_state(
        self: TestCspSubelementSubarrayComponentManager,
        component_manager: ReferenceCspSubarrayComponentManager,
        component: FakeCspSubarrayComponent,
        callbacks: MockCallableGroup,
        power_state: PowerState,
    ) -> None:
        """
        Test how changes to the components result in actions on the state model.

        For example, when we tell the component to simulate power off,
        does the state model receive an action that informs it that the
        component is off?

        :param component_manager: the component manager under test
        :param component: a subarray component for testing purposes
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        :param power_state: the power state to simulate; parametrized to
            return each of OFF, STANDBY and ON.
        """
        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call("communication_state", CommunicationStatus.ESTABLISHED)
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component.simulate_power_state(power_state)
        if power_state == PowerState.OFF:
            callbacks.assert_not_called()
        else:
            callbacks.assert_call("component_state", power=power_state)

    def test_simulate_fault(
        self: TestCspSubelementSubarrayComponentManager,
        component_manager: ReferenceCspSubarrayComponentManager,
        component: FakeCspSubarrayComponent,
        callbacks: MockCallableGroup,
    ) -> None:
        """
        Test how changes to the components result in actions on the state model.

        For example, when we tell the component to simulate power off,
        does the state model receive an action that informs it that the
        component is off?

        :param component_manager: the component manager under test
        :param component: a subarray component for testing purposes
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """
        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call("communication_state", CommunicationStatus.ESTABLISHED)
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component.simulate_fault(True)
        callbacks.assert_call("component_state", fault=True)

        component.simulate_fault(False)
        callbacks.assert_call("component_state", fault=False)

    def test_reset_from_fault(
        self: TestCspSubelementSubarrayComponentManager,
        component_manager: ReferenceCspSubarrayComponentManager,
        component: FakeCspSubarrayComponent,
        callbacks: MockCallableGroup,
    ) -> None:
        """
        Test that the component manager can reset a faulty component.

        :param component_manager: the component manager under test
        :param component: a subarray component for testing purposes
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """
        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call("communication_state", CommunicationStatus.ESTABLISHED)
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component.simulate_fault(True)
        callbacks.assert_call("component_state", fault=True)

        component_manager.reset()
        callbacks.assert_call("component_state", fault=False)

    def test_assign_release(
        self: TestCspSubelementSubarrayComponentManager,
        component_manager: ReferenceCspSubarrayComponentManager,
        callbacks: MockCallableGroup,
        mock_resource_factory: Callable[[], unittest.mock.Mock],
    ) -> None:
        """
        Test management of a component during assignment of resources.

        :param component_manager: the component manager under test
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        :param mock_resource_factory: a resource factory
        """
        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call("communication_state", CommunicationStatus.ESTABLISHED)
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component_manager.on()
        callbacks.assert_call("component_state", power=PowerState.ON)

        mock_resource_1 = mock_resource_factory()
        mock_resource_2 = mock_resource_factory()

        component_manager.assign([mock_resource_1])
        callbacks.assert_call("component_state", resourced=True)

        component_manager.assign([mock_resource_2])
        callbacks.assert_not_called()

        component_manager.release([mock_resource_1])
        callbacks.assert_not_called()

        component_manager.release_all()
        callbacks.assert_call("component_state", resourced=False)

    def test_configure(
        self: TestCspSubelementSubarrayComponentManager,
        component_manager: ReferenceCspSubarrayComponentManager,
        callbacks: MockCallableGroup,
        mock_resource_factory: Callable[[], unittest.mock.Mock],
        mock_config_factory: Callable[[], dict[str, str]],
    ) -> None:
        """
        Test management of a component through configuration.

        :param component_manager: the component manager under test
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        :param mock_resource_factory: a resource factory
        :param mock_config_factory: a configure factory
        """
        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call("communication_state", CommunicationStatus.ESTABLISHED)
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component_manager.on()
        callbacks.assert_call("component_state", power=PowerState.ON)

        mock_resource = mock_resource_factory()
        component_manager.assign([mock_resource])
        callbacks.assert_call("component_state", resourced=True)

        mock_configuration_1 = mock_config_factory()
        mock_configuration_2 = mock_config_factory()

        component_manager.configure(mock_configuration_1)
        callbacks.assert_call("component_state", configured=True)

        component_manager.configure(mock_configuration_2)
        callbacks.assert_not_called()

        component_manager.deconfigure()
        callbacks.assert_call("component_state", configured=False)

    def test_scan(  # pylint: disable=too-many-arguments
        self: TestCspSubelementSubarrayComponentManager,
        component_manager: ReferenceCspSubarrayComponentManager,
        component: FakeCspSubarrayComponent,
        callbacks: MockCallableGroup,
        mock_resource_factory: Callable[[], unittest.mock.Mock],
        mock_config_factory: Callable[[], dict[str, str]],
        mock_scan_args: unittest.mock.Mock,
    ) -> None:
        """
        Test management of a scanning component.

        :param component_manager: the component manager under test
        :param component: a subarray component for testing purposes
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        :param mock_resource_factory: a resource factory
        :param mock_config_factory: a configure factory
        :param mock_scan_args: mock scan arguments
        """
        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call("communication_state", CommunicationStatus.ESTABLISHED)
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component_manager.on()
        callbacks.assert_call("component_state", power=PowerState.ON)

        mock_resource = mock_resource_factory()
        component_manager.assign([mock_resource])
        callbacks.assert_call("component_state", resourced=True)

        mock_configuration = mock_config_factory()

        component_manager.configure(mock_configuration)
        callbacks.assert_call("component_state", configured=True)

        component_manager.scan(mock_scan_args)
        callbacks.assert_call("component_state", scanning=True)

        component_manager.end_scan()
        callbacks.assert_call("component_state", scanning=False)

        component_manager.scan(mock_scan_args)
        callbacks.assert_call("component_state", scanning=True)

        component.simulate_scan_stopped()
        callbacks.assert_call("component_state", scanning=False)

        component_manager.deconfigure()
        callbacks.assert_call("component_state", configured=False)

    def test_obsfault_reset(  # pylint: disable=too-many-arguments
        self: TestCspSubelementSubarrayComponentManager,
        component_manager: ReferenceCspSubarrayComponentManager,
        component: FakeCspSubarrayComponent,
        callbacks: MockCallableGroup,
        mock_resource_factory: Callable[[], unittest.mock.Mock],
        mock_config_factory: Callable[[], dict[str, str]],
        mock_scan_args: unittest.mock.Mock,
    ) -> None:
        """
        Test management of a faulting component.

        :param component_manager: the component manager under test
        :param component: a subarray component for testing purposes
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        :param mock_resource_factory: a resource factory
        :param mock_config_factory: a configure factory
        :param mock_scan_args: mock scan arguments
        """
        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call("communication_state", CommunicationStatus.ESTABLISHED)
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component_manager.on()
        callbacks.assert_call("component_state", power=PowerState.ON)

        mock_resource = mock_resource_factory()
        component_manager.assign([mock_resource])
        callbacks.assert_call("component_state", resourced=True)

        mock_configuration = mock_config_factory()

        component_manager.configure(mock_configuration)
        callbacks.assert_call("component_state", configured=True)

        component.simulate_obsfault(True)
        callbacks.assert_call("component_state", obsfault=True)

        component_manager.obsreset()
        callbacks.assert_call("component_state", obsfault=False, configured=False)

        component_manager.configure(mock_configuration)
        callbacks.assert_call("component_state", configured=True)

        component_manager.scan(mock_scan_args)
        callbacks.assert_call("component_state", scanning=True)

        component.simulate_obsfault(True)
        callbacks.assert_call("component_state", obsfault=True)

        component_manager.obsreset()
        callbacks.assert_call(
            "component_state", obsfault=False, scanning=False, configured=False
        )

    def test_obsfault_restart(  # pylint: disable=too-many-arguments
        self: TestCspSubelementSubarrayComponentManager,
        component_manager: ReferenceCspSubarrayComponentManager,
        component: FakeCspSubarrayComponent,
        callbacks: MockCallableGroup,
        mock_resource_factory: Callable[[], unittest.mock.Mock],
        mock_config_factory: Callable[[], dict[str, str]],
        mock_scan_args: unittest.mock.Mock,
    ) -> None:
        """
        Test management of a faulting component.

        :param component_manager: the component manager under test
        :param component: a subarray component for testing purposes
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        :param mock_resource_factory: a resource factory
        :param mock_config_factory: a configure factory
        :param mock_scan_args: mock scan arguments
        """
        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call("communication_state", CommunicationStatus.ESTABLISHED)
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component_manager.on()
        callbacks.assert_call("component_state", power=PowerState.ON)

        mock_resource = mock_resource_factory()
        component_manager.assign([mock_resource])
        callbacks.assert_call("component_state", resourced=True)

        mock_configuration = mock_config_factory()

        component_manager.configure(mock_configuration)
        callbacks.assert_call("component_state", configured=True)

        component.simulate_obsfault(True)
        callbacks.assert_call("component_state", obsfault=True)

        component_manager.restart()
        callbacks.assert_call(
            "component_state",
            obsfault=False,
            configured=False,
            resourced=False,
        )

        component_manager.assign([mock_resource])
        callbacks.assert_call("component_state", resourced=True)

        component_manager.configure(mock_configuration)
        callbacks.assert_call("component_state", configured=True)

        component_manager.scan(mock_scan_args)
        callbacks.assert_call("component_state", scanning=True)

        component.simulate_obsfault(True)
        callbacks.assert_call("component_state", obsfault=True)

        component_manager.restart()
        callbacks.assert_call(
            "component_state",
            obsfault=False,
            scanning=False,
            configured=False,
            resourced=False,
        )
