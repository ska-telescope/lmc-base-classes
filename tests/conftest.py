"""
A module defining a list of fixtures that are shared across all ska_tango_base tests.
"""
import logging
from queue import Empty, Queue

import pytest
from tango import EventType
from tango.test_context import DeviceTestContext


@pytest.fixture(scope="class")
def device_properties():
    """
    Fixture that returns device_properties to be provided to the
    device under test. This is a default implementiong that provides
    no properties.
    """
    return {}


@pytest.fixture(scope="class")
def tango_context(device_test_config):
    """
    Fixture that returns a Tango DeviceTestContext object, in which the
    device under test is running.
    """
    component_manager_patch = device_test_config.pop("component_manager_patch", None)
    if component_manager_patch is not None:
        device_test_config["device"].create_component_manager = component_manager_patch

    tango_context = DeviceTestContext(**device_test_config)
    tango_context.start()
    yield tango_context
    tango_context.stop()


def pytest_itemcollected(item):
    """Make Tango-related tests run in forked mode"""
    if "tango_context" in item.fixturenames:
        item.add_marker("forked")


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
    ``value`` methods.

    .. code-block:: py

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
                    "Event callback error: [%s] %s" % (error.reason, error.desc)
                )
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


@pytest.fixture()
def logger():
    """
    Fixture that returns a default logger for tests
    """
    return logging.Logger("Test logger")
