"""This module defines the test harness for all ska_tango_base tests."""
import itertools
import json
from collections import defaultdict

import pytest
from tango import DevState
from transitions import MachineError

from ska_tango_base.control_model import AdminMode, ObsState
from ska_tango_base.faults import StateModelError


def pytest_configure(config):
    """
    Configure pytest to register custom "state_machine_tester" marks.

    :param config: the pytest config object
    :type config: :py:class:`pytest.config.Config`
    """
    config.addinivalue_line(
        "markers",
        "state_machine_tester: indicate that this class is state machine "
        "tester class, and tests should be parameterised by the states and "
        "actions in the specification provided in its argument.",
    )


def pytest_generate_tests(metafunc):
    """
    Modify how pytest generates tests to support state machine testing.

    This implementation of this pytest hook ensures that any test class
    that is marked with the `state_machine_tester` custom marker will
    have its tests parameterised by the states and actions in the
    specification provided by that mark.

    :param metafunc: pytest object used to generate tests from a test
        function
    """
    mark = metafunc.definition.get_closest_marker("state_machine_tester")
    if mark:
        spec = mark.args[0]

        states = {
            state: spec["states"][state] or state for state in spec["states"]
        }

        triggers = set()
        expected = defaultdict(lambda: None)
        for transition in spec["transitions"]:
            triggers.add(transition["trigger"])
            expected[(transition["from"], transition["trigger"])] = states[
                transition["to"]
            ]
        test_cases = list(itertools.product(sorted(states), sorted(triggers)))
        test_ids = [f"{state}-{trigger}" for (state, trigger) in test_cases]

        metafunc.parametrize(
            "state_under_test, action_under_test, expected_state",
            [
                (states[state], trigger, expected[(state, trigger)])
                for (state, trigger) in test_cases
            ],
            ids=test_ids,
        )


class StateMachineTester:
    """Abstract base class for a class for testing state machines."""

    def test_state_machine(
        self,
        machine_under_test,
        state_under_test,
        action_under_test,
        expected_state,
    ):
        """
        Implements the unit test for a state machine.

        For a given initial state and an action, does execution of that
        action, from that state, yield the expected results?

        * If the action was allowed from that state, does the machine
          transition to the correct state?

        * If the action was not allowed from that state, does the
          machine reject the action (e.g. raise an exception or return
          an error code) and remain in the current state?

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param state_under_test: the state from which the
            `action_under_test` is being tested
        :type state_under_test: str
        :param action_under_test: the action being tested from the
            `state_under_test`
        :type action_under_test: str
        :param expected_state: the state to which the machine is
            expected to transition, as a result of performing the
            `action_under_test` in the `state_under_test`. If None, then
            the action should be disallowed and result in no change of
            state.
        :type expected_state: str
        """
        # Put the device into the state under test
        self.to_state(machine_under_test, state_under_test)

        # Check that we are in the state under test
        self.assert_state(machine_under_test, state_under_test)

        # Test that the action under test does what we expect it to
        if expected_state is None:
            # Action should fail and the state should not change
            assert not self.is_action_allowed(
                machine_under_test, action_under_test
            )
            self.check_action_fails(machine_under_test, action_under_test)
            self.assert_state(machine_under_test, state_under_test)
        else:
            # Action should succeed
            assert self.is_action_allowed(
                machine_under_test, action_under_test
            )
            self.perform_action(machine_under_test, action_under_test)
            self.assert_state(machine_under_test, expected_state)

    def assert_state(self, machine_under_test, state):
        """
        Assert the current state of the state machine.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param state: the state that we are asserting to be the current
            state of the state machine under test
        :type state: str

        :raises NotImplementedError: if now overriden by a concrete
            subclass
        """
        raise NotImplementedError()

    def is_action_allowed(self, machine_under_test, action):
        """
        Check whether an action on the state machine is allowed in the current state.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str

        :raises NotImplementedError: if now overriden by a concrete
            subclass
        """
        raise NotImplementedError()

    def perform_action(self, machine_under_test, action):
        """
        Perform an action on the state machine.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str

        :raises NotImplementedError: if now overriden by a concrete
            subclass
        """
        raise NotImplementedError()

    def check_action_fails(self, machine_under_test, action):
        """
        Check that an action on the state machine fails in its current state.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str

        :raises NotImplementedError: if now overriden by a concrete
            subclass
        """
        raise NotImplementedError()

    def to_state(self, machine_under_test, target_state):
        """
        Abstract method for getting the state machine into a target state.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param target_state: specification of the target state
            of the machine under test
        :type target_state: Any

        :raises NotImplementedError: if now overriden by a concrete
            subclass
        """
        raise NotImplementedError()


