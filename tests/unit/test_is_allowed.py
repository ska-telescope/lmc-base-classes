# pylint: disable=invalid-name
"""Tests for the is_allowed mechanism."""

from __future__ import annotations

import threading
from typing import Any

import pytest
from ska_control_model import CommunicationStatus, PowerState, ResultCode, TaskStatus
from tango import DeviceProxy, DevState
from tango.server import command

from ska_tango_base import SKABaseDevice
from ska_tango_base.base import TaskCallbackType
from ska_tango_base.executor import TaskExecutorComponentManager


# pylint: disable-next=abstract-method
class ComponentManager(TaskExecutorComponentManager):
    """Dummy component manager."""

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialise the thing.

        :param args: Arguments
        :param kwargs: Keyword arguments
        """
        super().__init__(*args, power=None, fault=None, **kwargs)

        # Every task for this component manager waits for this event before
        # starting.  This allows us to set up a queue in a desired
        # configuration, then call Go() when we are ready to set things off.
        self.wait_for_go_event = threading.Event()

    def go(self: ComponentManager) -> None:
        """Unblock the tasks."""
        self.wait_for_go_event.set()

    def do_on(
        self: ComponentManager,
        task_callback: TaskCallbackType,
        task_abort_event: threading.Event,
    ) -> None:
        """
        Turn the component on.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        task_callback(status=TaskStatus.IN_PROGRESS)

        self.wait_for_go_event.wait()

        if task_abort_event.is_set():
            task_callback(
                status=TaskStatus.ABORTED,
                result=(ResultCode.ABORTED, "On command aborted"),
            )

        self._update_component_state(power=PowerState.ON)
        task_callback(
            status=TaskStatus.COMPLETED,
            result=(ResultCode.OK, "On completed successfully"),
        )

    def do_reset(
        self: ComponentManager,
        task_callback: TaskCallbackType,
        task_abort_event: threading.Event,
    ) -> None:
        """
        Turn the component on.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        task_callback(status=TaskStatus.IN_PROGRESS)

        self.wait_for_go_event.wait()

        if task_abort_event.is_set():
            task_callback(
                status=TaskStatus.ABORTED,
                result=(ResultCode.ABORTED, "On command aborted"),
            )

        self._update_component_state(fault=False)

        task_callback(
            status=TaskStatus.COMPLETED,
            result=(ResultCode.OK, "On completed successfully"),
        )

    def on(
        self: ComponentManager,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Turn the component on.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: TaskStatus and message
        """
        return self.submit_task(self.do_on, task_callback=task_callback)

    def reset(
        self: ComponentManager,
        task_callback: TaskCallbackType | None = None,
    ) -> tuple[TaskStatus, str]:
        """
        Turn the component on.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: TaskStatus and message
        """
        return self.submit_task(self.do_reset, task_callback=task_callback)


class TestDevice(SKABaseDevice[ComponentManager]):
    """A device with attributes for testing is allowed."""

    class InitCommand(SKABaseDevice.InitCommand):
        """InitCommand for SimpleDevice."""

        def do(
            self: TestDevice.InitCommand,
            *args: Any,
            **kwargs: Any,
        ) -> tuple[ResultCode, str]:
            """
            Stateless hook for device initialisation.

            :param args: positional arguments to this do method
            :param kwargs: keyword arguments to this do method

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            """
            # pylint: disable=protected-access
            self._device._communication_state_changed(CommunicationStatus.ESTABLISHED)
            # pylint: disable=protected-access
            self._device._component_state_changed(power=PowerState.OFF)

            message = "TestDevice Init command completed OK"
            self.logger.info(message)
            self._completed()
            return (ResultCode.OK, message)

    def create_component_manager(
        self: TestDevice,
    ) -> ComponentManager:
        """
        Create and return a component manager for this device.

        :returns: the component manager
        """
        return ComponentManager(
            self.logger,
            self._communication_state_changed,
            self._component_state_changed,
        )

    @command  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def Go(self: TestDevice) -> None:
        """Let it go."""
        self.component_manager.go()


@pytest.fixture(scope="module")
def device_test_config() -> dict[str, Any]:
    """
    Specify device configuration for testing push_change_event.

    :return: specification of how the device under test should be
        configured
    """
    return {"device": TestDevice}


def test_queue(device_under_test: DeviceProxy) -> None:
    """Test that commands can be queued.

    :param device_under_test: a proxy to the device under test
    """
    assert device_under_test.state() == DevState.OFF
    device_under_test.On()
    # This should be allowed even though we are not ON yet, as the Reset command
    # just needs to enter the queue at this point.  We should only check if we
    # are in an allowed state when we dequeue the Reset task.
    device_under_test.Reset()
    device_under_test.Go()
