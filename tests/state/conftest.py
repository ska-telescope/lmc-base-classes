"""
A module defining a list of fixtures that are shared across all ska_tango_base tests.
"""
from collections import defaultdict
import itertools
import json
import pytest
from transitions import MachineError

from tango import DevState

from ska_tango_base.control_model import AdminMode, ObsState
from ska_tango_base.faults import StateModelError


def pytest_configure(config):
    """
    pytest hook, used here to register custom "state_machine_tester" marks
    """
    config.addinivalue_line(
        "markers",
        "state_machine_tester: indicate that this class is state machine "
        "tester class, and tests should be parameterised by the states and "
        "actions in the specification provided in its argument.",
    )


def pytest_generate_tests(metafunc):
    """
    pytest hook that generates tests; this hook ensures that any test
    class that is marked with the `state_machine_tester` custom marker
    will have its tests parameterised by the states and actions in the
    specification provided by that mark
    """
    mark = metafunc.definition.get_closest_marker("state_machine_tester")
    if mark:
        spec = mark.args[0]

        states = {state: spec["states"][state] or state for state in spec["states"]}

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
    """
    Abstract base class for a class for testing state machines
    """

    def test_state_machine(
        self,
        machine_under_test,
        state_under_test,
        action_under_test,
        expected_state,
    ):
        """
        Implements the unit test for a state machine: for a given
        initial state and an action, does execution of that action, from
        that state, yield the expected results? If the action was
        allowed from that state, does the machine transition to the
        correct state? If the action was not allowed from that state,
        does the machine reject the action (e.g. raise an exception or
        return an error code) and remain in the current state?

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param state_under_test: the state from which the
            `action_under_test` is being tested
        :type state_under_test: string
        :param action_under_test: the action being tested from the
            `state_under_test`
        :type action_under_test: string
        :param expected_state: the state to which the machine is
            expected to transition, as a result of performing the
            `action_under_test` in the `state_under_test`. If None, then
            the action should be disallowed and result in no change of
            state.
        :type expected_state: string

        """
        # Put the device into the state under test
        self.to_state(machine_under_test, state_under_test)

        # Check that we are in the state under test
        self.assert_state(machine_under_test, state_under_test)

        # Test that the action under test does what we expect it to
        if expected_state is None:
            # Action should fail and the state should not change
            assert not self.is_action_allowed(machine_under_test, action_under_test)
            self.check_action_fails(machine_under_test, action_under_test)
            self.assert_state(machine_under_test, state_under_test)
        else:
            # Action should succeed
            assert self.is_action_allowed(machine_under_test, action_under_test)
            self.perform_action(machine_under_test, action_under_test)
            self.assert_state(machine_under_test, expected_state)

    def assert_state(self, machine_under_test, state):
        """
        Abstract method for asserting the current state of the state
        machine under test

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param state: the state that we are asserting to be the current
            state of the state machine under test
        :type state: string
        """
        raise NotImplementedError()

    def is_action_allowed(self, machine_under_test, action):
        """
        Abstract method for checking whether the action under test is
        allowed from the current state.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        raise NotImplementedError()

    def perform_action(self, machine_under_test, action):
        """
        Abstract method for performing an action on the state machine

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        raise NotImplementedError()

    def check_action_fails(self, machine_under_test, action):
        """
        Abstract method for asserting that an action fails if performed
        on the state machine under test in its current state.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        raise NotImplementedError()

    def to_state(self, machine_under_test, target_state):
        """
        Abstract method for getting the state machine into a target
        state.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param target_state_kwargs: specification of the target state
            of the machine under test
        :type target_state_kwargs: Any
        """
        raise NotImplementedError()


class TransitionsStateMachineTester(StateMachineTester):
    """
    Concrete implementation of a StateMachineTester for a pytransitions
    state machine (with autotransitions turned on). The states and
    actions in the state machine specification must correspond exactly
    with the machine's states and triggers.
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
        Check whether the action under test is allowed from the current
        state.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        return action in machine_under_test.get_triggers(machine_under_test.state)

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
        Check that attempting a given action on the state machine under
        test fails in its current state.

        :param machine_under_test: the state machine under test
        :type machine_under_test: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        with pytest.raises(MachineError):
            self.perform_action(machine_under_test, action)

    def to_state(self, machine_under_test, target_state):
        """
        Transition the state machine to a target state. This
        implementation uses autotransitions. If the pytransitions state
        machine under test has autotransitions turned off, then this
        method will need to be overridden by some other method of
        putting the machine into the state under test.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param target_state: the state that we want to get the state
            machine under test into
        :type target_state: str
        """
        machine_under_test.trigger(f"to_{target_state}")


class StateModelTester(StateMachineTester):
    """
    Abstract base class for testing state models using state machines.

    The ``assert_state`` method has to be implemented in concrete classes,
    and the `machine_under_test` fixture must also be provided.
    """

    def assert_state(self, machine_under_test, state):
        """
        Assert the current state of the state model under test.

        :param machine_under_test: the state model under test
        :type machine_under_test: object
        :param state: the state that we are asserting to be the current
            state of the state machine under test
        :type state: dict
        """
        raise NotImplementedError()

    def is_action_allowed(self, machine_under_test, action):
        """
        Returns whether the state machine under test thinks an action
        is permitted in its current state

        :param machine_under_test: the state model under test
        :type machine_under_test: object
        :param action: action to be performed on the state machine
        :type action: str
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
        Assert that performing a given action on the state maching under
        test fails in its current state.

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
        machine_under_test._straight_to_state(**target_state)


def load_data(name):
    """
    Loads a dataset by name. This implementation uses the name to find a
    JSON file containing the data to be loaded.

    :param name: name of the dataset to be loaded; this implementation
        uses the name to find a JSON file containing the data to be
        loaded.
    :type name: string
    """
    with open(f"tests/state/data/{name}.json", "r") as json_file:
        return json.load(json_file)


def load_state_machine_spec(name):
    """
    Loads a state machine specification by name.

    :param name: name of the dataset to be loaded; this implementation
        uses the name to find a JSON file containing the data to be
        loaded.
    :type name: string
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
