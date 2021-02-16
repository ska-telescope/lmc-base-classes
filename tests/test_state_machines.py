"""
This module contains the tests for the ska_tango_base.state_machine module.
"""
import pytest

from ska_tango_base.state_machine import (
    AdminModeStateMachine,
    OperationStateMachine,
    ObservationStateMachine,
)
from .conftest import load_state_machine_spec, TransitionsStateMachineTester


@pytest.mark.state_machine_tester(load_state_machine_spec("operation_state_machine"))
class TestOperationStateMachine(TransitionsStateMachineTester):
    """
    This class contains the test for the DeviceStateMachine class.
    """

    @pytest.fixture
    def machine(self):
        """
        Fixture that returns the state machine under test in this class

        :yields: the state machine under test
        """
        yield OperationStateMachine()


@pytest.mark.state_machine_tester(load_state_machine_spec("admin_mode_state_machine"))
class TestAdminModeStateMachine(TransitionsStateMachineTester):
    """
    This class contains the test for the DeviceStateMachine class.
    """

    @pytest.fixture
    def machine(self):
        """
        Fixture that returns the state machine under test in this class

        :yields: the state machine under test
        """
        yield AdminModeStateMachine()


@pytest.mark.state_machine_tester(load_state_machine_spec("observation_state_machine"))
class TestObservationStateMachine(TransitionsStateMachineTester):
    """
    This class contains the test for the ObservationStateMachine class.
    """

    @pytest.fixture
    def machine(self):
        """
        Fixture that returns the state machine under test in this class

        :yields: the state machine under test
        """
        yield ObservationStateMachine()
