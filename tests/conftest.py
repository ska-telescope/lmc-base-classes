"""
A module defining a list of fixtures that are shared across all ska_tango_base tests.
"""
from collections import defaultdict
import importlib
import itertools
import json
import pytest
from queue import Empty, Queue
from transitions import MachineError

from tango import DevState, EventType
from tango.test_context import DeviceTestContext

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
        "actions in the specification provided in its argument."
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
            expected[(transition["from"], transition["trigger"])
                     ] = states[transition["to"]]
        test_cases = list(itertools.product(sorted(states), sorted(triggers)))
        test_ids = [f"{state}-{trigger}" for (state, trigger) in test_cases]

        metafunc.parametrize(
            "state_under_test, action_under_test, expected_state",
            [
                (
                    states[state],
                    trigger,
                    expected[(state, trigger)]
                ) for (state, trigger) in test_cases
            ],
            ids=test_ids
        )


class StateMachineTester:
    """
    Abstract base class for a class for testing state machines
    """

    def test_state_machine(
        self, machine, state_under_test, action_under_test, expected_state,
    ):
        """
        Implements the unit test for a state machine: for a given
        initial state and an action, does execution of that action, from
        that state, yield the expected results? If the action was
        allowed from that state, does the machine transition to the
        correct state? If the action was not allowed from that state,
        does the machine reject the action (e.g. raise an exception or
        return an error code) and remain in the current state?

        :param machine: the state machine under test
        :type machine: state machine object instance
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
        self.to_state(machine, state_under_test)

        # Check that we are in the state under test
        self.assert_state(machine, state_under_test)

        # Test that the action under test does what we expect it to
        if expected_state is None:
            # Action should fail and the state should not change
            assert not self.is_action_allowed(machine, action_under_test)
            self.check_action_fails(machine, action_under_test)
            self.assert_state(machine, state_under_test)
        else:
            # Action should succeed
            assert self.is_action_allowed(machine, action_under_test)
            self.perform_action(machine, action_under_test)
            self.assert_state(machine, expected_state)

    def assert_state(self, machine, state):
        """
        Abstract method for asserting the current state of the state
        machine under test

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param state: the state that we are asserting to be the current
            state of the state machine under test
        :type state: string
        """
        raise NotImplementedError()

    def is_action_allowed(self, machine, action):
        """
        Abstract method for checking whether the action under test is
        allowed from the current state.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        raise NotImplementedError()

    def perform_action(self, machine, action):
        """
        Abstract method for performing an action on the state machine

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        raise NotImplementedError()

    def check_action_fails(self, machine, action):
        """
        Abstract method for asserting that an action fails if performed
        on the state machine under test in its current state.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        raise NotImplementedError()

    def to_state(self, machine, target_state):
        """
        Abstract method for getting the state machine into a target
        state.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param target_state: the state that we want to get the state
            machine under test into
        :type target_state: str
        """
        raise NotImplementedError()


