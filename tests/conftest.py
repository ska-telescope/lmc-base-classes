"""This module defines elements of the pytest test harness shared by all tests."""

from __future__ import annotations

import logging
import socket
import time
from typing import Any, Generator, cast

import pytest
import pytest_mock
import tango
from ska_control_model import ResultCode, TaskStatus
from ska_tango_testing.mock import MockCallableGroup
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup
from tango import DevError
from tango.test_context import DeviceTestContext, MultiDeviceTestContext, get_host_ip

import ska_tango_base.base.base_device
from ska_tango_base.long_running_commands_api import LrcCallback


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
        "abort_task",
    )


@pytest.fixture(name="change_event_callbacks")
def change_event_callbacks_fixture() -> MockTangoEventCallbackGroup:
    """
    Return a dictionary of Tango device change event callbacks with asynchrony support.

    :return: a collections.defaultdict that returns change event
        callbacks by name.
    """
    return MockTangoEventCallbackGroup(
        "adminMode",
        "obsState",
        "commandedObsState",
        "state",
        "commandedState",
        "status",
        "longRunningCommandProgress",
        "longRunningCommandResult",
        "longRunningCommandStatus",
        "longRunningCommandInProgress",
    )


@pytest.fixture(name="logger")
def logger_fixture() -> logging.Logger:
    """
    Return a default logger for tests.

    :return: a default logger for tests.
    """
    logger = logging.getLogger("Test logger")
    logger.setLevel(logging.INFO)
    return logger


# TODO: Placeholder for a better type specification
DeviceSpecType = dict[str, Any]


@pytest.fixture(name="multi_device_tango_context", scope="function")
def fixture_multi_device_tango_context(
    mocker: pytest_mock.MockerFixture,
    devices_to_test: DeviceSpecType,
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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", 0))
        sock.listen(1)
        port = cast(int, sock.getsockname()[1])
        sock.close()
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


@pytest.fixture()
def patch_debugger_to_start_on_ephemeral_port() -> None:
    """
    Patch the debugger so that it starts on an ephemeral port.

    This is necessary because of intermittent debugger test failures: if
    the previous test has used the debugger port, then when the test
    tries to bind to that port, it may find that the OS has not made it
    available for use yet.
    """
    # pylint: disable-next=protected-access
    ska_tango_base.base.base_device._DEBUGGER_PORT = 0


@pytest.fixture(name="successful_lrc_callback")
def successful_lrc_callback_fixture(
    logger: logging.Logger,
) -> Generator[LrcCallback, None, None]:
    """
    Use this callback with invoke_lrc when the LRC should complete successfully.

    :yields: successful_lrc_callback function.
    :raises AssertionError: if unexpected status, progress, result or error is received.
    """  # noqa DAR401,DAR402
    assert_errors: list[AssertionError] = []

    def _successful_lrc_callback(
        status: TaskStatus | None = None,
        progress: int | None = None,
        result: dict[str, Any] | list[Any] | None = None,
        error: tuple[DevError] | None = None,
        **kwargs: Any,
    ) -> None:
        try:
            if status is not None:
                logger.info(f"lrc_callback(status={status.name})")
                assert status in [
                    TaskStatus.STAGING,
                    TaskStatus.QUEUED,
                    TaskStatus.IN_PROGRESS,
                    TaskStatus.COMPLETED,
                ], f"Unexpected status: {status.name}"
            if progress is not None:
                logger.info(f"lrc_callback(progress={progress})")
                assert progress in [33, 66], f"Unexpected progress: {progress}"
            if result is not None:
                logger.info(f"lrc_callback(result={result})")
                assert isinstance(result, list) and result[0] == ResultCode.OK, {
                    f"Unexpected result: {result}"
                }
            if error is not None:
                logger.error(f"lrc_callback(error={error})")
                assert False, f"Received {error}"
            if kwargs:
                logger.error(f"lrc_callback(kwargs={kwargs})")
        except AssertionError as e:
            assert_errors.append(e)

    yield _successful_lrc_callback
    if assert_errors:
        raise assert_errors[0]


@pytest.fixture(name="aborted_lrc_callback")
def aborted_lrc_callback_fixture(
    logger: logging.Logger,
) -> Generator[LrcCallback, None, None]:
    """
    Use this callback with invoke_lrc when the LRC should be aborted after starting.

    :yields: aborted_lrc_callback function.
    :raises AssertionError: if unexpected status, progress, result or error is received.
    """  # noqa DAR401,DAR402
    assert_errors: list[AssertionError] = []

    def _aborted_lrc_callback(
        status: TaskStatus | None = None,
        progress: int | None = None,
        result: dict[str, Any] | list[Any] | None = None,
        error: tuple[DevError] | None = None,
        **kwargs: Any,
    ) -> None:
        try:
            if status is not None:
                logger.info(f"lrc_callback(status={status.name})")
                assert status in [
                    TaskStatus.STAGING,
                    TaskStatus.QUEUED,
                    TaskStatus.IN_PROGRESS,
                    TaskStatus.ABORTED,
                ], f"Unexpected status: {status.name}"
            if progress is not None:
                logger.info(f"lrc_callback(progress={progress})")
                assert False, f"Unexpected progress: {progress}"
            if result is not None:
                logger.info(f"lrc_callback(result={result})")
                assert isinstance(result, list) and result[0] == ResultCode.ABORTED, {
                    f"Unexpected result: {result}"
                }
            if error is not None:
                logger.error(f"lrc_callback(error={error})")
                assert False, f"Received {error}"
            if kwargs:
                logger.error(f"lrc_callback(kwargs={kwargs})")
        except AssertionError as e:
            assert_errors.append(e)

    yield _aborted_lrc_callback
    if assert_errors:
        raise assert_errors[0]


class Helpers:
    """Static helper functions for tests."""

    @staticmethod
    def assert_lrcstatus_change_event_staging_queued_in_progress(
        change_event_callbacks: MockTangoEventCallbackGroup, command: Any
    ) -> None:
        """
        Assert the longRunningCommandStatus attribute change event multiple times.

        :param change_event_callbacks: dictionary of mock change event callbacks
        :param command: name/id of command to assert change events
        """
        for status in ["STAGING", "QUEUED", "IN_PROGRESS"]:
            change_event_callbacks.assert_change_event(
                "longRunningCommandStatus", (command, status)
            )

    @staticmethod
    def print_change_event_queue(
        change_event_callbacks: MockTangoEventCallbackGroup,
        attr_name: str,
    ) -> None:
        """
        Print the change event callback queue of the given attribute for debugging.

        :param change_event_callbacks: dictionary of mock change event callbacks
        :param attr_name: attribute in the change event callback group to print
        """
        print(f"{attr_name} change event queue:")
        # pylint: disable=protected-access
        for node in change_event_callbacks[
            attr_name
        ]._callable._consumer_view._iterable:
            print(node.payload["attribute_value"])

    @staticmethod
    def assert_expected_logs(
        caplog: pytest.LogCaptureFixture,
        expected_logs: list[str],
        timeout: int = 2,
    ) -> None:
        """
        Assert the expected log messages are in the captured logs.

        The expected list of log messages must appear in the records in the same order.
        The captured logs are cleared before returning for subsequent assertions.

        :param caplog: pytest log capture fixture.
        :param expected_logs: to assert are in the log capture fixture.
        :param timeout: time to wait for the last log message to appear, default 2 secs.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if expected_logs[-1] in caplog.text:
                break
        else:
            pytest.fail(f"'{expected_logs}' not found in logs within {timeout} seconds")
        test_logs = [record.message for record in caplog.records]
        assert test_logs == expected_logs
        caplog.clear()