class TransitionsStateMachineTester(StateMachineTester):
    """
    Concrete ``StateMachineTester`` class for a pytransitions state machine.

    This class assumes pytransitions has autotransitions turned on. The
    states and actions in the state machine specification must
    correspond exactly with the machine's states and triggers.
    """

    def assert_state(self, machine_under_test, state):
        """
        Assert the current state of the state machine under test.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param state: the state that we are asserting to be the current
            state of the state machine under test
        :type state: str
        """
        assert machine_under_test.state == state

    def is_action_allowed(self, machine_under_test, action):
        """
        Check whether the action under test is allowed from the current state.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str

        :return: whether the action is allowed
        :rtype: bool
        """
        return action in machine_under_test.get_triggers(
            machine_under_test.state
        )

    def perform_action(self, machine_under_test, action):
        """
        Perform a given action on the state machine under test.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        machine_under_test.trigger(action)

    def check_action_fails(self, machine_under_test, action):
        """
        Check that the action on the state machine fails in its current state.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        with pytest.raises(MachineError):
            self.perform_action(machine_under_test, action)

    def to_state(self, machine_under_test, target_state):
        """
        Transition the state machine to a target state.

        This implementation uses autotransitions. If the pytransitions
        state machine under test has autotransitions turned off, then
        this method will need to be overridden by some other method of
        putting the machine into the state under test.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param target_state: the state that we want to get the state
            machine under test into
        :type target_state: str
        """
        machine_under_test.trigger(f"to_{target_state}")


class StateModelTester(StateMachineTester):
    """
    Abstract base class for testing state models using state machines.

    The ``assert_state`` method has to be implemented in concrete
    classes, and the `machine_under_test` fixture must also be provided.
    """

    def assert_state(self, machine_under_test, state):
        """
        Assert the current state of the state model under test.

        :param machine_under_test: the state model under test
        :type machine_under_test: object
        :param state: the state that we are asserting to be the current
            state of the state machine under test
        :type state: dict

        :raises NotImplementedError: if now overriden by a concrete
            subclass
        """
        raise NotImplementedError()

    def is_action_allowed(self, machine_under_test, action):
        """
        Return whether the state machine allows a given action in its current state.

        :param machine_under_test: the state model under test
        :type machine_under_test: object
        :param action: action to be performed on the state machine
        :type action: str

        :return: whether the action is allowed
        """
        return machine_under_test.is_action_allowed(action)

    def perform_action(self, machine_under_test, action):
        """
        Perform a given action on the state machine under test.

        :param machine_under_test: the state model under test
        :type machine_under_test: object
        :param action: action to be performed on the state machine
        :type action: str
        """
        machine_under_test.perform_action(action)

    def check_action_fails(self, machine_under_test, action):
        """
        Check that an action is not permitted in the current state machine state.

        :param machine_under_test: the state model under test
        :type machine_under_test: object
        :param action: action to be performed on the state machine
        :type action: str
        """
        with pytest.raises(StateModelError):
            self.perform_action(machine_under_test, action)

    def to_state(self, machine_under_test, target_state):
        """
        Transition the state machine to a target state.

        :param machine_under_test: the state model under test
        :type machine_under_test: object
        :param target_state: specification of the target state that we
            want to get the state machine under test into
        :type target_state: keyword dictionary
        """
        # pylint: disable-next=protected-access
        machine_under_test._straight_to_state(**target_state)


def load_data(name):
    """
    Load a dataset by name.

    This implementation uses the name to find a JSON file containing the
    data to be loaded.

    :param name: name of the dataset to be loaded; this implementation
        uses the name to find a JSON file containing the data to be
        loaded.
    :type name: str

    :return: content of the named dataset
    """
    with open(
        f"tests/unit/state/data/{name}.json", "r", encoding="utf-8"
    ) as json_file:
        return json.load(json_file)


def load_state_machine_spec(name):
    """
    Load a state machine specification by name.

    :param name: name of the dataset to be loaded; this implementation
        uses the name to find a JSON file containing the data to be
        loaded.
    :type name: str

    :return: a state machine specification
    """
    machine_spec = load_data(name)
    for state in machine_spec["states"]:
        state_spec = machine_spec["states"][state]
        if "admin_mode" in state_spec:
            state_spec["admin_mode"] = AdminMode[state_spec["admin_mode"]]
        if "op_state" in state_spec:
            state_spec["op_state"] = getattr(DevState, state_spec["op_state"])
        if "obs_state" in state_spec:
            state_spec["obs_state"] = ObsState[state_spec["obs_state"]]
    return machine_spec
