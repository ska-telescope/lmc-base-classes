=======================================
How to implement a long running command
=======================================

Decide on a concurrency mechanism
---------------------------------

You will first need to decide how your long running command is going to be
fulfilled asynchronously.  A reasonable default choice is to use the
:class:`~ska_tango_base.executor.executor_component_manager.TaskExecutorComponentManager`
class provided by ska-tango-base.  This is the choice we will make for the rest
of this guide.

It is possible to implement long running commands using a different
concurrency mechanism.  Just follow the steps below replacing the use of
:meth:`~ska_tango_base.executor.executor_component_manager.TaskExecutorComponentManager.submit_task`
with your mechanism of choice.

Create a component manager
--------------------------

You must subclass
:class:`~ska_tango_base.executor.executor_component_manager.TaskExecutorComponentManager`
if you want to use this concurrency mechanism.

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

.. tip::

   If your device is a subarray device and must implement the default Subarray
   commands, you can inherit from both
   :class:`~ska_tango_base.subarray.component_manager.SubarrayComponentManager`
   and
   :class:`~ska_tango_base.executor.executor_component_manager.TaskExecutorComponentManager`.
   For example:

   .. code-block:: py

    class SampleSubarrayComponentManager(SubarrayComponentManager, TaskExecutorComponentManager):
        """A sample subarray component manager"""
        # ...

Add a task method to fulfil the long running command
----------------------------------------------------

At the start of your task method you must update the task status to be
:obj:`TaskStatus.IN_PROGRESS <ska_control_model.TaskStatus.IN_PROGRESS>` via the
`task_callback`.  During the execution of your task you may update the task
progress via the `task_callback`.

Before your task method returns it must update the task status to be either
:obj:`TaskStatus.COMPLETED <ska_control_model.TaskStatus.COMPLETED>` or
:obj:`TaskStatus.ABORTED <ska_control_model.TaskStatus.ABORTED>` as
appropriate, and provide a task result via the `task_callback`.

If your task method raises an exception, the task executor will treat this as an
abnormal failure (i.e. a bug) and set the task status to
:obj:`TaskStatus.FAILED <ska_control_model.TaskStatus.FAILED>` and provide a
result :code:`(ResultCode.FAILED, <message>)`.  To report a normal failure, set the
task status to :obj:`TaskStatus.COMPLETED <ska_control_model.TaskStatus.COMPLETED>`
and use the task result to communicate the failure.


See :ref:`lrc-concept-tasks` for details about the task status state machine.

.. code-block:: py

    # class SampleComponentManager

        def _a_very_slow_method(
            self: SampleComponentManager,
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
                    task_callback(status=TaskStatus.ABORTED, result=(ResultCode.ABORTED, "This task aborted"))
                    return

            # Indicate that the task has completed
            task_callback(status=TaskStatus.COMPLETED, result=(ResultCode.OK, "This slow task has completed"))

.. admonition:: Guidelines for task methods

    **Task progress**

    There is no mechanism for a client to be notified of the maximum value that
    the task progress can take, so it is recommended that this maximum be
    statically known.  For example, using 0 - 100 to represent percentage
    completed.  How to interpret the task progress should be well documented for
    clients invoking the LRC.

    **Task result**

    It is recommended to always include a :class:`~ska_control_model.ResultCode` to 
    indicate to clients if the task has completed successfully or not. Ideally, this
    :class:`~ska_control_model.ResultCode` should be accessed with
    :code:`result[0]` to fit in with task results provided by ska-tango-base.
    A client should know the type of :code:`result[1]` based on the value of
    :code:`result[0]`.

    If your task can complete "partially successfully", consider using multiple
    :class:`~ska_control_model.ResultCode`'s to provide more details.  For
    example, if your task coordinates multiple subordinate devices, you might
    provide a result such as the following:

    .. code-block:: py

        (ResultCode.OK, {
            "total_success": False,
            "device_responses":[
                (ResultCode.OK, "OK"),
                (ResultCode.FAILED, "Not enough quux available"),
                ...
            ]
        })

Optionally add an "is-allowed" method
----------------------------------------------------

If the is-allowed method is omitted it will be assumed that the task is always
allowed.

.. code-block:: py

    # class SampleComponentManager

        def _is_a_very_slow_method_allowed(
            self: SampleComponentManager,
        ):
            """ is _a_very_slow_method allowed

            :return: True if the very slow method can be executed
            """
            return True

.. warning ::

   Do not confuse this is-allowed method with the Tango :code:`is_cmd_allowed`
   callback.  This is-allowed method returns :code:`True` if the task can be
   executed at the point it is dequeued.  The Tango :code:`is_cmd_allowed`
   callback returns True if the task can be enqueued in the first place.

   Notably, the is-allowed method might return :code:`False` when the task is
   enqueued, but by the time the task has been dequeued it returns :code:`True`
   because other LRCs have been completed in the mean time.

Add a method to submit the slow method
--------------------------------------

If you are not using
:class:`~ska_tango_base.executor.executor_component_manager.TaskExecutorComponentManager`
you will have to use your concurrency mechanism of choice to schedule the task
method.

If your LRC implements one of the standard commands defined by either
:class:`~ska_tango_base.base.base_device.SKABaseDevice` or
:class:`~ska_tango_base.subarray.subarray_device.SKASubarray`, the name of this
method must be what the standard command is expecting.  For example the ``On``
command is expecting a method called ``on``.

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


Initialise the command object
-----------------------------

If your LRC implements one of the standard commands defined by either
:class:`~ska_tango_base.base.base_device.SKABaseDevice` or
:class:`~ska_tango_base.subarray.subarray_device.SKASubarray`, you do not have to
reinitialise the command object.

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

Create the Tango Command to initiate the LRC
--------------------------------------------

Similarly, if your LRC implements one of the standard commands defined by either
:class:`~ska_tango_base.base.base_device.SKABaseDevice` or
:class:`~ska_tango_base.subarray.subarray_device.SKASubarray`, you will not have
to create the Tango command.

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

