"""This module contains the tests for the ``op_state_model`` module."""
import pytest

from ska_tango_base.base.op_state_model import _OpStateMachine

from .conftest import load_state_machine_spec, TransitionsStateMachineTester


@pytest.mark.state_machine_tester(load_state_machine_spec("op_state_machine"))
class TestOpStateMachine(TransitionsStateMachineTester):
    """This class contains the test for the _OpStateMachine class."""

    @pytest.fixture
    def machine_under_test(self):
        """
        Fixture that returns the state machine under test in this class.

        :yield: the state machine under test
        """
        yield _OpStateMachine()
