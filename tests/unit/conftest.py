"""This module defines elements of the pytest test harness shared by all tests."""
from __future__ import annotations

import collections
import logging
import time

import pytest
import tango
from tango.test_context import DeviceTestContext

from ska_tango_base.testing.mock import MockCallable, MockChangeEventCallback


@pytest.fixture(scope="class")
def device_properties():
    """
    Fixture that returns device_properties to be provided to the device under test.

    This is a default implementation that provides no properties.

    :return: properties of the device under test
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
    time.sleep(0.15)  # required because of PushChanges segfault workaround
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


@pytest.fixture()
def callbacks():
    """
    Return a dictionary of callbacks with asynchrony support.

    :return: a collections.defaultdict that returns callbacks by name.
    """
    return collections.defaultdict(MockCallable)


@pytest.fixture()
def change_event_callbacks():
    """
    Return a dictionary of Tango device change event callbacks with asynchrony support.

    :return: a collections.defaultdict that returns change event
        callbacks by name.
    """

    class _ChangeEventDict:
        def __init__(self):
            self._dict = {}

        def __getitem__(self, key):
            if key not in self._dict:
                self._dict[key] = MockChangeEventCallback(key)
            return self._dict[key]

    return _ChangeEventDict()


@pytest.fixture()
def tango_change_event_helper(device_under_test, change_event_callbacks):
    """
    Return a helper to simplify subscription to the device under test with a callback.

    :param device_under_test: a proxy to the device under test
    :param change_event_callbacks: dictionary of callbacks with
        asynchrony support, specifically for receiving Tango device
        change events.
    """

    class _TangoChangeEventHelper:
        def subscribe(self, attribute_name):
            device_under_test.subscribe_event(
                attribute_name,
                tango.EventType.CHANGE_EVENT,
                change_event_callbacks[attribute_name],
            )
            return change_event_callbacks[attribute_name]

    return _TangoChangeEventHelper()


@pytest.fixture()
def logger():
    """Fixture that returns a default logger for tests."""
    return logging.Logger("Test logger")
