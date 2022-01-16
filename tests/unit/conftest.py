"""This module defines elements of the pytest test harness shared by all tests."""
from __future__ import annotations

import collections
import logging
import queue
from typing import Any, Optional, Tuple, Sequence

import pytest
from tango import EventType
from tango.test_context import DeviceTestContext


@pytest.fixture(scope="class")
def device_properties():
    """
    Fixture that returns device_properties to be provided to the device under test.

    This is a default implementation that provides no properties.
    """
    return {}


@pytest.fixture()
def tango_context(device_test_config):
    """Return a Tango test context object, in which the device under test is running."""
    component_manager_patch = device_test_config.pop("component_manager_patch", None)
    if component_manager_patch is not None:
        device_test_config["device"].create_component_manager = component_manager_patch

    tango_context = DeviceTestContext(**device_test_config)
    tango_context.start()
    yield tango_context
    tango_context.stop()


@pytest.fixture()
def device_under_test(tango_context):
    """
    Return a device proxy to the device under test.

    :param tango_context: a Tango test context with the specified device
        running
    :type tango_context: :py:class:`tango.DeviceTestContext`

    :return: a proxy to the device under test
    :rtype: :py:class:`tango.DeviceProxy`
    """
    return tango_context.device


def pytest_itemcollected(item):
    """Make Tango-related tests run in forked mode."""
    if "device_under_test" in item.fixturenames:
        item.add_marker("forked")


@pytest.fixture(scope="function")
def tango_change_event_helper(device_under_test):
    """
    Return a helper for testing tango change events.

    To use it, call the subscribe method with the name of the attribute
    for which you want change events. The returned value will be a
    callback handler that you can interrogate with
    ``assert_not_called``, ``assert_call``, ``assert_calls``, and
    ``value`` methods.

    .. code-block:: py

        state_callback = tango_change_event_helper.subscribe("state")
        state_callback.assert_call(DevState.OFF)

        # Check that we can't turn off a device that isn't on
        with pytest.raises(DevFailed):
            device_under_test.Off()
        state_callback.assert_not_called()

        # Now turn it on and check that we can turn it off
        device_under_test.On()
        state_callback.assert_call(DevState.ON)

        # Or we can test a sequence of events
        device_under_test.Off()
        device_under_test.On()
        state_callback.assert_calls([DevState.OFF, DevState.ON])

    :param device_under_test: a :py:class:`tango.DeviceProxy` to the
        device under test, running in a
        :py:class:`tango.test_context.DeviceTestContext`.
    :type device_under_test: :py:class:`tango.DeviceProxy`
    """

    class _Callback:
        """
        Private callback handler class.

        An instance is returned by the tango_change_event_helper each
        time it is used to subscribe to a change event.
        """

        @staticmethod
        def subscribe(attribute_name):
            """
            Return an instance that is subscribed to change events on a named attribute.

            :param attribute_name: name of the attribute for which
                change events will be subscribed
            :type attribute_name: str
            :return: an event subscriber helper object
            :rtype: object
            """
            return _Callback(attribute_name)

        def __init__(self, attribute_name):
            """
            Initialise a new instance.

            The instance will be subscribed to change events on the
            named attribute.

            :param attribute_name: name of the attribute for which
                change events will be subscribed
            :type attribute_name: str
            """
            self._value = None
            self._values_queue = queue.Queue()
            self._errors = []
            self._attribute_name = attribute_name

            # Subscription will result in an immediate
            # synchronous callback with the current value,
            # so keep this as the last step in __init__.
            self._id = device_under_test.subscribe_event(
                attribute_name, EventType.CHANGE_EVENT, self
            )

        def __del__(self):
            """Unsubscribe from events before object is destroyed."""
            if hasattr(self, "_id"):
                device_under_test.unsubscribe_event(self._id)

        def __call__(self, event_data):
            """
            Event subscription callback.

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
            Get the attribute value from the next event.

            A value is returned if there is already one,  or if it
            arrives in time.

            :return: the attribute value reported in next change event,
                or None if there is no event
            :rtype: same as attribute type
            """
            assert not self._errors, f"Some errors: {self._errors}"
            try:
                return self._values_queue.get(timeout=1.5)
            except queue.Empty:
                return None

        def assert_not_called(self):
            """
            Assert that there are no new callbacks calls.

            (That is, there are no callback calls that have not already
            been consumed by an ``assert_call`` or ``assert_calls``.)
            """
            assert self._values_queue.empty()

        def get_call(self):
            return self._next()

        def assert_call(self, value):
            """
            Assert a call that has been made on this callback.

            Specifically, asserts that this callback has been called
            with a change event that updates the attribute value to a
            given value.

            Note that this method consumes a single event, but may leave
            other events unconsumed.

            :param value: the value that the attribute is asserted to
                have been changed to
            :type value: same as the attribute type
            """
            assert self._next() == value

        def assert_calls(self, values):
            """
            Assert a sequence of calls that have been made on this callback.

            Specifically, assert that this callback has been called with
            a sequence of change events that update the attribute values
            to the given sequence of values.

            Note that this method consumes the events associated with
            the given values, but may leave subsequent events
            unconsumed.

            :param values: sequence of values that the attribute
                is asserted to have been changed to
            :type values: list
            """
            for value in values:
                self.assert_call(value)

        def wait_for_lrc_id(self, unique_id: str):
            """
            Wait for longRunningCommandResult unique ID to be the same as the parameter.

            :param unique_id: The long running command unique ID
            :type unique_id: str
            """
            assert (
                self._attribute_name == "longRunningCommandResult"
            ), "Method only available for longRunningCommandResult"
            while True:
                next_val = self._next()
                assert next_val, "No more events"
                if unique_id == next_val[0]:
                    break

    yield _Callback


