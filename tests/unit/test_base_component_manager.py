# pylint: skip-file  # TODO: Incrementally lint this repo
"""Tests for the :py:mod:`ska_tango_base.base.component_manager` module."""
import pytest

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import CommunicationStatus, PowerState
from ska_tango_base.executor import TaskStatus
from ska_tango_base.testing.reference import (
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

        :param logger: a logger for the component manager
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test

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
        assert (
            component_manager.communication_state
            == CommunicationStatus.DISABLED
        )
        callbacks.assert_not_called()

        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call(
            "communication_state", CommunicationStatus.ESTABLISHED
        )
        assert (
            component_manager.communication_state
            == CommunicationStatus.ESTABLISHED
        )

        callbacks.assert_call("component_state", power=PowerState.OFF)

        component_manager.stop_communicating()

        callbacks.assert_call("component_state", power=PowerState.UNKNOWN)
        callbacks.assert_call(
            "communication_state", CommunicationStatus.DISABLED
        )
        assert (
            component_manager.communication_state
            == CommunicationStatus.DISABLED
        )

    def test_simulate_communication_failure(
        self, component_manager, callbacks
    ):
        """
        Test that we can simulate connection failure.

        :param component_manager: the component manager under test
        """
        assert (
            component_manager.communication_state
            == CommunicationStatus.DISABLED
        )
        callbacks.assert_not_called()

        component_manager.simulate_communication_failure(True)

        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        assert (
            component_manager.communication_state
            == CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_not_called()

        component_manager.simulate_communication_failure(False)
        callbacks.assert_call(
            "communication_state", CommunicationStatus.ESTABLISHED
        )
        assert (
            component_manager.communication_state
            == CommunicationStatus.ESTABLISHED
        )

        callbacks.assert_call("component_state", power=PowerState.OFF)

        component_manager.simulate_communication_failure(True)
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        assert (
            component_manager.communication_state
            == CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_not_called()

        component_manager.stop_communicating()

        callbacks.assert_call("component_state", power=PowerState.UNKNOWN)
        callbacks.assert_call(
            "communication_state", CommunicationStatus.DISABLED
        )
        assert (
            component_manager.communication_state
            == CommunicationStatus.DISABLED
        )

    @pytest.mark.parametrize("command", ["off", "standby", "on"])
    def test_command_fails_when_disconnected(
        self, component_manager, callbacks, command
    ):
        """
        Test that commands fail when there is not connection to the component.

        :param component_manager: the component manager under test
        :param command: the command under test
        """
        assert (
            component_manager.communication_state
            == CommunicationStatus.DISABLED
        )
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
            component_manager.communication_state
            == CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_not_called()

        with pytest.raises(
            ConnectionError,
            match="Communication with component is not established.",
        ):
            getattr(component_manager, command)()

        component_manager.simulate_communication_failure(False)
        callbacks.assert_call(
            "communication_state", CommunicationStatus.ESTABLISHED
        )
        assert (
            component_manager.communication_state
            == CommunicationStatus.ESTABLISHED
        )
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component_manager.simulate_communication_failure(True)
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        assert (
            component_manager.communication_state
            == CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_not_called()

        with pytest.raises(
            ConnectionError,
            match="Communication with component is not established.",
        ):
            getattr(component_manager, command)()

        component_manager.stop_communicating()
        callbacks.assert_call("component_state", power=PowerState.UNKNOWN)
        callbacks.assert_call(
            "communication_state", CommunicationStatus.DISABLED
        )
        assert (
            component_manager.communication_state
            == CommunicationStatus.DISABLED
        )

        with pytest.raises(
            ConnectionError,
            match="Communication with component is not established.",
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
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """
        assert (
            component_manager.communication_state
            == CommunicationStatus.DISABLED
        )
        callbacks.assert_not_called()

        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call(
            "communication_state", CommunicationStatus.ESTABLISHED
        )
        assert (
            component_manager.communication_state
            == CommunicationStatus.ESTABLISHED
        )
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component_manager.standby(callbacks["standby_task"])
        callbacks.assert_call("standby_task", status=TaskStatus.QUEUED)
        callbacks.assert_call("standby_task", status=TaskStatus.IN_PROGRESS)
        callbacks.assert_call("standby_task", progress=33)
        callbacks.assert_call("standby_task", progress=66)
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
        callbacks.assert_call("off_task", progress=33)
        callbacks.assert_call("off_task", progress=66)
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
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call(
            "communication_state", CommunicationStatus.ESTABLISHED
        )
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component.simulate_power_state(power_state)
        if power_state == PowerState.OFF:
            callbacks.assert_not_called()
        else:
            callbacks.assert_call("component_state", power=power_state)

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
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call(
            "communication_state", CommunicationStatus.ESTABLISHED
        )
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component.simulate_fault(True)
        callbacks.assert_call("component_state", fault=True)

        component.simulate_fault(False)
        callbacks.assert_call("component_state", fault=False)

    def test_reset_from_fault(
        self,
        component_manager,
        component,
        callbacks,
    ):
        """Test that the component manager can reset a faulty component."""
        component_manager.start_communicating()
        callbacks.assert_call(
            "communication_state", CommunicationStatus.NOT_ESTABLISHED
        )
        callbacks.assert_call(
            "communication_state", CommunicationStatus.ESTABLISHED
        )
        callbacks.assert_call("component_state", power=PowerState.OFF)

        component.simulate_fault(True)
        callbacks.assert_call("component_state", fault=True)

        component_manager.reset()
        callbacks.assert_call("component_state", fault=False)
