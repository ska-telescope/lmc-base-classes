# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""Tests for the :py:mod:`ska_tango_base.component_manager` module."""
from __future__ import annotations

import itertools
import logging
import unittest.mock
from typing import Callable, cast

import pytest
import pytest_mock
from ska_control_model import CommunicationStatus, PowerState, ResultCode, TaskStatus
from ska_tango_testing.mock import MockCallableGroup

from ska_tango_base.testing.reference import (
    FakeSubarrayComponent,
    ReferenceSubarrayComponentManager,
)


class TestResourcePool:
    """Test suite for the SubarrayComponentManager._ResourcePool."""

    @pytest.fixture
    def resource_pool(
        self: TestResourcePool,
    ) -> FakeSubarrayComponent._ResourcePool:  # , mock_callback):
        """
        Fixture that yields the component's resource manager.

        :return: a resource pool.
        """
        # pylint: disable-next=protected-access
        return FakeSubarrayComponent._ResourcePool()

    def test_assign(
        self: TestResourcePool, resource_pool: FakeSubarrayComponent._ResourcePool
    ) -> None:
        """
        Test that the ResourceManager assigns resource correctly.

        :param resource_pool: resource pool for testing purposes
        """
        # create a resource manager and check that it is empty
        assert not resource_pool
        assert resource_pool.get() == set()

        resource_pool.assign(set(["A"]))
        assert len(resource_pool) == 1
        assert resource_pool.get() == set(["A"])

        resource_pool.assign(set(["A"]))
        assert len(resource_pool) == 1
        assert resource_pool.get() == set(["A"])

        resource_pool.assign(set(["A", "B"]))
        assert len(resource_pool) == 2
        assert resource_pool.get() == set(["A", "B"])

        resource_pool.assign(set(["A"]))
        assert len(resource_pool) == 2
        assert resource_pool.get() == set(["A", "B"])

        resource_pool.assign(set(["A", "C"]))
        assert len(resource_pool) == 3
        assert resource_pool.get() == set(["A", "B", "C"])

        resource_pool.assign(set(["D"]))
        assert len(resource_pool) == 4
        assert resource_pool.get() == set(["A", "B", "C", "D"])

    def test_release(
        self: TestResourcePool, resource_pool: FakeSubarrayComponent._ResourcePool
    ) -> None:
        """
        Test that the ResourceManager releases resource correctly.

        :param resource_pool: a resource pool
        """
        resource_pool.assign(set(["A", "B", "C", "D"]))

        # okay to release resources not assigned; does nothing
        resource_pool.release(set(["E"]))
        assert len(resource_pool) == 4
        assert resource_pool.get() == set(["A", "B", "C", "D"])

        # check release does what it should
        resource_pool.release(set(["D"]))
        assert len(resource_pool) == 3
        assert resource_pool.get() == set(["A", "B", "C"])

        # okay to release resources both assigned and not assigned
        resource_pool.release(set(["C", "D"]))
        assert len(resource_pool) == 2
        assert resource_pool.get() == set(["A", "B"])

        # check release all does what it should
        resource_pool.release_all()
        assert len(resource_pool) == 0
        assert resource_pool.get() == set()

        # okay to call release_all when already empty
        resource_pool.release_all()
        assert len(resource_pool) == 0
        assert resource_pool.get() == set()


