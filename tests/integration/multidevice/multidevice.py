"""Device to test multi layered commands."""
from tango import DebugIt
from tango.server import command, device_property

from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.commands import (
    FastCommand,
    ResultCode,
    SubmittedSlowCommand,
)

from .multidevice_component_manager import MultiDeviceComponentManager


class ExampleMultiDevice(SKABaseDevice):
    """Implement commands to test queued work."""

    client_devices = device_property(dtype="DevVarStringArray")

    def create_component_manager(self):
        """Create a component manager."""
        return MultiDeviceComponentManager(
            client_devices=self.client_devices,
            max_workers=2,
            logger=self.logger,
            communication_state_callback=self._communication_state_changed,
            component_state_callback=self._component_state_changed,
        )

    def init_command_objects(self):
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

        def do(self, argin):
            """Do command."""
            self.logger.info("In AddTwoCommand")
            result = argin + 2
            return ResultCode.OK, result

    @command(
        dtype_in=int,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def Short(self, argin):
        """Short command."""
        handler = self.get_command_object("Short")
        (return_code, message) = handler(argin)
        return f"{return_code}", f"{message}"

    @command(
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def NonAbortingLongRunning(self, argin):
        """Non AbortingLongRunning command."""
        handler = self.get_command_object("NonAbortingLongRunning")
        (return_code, message) = handler(argin)
        return f"{return_code}", message

    @command(
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def AbortingLongRunning(self, argin):
        """AbortingLongRunning."""
        handler = self.get_command_object("AbortingLongRunning")
        (return_code, message) = handler(argin)
        return f"{return_code}", message

    @command(
        dtype_in=None,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def LongRunningException(self):
        """Command that queues a task that raises an exception."""
        handler = self.get_command_object("LongRunningException")
        (return_code, message) = handler()
        return f"{return_code}", f"{message}"

    @command(
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def TestProgress(self, argin):
        """Command to test the progress indicator."""
        handler = self.get_command_object("TestProgress")
        (return_code, message) = handler(argin)
        return f"{return_code}", message

    @command(
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def CallChildren(self, argin):
        """Command to call `CallChildren` on children, or block if not."""
        handler = self.get_command_object("CallChildren")
        (return_code, message) = handler(argin)
        return f"{return_code}", message
