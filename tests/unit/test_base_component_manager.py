"""Tests for the :py:mod:`ska_tango_base.base.component_manager` module."""
import pytest

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import CommunicationStatus, PowerState
from ska_tango_base.executor import TaskStatus
from ska_tango_base.testing import (
    FakeBaseComponent,
    ReferenceBaseComponentManager,
)


class TestReferenceBaseComponentManager:
    """
    This class contains tests of the ReferenceBaseComponentManager class.

    Since this is a concrete implementation of the abstract
    BaseComponentManager class, these serve as tests for that too.
    """

    @pytest.fixture()
    def component(self):
        """Return a component for testing."""
        return FakeBaseComponent()

    @pytest.fixture()
    def component_manager(self, logger, callbacks, component):
        """
        Fixture that returns the component manager under test.

        :param mock_op_state_model: a mock state model for testing
        :param logger: a logger for the component manager

        :return: the component manager under test
        """
        return ReferenceBaseComponentManager(
            logger,
            callbacks["communication_state"],
            callbacks["component_state"],
            _component=component,
        )

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
