"""
This module provided a reference implementation of a BaseDevice.

There are two versions used for testing long running commands.
  - BlockingBaseDevice - Uses the default QueueManager. No threads,
    thus blocking commands.
  - AsyncBaseDevice - Uses the custom QueueManager. Multiple threads,
    async commands/responses.

It is provided for explanatory purposes, and to support testing of this
package.
"""
import time
from tango.server import command
from tango import DebugIt

from ska_tango_base.base.component_manager import BaseComponentManager
from ska_tango_base.base.base_device import SKABaseDevice
from ska_tango_base.base.task_queue_manager import QueueManager, ResultCode, QueueTask
from ska_tango_base.commands import ResponseCommand


class BaseTestDevice(SKABaseDevice):
    """Implement commands to test queued work."""

    def init_command_objects(self):
        """Initialise the command handlers."""
        super().init_command_objects()

        self.register_command_object(
            "Short",
            self.ShortCommand(self.component_manager, logger=self.logger),
        )
        self.register_command_object(
            "NonAbortingLongRunning",
            self.NonAbortingLongRunningCommand(
                self.component_manager, logger=self.logger
            ),
        )
        self.register_command_object(
            "AbortingLongRunning",
            self.AbortingLongRunningCommand(self.component_manager, logger=self.logger),
        )
        self.register_command_object(
            "LongRunningException",
            self.LongRunningExceptionCommand(
                self.component_manager, logger=self.logger
            ),
        )

        self.register_command_object(
            "TestProgress",
            self.TestProgressCommand(self.component_manager, logger=self.logger),
        )

    class ShortCommand(ResponseCommand):
        """The command class for the Short command."""

        def do(self, argin):
            """Do command."""

            class SimpleTask(QueueTask):
                def do(self):
                    num_one = self.args[0]
                    return num_one + 2

            self.logger.info("In ShortCommand")
            unique_id = self.target.enqueue(SimpleTask(2))

            return ResultCode.OK, unique_id

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

    class NonAbortingLongRunningCommand(ResponseCommand):
        """The command class for the NonAbortingLongRunning command."""

        def do(self, argin):
            """NOTE This is an example of what _not_ to do.

            Always check self.is_aborting periodically so that the command
            will exit out if long running commands are aborted.

            See the implementation of AnotherLongRunningCommand.
            """

            class NonAbortingTask(QueueTask):
                """NonAbortingTask."""

                def do(self):
                    """NonAborting."""
                    retries = 45
                    while retries > 0:
                        retries -= 1
                        time.sleep(self.args[0])  # This command takes long
                        self.logger.info(
                            "In NonAbortingTask repeating %s",
                            retries,
                        )

            self.logger.info("In NonAbortingTask")
            unique_id = self.target.enqueue(NonAbortingTask(argin, logger=self.logger))

            return ResultCode.OK, unique_id

    @command(
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def NonAbortingLongRunning(self, argin):
        """Non AbortingLongRunning command."""
        handler = self.get_command_object("NonAbortingLongRunning")
        (return_code, message) = handler(argin)
        return f"{return_code}", f"{message}"

    class AbortingLongRunningCommand(ResponseCommand):
        """The command class for the AbortingLongRunning command."""

        def do(self, argin):
            """Abort."""

            class AbortingTask(QueueTask):
                """Abort."""

                def do(self):
                    """Abort."""
                    retries = 45
                    while (not self.aborting_event.is_set()) and retries > 0:
                        retries -= 1
                        time.sleep(argin)  # This command takes long
                        self.logger.info("In NonAbortingTask repeating %s", retries)

                    if retries == 0:  # Normal finish
                        return (
                            ResultCode.OK,
                            f"NonAbortingTask completed {argin}",
                        )
                    else:  # Aborted finish
                        return (
                            ResultCode.ABORTED,
                            f"NonAbortingTask Aborted {argin}",
                        )

            self.logger.info("In AbortingLongRunningCommand")
            unique_id = self.target.enqueue(AbortingTask(argin, logger=self.logger))

            return ResultCode.OK, unique_id

    @command(
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def AbortingLongRunning(self, argin):
        """AbortingLongRunning."""
        handler = self.get_command_object("AbortingLongRunning")
        (return_code, message) = handler(argin)
        return f"{return_code}", f"{message}"

    class LongRunningExceptionCommand(ResponseCommand):
        """The command class for the LongRunningException command."""

        def do(self):
            """Throw an exception."""

            class ExcTask(QueueTask):
                """Throw an exception."""

                def do(self):
                    """Throw an exception."""
                    raise Exception("An error occurred")

            unique_id = self.target.enqueue(ExcTask())

            return ResultCode.OK, unique_id

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

    class TestProgressCommand(ResponseCommand):
        """The command class for the TestProgress command."""

        def do(self, argin):
            """Do the task."""

            class ProgressTask(QueueTask):
                """A task that updates its progress."""

                def do(self):
                    """Update progress."""
                    for progress in [1, 25, 50, 74, 100]:
                        self.update_progress(f"{progress}")
                        time.sleep(self.args[0])

            unique_id = self.target.enqueue(ProgressTask(argin))
            return ResultCode.OK, unique_id

    @command(
        dtype_in=float,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def TestProgress(self, argin):
        """Command to test the progress indicator."""
        handler = self.get_command_object("TestProgress")
        (return_code, message) = handler(argin)
        return f"{return_code}", f"{message}"


class BlockingBaseDevice(BaseTestDevice):
    """Test device that has a component manager with the default queue manager that has no workers."""

    pass


class AsyncBaseDevice(BaseTestDevice):
    """Test device that has a component manager with workers."""

    def create_component_manager(self):
        """Create the component manager with a queue manager that has workers."""
        queue_manager = QueueManager(
            max_queue_size=10, num_workers=3, logger=self.logger
        )
        return BaseComponentManager(op_state_model=None, queue_manager=queue_manager)
