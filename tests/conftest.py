# pylint: skip-file  # TODO: Incrementally lint this repo
"""This module defines elements of the pytest test harness shared by all tests."""
from __future__ import annotations

import collections
import logging
import socket
import time

import pytest
import tango
from tango.test_context import (
    DeviceTestContext,
    MultiDeviceTestContext,
    get_host_ip,
)

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
    component_manager_patch = device_test_config.pop(
        "component_manager_patch", None
    )
    if component_manager_patch is not None:
        device_test_config[
            "device"
        ].create_component_manager = component_manager_patch

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
    # Give the PushChanges polled command time to run once.
    time.sleep(0.15)
    # TODO: This would be better handled by waiting for the state to be OFF.

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


@pytest.fixture(scope="module")
def devices_to_test(request):
    """Fixture for devices to test."""
    raise NotImplementedError(
        "You have to specify the devices to test by overriding the 'devices_to_test' fixture."
    )


@pytest.fixture(scope="function")
def multi_device_tango_context(
    mocker, devices_to_test  # pylint: disable=redefined-outer-name
):
    """
    Create and return a TANGO MultiDeviceTestContext object.

    tango.DeviceProxy patched to work around a name-resolving issue.
    """

    def _get_open_port():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port

    HOST = get_host_ip()
    PORT = _get_open_port()
    _DeviceProxy = tango.DeviceProxy
    mocker.patch(
        "tango.DeviceProxy",
        wraps=lambda fqdn, *args, **kwargs: _DeviceProxy(
            "tango://{0}:{1}/{2}#dbase=no".format(HOST, PORT, fqdn),
            *args,
            **kwargs,
        ),
    )
    with MultiDeviceTestContext(
        devices_to_test, host=HOST, port=PORT, process=True
    ) as context:
        yield context


@pytest.fixture()
def multi_tango_change_event_helper(
    multi_device_tango_context, change_event_callbacks
):
    """
    Return a helper to simplify subscription to the multiple devices under test with a callback.

    :param multi_device_tango_context: A MultiDeviceTestContext where several devices are defined
    :param change_event_callbacks: dictionary of callbacks with
        asynchrony support, specifically for receiving Tango device
        change events.
    """

    class _TangoChangeEventHelper:
        def subscribe(self, device_name, attribute_name):
            device_under_test = multi_device_tango_context.get_device(
                device_name
            )
            device_under_test.subscribe_event(
                attribute_name,
                tango.EventType.CHANGE_EVENT,
                change_event_callbacks[attribute_name],
            )
            return change_event_callbacks[attribute_name]

    return _TangoChangeEventHelper()