@pytest.fixture()
def mock_callable_factory(mocker):
    """
    Return a factory that returns a mock callable each time it is called.

    The mock callables returned by this factory queue up their calls,
    allowing us to block for new calls. That means that when we are
    testing asynchronous code, we don't need to sleep while waiting for
    a callback; we can block on the queue instead.
    """

    class _MockCallable:
        """
        This class implements a mock callable.

        It is useful for when you want to assert that a callable is
        called, but the callback is called asynchronously, so that you
        might have to wait a short time for the call to occur.

        If you use a regular mock for the callback, your tests will end
        up littered with sleeps:

        .. code-block:: python

            antenna_apiu_proxy.start_communicating()
            communication_state_changed_callback.assert_called_once_with(
                CommunicationStatus.NOT_ESTABLISHED
            )
            time.sleep(0.1)
            communication_state_changed_callback.assert_called_once_with(
                CommunicationStatus.ESTABLISHED
            )

        These sleeps waste time, slow down the tests, and they are
        difficult to tune: maybe you only need to sleep 0.1 seconds on
        your development machine, but what if the CI pipeline deploys
        the tests to an environment that needs 0.2 seconds for this?

        This class solves that by putting each call to the callback onto
        a queue. Then, each time we assert that a callback was called,
        we get a call from the queue, waiting if necessary for the call
        to arrive, but with a timeout:

        .. code-block:: python

            antenna_apiu_proxy.start_communicating()
            communication_state_changed_callback.assert_next_call(
                CommunicationStatus.NOT_ESTABLISHED
            )
            communication_state_changed_callback.assert_next_call(
                CommunicationStatus.ESTABLISHED
            )
        """

        def __init__(
            self: _MockCallable,
            return_value: Any = None,
            called_timeout: float = 5.0,
            not_called_timeout: float = 0.5,
        ):
            """
            Initialise a new instance.

            :param return_value: what to return when called
            :param called_timeout: how long to wait for a call to occur
                when we are expecting one. It makes sense to wait a long
                time for the expected call, as it will generally arrive
                much much sooner anyhow, and failure for the call to
                arrive in time will cause the assertion to fail. The
                default is 5 seconds.
            :param not_called_timeout: how long to wait for a callback
                when we are *not* expecting one. Since we need to wait
                the full timeout period in order to determine that a
                callback has not arrived, asserting that a call has
                *not* is extremely costly. By keeping this timeout quite
                short, we can speed up our tests, at the risk of
                prematurely passing an assertion. The default is 0.5
                seconds.
            """
            self._return_value: Any = return_value
            self._called_timeout = called_timeout
            self._not_called_timeout = not_called_timeout
            self._queue: queue.Queue = queue.Queue()

        def __call__(self: _MockCallable, *args: Any, **kwargs: Any) -> Any:
            """
            Handle a callback call.

            Create a standard mock, call it, and put it on the queue.
            (This approach lets us take advantange of the mock's
            assertion functionality later.)

            :param args: positional args in the call
            :param kwargs: keyword args in the call

            :return: the object's return calue
            """
            called_mock = mocker.Mock()
            called_mock(*args, **kwargs)
            self._queue.put(called_mock)
            return self._return_value

        def assert_not_called(
            self: _MockCallable, timeout: Optional[float] = None
        ) -> None:
            """
            Assert that the callback still has not been called after the timeout period.

            This is a slow method because it has to wait the full
            timeout period in order to determine that the call is not
            coming. An optional timeout parameter is provided for the
            situation where you are happy for the assertion to pass
            after a shorter wait time.

            :param timeout: optional timeout for the check. If not
                provided, the default is the class setting
            """
            timeout = self._not_called_timeout if timeout is None else timeout
            try:
                called_mock = self._queue.get(timeout=timeout)
            except queue.Empty:
                return
            called_mock.assert_not_called()  # we know this will fail

        def assert_next_call(self: _MockCallable, *args: Any, **kwargs: Any) -> None:
            """
            Assert the arguments of the next call to this mock callback.

            If the call has not been made, this method will wait up to
            the specified timeout for a call to arrive.

            :param args: positional args that the call is asserted to
                have
            :param kwargs: keyword args that the call is asserted to
                have

            :raises AssertionError: if the callback has not been called.
            """
            try:
                called_mock = self._queue.get(timeout=self._called_timeout)
            except queue.Empty:
                raise AssertionError("Callback has not been called.")
            called_mock.assert_called_once_with(*args, **kwargs)

        def get_next_call(self: _MockCallable) -> Tuple[Sequence[Any], Sequence[Any]]:
            """
            Return the arguments of the next call to this mock callback.

            This is useful for situations where you do not know exactly
            what the arguments of the next call will be, so you cannot
            use the :py:meth:`.assert_next_call` method. Instead you
            want to assert some specific properties on the arguments:

            .. code-block:: python

                (args, kwargs) = mock_callback.get_next_call()
                event_data = args[0].attr_value
                assert event_data.name == "healthState"
                assert event_data.value == HealthState.UNKNOWN
                assert event_data.quality == tango.AttrQuality.ATTR_VALID

            If the call has not been made, this method will wait up to
            the specified timeout for a call to arrive.

            :raises AssertionError: if the callback has not been called
            :return: an (args, kwargs) tuple
            """
            try:
                called_mock = self._queue.get(timeout=self._called_timeout)
            except queue.Empty:
                raise AssertionError("Callback has not been called.")
            return called_mock.call_args

        def assert_last_call(self: _MockCallable, *args: Any, **kwargs: Any) -> None:
            """
            Assert the arguments of the last call to this mock callback.

            The "last" call is the last call before an attempt to get
            the next event times out.

            This is useful for situations where we know a device may
            call a callback several times, and we don't care too much
            about the exact order of calls, but we do know what the
            final call should be.

            :param args: positional args that the call is asserted to
                have
            :param kwargs: keyword args that the call is asserted to
                have

            :raises AssertionError: if the callback has not been called.
            """
            called_mock = None
            while True:
                try:
                    called_mock = self._queue.get(timeout=self._not_called_timeout)
                except queue.Empty:
                    break
            if called_mock is None:
                raise AssertionError("Callback has not been called.")

            called_mock.assert_called_once_with(*args, **kwargs)

    return _MockCallable


@pytest.fixture()
def callbacks(mock_callable_factory):
    """
    Return a dictionary of callbacks with asynchrony support.

    :param mock_callable_factory: a factory that returns mocks that can
        be used as callbacks with asynchronous support.

    :return: a collections.defaultdict that returns callbacks by name.
    """
    return collections.defaultdict(mock_callable_factory)


@pytest.fixture()
def logger():
    """Fixture that returns a default logger for tests."""
    return logging.Logger("Test logger")
