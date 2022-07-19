# pylint: skip-file  # TODO: Incrementally lint this repo
"""This module implements infrastructure for mocking callbacks and other callables."""
from __future__ import annotations

import queue
import unittest.mock
from typing import Any, Optional, Sequence, Tuple

import tango

__all__ = ["MockCallable", "MockChangeEventCallback"]


class MockCallable:
    """
    This class implements a mock callable.

    It is useful for when you want to assert that a callable is called,
    but the callback is called asynchronously, so that you might have to
    wait a short time for the call to occur.

    If you use a regular mock for the callback, your tests will end up
    littered with sleeps:

    .. code-block:: python

        proxy.start_communicating()
        communication_status_changed_callback.assert_called_once_with(
            CommunicationStatus.NOT_ESTABLISHED
        )
        time.sleep(0.1)
        communication_status_changed_callback.assert_called_once_with(
            CommunicationStatus.ESTABLISHED
        )

    These sleeps waste time, slow down the tests, and they are difficult
    to tune: maybe you only need to sleep 0.1 seconds on your
    development machine, but what if the CI pipeline deploys the tests
    to an environment that needs 0.2 seconds for this?

    This class solves that by putting each call to the callback onto a
    queue. Then, each time we assert that a callback was called, we get
    a call from the queue, waiting if necessary for the call to arrive,
    but with a timeout:

    .. code-block:: python

        proxy.start_communicating()
        communication_status_changed_callback.assert_next_call(
            CommunicationStatus.NOT_ESTABLISHED
        )
        communication_status_changed_callback.assert_next_call(
            CommunicationStatus.ESTABLISHED
        )
    """

    def __init__(
        self: MockCallable,
        return_value: Any = None,
        called_timeout: float = 5.0,
        not_called_timeout: float = 1.0,
    ):
        """
        Initialise a new instance.

        :param return_value: what to return when called
        :param called_timeout: how long to wait for a call to occur when
            we are expecting one. It makes sense to wait a long time for
            the expected call, as it will generally arrive much much
            sooner anyhow, and failure for the call to arrive in time
            will cause the assertion to fail. The default is 5 seconds.
        :param not_called_timeout: how long to wait for a callback when
            we are *not* expecting one. Since we need to wait the full
            timeout period in order to determine that a callback has not
            arrived, asserting that a call has not been made can
            severely slow down your tests. By keeping this timeout quite
            short, we can speed up our tests, at the risk of prematurely
            passing an assertion. The default is 0.5
        """
        self._return_value: Any = return_value
        self._called_timeout = called_timeout
        self._not_called_timeout = not_called_timeout
        self._queue: queue.SimpleQueue = queue.SimpleQueue()

    def __call__(self: MockCallable, *args: Any, **kwargs: Any) -> Any:
        """
        Handle a callback call.

        Create a standard mock, call it, and put it on the queue. (This
        approach lets us take advantange of the mock's assertion
        functionality later.)

        :param args: positional args in the call
        :param kwargs: keyword args in the call

        :return: the object's return calue
        """
        called_mock = unittest.mock.Mock()
        called_mock(*args, **kwargs)
        self._queue.put(called_mock)
        return self._return_value

    def _fetch_call(
        self: MockCallable, timeout: float
    ) -> Optional[unittest.mock.Mock]:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def assert_not_called(
        self: MockCallable, timeout: Optional[float] = None
    ) -> None:
        """
        Assert that the callback still has not been called after the timeout period.

        This is a slow method because it has to wait the full timeout
        period in order to determine that the call is not coming. An
        optional timeout parameter is provided for the situation where
        you are happy for the assertion to pass after a shorter wait
        time.

        :param timeout: optional timeout for the check. If not provided, the
            default is the class setting
        """
        timeout = self._not_called_timeout if timeout is None else timeout
        called_mock = self._fetch_call(timeout)
        if called_mock is None:
            return
        called_mock.assert_not_called()  # we know this will fail and raise an exception

    def assert_next_call(
        self: MockCallable, *args: Any, **kwargs: Any
    ) -> None:
        """
        Assert the arguments of the next call to this mock callback.

        If the call has not been made, this method will wait up to the
        specified timeout for a call to arrive.

        :param args: positional args that the call is asserted to have
        :param kwargs: keyword args that the call is asserted to have

        :raises AssertionError: if the callback has not been called.
        """
        called_mock = self._fetch_call(self._called_timeout)
        assert called_mock is not None, "Callback has not been called."
        called_mock.assert_called_once_with(*args, **kwargs)

    def get_next_call(
        self: MockCallable,
    ) -> Tuple[Sequence[Any], Sequence[Any]]:
        """
        Return the arguments of the next call to this mock callback.

        This is useful for situations where you do not know exactly what
        the arguments of the next call will be, so you cannot use the
        :py:meth:`.assert_next_call` method. Instead you want to assert
        some specific properties on the arguments:

        .. code-block:: python

            (args, kwargs) = mock_callback.get_next_call()
            event_data = args[0].attr_value
            assert event_data.name == "healthState"
            assert event_data.value == HealthState.UNKNOWN
            assert event_data.quality == tango.AttrQuality.ATTR_VALID

        If the call has not been made, this method will wait up to the
        specified timeout for a call to arrive.

        :raises AssertionError: if the callback has not been called
        :return: an (args, kwargs) tuple
        """
        called_mock = self._fetch_call(self._called_timeout)
        assert called_mock is not None, "Callback has not been called."
        return called_mock.call_args

    def assert_last_call(
        self: MockCallable, *args: Any, **kwargs: Any
    ) -> None:
        """
        Assert the arguments of the last call to this mock callback.

        The "last" call is the last call before an attempt to get the
        next event times out.

        This is useful for situations where we know a device may call a
        callback several time, and we don't care too much about the
        exact order of calls, but we do know what the final call should
        be.

        :param args: positional args that the call is asserted to have
        :param kwargs: keyword args that the call is asserted to have

        :raises AssertionError: if the callback has not been called.
        """
        called_mock = None
        while True:
            next_called_mock = self._fetch_call(self._not_called_timeout)
            if next_called_mock is None:
                break
            called_mock = next_called_mock
        assert called_mock is not None, "Callback has not been called."
        called_mock.assert_called_once_with(*args, **kwargs)