class TestSubarrayComponentManager:
    """Tests of the ``SubarrayComponentManager`` class."""

    @pytest.fixture()
    def mock_capability_types(self: TestSubarrayComponentManager) -> list[str]:
        """
        Return some mock capability types.

        :return: a list of capabilities
        """
        return ["foo", "bah"]

    @pytest.fixture()
    def component(
        self: TestSubarrayComponentManager, mock_capability_types: list[str]
    ) -> FakeSubarrayComponent:
        """
        Return a component for testing.

        :param mock_capability_types: capability types

        :return: a component for testing purposes
        """
        return FakeSubarrayComponent(mock_capability_types)

    @pytest.fixture()
    def component_manager(
        self: TestSubarrayComponentManager,
        logger: logging.Logger,
        callbacks: MockCallableGroup,
        component: FakeSubarrayComponent,
        mock_capability_types: list[str],
    ) -> ReferenceSubarrayComponentManager:
        """
        Fixture that returns the component manager under test.

        :param logger: a logger for the component manager
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        :param component: a subarray component for testing purposes
        :param mock_capability_types: a list of capabilities

        :return: the component manager under test
        """
        return ReferenceSubarrayComponentManager(
            mock_capability_types,
            logger,
            callbacks["communication_state"],
            callbacks["component_state"],
            _component=component,
        )

    @pytest.fixture()
    def mock_resource_factory(
        self: TestSubarrayComponentManager, mocker: pytest_mock.MockerFixture
    ) -> type[unittest.mock.Mock]:
        """
        Return a factory that provides mock resources.

        :param mocker: pytest fixture that wraps
            :py:mod:`unittest.mock`.

        :return: a factory that provides mock resources
        """
        return cast(type[unittest.mock.Mock], mocker.Mock)

    @pytest.fixture()
    def mock_config_factory(
        self: TestSubarrayComponentManager,
    ) -> Callable[[], dict[str, int]]:
        """
        Return a factory that provides mock arguments to the configure() method.

        :return: a factory that provides mock configure arguments
        """
        mock_config_generator = ({"foo": i, "bah": i} for i in itertools.count(1))
        return lambda: next(mock_config_generator)

    @pytest.fixture()
    def mock_scan_args(
        self: TestSubarrayComponentManager, mocker: pytest_mock.MockerFixture
    ) -> unittest.mock.Mock:
        """
        Return mock arguments to the scan() method.

        :param mocker: pytest fixture that wraps
            :py:mod:`unittest.mock`.

        :return: mock scan arguments
        """
        return cast(unittest.mock.Mock, mocker.Mock())

    def test_state_changes_with_start_and_stop_communicating(
        self: TestSubarrayComponentManager,
        component_manager: ReferenceSubarrayComponentManager,
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
        self: TestSubarrayComponentManager,
        component_manager: ReferenceSubarrayComponentManager,
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
        self: TestSubarrayComponentManager,
        component_manager: ReferenceSubarrayComponentManager,
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
        self: TestSubarrayComponentManager,
        component_manager: ReferenceSubarrayComponentManager,
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
        for progress_point in FakeSubarrayComponent.PROGRESS_REPORTING_POINTS:
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
        for progress_point in FakeSubarrayComponent.PROGRESS_REPORTING_POINTS:
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
        self: TestSubarrayComponentManager,
        component_manager: ReferenceSubarrayComponentManager,
        component: FakeSubarrayComponent,
        callbacks: MockCallableGroup,
        power_state: PowerState,
    ) -> None:
        """
        Test how changes to the components result in actions on the state model.

        For example, when we tell the component to simulate power off,
        does the state model receive an action that informs it that the
        component is off?

        :param component_manager: the component manager under test
        :param component: a base component for testing purposes
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        :param power_state: the power state under test
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
        self: TestSubarrayComponentManager,
        component_manager: ReferenceSubarrayComponentManager,
        component: FakeSubarrayComponent,
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
        self: TestSubarrayComponentManager,
        component_manager: ReferenceSubarrayComponentManager,
        component: FakeSubarrayComponent,
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
        self: TestSubarrayComponentManager,
        component_manager: ReferenceSubarrayComponentManager,
        callbacks: MockCallableGroup,
        # initial_power_mode,
        # initial_fault,
        # mock_obs_state_model,
        mock_resource_factory: unittest.mock.Mock,
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

        component_manager.assign(resources=set([mock_resource_1]))
        callbacks.assert_call("component_state", resourced=True)

        component_manager.assign(resources=set([mock_resource_2]))
        callbacks.assert_not_called()

        component_manager.release(resources=set([mock_resource_1]))
        callbacks.assert_not_called()

        component_manager.release(resources=set([mock_resource_2]))
        callbacks.assert_call("component_state", resourced=False)

        component_manager.assign(resources=set([mock_resource_1, mock_resource_2]))
        callbacks.assert_call("component_state", resourced=True)

        component_manager.release_all()
        callbacks.assert_call("component_state", resourced=False)

    def test_configure(
        self: TestSubarrayComponentManager,
        component_manager: ReferenceSubarrayComponentManager,
        callbacks: MockCallableGroup,
        # initial_power_mode,
        # initial_fault,
        # mock_obs_state_model,
        mock_resource_factory: unittest.mock.Mock,
        mock_config_factory: Callable[[], dict[str, int]],
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
        component_manager.assign(resources=set([mock_resource]))
        callbacks.assert_call("component_state", resourced=True)

        mock_configuration_1 = mock_config_factory()
        mock_configuration_2 = mock_config_factory()

        component_manager.configure(configuration=mock_configuration_1)
        callbacks.assert_call("component_state", configured=True)

        component_manager.configure(configuration=mock_configuration_2)
        callbacks.assert_not_called()

        component_manager.deconfigure()
        callbacks.assert_call("component_state", configured=False)

    def test_scan(  # pylint: disable=too-many-arguments
        self: TestSubarrayComponentManager,
        component_manager: ReferenceSubarrayComponentManager,
        component: FakeSubarrayComponent,
        callbacks: MockCallableGroup,
        # component,
        # initial_power_mode,
        # initial_fault,
        # mock_obs_state_model,
        mock_resource_factory: unittest.mock.Mock,
        mock_config_factory: Callable[[], dict[str, int]],
        mock_scan_args: list[str],
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
        component_manager.assign(resources=set([mock_resource]))
        callbacks.assert_call("component_state", resourced=True)

        mock_configuration = mock_config_factory()

        component_manager.configure(configuration=mock_configuration)
        callbacks.assert_call("component_state", configured=True)

        component_manager.scan(scan_args=mock_scan_args)
        callbacks.assert_call("component_state", scanning=True)

        component_manager.end_scan()
        callbacks.assert_call("component_state", scanning=False)

        component_manager.scan(scan_args=mock_scan_args)
        callbacks.assert_call("component_state", scanning=True)

        component.simulate_scan_stopped()
        callbacks.assert_call("component_state", scanning=False)

        component_manager.deconfigure()
        callbacks.assert_call("component_state", configured=False)

    def test_obsfault_reset(  # pylint: disable=too-many-arguments
        self: TestSubarrayComponentManager,
        component_manager: ReferenceSubarrayComponentManager,
        component: FakeSubarrayComponent,
        callbacks: MockCallableGroup,
        mock_resource_factory: unittest.mock.Mock,
        mock_config_factory: Callable[[], dict[str, int]],
        mock_scan_args: str,
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
        component_manager.assign(resources=set([mock_resource]))
        callbacks.assert_call("component_state", resourced=True)

        mock_configuration = mock_config_factory()

        component_manager.configure(configuration=mock_configuration)
        callbacks.assert_call("component_state", configured=True)

        component.simulate_obsfault(True)
        callbacks.assert_call("component_state", obsfault=True)

        component_manager.obsreset()
        callbacks.assert_call("component_state", obsfault=False, configured=False)

        component_manager.configure(configuration=mock_configuration)
        callbacks.assert_call("component_state", configured=True)

        component_manager.scan(scan_args=mock_scan_args)
        callbacks.assert_call("component_state", scanning=True)

        component.simulate_obsfault(True)
        callbacks.assert_call("component_state", obsfault=True)

        component_manager.obsreset()
        callbacks.assert_call(
            "component_state", obsfault=False, scanning=False, configured=False
        )

    def test_obsfault_restart(  # pylint: disable=too-many-arguments
        self: TestSubarrayComponentManager,
        component_manager: ReferenceSubarrayComponentManager,
        component: FakeSubarrayComponent,
        callbacks: MockCallableGroup,
        mock_resource_factory: unittest.mock.Mock,
        mock_config_factory: Callable[[], dict[str, int]],
        mock_scan_args: str,
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
        component_manager.assign(resources=set([mock_resource]))
        callbacks.assert_call("component_state", resourced=True)

        mock_configuration = mock_config_factory()

        component_manager.configure(configuration=mock_configuration)
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

        component_manager.assign(resources=set([mock_resource]))
        callbacks.assert_call("component_state", resourced=True)

        component_manager.configure(configuration=mock_configuration)
        callbacks.assert_call("component_state", configured=True)

        component_manager.scan(scan_args=mock_scan_args)
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
