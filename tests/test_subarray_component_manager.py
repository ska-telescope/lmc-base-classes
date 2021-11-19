"""Tests for the :py:mod:`ska_tango_base.component_manager` module."""
import contextlib
import itertools

import pytest

# from tango import DevState

from ska_tango_base.faults import ComponentError, ComponentFault
from ska_tango_base.subarray import ReferenceSubarrayComponentManager
from ska_tango_base.control_model import PowerState


class TestSubarrayComponentResourceManager:
    """Test suite for the Subarray._Component._ResourceManager."""

    @pytest.fixture
    def mock_callback(self, mocker):
        """Return a mock that can be used as a callback."""
        return mocker.Mock()

    @pytest.fixture
    def resource_pool(self, mock_callback):
        """
        Fixture that yields the component's resource manager.

        :return:
            :py:class:`SubarrayComponentManager._ResourcePool`
        """
        return ReferenceSubarrayComponentManager._ResourcePool(mock_callback)

    def test_ResourceManager_assign(self, resource_pool, mock_callback):
        """Test that the ResourceManager assigns resource correctly."""
        # create a resource manager and check that it is empty
        assert not len(resource_pool)
        assert resource_pool.get() == set()

        resource_pool.assign(["A"])
        mock_callback.assert_called_once_with(True)
        assert len(resource_pool) == 1
        assert resource_pool.get() == set(["A"])
        mock_callback.reset_mock()

        resource_pool.assign(["A"])
        assert len(resource_pool) == 1
        assert resource_pool.get() == set(["A"])
        mock_callback.assert_not_called()

        resource_pool.assign(["A", "B"])
        assert len(resource_pool) == 2
        assert resource_pool.get() == set(["A", "B"])
        mock_callback.assert_not_called()

        resource_pool.assign(["A"])
        assert len(resource_pool) == 2
        assert resource_pool.get() == set(["A", "B"])
        mock_callback.assert_not_called()

        resource_pool.assign(["A", "C"])
        assert len(resource_pool) == 3
        assert resource_pool.get() == set(["A", "B", "C"])
        mock_callback.assert_not_called()

        resource_pool.assign(["D"])
        assert len(resource_pool) == 4
        assert resource_pool.get() == set(["A", "B", "C", "D"])
        mock_callback.assert_not_called()

    def test_ResourceManager_release(self, resource_pool, mock_callback):
        """Test that the ResourceManager releases resource correctly."""
        resource_pool.assign(["A", "B", "C", "D"])
        mock_callback.assert_called_once_with(True)
        mock_callback.reset_mock()

        # okay to release resources not assigned; does nothing
        resource_pool.release(["E"])
        assert len(resource_pool) == 4
        assert resource_pool.get() == set(["A", "B", "C", "D"])
        mock_callback.assert_not_called()

        # check release does what it should
        resource_pool.release(["D"])
        assert len(resource_pool) == 3
        assert resource_pool.get() == set(["A", "B", "C"])
        mock_callback.assert_not_called()

        # okay to release resources both assigned and not assigned
        resource_pool.release(["C", "D"])
        assert len(resource_pool) == 2
        assert resource_pool.get() == set(["A", "B"])
        mock_callback.assert_not_called()

        # check release all does what it should
        resource_pool.release_all()
        assert len(resource_pool) == 0
        assert resource_pool.get() == set()
        mock_callback.assert_called_once_with(False)
        mock_callback.reset_mock()

        # okay to call release_all when already empty
        resource_pool.release_all()
        assert len(resource_pool) == 0
        assert resource_pool.get() == set()
        mock_callback.assert_not_called()