class MockChangeEventCallback(MockCallable):
    """
    This class implements a mock change event callback.

    It is a special case of a :py:class:`MockCallable` where the
    callable expects to be called with event_name, event_value and
    event_quality arguments (which is how
    :py:class:`ska_low_mccs.device_proxy.MccsDeviceProxy` calls its change event
    callbacks).
    """

    def __init__(
        self: MockChangeEventCallback,
        event_name: str,
        called_timeout: float = 5.0,
        not_called_timeout: float = 0.5,
        filter_for_change: bool = False,
    ):
        """
        Initialise a new instance.

        :param event_name: the name of the event for which this callable
            is a callback
        :param called_timeout: how long to wait for a call to occur when
            we are expecting one. It makes sense to wait a long time for
            the expected call, as it will generally arrive much much
            sooner anyhow, and failure for the call to arrive in time
            will cause the assertion to fail. The default is 5 seconds.
        :param not_called_timeout: how long to wait for a callback when
            we are *not* expecting one. Since we need to wait the full
            timeout period in order to determine that a callback has not
            arrived, asserting that a call has not been made can
            severely slow down your tests. By keeping this timeout quite
            short, we can speed up our tests, at the risk of prematurely
            passing an assertion. The default is 0.5
        """
        self._event_name = event_name.lower()
        self._filter_for_change = filter_for_change
        self._previous_value = None

        super().__init__(None, called_timeout, not_called_timeout)

    def _fetch_change_event(self: MockChangeEventCallback, timeout: float):
        while True:
            called_mock = self._fetch_call(timeout)
            if called_mock is None:
                return called_mock

            (args, kwargs) = called_mock.call_args
            assert len(args) == 1
            assert not kwargs

            event = args[0]
            assert (
                not event.err
            ), f"Received failed change event: error stack is {event.errors}."

            attribute_data = event.attr_value

            if (
                self._filter_for_change
                and attribute_data.value == self._previous_value
            ):
                continue

            self._previous_value = attribute_data.value
            return (
                attribute_data.name,
                attribute_data.value,
                attribute_data.quality,
            )

    def get_next_change_event(self: MockChangeEventCallback):
        """
        Return the attribute value in the next call to this mock change event callback.

        This is useful for situations where you do not know exactly what
        the value will be, so you cannot use the
        :py:meth:`.assert_next_change_event` method. Instead you want to
        assert some specific properties on the arguments.

        :raises AssertionError: if the callback has not been called
        :return: an (args, kwargs) tuple
        """
        call_data = self._fetch_change_event(self._called_timeout)
        assert (
            call_data is not None
        ), "Change event callback has not been called"
        (call_name, call_value, _) = call_data
        assert (
            call_name.lower() == self._event_name
        ), f"Event name '{call_name.lower()}'' does not match expected name '{self._event_name}'"
        return call_value

    def assert_next_change_event(
        self: MockChangeEventCallback,
        value: Any,
        quality: tango.AttrQuality = tango.AttrQuality.ATTR_VALID,
    ) -> None:
        """
        Assert the arguments of the next call to this mock callback.

        If the call has not been made, this method will wait up to the
        specified timeout for a call to arrive.

        :param value: the asserted value of the change event
        :param quality: the asserted quality of the change event. This
            is optional, with a default of ATTR_VALID.

        :raises AssertionError: if the callback has not been called.
        """
        call_data = self._fetch_change_event(self._called_timeout)
        assert (
            call_data is not None
        ), "Change event callback has not been called"
        (call_name, call_value, call_quality) = call_data
        assert (
            call_name.lower() == self._event_name
        ), f"Event name '{call_name.lower()}'' does not match expected name '{self._event_name}'"
        assert (
            call_value == value
        ), f"Call value {call_value} does not match expected value {value}"
        assert (
            call_quality == quality
        ), f"Call quality {call_quality} does not match expected quality {quality}"

    def assert_not_called(self: MockChangeEventCallback):
        call_data = self._fetch_change_event(self._not_called_timeout)
        if call_data is not None:
            (_, call_value, _) = call_data
            raise AssertionError(
                f"Change event callback has been called with {call_value}"
            )