class TransitionsStateMachineTester(StateMachineTester):
    """
    Concrete implementation of a StateMachineTester for a pytransitions
    state machine (with autotransitions turned on). The states and
    actions in the state machine specification must correspond exactly
    with the machine's states and triggers.
    """

    def assert_state(self, machine, state):
        """
        Assert the current state of the state machine under test.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param state: the state that we are asserting to be the current
            state of the state machine under test
        :type state: str
        """
        assert machine.state == state

    def is_action_allowed(self, machine, action):
        """
        Check whether the action under test is allowed from the current
        state.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        return action in machine.get_triggers(machine.state)

    def perform_action(self, machine, action):
        """
        Perform a given action on the state machine under test.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        machine.trigger(action)

    def check_action_fails(self, machine, action):
        """
        Check that attempting a given action on the state machine under
        test fails in its current state.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        with pytest.raises(MachineError):
            self.perform_action(machine, action)

    def to_state(self, machine, target_state):
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
        machine.trigger(f"to_{target_state}")


class ModelStateMachineTester(StateMachineTester):
    """
    Abstract base class for testing state models using state machines.

    The ``assert_state`` method has to be implemented in concrete classes,
    and the `machine` fixture must also be provided.
    """

    def assert_state(self, machine, state):
        """
        Assert the current state of this state machine, based on the
        values of the adminMode, opState and obsState attributes of this
        model.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param state: the state that we are asserting to be the current
            state of the state machine under test
        :type state: dict
        """
        raise NotImplementedError()

    def is_action_allowed(self, machine, action):
        """
        Returns whether the state machine under test thinks an action
        is permitted in its current state

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        return machine.is_action_allowed(action)

    def perform_action(self, machine, action):
        """
        Perform a given action on the state machine under test.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        machine.perform_action(action)

    def check_action_fails(self, machine, action):
        """
        Assert that performing a given action on the state maching under
        test fails in its current state.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param action: action to be performed on the state machine
        :type action: str
        """
        with pytest.raises(StateModelError):
            self.perform_action(machine, action)

    def to_state(self, machine, target_state):
        """
        Transition the state machine to a target state.

        :param machine: the state machine under test
        :type machine: state machine object instance
        :param target_state: the state that we want to get the state
            machine under test into
        :type target_state: dict
        """
        machine._straight_to_state(**target_state)


def load_data(name):
    """
    Loads a dataset by name. This implementation uses the name to find a
    JSON file containing the data to be loaded.

    :param name: name of the dataset to be loaded; this implementation
        uses the name to find a JSON file containing the data to be
        loaded.
    :type name: string
    """
    with open(f"tests/data/{name}.json", "r") as json_file:
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


@pytest.fixture(scope="class")
def tango_context(request):
    """Creates and returns a TANGO DeviceTestContext object.

    Parameters
    ----------
    request: _pytest.fixtures.SubRequest
        A request object gives access to the requesting test context.
    """
    test_properties = {
        'SKAMaster': {
            'SkaLevel': '4',
            'LoggingTargetsDefault': '',
            'GroupDefinitions': '',
            'NrSubarrays': '16',
            'CapabilityTypes': '',
            'MaxCapabilities': ['BAND1:1', 'BAND2:1']
        },
        'SKASubarray': {
            "CapabilityTypes": ["BAND1", "BAND2"],
            'LoggingTargetsDefault': '',
            'GroupDefinitions': '',
            'SkaLevel': '4',
            'SubID': '1',
        },
        'CspSubElementMaster': {
            'PowerDelayStandbyOn': '1.5',
            'PowerDelayStandbyOff': '1.0',
        },

        'CspSubElementObsDevice': {
            'DeviceID': '11',
        },
    }

    # This fixture is used to decorate classes like "TestSKABaseDevice" or
    # "TestSKALogger". We drop the first "Test" from the string to get the
    # class name of the device under test.
    # Similarly, the test module is like "test_base_device.py".  We drop the
    # first "test_" to get the module name
    test_class_name = request.cls.__name__
    class_name = test_class_name.split('Test', 1)[-1]
    module = importlib.import_module("ska_tango_base", class_name)
    class_type = getattr(module, class_name)

    tango_context = DeviceTestContext(
        class_type, properties=test_properties.get(class_name))
    tango_context.start()
    yield tango_context
    tango_context.stop()


@pytest.fixture(scope="function")
def initialize_device(tango_context):
    """Re-initializes the device.

    Parameters
    ----------
    tango_context: tango.test_context.DeviceTestContext
        Context to run a device without a database.
    """
    yield tango_context.device.Init()


@pytest.fixture(scope="function")
def tango_change_event_helper(tango_context):
    """
    Helper for testing tango change events. To use it, call the subscribe
    method with the name of the attribute for which you want change events.
    The returned value will be a callback handler that you can interrogate
    with ``assert_not_called``, ``assert_call``, ``assert_calls``, and
    ``value`` methods.::

    .. code-block:: python

        state_callback = tango_change_event_helper.subscribe("state")
        state_callback.assert_call(DevState.OFF)

        # Check that we can't turn off a device that isn't on
        with pytest.raises(DevFailed):
            tango_context.device.Off()
        state_callback.assert_not_called()

        # Now turn it on and check that we can turn it off
        tango_context.device.On()
        state_callback.assert_call(DevState.ON)

        # Or we can test a sequence of events
        tango_context.device.Off()
        tango_context.device.On()
        state_callback.assert_calls([DevState.OFF, DevState.ON])

    """

    class _Callback:
        """
        Private callback handler class, an instance of which is returned
        by the tango_change_event_helper each time it is used to
        subscribe to a change event.
        """

        @staticmethod
        def subscribe(attribute_name):
            """
            Returns an event subscriber helper object that is subscribed
            to change events on the named attribute.

            :param attribute_name: name of the attribute for which
                change events will be subscribed
            :type attribute_name: str
            :return: an event subscriber helper object
            :rtype: object
            """
            return _Callback(attribute_name)

        def __init__(self, attribute_name):
            """
            Creates an event subscriber helper object that is subscribed
            to change events on the name attribute

            :param attribute_name: name of the attribute for which
                change events will be subscribed
            :type attribute_name: str
            """
            self._value = None
            self._values_queue = Queue()
            self._errors = []

            # Subscription will result in an immediate
            # synchronous callback with the current value,
            # so keep this as the last step in __init__.
            self._id = tango_context.device.subscribe_event(
                attribute_name, EventType.CHANGE_EVENT, self
            )

        def __del__(self):
            """
            Unsubscribe from events before object is destroyed
            """
            if hasattr(self, "_id"):
                tango_context.device.unsubscribe_event(self._id)

        def __call__(self, event_data):
            """
            Event subscription callback

            :param event_data: data about the change events
            :type event_data: :py:class:`tango.EventData`
            """
            if event_data.err:
                error = event_data.errors[0]
                self._errors.append(
                    "Event callback error: [%s] %s" % (error.reason, error.desc))
            else:
                self._values_queue.put(event_data.attr_value.value)

        def _next(self):
            """
            Gets the attribute value from the next event if there is
            one or if it arrives in time.

            :return: the attribute value reported in next change event,
                or None if there is no event
            :rtype: same as attribute type
            """
            assert not self._errors, f"Some errors: {self._errors}"
            try:
                return self._values_queue.get(timeout=1.5)
            except Empty:
                return None

        def assert_not_called(self):
            """
            Assert that there are no new callbacks calls. (That is,
            there are no callback calls that have not already been
            consumed by an ``assert_call`` or ``assert_calls``.)
            """
            assert self._values_queue.empty()

        def assert_call(self, value):
            """
            Asserts that this callback has been called with a change
            event that updates the attribute value to a given value.

            Note that this method consumes a single event, but may leave
            other events unconsumed.

            :param value: the value that the attribute is asserted to
                have been changed to
            :type value: same as the attribute type
            """
            assert self._next() == value

        def assert_calls(self, values):
            """
            Asserts that this callback has been called with a sequence
            of change events that update the attribute values to the
            given sequence of values.

            Note that this method consumes the events associated with
            the given values, but may leave subsequent events
            unconsumed.

            :param values: sequence of values that the attribute
                is asserted to have been changed to
            :type values: list
            """
            for value in values:
                self.assert_call(value)

    yield _Callback
