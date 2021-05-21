"""
This module contains the tests for the
:py:mod:`ska_tango_base.base_device.admin_mode_model` module.
"""
import pytest

from ska_tango_base.control_model import AdminMode
from ska_tango_base.base_device import AdminModeModel

from .conftest import load_state_machine_spec, StateModelTester


@pytest.mark.state_machine_tester(load_state_machine_spec("admin_mode_model"))
class TestAdminModeModel(StateModelTester):
    """
    This class contains the test for the AdminModeModel class.
    """

    @pytest.fixture
    def machine_under_test(self, logger):
        """
        Fixture that returns the state model under test in this class

        :param logger: a logger for the model under test
        :type logger: :py:class:`logging.Logger`

        :returns: the state model under test
        :rtype: :py:class:`ska_tango_base.base_device.AdminModeModel`
        """
        return AdminModeModel(logger)

    def assert_state(self, machine_under_test, state):
        """
        Assert the current admin mode of the model under test

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param state: the state that we are asserting to be the current
            state of the state machine under test
        :type state: dict
        """
        assert machine_under_test.admin_mode == AdminMode[state]

    def to_state(self, machine_under_test, state):
        machine_under_test._straight_to_state(admin_mode=AdminMode[state])
