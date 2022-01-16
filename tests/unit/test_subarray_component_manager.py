"""Tests for the :py:mod:`ska_tango_base.component_manager` module."""
import itertools

import pytest

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import CommunicationStatus, PowerState
from ska_tango_base.executor import TaskStatus
from ska_tango_base.testing import (
    FakeSubarrayComponent,
    ReferenceSubarrayComponentManager,
)


class TestResourcePool:
    """Test suite for the SubarrayComponentManager._ResourcePool."""

    @pytest.fixture
    def resource_pool(self):  # , mock_callback):
        """
        Fixture that yields the component's resource manager.

        :return:
            :py:class:`SubarrayComponentManager._ResourcePool`
        """
        return FakeSubarrayComponent._ResourcePool()

    def test_assign(self, resource_pool):
        """Test that the ResourceManager assigns resource correctly."""
        # create a resource manager and check that it is empty
        assert not len(resource_pool)
        assert resource_pool.get() == set()

        resource_pool.assign(["A"])
        assert len(resource_pool) == 1
        assert resource_pool.get() == set(["A"])

        resource_pool.assign(["A"])
        assert len(resource_pool) == 1
        assert resource_pool.get() == set(["A"])

        resource_pool.assign(["A", "B"])
        assert len(resource_pool) == 2
        assert resource_pool.get() == set(["A", "B"])

        resource_pool.assign(["A"])
        assert len(resource_pool) == 2
        assert resource_pool.get() == set(["A", "B"])

        resource_pool.assign(["A", "C"])
        assert len(resource_pool) == 3
        assert resource_pool.get() == set(["A", "B", "C"])

        resource_pool.assign(["D"])
        assert len(resource_pool) == 4
        assert resource_pool.get() == set(["A", "B", "C", "D"])

    def test_release(self, resource_pool):
        """Test that the ResourceManager releases resource correctly."""
        resource_pool.assign(["A", "B", "C", "D"])

        # okay to release resources not assigned; does nothing
        resource_pool.release(["E"])
        assert len(resource_pool) == 4
        assert resource_pool.get() == set(["A", "B", "C", "D"])

        # check release does what it should
        resource_pool.release(["D"])
        assert len(resource_pool) == 3
        assert resource_pool.get() == set(["A", "B", "C"])

        # okay to release resources both assigned and not assigned
        resource_pool.release(["C", "D"])
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
    def mock_capability_types(self):
        """Return some mock capability types."""
        return ["foo", "bah"]

    @pytest.fixture()
    def component(self, mock_capability_types):
        """Return a component for testing."""
        return FakeSubarrayComponent(mock_capability_types)

    @pytest.fixture()
    def component_manager(self, logger, callbacks, component, mock_capability_types):
        """
        Fixture that returns the component manager under test.

        :param mock_op_state_model: a mock state model for testing
        :param logger: a logger for the component manager

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
    def mock_resource_factory(self, mocker):
        """Return a factory that provides mock resources."""
        return mocker.Mock

    @pytest.fixture()
    def mock_config_factory(self):
        """Return a factory that provides mock arguments to the configure() method."""
        mock_config_generator = ({"foo": i, "bah": i} for i in itertools.count(1))
        return lambda: next(mock_config_generator)

    @pytest.fixture()
    def mock_scan_args(self, mocker):
        """Return mock arguments to the scan() method."""
        return mocker.Mock()

    def test_state_changes_with_start_and_stop_communicating(
        self,
        component_manager,
        callbacks,
    ):
        """
        Test that state is updated when the component is connected / disconnected.

        :param component_manager: the component manager under test
        """
        assert component_manager.communication_state == CommunicationStatus.DISABLED
        callbacks["communication_state"].assert_not_called()
        callbacks["component_state"].assert_not_called()

        component_manager.start_communicating()
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.ESTABLISHED
        )
        assert component_manager.communication_state == CommunicationStatus.ESTABLISHED

        callbacks["component_state"].assert_next_call(power=PowerState.OFF)

        component_manager.stop_communicating()
        callbacks["communication_state"].assert_next_call(CommunicationStatus.DISABLED)
        assert component_manager.communication_state == CommunicationStatus.DISABLED

    def test_simulate_communication_failure(self, component_manager, callbacks):
        """
        Test that we can simulate connection failure.

        :param component_manager: the component manager under test
        """
        assert component_manager.communication_state == CommunicationStatus.DISABLED
        callbacks["communication_state"].assert_not_called()
        callbacks["component_state"].assert_not_called()

        component_manager.simulate_communication_failure(True)

        component_manager.start_communicating()
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        assert (
            component_manager.communication_state == CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["communication_state"].assert_not_called()

        callbacks["component_state"].assert_not_called()

        component_manager.simulate_communication_failure(False)
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.ESTABLISHED
        )
        assert component_manager.communication_state == CommunicationStatus.ESTABLISHED

        callbacks["component_state"].assert_next_call(power=PowerState.OFF)

        component_manager.simulate_communication_failure(True)
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        assert (
            component_manager.communication_state == CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["component_state"].assert_not_called()

        component_manager.stop_communicating()
        callbacks["communication_state"].assert_next_call(CommunicationStatus.DISABLED)
        assert component_manager.communication_state == CommunicationStatus.DISABLED

    @pytest.mark.parametrize("command", ["off", "standby", "on"])
    def test_command_fails_when_disconnected(
        self, component_manager, callbacks, command
    ):
        """
        Test that commands fail when there is not connection to the component.

        :param component_manager: the component manager under test
        :param command: the command under test
        """
        assert component_manager.communication_state == CommunicationStatus.DISABLED
        callbacks["communication_state"].assert_not_called()
        callbacks["component_state"].assert_not_called()

        with pytest.raises(
            ConnectionError, match="Communication with component is not established."
        ):
            getattr(component_manager, command)()

        component_manager.simulate_communication_failure(True)
        component_manager.start_communicating()
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        assert (
            component_manager.communication_state == CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["communication_state"].assert_not_called()
        callbacks["component_state"].assert_not_called()

        with pytest.raises(
            ConnectionError, match="Communication with component is not established."
        ):
            getattr(component_manager, command)()

        component_manager.simulate_communication_failure(False)
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.ESTABLISHED
        )
        assert component_manager.communication_state == CommunicationStatus.ESTABLISHED
        callbacks["component_state"].assert_next_call(power=PowerState.OFF)

        component_manager.simulate_communication_failure(True)
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        assert (
            component_manager.communication_state == CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["component_state"].assert_not_called()

        with pytest.raises(
            ConnectionError, match="Communication with component is not established."
        ):
            getattr(component_manager, command)()

        component_manager.stop_communicating()
        callbacks["communication_state"].assert_next_call(CommunicationStatus.DISABLED)
        assert component_manager.communication_state == CommunicationStatus.DISABLED

        with pytest.raises(
            ConnectionError, match="Communication with component is not established."
        ):
            getattr(component_manager, command)()

    def test_command_succeeds_when_connected(
        self,
        component_manager,
        callbacks,
    ):
        """
        Test that commands succeed when there is a connection to the component.

        :param component_manager: the component manager under test
        :param mock_op_state_model: a mock state model for testing
        :param command: the name of the command under test
        :param action: the action that is expected to be performed on
            the state model
        """
        assert component_manager.communication_state == CommunicationStatus.DISABLED
        callbacks["communication_state"].assert_not_called()
        callbacks["component_state"].assert_not_called()

        component_manager.start_communicating()
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.ESTABLISHED
        )
        assert component_manager.communication_state == CommunicationStatus.ESTABLISHED
        callbacks["component_state"].assert_next_call(power=PowerState.OFF)

        component_manager.standby(callbacks["standby_task"])
        callbacks["standby_task"].assert_next_call(status=TaskStatus.QUEUED)
        callbacks["standby_task"].assert_next_call(status=TaskStatus.IN_PROGRESS)
        callbacks["standby_task"].assert_next_call(progress=33)
        callbacks["standby_task"].assert_next_call(progress=66)
        callbacks["standby_task"].assert_next_call(
            status=TaskStatus.COMPLETED,
            result=(ResultCode.OK, "Standby command completed OK"),
        )
        callbacks["component_state"].assert_next_call(power=PowerState.STANDBY)

        callbacks["standby_task"].assert_not_called()
        callbacks["component_state"].assert_not_called()

        # Let's use our test of on() to test the case of not providing a task callback.
        component_manager.on()
        callbacks["component_state"].assert_next_call(power=PowerState.ON)

        component_manager.off(callbacks["off_task"])
        callbacks["off_task"].assert_next_call(status=TaskStatus.QUEUED)
        callbacks["off_task"].assert_next_call(status=TaskStatus.IN_PROGRESS)
        callbacks["off_task"].assert_next_call(progress=33)
        callbacks["off_task"].assert_next_call(progress=66)
        callbacks["off_task"].assert_next_call(
            status=TaskStatus.COMPLETED,
            result=(ResultCode.OK, "Off command completed OK"),
        )
        callbacks["component_state"].assert_next_call(power=PowerState.OFF)

    @pytest.mark.parametrize(
        "power_state", [PowerState.OFF, PowerState.STANDBY, PowerState.ON]
    )
    def test_simulate_power_state(
        self,
        component_manager,
        component,
        callbacks,
        power_state,
    ):
        """
        Test how changes to the components result in actions on the state model.

        For example, when we tell the component to simulate power off,
        does the state model receive an action that informs it that the
        component is off?

        :param component_manager: the component manager under test
        """
        component_manager.start_communicating()
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.ESTABLISHED
        )
        callbacks["component_state"].assert_next_call(power=PowerState.OFF)

        component.simulate_power_state(power_state)
        if power_state == PowerState.OFF:
            callbacks["component_state"].assert_not_called()
        else:
            callbacks["component_state"].assert_next_call(power=power_state)

    def test_simulate_fault(
        self,
        component_manager,
        component,
        callbacks,
    ):
        """
        Test how changes to the components result in actions on the state model.

        For example, when we tell the component to simulate power off,
        does the state model receive an action that informs it that the
        component is off?

        :param component_manager: the component manager under test
        """
        component_manager.start_communicating()
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.ESTABLISHED
        )
        callbacks["component_state"].assert_next_call(power=PowerState.OFF)

        component.simulate_fault(True)
        callbacks["component_state"].assert_next_call(fault=True)

        component.simulate_fault(False)
        callbacks["component_state"].assert_next_call(fault=False)

    def test_reset_from_fault(
        self,
        component_manager,
        component,
        callbacks,
    ):
        """Test that the component manager can reset a faulty component."""
        component_manager.start_communicating()
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.ESTABLISHED
        )
        callbacks["component_state"].assert_next_call(power=PowerState.OFF)

        component.simulate_fault(True)
        callbacks["component_state"].assert_next_call(fault=True)

        component_manager.reset()
        callbacks["component_state"].assert_next_call(fault=False)

    def test_assign_release(
        self,
        component_manager,
        callbacks,
        # initial_power_mode,
        # initial_fault,
        # mock_obs_state_model,
        mock_resource_factory,
    ):
        """Test management of a component during assignment of resources."""
        component_manager.start_communicating()
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.ESTABLISHED
        )
        callbacks["component_state"].assert_next_call(power=PowerState.OFF)

        component_manager.on()
        callbacks["component_state"].assert_next_call(power=PowerState.ON)

        mock_resource_1 = mock_resource_factory()
        mock_resource_2 = mock_resource_factory()

        component_manager.assign([mock_resource_1])
        callbacks["component_state"].assert_next_call(resourced=True)

        component_manager.assign([mock_resource_2])
        callbacks["component_state"].assert_not_called()

        component_manager.release([mock_resource_1])
        callbacks["component_state"].assert_not_called()

        component_manager.release([mock_resource_2])
        callbacks["component_state"].assert_next_call(resourced=False)

        component_manager.assign([mock_resource_1, mock_resource_2])
        callbacks["component_state"].assert_next_call(resourced=True)

        component_manager.release_all()
        callbacks["component_state"].assert_next_call(resourced=False)

    def test_configure(
        self,
        component_manager,
        callbacks,
        # initial_power_mode,
        # initial_fault,
        # mock_obs_state_model,
        mock_resource_factory,
        mock_config_factory,
    ):
        """Test management of a component through configuration."""
        component_manager.start_communicating()
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.ESTABLISHED
        )
        callbacks["component_state"].assert_next_call(power=PowerState.OFF)

        component_manager.on()
        callbacks["component_state"].assert_next_call(power=PowerState.ON)

        mock_resource = mock_resource_factory()
        component_manager.assign([mock_resource])
        callbacks["component_state"].assert_next_call(resourced=True)

        mock_configuration_1 = mock_config_factory()
        mock_configuration_2 = mock_config_factory()

        component_manager.configure(mock_configuration_1)
        callbacks["component_state"].assert_next_call(configured=True)

        component_manager.configure(mock_configuration_2)
        callbacks["component_state"].assert_not_called()

        component_manager.deconfigure()
        callbacks["component_state"].assert_next_call(configured=False)

    def test_scan(
        self,
        component_manager,
        component,
        callbacks,
        # component,
        # initial_power_mode,
        # initial_fault,
        # mock_obs_state_model,
        mock_resource_factory,
        mock_config_factory,
        mock_scan_args,
    ):
        """Test management of a scanning component."""
        component_manager.start_communicating()
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.ESTABLISHED
        )
        callbacks["component_state"].assert_next_call(power=PowerState.OFF)

        component_manager.on()
        callbacks["component_state"].assert_next_call(power=PowerState.ON)

        mock_resource = mock_resource_factory()
        component_manager.assign([mock_resource])
        callbacks["component_state"].assert_next_call(resourced=True)

        mock_configuration = mock_config_factory()

        component_manager.configure(mock_configuration)
        callbacks["component_state"].assert_next_call(configured=True)

        component_manager.scan(mock_scan_args)
        callbacks["component_state"].assert_next_call(scanning=True)

        component_manager.end_scan()
        callbacks["component_state"].assert_next_call(scanning=False)

        component_manager.scan(mock_scan_args)
        callbacks["component_state"].assert_next_call(scanning=True)

        component.simulate_scan_stopped()
        callbacks["component_state"].assert_next_call(scanning=False)

        component_manager.deconfigure()
        callbacks["component_state"].assert_next_call(configured=False)

    def test_obsfault_reset(
        self,
        component_manager,
        component,
        callbacks,
        # initial_power_mode,
        # initial_fault,
        # mock_obs_state_model,
        mock_resource_factory,
        mock_config_factory,
        mock_scan_args,
    ):
        """Test management of a faulting component."""
        component_manager.start_communicating()
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.ESTABLISHED
        )
        callbacks["component_state"].assert_next_call(power=PowerState.OFF)

        component_manager.on()
        callbacks["component_state"].assert_next_call(power=PowerState.ON)

        mock_resource = mock_resource_factory()
        component_manager.assign([mock_resource])
        callbacks["component_state"].assert_next_call(resourced=True)

        mock_configuration = mock_config_factory()

        component_manager.configure(mock_configuration)
        callbacks["component_state"].assert_next_call(configured=True)

        component.simulate_obsfault(True)
        callbacks["component_state"].assert_next_call(obsfault=True)

        component_manager.obsreset()
        callbacks["component_state"].assert_next_call(obsfault=False, configured=False)

        component_manager.configure(mock_configuration)
        callbacks["component_state"].assert_next_call(configured=True)

        component_manager.scan(mock_scan_args)
        callbacks["component_state"].assert_next_call(scanning=True)

        component.simulate_obsfault(True)
        callbacks["component_state"].assert_next_call(obsfault=True)

        component_manager.obsreset()
        callbacks["component_state"].assert_next_call(
            obsfault=False, scanning=False, configured=False
        )

    def test_obsfault_restart(
        self,
        component_manager,
        component,
        callbacks,
        # initial_power_mode,
        # initial_fault,
        # mock_obs_state_model,
        mock_resource_factory,
        mock_config_factory,
        mock_scan_args,
    ):
        """Test management of a faulting component."""
        component_manager.start_communicating()
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks["communication_state"].assert_next_call(
            CommunicationStatus.ESTABLISHED
        )
        callbacks["component_state"].assert_next_call(power=PowerState.OFF)

        component_manager.on()
        callbacks["component_state"].assert_next_call(power=PowerState.ON)

        mock_resource = mock_resource_factory()
        component_manager.assign([mock_resource])
        callbacks["component_state"].assert_next_call(resourced=True)

        mock_configuration = mock_config_factory()

        component_manager.configure(mock_configuration)
        callbacks["component_state"].assert_next_call(configured=True)

        component.simulate_obsfault(True)
        callbacks["component_state"].assert_next_call(obsfault=True)

        component_manager.restart()
        callbacks["component_state"].assert_next_call(
            obsfault=False, configured=False, resourced=False
        )

        component_manager.assign([mock_resource])
        callbacks["component_state"].assert_next_call(resourced=True)

        component_manager.configure(mock_configuration)
        callbacks["component_state"].assert_next_call(configured=True)

        component_manager.scan(mock_scan_args)
        callbacks["component_state"].assert_next_call(scanning=True)

        component.simulate_obsfault(True)
        callbacks["component_state"].assert_next_call(obsfault=True)

        component_manager.restart()
        callbacks["component_state"].assert_next_call(
            obsfault=False, scanning=False, configured=False, resourced=False
        )
