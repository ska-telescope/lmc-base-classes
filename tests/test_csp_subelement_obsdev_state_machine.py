"""
Module to test the transitions of a CSP SubElement ObsDevice 
(ska.base.csp_subelement_obsdev_state_machine module).
"""
import pytest

from ska.base.csp_subelement_state_machine import (
    CspSubElementObsDeviceStateMachine,
)
from .conftest import load_state_machine_spec, TransitionsStateMachineTester


@pytest.mark.state_machine_tester(load_state_machine_spec("csp_subelement_obsdev_transitions"))
class TestCspSubElementObsDeviceStateMachine(TransitionsStateMachineTester):
    """
    This class contains the test for the CspSubElementObsDeviceStateMachine class.
    """

    @pytest.fixture
    def machine(self):
        """
        Fixture that returns the state machine under test in this class

        :yields: the state machine under test
        """
        yield CspSubElementObsDeviceStateMachine()
