"""This module contains the tests for the ``subarray_state_model`` module."""
import pytest

from ska_tango_base.subarray.subarray_obs_state_model import _SubarrayObsStateMachine

from .conftest import load_state_machine_spec, TransitionsStateMachineTester


@pytest.mark.state_machine_tester(load_state_machine_spec("subarray_state_machine"))
class TestSubarrayObsStateMachine(TransitionsStateMachineTester):
    """This class contains the test for the SubarrayObsStateModel class."""

    @pytest.fixture
    def machine_under_test(self):
        """
        Fixture that returns the state model under test in this class.

        :yield: the state machine under test
        """
        yield _SubarrayObsStateMachine()
