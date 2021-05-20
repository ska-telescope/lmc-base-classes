"""
Tests for the
:py:mod:`ska_tango_base.csp_subelement_subarray_component_manager`
module.
"""
import contextlib
import itertools

import pytest

from ska_tango_base.faults import ComponentError, ComponentFault
from ska_tango_base.csp_subelement_subarray_component_manager import (
    CspSubelementSubarrayComponentManager,
)
from ska_tango_base.control_model import PowerMode


class TestCspSubelementSubarrayComponentManager:
    """
    Tests of the
    :py:class:`ska_tango_base.csp_subelement_subarray_component_manager.SubarrayComponentManager`
    class.
    """

    @pytest.fixture()
    def mock_op_state_model(self, mocker):
        """
        Fixture that returns a mock op state model

        :param mocker: pytest fixture that wraps
            :py:mod:`unittest.mock`.

        :return: a mock state model
        """
        return mocker.Mock()

    @pytest.fixture()
    def mock_obs_state_model(self, mocker):
        """
        Fixture that returns a mock observation state model

        :param mocker: pytest fixture that wraps
            :py:mod:`unittest.mock`.

        :return: a mock state model
        """
        return mocker.Mock()

    @pytest.fixture()
    def mock_resource_factory(self, mocker):
        return mocker.Mock

    @pytest.fixture()
    def mock_capability_types(self, mocker):
        return ["foo", "bah"]

    @pytest.fixture()
    def mock_config_factory(self):
        mock_config_generator = ({"id": f"mock_id_{i}"} for i in itertools.count(1))
        return lambda: next(mock_config_generator)

    @pytest.fixture()
    def mock_scan_args(self, mocker):
        return mocker.Mock()

    @pytest.fixture(params=[PowerMode.OFF, PowerMode.STANDBY, PowerMode.ON])
    def initial_power_mode(self, request):
        return request.param

    @pytest.fixture(params=[False, True])
    def initial_fault(self, request):
        return request.param

    @pytest.fixture()
    def component(self, mock_capability_types, initial_power_mode, initial_fault):
        return CspSubelementSubarrayComponentManager._CspSubelementSubarrayComponent(
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
        Fixture that returns the component manager under test

        :param mock_op_state_model: a mock state model for testing
        :param logger: a logger for the component manager

        :return: the component manager under test
        """
        return CspSubelementSubarrayComponentManager(
            mock_op_state_model,
            mock_obs_state_model,
            mock_capability_types,
            logger,
            _component=component,
        )

    def test_state_changes_with_connect_and_disconnect(
        self, component_manager, mock_op_state_model, initial_power_mode, initial_fault
    ):
        """
        Test that the state model is updated with state changes when the
        component manager connects to and disconnects from its
        component.

        :param component_manager: the component manager under test
        :param mock_op_state_model: a mock state model for testing
        """
        power_mode_map = {
            PowerMode.OFF: "component_off",
            PowerMode.STANDBY: "component_standby",
            PowerMode.ON: "component_on",
        }
        expected_action = (
            "component_fault" if initial_fault else power_mode_map[initial_power_mode]
        )

        assert not component_manager.is_connected
        component_manager.connect()
        assert component_manager.is_connected
        assert mock_op_state_model.perform_action.call_args_list == [
            (("component_unknown",),),
            ((expected_action,),),
        ]

        mock_op_state_model.reset_mock()

        component_manager.disconnect()
        assert not component_manager.is_connected
        mock_op_state_model.perform_action.assert_called_once_with(
            "component_disconnected"
        )

    def test_simulate_connection_failure(self, component_manager, mock_op_state_model):
        """
        Test that we can simulate connection failure.

        :param component_manager: the component manager under test
        :param mock_op_state_model: a mock state model for testing
        """
        component_manager.connect()
        assert component_manager.is_connected

        mock_op_state_model.reset_mock()
        component_manager.simulate_connection_failure(True)
        assert not component_manager.is_connected
        mock_op_state_model.perform_action.assert_called_once_with("component_unknown")

        with pytest.raises(ConnectionError, match="Failed to connect"):
            component_manager.connect()

    @pytest.mark.parametrize("command", ["off", "standby", "on"])
    def test_base_command_fails_when_disconnected(self, component_manager, command):
        """
        Test that component commands fail when the component manager
        isn't connected to the component.

        :param component_manager: the component manager under test
        :param command: the command under test
        """
        assert not component_manager.is_connected
        with pytest.raises(ConnectionError, match="Not connected"):
            getattr(component_manager, command)()

        component_manager.connect()
        assert component_manager.is_connected

        component_manager.disconnect()
        assert not component_manager.is_connected
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
        Test that component commands succeed when the component manager
        is connected to the component.

        :param component_manager: the component manager under test
        :param mock_op_state_model: a mock state model for testing
        :param command: the name of the command under test
        :param action: the action that is expected to be performed on
            the state model
        """
        power_mode_map = {
            PowerMode.OFF: "component_off",
            PowerMode.STANDBY: "component_standby",
            PowerMode.ON: "component_on",
        }

        component_manager.connect()
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
        Test that spontaneous changes to the state of the component
        result in the correct action being performed on the state model.

        :param component_manager: the component manager under test
        :param mock_op_state_model: a mock state model for testing
        :param state:
        :param action: the action that is expected to be performed on
            the state model
        """
        power_mode_map = {
            PowerMode.OFF: "component_off",
            PowerMode.STANDBY: "component_standby",
            PowerMode.ON: "component_on",
        }

        component_manager.connect()
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
        component_manager.connect()
        assert component_manager.faulty == initial_fault
        mock_op_state_model.reset_mock()

        component_manager.reset()
        assert not component_manager.faulty
        mock_op_state_model.perform_action.assert_not_called()

    def test_assign(
        self,
        component_manager,
        component,
        initial_power_mode,
        initial_fault,
        mock_obs_state_model,
        mock_resource_factory,
    ):
        component_manager.connect()

        mock_resource_1 = mock_resource_factory()
        mock_resource_2 = mock_resource_factory()

        raise_context = (
            pytest.raises(ComponentFault, match="")
            if initial_fault
            else pytest.raises(ComponentError, match="Component is not ON")
            if initial_power_mode != PowerMode.ON
            else contextlib.nullcontext()
        )

        with raise_context:
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
        component,
        initial_power_mode,
        initial_fault,
        mock_obs_state_model,
        mock_resource_factory,
        mock_config_factory,
    ):
        component_manager.connect()

        mock_resource = mock_resource_factory()
        mock_configuration_1 = mock_config_factory()
        mock_configuration_2 = mock_config_factory()

        raise_context = (
            pytest.raises(ComponentFault, match="")
            if initial_fault
            else pytest.raises(ComponentError, match="Component is not ON")
            if initial_power_mode != PowerMode.ON
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
        component_manager.connect()

        mock_resource = mock_resource_factory()
        mock_configuration = mock_config_factory()

        raise_context = (
            pytest.raises(ComponentFault, match="")
            if initial_fault
            else pytest.raises(ComponentError, match="Component is not ON")
            if initial_power_mode != PowerMode.ON
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
        component_manager.connect()

        mock_resource = mock_resource_factory()
        mock_configuration = mock_config_factory()

        raise_context = (
            pytest.raises(ComponentFault, match="")
            if initial_fault
            else pytest.raises(ComponentError, match="Component is not ON")
            if initial_power_mode != PowerMode.ON
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
