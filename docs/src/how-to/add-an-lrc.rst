=======================================
How to implement a long running command
=======================================

A task executor has been provisioned to handle the asynchronous execution of tasks
put on the queue. Your sample component manager will be asynchronous if it inherits
from the provisioned executor. You can also swap out the default executor with any
asynchronous mechanism for your component manager.

Create a component manager
--------------------------

.. code-block:: py

    class SampleComponentManager(TaskExecutorComponentManager):
        """A sample component manager"""

        def __init__(
            self,
            *args,
            logger: logging.Logger = None,
            **kwargs,
        ):
            """Init SampleComponentManager."""
            
            # Set up your class

            super().__init__(*args, logger=logger, **kwargs)

Add a method that should be executed in a background thread
-----------------------------------------------------------

.. code-block:: py

    # class SampleComponentManager

        def _a_very_slow_method(
            logger: logging.Logger,
            task_callback: Callable,
            task_abort_event: Event,
        ):
            """This is a long running method

            :param logger: logger
            :param task_callback: Update task state, defaults to None
            :param task_abort_event: Check for abort, defaults to None
            """
            # Indicate that the task has started
            task_callback(status=TaskStatus.IN_PROGRESS)
            for current_iteration in range(100):
                # Update the task progress
                task_callback(progress=current_iteration)
                
                # Do something
                time.sleep(10)

                # Periodically check that tasks have not been ABORTED
                if task_abort_event.is_set():
                    # Indicate that the task has been aborted
                    task_callback(status=TaskStatus.ABORTED, result="This task aborted")
                    return

            # Indicate that the task has completed
            task_callback(status=TaskStatus.COMPLETED, result="This slow task has completed")

.. note:: This can be accompanied with another method (e.g. _is_very_slow_method_allowed)
   which will be a check against the component to check if the command is allowed before
   sending it over to be run in the background. The component manager receives the check as
   `is_cmd_allowed` (example below).

Add a method to submit the slow method
--------------------------------------

.. code-block:: py

    # class SampleComponentManager

        def submit_slow_method(self, task_callback: Callable | None = None):
            """Submit the slow task. 

            This method returns immediately after it submitted
            `self._a_very_slow_method` for execution.

            :param task_callback: Update task state, defaults to None
            """
            task_status, response = self.submit_task(
                self._a_very_slow_method, args=[],
                is_cmd_allowed=self._is_very_slow_method_allowed,
                task_callback=task_callback
            )
            return task_status, response


Create the component manager in your Tango device
-------------------------------------------------

.. code-block:: py

    class SampleDevice(SKABaseDevice):
        """A sample Tango device"""

        def create_component_manager(self):
            """Create a component manager."""
            return SampleComponentManager(
                logger=self.logger,
                communication_state_callback=self._communication_state_changed,
                component_state_callback=self._component_state_changed,
            )

Init the command object
-----------------------

.. code-block:: py

    # class SampleDevice(SKABaseDevice):

        def init_command_objects(self):
            """Initialise the command handlers."""
            super().init_command_objects()

            ...

            self.register_command_object(
                "VerySlow",
                SubmittedSlowCommand(
                    "VerySlow",
                    self._command_tracker,
                    self.component_manager,
                    "submit_slow_method",
                    callback=None,
                    logger=self.logger,
                ),
            )

Create the Tango Command
------------------------

.. code-block:: py

    # class SampleDevice(SKABaseDevice):

        @command(
            dtype_in=None,
            dtype_out="DevVarStringArray",
        )
        @DebugIt()
        def VerySlow(self):
            """A very slow command."""
            handler = self.get_command_object("VerySlow")
            (return_code, message) = handler()
            return f"{return_code}", message