class TestSubarrayComponentManager:
    """Tests of the ``SubarrayComponentManager`` class."""

    @pytest.fixture()
    def mock_op_state_model(self, mocker):
        """
        Fixture that returns a mock op state model.

        :param mocker: pytest fixture that wraps
            :py:mod:`unittest.mock`.

        :return: a mock state model
        """
        return mocker.Mock()

    @pytest.fixture()
    def mock_obs_state_model(self, mocker):
        """
        Fixture that returns a mock observation state model.

        :param mocker: pytest fixture that wraps
            :py:mod:`unittest.mock`.

        :return: a mock state model
        """
        return mocker.Mock()

    @pytest.fixture()
    def mock_resource_factory(self, mocker):
        """Return a factory that provides mock resources."""
        return mocker.Mock

    @pytest.fixture()
    def mock_capability_types(self, mocker):
        """Return some mock capability types."""
        return ["foo", "bah"]

    @pytest.fixture()
    def mock_config_factory(self):
        """Return a factory that provides mock arguments to the configure() method."""
        mock_config_generator = ({"foo": i, "bah": i} for i in itertools.count(1))
        return lambda: next(mock_config_generator)

    @pytest.fixture()
    def mock_scan_args(self, mocker):
        """Return mock arguments to the scan() method."""
        return mocker.Mock()

    @pytest.fixture(params=[PowerState.OFF, PowerState.STANDBY, PowerState.ON])
    def initial_power_mode(self, request):
        """Return the initial power mode of the component under test."""
        return request.param

    @pytest.fixture(params=[False, True])
    def initial_fault(self, request):
        """Return whether the component under test should initially be faulty."""
        return request.param

    @pytest.fixture()
    def component(self, mock_capability_types, initial_power_mode, initial_fault):
        """Return a component for use in testing."""
        return ReferenceSubarrayComponentManager._Component(
            mock_capability_types, _power_mode=initial_power_mode, _faulty=initial_fault
        )

    @pytest.fixture()
    def component_manager(
        self,
        mock_op_state_model,
        mock_obs_state_model,
        mock_capability_types,
        logger,
        component,
    ):
        """
        Fixture that returns the component manager under test.

        :param mock_op_state_model: a mock state model for testing
        :param logger: a logger for the component manager

        :return: the component manager under test
        """
        return ReferenceSubarrayComponentManager(
            mock_op_state_model,
            mock_obs_state_model,
            mock_capability_types,
            logger=logger,
            _component=component,
        )

    def test_state_changes_with_connect_and_disconnect(
        self,
        component,
        component_manager,
        mock_op_state_model,
        mock_obs_state_model,
        initial_power_mode,
        initial_fault,
    ):
        """
        Test that the state model updates with component connection and disconnection.

        :param component_manager: the component manager under test
        :param mock_op_state_model: a mock state model for testing
        """
        power_mode_map = {
            PowerState.OFF: "component_off",
            PowerState.STANDBY: "component_standby",
            PowerState.ON: "component_on",
        }
        expected_action = (
            "component_fault" if initial_fault else power_mode_map[initial_power_mode]
        )

        assert not component_manager.is_communicating

        # While disconnected, tell the component to simulate an obsfault
        # (but only if it is turned on and not faulty)
        if initial_power_mode == PowerState.ON and not initial_fault:
            component.simulate_obsfault(True)

            # The component is disconnected, so the state model cannot
            # know that it has changed obs state
            mock_obs_state_model.to_OBSFAULT.assert_not_called()

        component_manager.start_communicating()
        assert component_manager.is_communicating
        assert mock_op_state_model.perform_action.call_args_list == [
            (("component_unknown",),),
            ((expected_action,),),
        ]

        if initial_power_mode == PowerState.ON and not initial_fault:
            # The component manager has noticed that it missed a change
            # in the component while it was disconnected, and his
            # updated the obs state model
            mock_obs_state_model.to_OBSFAULT.assert_called_once_with()

        mock_op_state_model.reset_mock()

        component_manager.stop_communicating()
        assert not component_manager.is_communicating
        mock_op_state_model.perform_action.assert_called_once_with(
            "component_disconnected"
        )

    def test_simulate_communication_failure(
        self, component_manager, mock_op_state_model
    ):
        """
        Test that we can simulate connection failure.

        :param component_manager: the component manager under test
        :param mock_op_state_model: a mock state model for testing
        """
        component_manager.start_communicating()
        assert component_manager.is_communicating

        mock_op_state_model.reset_mock()
        component_manager.simulate_communication_failure(True)
        assert not component_manager.is_communicating
        mock_op_state_model.perform_action.assert_called_once_with("component_unknown")

        with pytest.raises(ConnectionError, match="Failed to connect"):
            component_manager.start_communicating()

    @pytest.mark.parametrize("command", ["off", "standby", "on"])
    def test_base_command_fails_when_disconnected(self, component_manager, command):
        """
        Test that component commands fail when there's no connection to the component.

        :param component_manager: the component manager under test
        :param command: the command under test
        """
        assert not component_manager.is_communicating
        with pytest.raises(ConnectionError, match="Not connected"):
            getattr(component_manager, command)()

        component_manager.start_communicating()
        assert component_manager.is_communicating

        component_manager.stop_communicating()
        assert not component_manager.is_communicating
        with pytest.raises(ConnectionError, match="Not connected"):
            getattr(component_manager, command)()

    @pytest.mark.parametrize(
        ("command", "action"),
        [
            ("off", "component_off"),
            ("standby", "component_standby"),
            ("on", "component_on"),
        ],
    )
    def test_base_command_succeeds_when_connected(
        self,
        component_manager,
        mock_op_state_model,
        initial_power_mode,
        initial_fault,
        command,
        action,
    ):
        """
        Test that component commands succeed when there's a connection to the component.

        :param component_manager: the component manager under test
        :param mock_op_state_model: a mock state model for testing
        :param command: the name of the command under test
        :param action: the action that is expected to be performed on
            the state model
        """
        power_mode_map = {
            PowerState.OFF: "component_off",
            PowerState.STANDBY: "component_standby",
            PowerState.ON: "component_on",
        }

        component_manager.start_communicating()
        mock_op_state_model.reset_mock()

        raise_context = (
            pytest.raises(ComponentFault, match="")
            if initial_fault
            else contextlib.nullcontext()
        )

        with raise_context:
            getattr(component_manager, command)()

            if power_mode_map[initial_power_mode] == action:
                mock_op_state_model.perform_action.assert_not_called()
            else:
                mock_op_state_model.perform_action.assert_called_once_with(action)

    @pytest.mark.parametrize(
        ("call", "action"),
        [
            ("simulate_off", "component_off"),
            ("simulate_standby", "component_standby"),
            ("simulate_on", "component_on"),
        ],
    )
    def test_simulated_change_propagates(
        self,
        component_manager,
        mock_op_state_model,
        component,
        initial_power_mode,
        initial_fault,
        call,
        action,
    ):
        """
        Test that component changes propagate up to the state model.

        Specifically, test that spontaneous changes to the state of the
        component result in the correct action being performed on the
        state model.

        :param component_manager: the component manager under test
        :param mock_op_state_model: a mock state model for testing
        :param state:
        :param action: the action that is expected to be performed on
            the state model
        """
        power_mode_map = {
            PowerState.OFF: "component_off",
            PowerState.STANDBY: "component_standby",
            PowerState.ON: "component_on",
        }

        component_manager.start_communicating()
        mock_op_state_model.reset_mock()

        raise_context = (
            pytest.raises(ComponentFault, match="")
            if initial_fault
            else contextlib.nullcontext()
        )

        with raise_context:
            getattr(component, call)()
            if action == power_mode_map[initial_power_mode]:
                mock_op_state_model.perform_action.assert_not_called()
            else:
                mock_op_state_model.perform_action.assert_called_once_with(action)

    def test_reset_from_fault(
        self, component_manager, mock_op_state_model, initial_fault
    ):
        """Test that the component manager can reset a faulty component."""
        component_manager.start_communicating()
        assert component_manager.faulty == initial_fault
        mock_op_state_model.reset_mock()

        component_manager.reset()
        assert not component_manager.faulty
        mock_op_state_model.perform_action.assert_not_called()

    def test_assign(
        self,
        component_manager,
        initial_power_mode,
        initial_fault,
        mock_obs_state_model,
        mock_resource_factory,
    ):
        """Test management of a component during assignment of resources."""
        component_manager.start_communicating()

        mock_resource_1 = mock_resource_factory()
        mock_resource_2 = mock_resource_factory()

        component_manager.assign([mock_resource_1])
        mock_obs_state_model.perform_action.assert_called_once_with(
            "component_resourced"
        )
        mock_obs_state_model.reset_mock()

        component_manager.assign([mock_resource_2])
        mock_obs_state_model.perform_action.assert_not_called()

        component_manager.release([mock_resource_1])
        mock_obs_state_model.perform_action.assert_not_called()

        component_manager.release([mock_resource_2])
        mock_obs_state_model.perform_action.assert_called_once_with(
            "component_unresourced"
        )
        mock_obs_state_model.reset_mock()

        component_manager.assign([mock_resource_1, mock_resource_2])
        mock_obs_state_model.perform_action.assert_called_once_with(
            "component_resourced"
        )
        mock_obs_state_model.reset_mock()

        component_manager.release_all()
        mock_obs_state_model.perform_action.assert_called_once_with(
            "component_unresourced"
        )

    def test_configure(
        self,
        component_manager,
        initial_power_mode,
        initial_fault,
        mock_obs_state_model,
        mock_resource_factory,
        mock_config_factory,
    ):
        """Test management of a component through configuration."""
        component_manager.start_communicating()

        mock_resource = mock_resource_factory()
        mock_configuration_1 = mock_config_factory()
        mock_configuration_2 = mock_config_factory()

        raise_context = (
            pytest.raises(ComponentFault, match="")
            if initial_fault
            else pytest.raises(ComponentError, match="Component is not ON")
            if initial_power_mode != PowerState.ON
            else contextlib.nullcontext()
        )

        with raise_context:
            component_manager.assign([mock_resource])
            mock_obs_state_model.perform_action.assert_called_once_with(
                "component_resourced"
            )
            mock_obs_state_model.reset_mock()

            component_manager.configure(mock_configuration_1)
            mock_obs_state_model.perform_action.assert_called_once_with(
                "component_configured"
            )
            mock_obs_state_model.reset_mock()

            component_manager.configure(mock_configuration_2)
            mock_obs_state_model.perform_action.assert_not_called()

            component_manager.deconfigure()
            mock_obs_state_model.perform_action.assert_called_once_with(
                "component_unconfigured"
            )
            mock_obs_state_model.reset_mock()

    def test_scan(
        self,
        component_manager,
        component,
        initial_power_mode,
        initial_fault,
        mock_obs_state_model,
        mock_resource_factory,
        mock_config_factory,
        mock_scan_args,
    ):
        """Test management of a scanning component."""
        component_manager.start_communicating()

        mock_resource = mock_resource_factory()
        mock_configuration = mock_config_factory()

        raise_context = (
            pytest.raises(ComponentFault, match="")
            if initial_fault
            else pytest.raises(ComponentError, match="Component is not ON")
            if initial_power_mode != PowerState.ON
            else contextlib.nullcontext()
        )

        with raise_context:
            component_manager.assign([mock_resource])
            component_manager.configure(mock_configuration)
            mock_obs_state_model.reset_mock()

            component_manager.scan(mock_scan_args)
            mock_obs_state_model.perform_action.assert_called_once_with(
                "component_scanning"
            )
            mock_obs_state_model.reset_mock()

            component_manager.end_scan()
            mock_obs_state_model.perform_action.assert_called_once_with(
                "component_not_scanning"
            )
            mock_obs_state_model.reset_mock()

            component_manager.scan(mock_scan_args)
            mock_obs_state_model.perform_action.assert_called_once_with(
                "component_scanning"
            )
            mock_obs_state_model.reset_mock()

            component.simulate_scan_stopped()
            mock_obs_state_model.perform_action.assert_called_once_with(
                "component_not_scanning"
            )
            mock_obs_state_model.reset_mock()

    def test_obsfault_reset_restart(
        self,
        component_manager,
        component,
        initial_power_mode,
        initial_fault,
        mock_obs_state_model,
        mock_resource_factory,
        mock_config_factory,
        mock_scan_args,
    ):
        """Test management of a faulting component."""
        component_manager.start_communicating()

        mock_resource = mock_resource_factory()
        mock_configuration = mock_config_factory()

        raise_context = (
            pytest.raises(ComponentFault, match="")
            if initial_fault
            else pytest.raises(ComponentError, match="Component is not ON")
            if initial_power_mode != PowerState.ON
            else contextlib.nullcontext()
        )

        with raise_context:
            component_manager.assign([mock_resource])
            component_manager.configure(mock_configuration)
            component_manager.scan(mock_scan_args)
            mock_obs_state_model.reset_mock()

            component.simulate_obsfault(True)
            mock_obs_state_model.perform_action.assert_called_once_with(
                "component_obsfault"
            )
            mock_obs_state_model.reset_mock()

            component.simulate_obsfault(False)
            component_manager.obsreset()
            mock_obs_state_model.perform_action.assert_called_once_with(
                "component_unconfigured"
            )

            component_manager.configure(mock_configuration)
            component_manager.scan(mock_scan_args)
            mock_obs_state_model.reset_mock()

            component.simulate_obsfault(True)
            mock_obs_state_model.perform_action.assert_called_once_with(
                "component_obsfault"
            )
            mock_obs_state_model.reset_mock()

            component.simulate_obsfault(False)
            component_manager.restart()
            assert mock_obs_state_model.perform_action.call_args_list == [
                (("component_unconfigured",),),
                (("component_unresourced",),),
            ]
