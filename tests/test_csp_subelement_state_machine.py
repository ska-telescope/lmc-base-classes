"""
This module contains the tests for the ska.base.state_machine module.
"""
import pytest

from ska.base.csp_subelement_state_machine import (
    CspObservationStateMachine,
)
from .conftest import load_state_machine_spec, TransitionsStateMachineTester


@pytest.mark.state_machine_tester(load_state_machine_spec("csp_observation_state_machine"))
class TestCspObservationStateMachine(TransitionsStateMachineTester):
    """
    This class contains the test for the CspObservationStateMachine class.
    """

    @pytest.fixture
    def machine(self):
        """
        Fixture that returns the state machine under test in this class

        :yields: the state machine under test
        """
        yield CspObservationStateMachine()
