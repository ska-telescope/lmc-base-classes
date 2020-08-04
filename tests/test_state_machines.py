"""
This module contains the tests for the ska.base.state_machine module.
"""
import pytest

from ska.base.state_machine import BaseDeviceStateMachine, ObservationStateMachine
from .conftest import load_data, TransitionsStateMachineTester


@pytest.mark.state_machine_tester(load_data("base_device_state_machine"))
class BaseDeviceStateMachineTester(TransitionsStateMachineTester):
    """
    This class contains the test for the BaseDeviceStateMachine class.
    """
    @pytest.fixture
    def machine(self):
        """
        Fixture that returns the state machine under test in this class
        """
        yield BaseDeviceStateMachine()


@pytest.mark.state_machine_tester(load_data("observation_state_machine"))
class TestObservationStateMachine(TransitionsStateMachineTester):
    """
    This class contains the test for the ObservationStateMachine class.
    """
    @pytest.fixture
    def machine(self):
        """
        Fixture that returns the state machine under test in this class
        """
        yield ObservationStateMachine()
