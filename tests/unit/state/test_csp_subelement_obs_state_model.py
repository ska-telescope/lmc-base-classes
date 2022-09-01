# type: ignore
# pylint: skip-file  # TODO: Incrementally lint this repo
"""This module tests the ``csp_subelement_obs_state_model`` module."""
import pytest

from ska_tango_base.csp.obs.obs_state_model import CspSubElementObsStateMachine

from .conftest import TransitionsStateMachineTester, load_state_machine_spec


@pytest.mark.state_machine_tester(
    load_state_machine_spec("csp_subelement_obs_state_machine")
)
class TestCspSubElementObsStateMachine(TransitionsStateMachineTester):
    """This class contains the test for the CspSubElementObsStateMachine class."""

    @pytest.fixture
    def machine_under_test(self):
        """
        Fixture that returns the state model under test in this class.

        :yield: the state machine under test
        """
        yield CspSubElementObsStateMachine()
