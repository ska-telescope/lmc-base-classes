"""
Tests for the :py:mod:`skabase.component_manager` module.
"""
import contextlib
import pytest

from ska_tango_base.component_manager import ComponentFault, ComponentManager
from ska_tango_base.control_model import PowerMode


class TestComponentManager:
    """
    Tests of the :py:class:`skabase.component_manager.ComponentManager`
    class.
    """

    @pytest.fixture()
    def mock_op_state_model(self, mocker):
        """
        Fixture that returns a mock state model

        :param mocker: pytest fixture that wraps
            :py:mod:`unittest.mock`.

        :return: a mock state model
        """
        return mocker.Mock()

    @pytest.fixture(params=[PowerMode.OFF, PowerMode.STANDBY, PowerMode.ON])
    def initial_power_mode(self, request):
        return request.param

    @pytest.fixture(params=[False, True])
    def initial_fault(self, request):
        return request.param

    @pytest.fixture()
    def component(self, initial_power_mode, initial_fault):
        return ComponentManager._Component(
            _power_mode=initial_power_mode, _faulty=initial_fault
        )

    @pytest.fixture()
    def component_manager(self, mock_op_state_model, logger, component):
        """
        Fixture that returns the component manager under test

        :param mock_op_state_model: a mock state model for testing
        :param logger: a logger for the component manager

        :return: the component manager under test
        """
        return ComponentManager(mock_op_state_model, logger, _component=component)

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
        mock_op_state_model.perform_action.assert_called_once_with(expected_action)
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
    def test_command_fails_when_disconnected(self, component_manager, command):
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
    def test_command_succeeds_when_connected(
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
