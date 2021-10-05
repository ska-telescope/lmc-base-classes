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
        # self.register_command_object(
        #     "TestA",
        #     self.TestACommand(self),
        # )
        # self.register_command_object(
        #     "TestB",
        #     self.TestBCommand(self),
        # )
        # self.register_command_object(
        #     "TestC",
        #     self.TestCCommand(self),
        # )
        # self.register_command_object(
        #     "TestProgress",
        #     self.TestProgressCommand(self),
        # )
        # self.register_command_object(
        #     "NotAllowedExc",
        #     self.NotAllowedExcCommand(self),
        # )

        # self.register_command_object(
        #     "NotAllowedBool",
        #     self.NotAllowedBoolCommand(self),
        # )

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

    # class TestACommand(ResponseCommand):
    #     """The command class for the TestA command."""

    #     def do(self):
    #         """ """
    #         time.sleep(1)
    #         return (ResultCode.OK, "Done TestACommand")

    # @command(
    #     dtype_in=None,
    #     dtype_out="DevVarLongStringArray",
    # )
    # @DebugIt()
    # def TestA(self):
    #     """ """
    #     handler = self.get_command_object("TestA")
    #     (return_code, message) = handler()
    #     return [[return_code], [message]]

    # class TestBCommand(ResponseCommand):
    #     """The command class for the TestB command."""

    #     def do(self):
    #         """ """
    #         time.sleep(1)
    #         return (ResultCode.OK, "Done TestBCommand")

    # @command(
    #     dtype_in=None,
    #     dtype_out="DevVarLongStringArray",
    # )
    # @DebugIt()
    # def TestB(self):
    #     """ """
    #     handler = self.get_command_object("TestB")
    #     (return_code, message) = handler()
    #     return [[return_code], [message]]

    # class TestCCommand(ResponseCommand):
    #     """The command class for the TestC command."""

    #     def do(self):
    #         """ """
    #         time.sleep(1)
    #         return (ResultCode.OK, "Done TestCCommand")

    # @command(
    #     dtype_in=None,
    #     dtype_out="DevVarLongStringArray",
    # )
    # @DebugIt()
    # def TestC(self):
    #     """ """
    #     handler = self.get_command_object("TestC")
    #     (return_code, message) = handler()
    #     return [[return_code], [message]]

    # class TestProgressCommand(ResponseCommand):
    #     """The command class for the TestProgress command."""

    #     def do(self, argin):
    #         """Use self.command_progress to indicate progress"""
    #         for progress in [1, 25, 50, 74, 100]:
    #             self.current_command_progress = progress
    #             time.sleep(argin)

    #         return (ResultCode.OK, "Done TestProgressCommand")

    # @command(
    #     dtype_in=float,
    #     dtype_out="DevVarLongStringArray",
    # )
    # @DebugIt()
    # def TestProgress(self, argin):
    #     """Command to test the progress indicator"""
    #     handler = self.get_command_object("TestProgress")
    #     (return_code, message) = handler(argin)
    #     return [[return_code], [message]]

    # class NotAllowedExcCommand(ResponseCommand):
    #     """The command class for the NotAllowedExc command."""

    #     def is_allowed(self, raise_if_disallowed=True):
    #         """Raises a CommandError to mark as not allowed"""
    #         if raise_if_disallowed:
    #             raise CommandError("Command not allowed")

    #     def do(self):
    #         """Don't do anything, command should be rejected"""
    #         return (ResultCode.OK, "Done NotAllowedExcCommand")

    # @command(
    #     dtype_in=None,
    #     dtype_out="DevVarLongStringArray",
    # )
    # @DebugIt()
    # def NotAllowedExc(self):
    #     """Command to test not allowed with exception"""
    #     handler = self.get_command_object("NotAllowedExc")
    #     (return_code, message) = handler()
    #     return [[return_code], [message]]

    # class NotAllowedBoolCommand(ResponseCommand):
    #     """The command class for the NotAllowedBoolCommand command."""

    #     def is_allowed(self, raise_if_disallowed=True):
    #         """Return True or False depending on the
    #         is_allowed_return_value attribute
    #         """
    #         self.logger.info("raise_if_disallowed %s", raise_if_disallowed)
    #         return getattr(self.tango_device, "is_allowed_return_value")

    #     def do(self, _argin):
    #         """Simulate some work done"""
    #         time.sleep(0.5)
    #         return (ResultCode.OK, "Done NotAllowedExcCommand")

    # @command(
    #     dtype_in=bool,
    #     dtype_out="DevVarLongStringArray",
    # )
    # @DebugIt()
    # def NotAllowedBool(self, argin):
    #     """Command to test not_allowed returning
    #     true or false in not_allowed
    #     """
    #     setattr(self, "is_allowed_return_value", argin)
    #     handler = self.get_command_object("NotAllowedBool")
    #     (return_code, message) = handler(argin)
    #     return [[return_code], [message]]


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
