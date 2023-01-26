"""Device to test multi layered commands."""
from __future__ import annotations

from typing import Any, Tuple

from ska_control_model import ResultCode
from tango import DebugIt
from tango.server import command, device_property

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import FastCommand, SubmittedSlowCommand

from .multidevice_component_manager import MultiDeviceComponentManager


class ExampleMultiDevice(SKABaseDevice):
    """Implement commands to test queued work."""

    client_devices = device_property(dtype="DevVarStringArray")

    def create_component_manager(
        self: ExampleMultiDevice,
    ) -> MultiDeviceComponentManager:
        """
        Create a component manager.

        :return: the component manager
        """
        return MultiDeviceComponentManager(
            self.logger,
            client_devices=self.client_devices,
            max_workers=2,
            communication_state_callback=self._communication_state_changed,
            component_state_callback=self._component_state_changed,
        )

    def init_command_objects(self: ExampleMultiDevice) -> None:
        """Initialise the command handlers."""
        super().init_command_objects()

        self.register_command_object(
            "Short",
            self.AddTwoCommand(logger=self.logger),
        )

        self.register_command_object(
            "NonAbortingLongRunning",
            SubmittedSlowCommand(
                "NonAbortingLongRunning",
                self._command_tracker,
                self.component_manager,
                "non_aborting_lrc",
                callback=None,
                logger=self.logger,
            ),
        )

        self.register_command_object(
            "AbortingLongRunning",
            SubmittedSlowCommand(
                "AbortingLongRunning",
                self._command_tracker,
                self.component_manager,
                "aborting_lrc",
                callback=None,
                logger=self.logger,
            ),
        )

        self.register_command_object(
            "LongRunningException",
            SubmittedSlowCommand(
                "LongRunningException",
                self._command_tracker,
                self.component_manager,
                "throw_exc",
                callback=None,
                logger=self.logger,
            ),
        )

        self.register_command_object(
            "TestProgress",
            SubmittedSlowCommand(
                "TestProgress",
                self._command_tracker,
                self.component_manager,
                "show_progress",
                callback=None,
                logger=self.logger,
            ),
        )

        self.register_command_object(
            "CallChildren",
            SubmittedSlowCommand(
                "CallChildren",
                self._command_tracker,
                self.component_manager,
                "call_children",
                callback=None,
                logger=self.logger,
            ),
        )

    class AddTwoCommand(FastCommand):
        """The command class for the Short command."""

        def do(
            self: ExampleMultiDevice.AddTwoCommand,
            *args: Any,
            **kwargs: Any,
        ) -> Tuple[ResultCode, int]:
            """
            Do command.

            :param args: positional arguments to the method. There
                should be only one: the input arg
            :param kwargs: keyword arguments to the method.

            :return: a result code and the result of adding two to the
                provided integer.
            """
            argin = args[0]
            self.logger.info("In AddTwoCommand")
            result = argin + 2
            return ResultCode.OK, result

    @command(
        dtype_in=int,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def Short(self: ExampleMultiDevice, argin: int) -> Tuple[str, str]:
        """
        Short command.

        Takes in an integer and adds two to it

        :param argin: the integer to be added with two.

        :return: a string result code and message. The message is a
            string representation of the resulting sum.
        """
        handler = self.get_command_object("Short")
        (return_code, message) = handler(argin)
        return f"{return_code}", f"{message}"

    @command(
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def NonAbortingLongRunning(
        self: ExampleMultiDevice, argin: float
    ) -> Tuple[str, str]:
        """
        Non AbortingLongRunning command.

        :param argin: how long to sleep per iteration

        :return: a string result code and message.
        """
        handler = self.get_command_object("NonAbortingLongRunning")
        (return_code, message) = handler(argin)
        return f"{return_code}", message

    @command(
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def AbortingLongRunning(self: ExampleMultiDevice, argin: float) -> Tuple[str, str]:
        """
        AbortingLongRunning.

        :param argin: how long to sleep per iteration

        :return: a string result code and message.
        """
        handler = self.get_command_object("AbortingLongRunning")
        (return_code, message) = handler(argin)
        return f"{return_code}", message

    @command(dtype_out="DevVarStringArray")
    @DebugIt()
    def LongRunningException(self: ExampleMultiDevice) -> Tuple[str, str]:
        """
        Command that queues a task that raises an exception.

        :return: a string result code and message.
        """
        handler = self.get_command_object("LongRunningException")
        (return_code, message) = handler()
        return f"{return_code}", f"{message}"

    @command(
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def TestProgress(self: ExampleMultiDevice, argin: float) -> Tuple[str, str]:
        """
        Command to test the progress indicator.

        :param argin: time to sleep between each progress update.

        :return: a string result code and message.
        """
        handler = self.get_command_object("TestProgress")
        (return_code, message) = handler(argin)
        return f"{return_code}", message

    @command(
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def CallChildren(self: ExampleMultiDevice, argin: float) -> Tuple[str, str]:
        """
        Command to call `CallChildren` on children, or block if not.

        :param argin: how long children should sleep

        :return: a string result code and message
        """
        handler = self.get_command_object("CallChildren")
        (return_code, message) = handler(argin)
        return f"{return_code}", message
