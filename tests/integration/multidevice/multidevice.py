# pylint: disable=invalid-name
"""Device to test multi layered commands."""
from __future__ import annotations

from typing import Any, cast

from ska_control_model import ResultCode
from tango import DebugIt
from tango.server import attribute, command, device_property

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import FastCommand, SubmittedSlowCommand

from .multidevice_component_manager import MultiDeviceComponentManager


class ExampleMultiDevice(SKABaseDevice[MultiDeviceComponentManager]):
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
            communication_state_callback=self._communication_state_changed,
            component_state_callback=self.component_state_changed_callback,
        )

    def init_command_objects(self: ExampleMultiDevice) -> None:
        """Initialise the command handlers."""
        super().init_command_objects()

        self.register_command_object(
            "Short",
            self.AddTwoCommand(logger=self.logger),
        )

        for command_name, method_name in [
            ("NonAbortingLongRunning", "non_aborting_lrc"),
            ("AbortingLongRunning", "aborting_lrc"),
            ("LongRunningException", "throw_exc"),
            ("TestProgress", "show_progress"),
            ("CallChildren", "call_children"),
            ("Transpose", "transpose"),
            ("Invert", "invert"),
        ]:
            self.register_command_object(
                command_name,
                SubmittedSlowCommand(
                    command_name,
                    self._command_tracker,
                    self.component_manager,
                    method_name,
                    callback=None,
                    logger=self.logger,
                ),
            )

    class InitCommand(SKABaseDevice.InitCommand):
        # pylint: disable=protected-access
        """ExampleMultiDevice Init command."""

        def do(
            self: SKABaseDevice.InitCommand,
            *args: Any,
            **kwargs: Any,
        ) -> tuple[ResultCode, str]:
            """
            Initialise ExampleMultiDevice.

            :param args: positional arguments
            :param kwargs: keyword arguments

            :return: A tuple containing a return code and a string
            """
            self._device._matrix_operation = ""

            return (ResultCode.OK, "Multidevice initialised successfully")

    def component_state_changed_callback(
        # pylint: disable=attribute-defined-outside-init
        self: ExampleMultiDevice,
        **state_change: dict[str, Any],
    ) -> None:
        """
        Handle change in the state of the component.

        :param state_change: keyword arguments to the method
        """
        recent_operation = state_change.get("matrix_operation", "")
        self._matrix_operation = recent_operation

    @attribute(dtype="str")  # type: ignore[misc]
    def matrixOperation(self: ExampleMultiDevice) -> str:
        """
        Return the recent matrix operation.

        :return: A string representing the most recent operation
        """
        return self._matrix_operation  # type: ignore[return-value]

    class AddTwoCommand(FastCommand[tuple[ResultCode, int]]):
        """The command class for the Short command."""

        def do(
            self: ExampleMultiDevice.AddTwoCommand,
            *args: Any,
            **kwargs: Any,
        ) -> tuple[ResultCode, int]:
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

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=int,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def Short(self: ExampleMultiDevice, argin: int) -> tuple[str, str]:
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

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def NonAbortingLongRunning(
        self: ExampleMultiDevice, argin: float
    ) -> tuple[str, str]:
        """
        Non AbortingLongRunning command.

        :param argin: how long to sleep per iteration

        :return: a string result code and message.
        """
        handler = self.get_command_object("NonAbortingLongRunning")
        (return_code, message) = handler(argin)
        return f"{return_code}", message

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def AbortingLongRunning(self: ExampleMultiDevice, argin: float) -> tuple[str, str]:
        """
        AbortingLongRunning.

        :param argin: how long to sleep per iteration

        :return: a string result code and message.
        """
        handler = self.get_command_object("AbortingLongRunning")
        (return_code, message) = handler(argin)
        return f"{return_code}", message

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarStringArray"
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def LongRunningException(self: ExampleMultiDevice) -> tuple[str, str]:
        """
        Command that queues a task that raises an exception.

        :return: a string result code and message.
        """
        handler = self.get_command_object("LongRunningException")
        (return_code, message) = handler()
        return f"{return_code}", f"{message}"

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def TestProgress(self: ExampleMultiDevice, argin: float) -> tuple[str, str]:
        """
        Command to test the progress indicator.

        :param argin: time to sleep between each progress update.

        :return: a string result code and message.
        """
        handler = self.get_command_object("TestProgress")
        (return_code, message) = handler(argin)
        return f"{return_code}", message

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def CallChildren(self: ExampleMultiDevice, argin: float) -> tuple[str, str]:
        """
        Command to call `CallChildren` on children, or block if not.

        :param argin: how long children should sleep

        :return: a string result code and message
        """
        handler = self.get_command_object("CallChildren")
        (return_code, message) = handler(argin)
        return f"{return_code}", message

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def Transpose(self: ExampleMultiDevice) -> tuple[str, str]:
        """
        Transpose a matrix.

        :return: a string result code and message
        """
        handler = self.get_command_object("Transpose")
        (return_code, message) = handler()
        return f"{return_code}", message

    @command(  # type: ignore[misc]  # "Untyped decorator makes function untyped"
        dtype_out="DevVarStringArray",
    )
    @DebugIt()  # type: ignore[misc]  # "Untyped decorator makes function untyped"
    def Invert(self: ExampleMultiDevice) -> tuple[str, str]:
        """
        Invert a matrix.

        :return: a string result code and message
        """
        handler = self.get_command_object("Invert")
        (return_code, message) = handler()
        return f"{return_code}", message


def main(*args: str, **kwargs: str) -> int:
    """
    Entry point for module.

    :param args: positional arguments
    :param kwargs: named arguments

    :return: exit code
    """
    return cast(int, ExampleMultiDevice.run_server(args=args or None, **kwargs))


if __name__ == "__main__":
    main()
