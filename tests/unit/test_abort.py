"""Contain the tests for the SKASubarray Abort command."""
from __future__ import annotations

import itertools
import logging
import threading
import time
from typing import Any

import pytest
import tango
from ska_control_model import AdminMode, ResultCode, TaskStatus
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup

from ska_tango_base.base import TaskCallbackType
from ska_tango_base.executor import TaskExecutorComponentManager
from ska_tango_base.subarray.component_manager import SubarrayComponentManager
from ska_tango_base.subarray.subarray_device import SKASubarray


# pylint: disable=protected-access
def print_change_event_queue(
    change_event_callbacks: MockTangoEventCallbackGroup, attr_name: str
) -> None:
    """
    Print the change event callback queue of the given attribute for debugging.

    :param change_event_callbacks: dictionary of mock change event callbacks
    :param attr_name: attribute name to inspect
    """
    print(f"{attr_name} change event queue:")
    for node in itertools.islice(
        change_event_callbacks[attr_name]._callable._consumer_view._iterable, 5
    ):
        print(node.payload["attribute_value"])


# pylint: disable=abstract-method
class RacingComponentManager(TaskExecutorComponentManager, SubarrayComponentManager):
    """A component for testing the abort command."""

    def __init__(
        self: RacingComponentManager,
        logger: logging.Logger,
    ):
        """Initialise it.

        :param logger: to log stuff
        """
        super().__init__(logger)

    def start_communicating(self: RacingComponentManager) -> None:
        """Do nothing stub."""

    def stop_communicating(self: RacingComponentManager) -> None:
        """Do nothing stub."""

    def _assign(
        self: RacingComponentManager,
        in_omnithread: bool,
        task_callback: TaskCallbackType | None,
        task_abort_event: threading.Event,
    ) -> None:
        """
        Call the task_callback with progress information.

        :param in_omnithread: True if the callback should be called in an
            EnsureOmniThread context
        :param task_callback: callback to be called when the status of
            the command changes
        :param task_abort_event: set when we are aborting
        """

        def do_it() -> None:
            """Call the task callback."""
            logging.info(f"Doing it in_omnithread={in_omnithread}")
            if task_callback is not None:
                task_callback(status=TaskStatus.IN_PROGRESS)

            for i in range(4096):
                if task_abort_event.is_set():
                    if task_callback is not None:
                        task_callback(status=TaskStatus.ABORTED)
                    return

                if task_callback is not None:
                    task_callback(progress=i)

                time.sleep(0.001)

            if task_callback is not None:
                task_callback(status=TaskStatus.COMPLETED)

        if in_omnithread:
            with tango.EnsureOmniThread():
                do_it()
        else:
            do_it()

    def assign(
        self: RacingComponentManager,
        task_callback: TaskCallbackType | None,
        **kwargs: Any,
    ) -> tuple[TaskStatus, str]:
        """
        Assign resources to the component.

        :param task_callback: callback to be called when the status of
            the command changes
        :param kwargs: keyword arguments.
            These will be the root keys defined by the command schema.

        :returns: TaskStatus and helpful message
        """
        in_omnithread = kwargs.get("in_omnithread", True)
        return self.submit_task(
            self._assign, [in_omnithread], task_callback=task_callback
        )

    def abort(
        self: RacingComponentManager, task_callback: TaskCallbackType | None
    ) -> tuple[TaskStatus, str]:
        """
        Tell the component to abort whatever it was doing.

        :param task_callback: callback to be called when the status of
            the command changes

        :returns: TaskStatus and helpful message
        """
        return self.abort_commands(task_callback=task_callback)


class RacingSubarray(SKASubarray[RacingComponentManager]):
    """A subarray for testing the abort command."""

    def create_component_manager(
        self: RacingSubarray,
    ) -> RacingComponentManager:
        """
        Create and return a component manager for this device.

        :returns: a reference subarray component manager.
        """
        return RacingComponentManager(self.logger)


@pytest.fixture(scope="module")
def device_test_config() -> dict[str, Any]:
    """
    Specify device configuration, including properties and memorized attributes.

    This implementation provides a concrete subclass of the device
    class under test, some properties, and a memorized value for
    adminMode.

    :return: specification of how the device under test should be
        configured
    """
    return {
        "device": RacingSubarray,
        "memorized": {"adminMode": str(AdminMode.ONLINE.value)},
    }


def test_abort_deadlock(
    device_under_test: tango.DeviceProxy,
    change_event_callbacks: MockTangoEventCallbackGroup,
) -> None:
    """Shows for a deadlock when aborting.

    :param device_under_test: proxy to device we are testing
    :param change_event_callbacks: callback dictionary
    """
    attribute = "longRunningCommandProgress"
    device_under_test.subscribe_event(
        attribute,
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks[attribute],
    )
    change_event_callbacks.assert_change_event(attribute, ())
    [
        [result_code],
        [cmd_id],
    ] = device_under_test.assignresources("{}")
    assert result_code == ResultCode.QUEUED
    print_change_event_queue(change_event_callbacks, attribute)
    change_event_callbacks.assert_change_event(attribute, (cmd_id, "0"))
    device_under_test.abort()


def test_abort_no_deadlock(
    device_under_test: tango.DeviceProxy,
    change_event_callbacks: MockTangoEventCallbackGroup,
) -> None:
    """Shows that the is no deadlock .

    :param device_under_test: proxy to device we are testing
    :param change_event_callbacks: callback dictionary
    """
    attribute = "longRunningCommandProgress"
    device_under_test.subscribe_event(
        attribute,
        tango.EventType.CHANGE_EVENT,
        change_event_callbacks[attribute],
    )
    change_event_callbacks.assert_change_event(attribute, ())
    [
        [result_code],
        [cmd_id],
    ] = device_under_test.assignresources('{"in_omnithread": false}')
    assert result_code == ResultCode.QUEUED
    print_change_event_queue(change_event_callbacks, attribute)
    change_event_callbacks.assert_change_event(attribute, (cmd_id, "0"))
    device_under_test.abort()
