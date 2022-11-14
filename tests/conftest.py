"""This module defines elements of the pytest test harness shared by all tests."""
from __future__ import annotations

import logging
import socket
from typing import Any, Dict, Generator, List

import pytest
import pytest_mock
import tango
from ska_tango_testing.mock import MockCallableGroup
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup
from tango.test_context import DeviceTestContext, MultiDeviceTestContext, get_host_ip


@pytest.fixture(scope="class")
def device_properties() -> dict[str, Any]:
    """
    Fixture that returns device_properties to be provided to the device under test.

    This is a default implementation that provides no properties.

    :return: properties of the device under test
    """
    return {}


@pytest.fixture(name="tango_context")
def fixture_tango_context(
    device_test_config: dict[str, Any],
) -> Generator[DeviceTestContext, None, None]:
    """
    Return a Tango test context in which the device under test is running.

    :param device_test_config: specification of the device under test,
        including its properties and memorized attributes.

    :yields: a Tango test context in which the device under test is running.
    """
    component_manager_patch = device_test_config.pop("component_manager_patch", None)
    if component_manager_patch is not None:
        device_test_config["device"].create_component_manager = component_manager_patch

    tango_context = DeviceTestContext(**device_test_config, process=True)
    tango_context.start()
    yield tango_context
    tango_context.stop()


@pytest.fixture()
def device_under_test(tango_context: DeviceTestContext) -> tango.DeviceProxy:
    """
    Return a device proxy to the device under test.

    :param tango_context: a Tango test context with the specified device
        running

    :return: a proxy to the device under test
    """
    return tango_context.device


def pytest_itemcollected(item: pytest.Item) -> None:
    """
    Modify a test after it has been collected by pytest.

    This hook implementation adds the "forked" custom mark to all tests
    that use the `device_under_test` fixture, causing them to be
    sandboxed in their own process.

    :param item: the collected test for which this hook is called
    """
    if "device_under_test" in item.fixturenames:  # type: ignore[attr-defined]
        item.add_marker("forked")


@pytest.fixture()
def callbacks() -> MockCallableGroup:
    """
    Return a dictionary of callbacks with asynchrony support.

    :return: a collections.defaultdict that returns callbacks by name.
    """
    return MockCallableGroup(
        "communication_state",
        "component_state",
        "off_task",
        "standby_task",
    )


@pytest.fixture()
def change_event_callbacks() -> MockTangoEventCallbackGroup:
    """
    Return a dictionary of Tango device change event callbacks with asynchrony support.

    :return: a collections.defaultdict that returns change event
        callbacks by name.
    """
    return MockTangoEventCallbackGroup(
        "adminMode",
        "obsState",
        "state",
        "status",
        "longRunningCommandProgress",
        "longRunningCommandResult",
        "longRunningCommandStatus",
    )


@pytest.fixture()
def logger() -> logging.Logger:
    """
    Return a default logger for tests.

    :return: a default logger for tests.
    """
    return logging.Logger("Test logger")


@pytest.fixture(name="multi_device_tango_context", scope="function")
def fixture_multi_device_tango_context(
    mocker: pytest_mock.MockerFixture,
    devices_to_test: List[Dict],
) -> Generator[MultiDeviceTestContext, None, None]:
    """
    Create and return a TANGO MultiDeviceTestContext object.

    tango.DeviceProxy patched to work around a name-resolving issue.

    :param mocker: pytest fixture that wraps :py:mod:`unittest.mock`.
    :param devices_to_test: list of specifications of devices to include
        in the tango context.

    :yields: a tango context
    """

    def _get_open_port() -> int:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port

    host = get_host_ip()
    port = _get_open_port()
    device_proxy_type = tango.DeviceProxy
    mocker.patch(
        "tango.DeviceProxy",
        wraps=lambda fqdn, *args, **kwargs: device_proxy_type(
            f"tango://{host}:{port}/{fqdn}#dbase=no",
            *args,
            **kwargs,
        ),
    )
    with MultiDeviceTestContext(
        devices_to_test, host=host, port=port, process=True
    ) as context:
        yield context
