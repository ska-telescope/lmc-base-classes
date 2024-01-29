=====================
Long Running Commands
=====================

Many SKA device commands involve actions whose duration is inherently slow or unpredictable. 
For example, a command might need to interact with hardware, other devices, or other external
systems over a network; read to or write from a file system; or perform intensive computation.
If a TANGO device blocks while such a command runs, then there is a period of time in which it
cannot respond to other requests. Its overall performance declines, and timeouts may even occur.

To address this, the base device provides long running commands (LRC) support, in the form of
an interface and mechanism for running such commands asynchronously.

.. note:: Long Running Command: A TANGO command for which the execution time
   is in the order of seconds (CS Guidelines recommends less than 10 ms).
   In this context it also means a command which is implemented to execute
   asynchronously. Long running, slow command and asynchronous command are used
   interchangeably in this text and the code base. In the event where the meaning
   differ it will be explained but all refer to non-blocking calls.

This means that devices return immediately with a response while busy with the
actual task in the background or parked on a queue pending the next available worker.

New attributes and commands have been added to the base device to support the
mechanism to execute long running TANGO commands asynchronously.

Monitoring Progress of Long Running Commands
--------------------------------------------
In addition to the listed requirements above, the device should provide monitoring points
to allow clients determine when a LRC is received, executing or completed (success or fail).
LRCs can assume any of the following defined task states: STAGING, QUEUED, IN_PROGRESS, ABORTED,
NOT_FOUND, COMPLETED, REJECTED, FAILED.

A new set of attributes and commands have been added to the base device to enable
monitoring and reporting of result, status and progress of LRCs.

**LRC Attributes**

+-----------------------------+-------------------------------------------+----------------------+
| Attribute                   | Example Value                             |  Description         |
+=============================+===========================================+======================+
| longRunningCommandsInQueue  | ('Standby', 'On', 'Off')                  | Keeps track of which |
|                             |                                           | commands are on the  |
|                             |                                           | queue                |
+-----------------------------+-------------------------------------------+----------------------+
| longRunningCommandIDsInQueue|('1636437568.0723004_235210334802782_On',  | Keeps track of IDs in|
|                             |                                           | the queue            |
|                             |1636437789.493874_116219429722764_Off)     |                      |
+-----------------------------+-------------------------------------------+----------------------+
| longRunningCommandStatus    | ('1636437568.0723004_235210334802782_On', | ID, status pair of   |
|                             | 'IN_PROGRESS',                            | the currently        |
|                             |                                           | executing commands   |
|                             | '1636437789.493874_116219429722764_Off',  |                      |
|                             | 'IN_PROGRESS')                            |                      |
+-----------------------------+-------------------------------------------+----------------------+
| commandInProgress           | '1636437568.0723004_235210334802782_On    | ID of command        |
|                             |                                           | currently executing  |
|                             |                                           | or an empty string   |
|                             |                                           | if idle              |
+-----------------------------+-------------------------------------------+----------------------+
| longRunningCommandProgress  | ('1636437568.0723004_235210334802782_On', | ID, progress pair of |
|                             | '12',                                     | the currently        |
|                             |                                           | executing commands   |
|                             | '1636437789.493874_116219429722764_Off',  |                      |
|                             | '1')                                      |                      |
+-----------------------------+-------------------------------------------+----------------------+
| longRunningCommandResult    | ('1636438076.6105473_101143779281769_On', | ID, ResultCode,      |
|                             | '0', 'OK')                                | result of the        |
|                             |                                           | completed command    |
+-----------------------------+-------------------------------------------+----------------------+


**LRC Commands**

+-------------------------------+------------------------------+
| Command                       | Description                  |
+===============================+==============================+
| CheckLongRunningCommandStatus | Check the status of a long   |
|                               | running command by ID        |
+-------------------------------+------------------------------+
| AbortCommands                 | Abort the currently executing|
|                               | LRC and remove all enqueued  |
|                               | LRCs                         |
+-------------------------------+------------------------------+

In addition to the set of commands in the table above, a number of candidate SKA
commands in the base device previously implemented as blocking commands have been
converted to execute as long running commands (asynchronously), namely: Standby, On, Off,
Reset and GetVersionInfo.

**commandedState and commandedObsState attributes**

These attributes indicate the expected stable operating or observation state after the last long running command that has started is completed.

The *commandedState* string initialises to "None". Only other strings it can change to is "OFF",
"STANDBY" or "ON", following the start of the Off, Standby, On or Reset long running commands.
The following table shows the *commandedState* given current device state and issued command in progress: 

+-------------+-------+-------------+-------------+-------------+
| state       | *commandedState* for issued command             |
+             +-------+-------------+-------------+-------------+
| (DevState)  | Off   | Standby     | On          | Reset       |
+=============+=======+=============+=============+=============+
| **UNKNOWN** | OFF   | STANDBY     | ON          |             |
+-------------+-------+-------------+-------------+-------------+
| **OFF**     | OFF   | STANDBY     | ON          |             |
+-------------+-------+-------------+-------------+-------------+
| **STANDBY** | OFF   | STANDBY     | ON          | STANDBY     |
+-------------+-------+-------------+-------------+-------------+
| **ON**      | OFF   | STANDBY     | ON          | ON          |
+-------------+-------+-------------+-------------+-------------+
| **FAULT**   | OFF   |             |             | ON          |
+-------------+-------+-------------+-------------+-------------+

The *commandedObsState* initial value is ObsState.EMPTY. The only stable (nontransitional) state values it can
change to is EMPTY, IDLE, READY or ABORTED following the start of any of the SKASubarray device's long running commands.
The following table shows the *commandedObsState* given current *obsState* and issued command in progress: 

+-----------------+-----------------+------------------+---------------------+-----------+-------+---------+------+---------+---------------+---------+
|                 | *commandedObsState* for issued command                                                                                            |
+                 +-----------------+------------------+---------------------+-----------+-------+---------+------+---------+---------------+---------+
| obsState        | AssignResources | ReleaseResources | ReleaseAllResources | Configure | Scan  | EndScan | End  | Abort   | ObsReset      | Restart |
+=================+=================+==================+=====================+===========+=======+=========+======+=========+===============+=========+
| **EMPTY**       | IDLE            |                  |                     |           |       |         |      |         |               |         |
+-----------------+-----------------+------------------+---------------------+-----------+-------+---------+------+---------+---------------+---------+
| **RESOURCING**  |                 |                  |                     |           |       |         |      | ABORTED |               |         |
+-----------------+-----------------+------------------+---------------------+-----------+-------+---------+------+---------+---------------+---------+
| **IDLE**        | IDLE            | IDLE             | EMPTY               | READY     |       |         |      | ABORTED |               |         |
+-----------------+-----------------+------------------+---------------------+-----------+-------+---------+------+---------+---------------+---------+
| **CONFIGURING** |                 |                  |                     |           |       |         |      | ABORTED |               |         |
+-----------------+-----------------+------------------+---------------------+-----------+-------+---------+------+---------+---------------+---------+
| **READY**       |                 |                  |                     |           | READY |         | IDLE | ABORTED |               |         |
+-----------------+-----------------+------------------+---------------------+-----------+-------+---------+------+---------+---------------+---------+
| **SCANNING**    |                 |                  |                     |           |       | READY   |      | ABORTED |               |         |
+-----------------+-----------------+------------------+---------------------+-----------+-------+---------+------+---------+---------------+---------+
| **ABORTED**     |                 |                  |                     |           |       |         |      |         | IDLE or EMPTY | EMPTY   |
+-----------------+-----------------+------------------+---------------------+-----------+-------+---------+------+---------+---------------+---------+
| **RESETTING**   |                 |                  |                     |           |       |         |      | ABORTED |               |         |
+-----------------+-----------------+------------------+---------------------+-----------+-------+---------+------+---------+---------------+---------+
| **FAULT**       |                 |                  |                     |           |       |         |      |         | IDLE or EMPTY | EMPTY   |
+-----------------+-----------------+------------------+---------------------+-----------+-------+---------+------+---------+---------------+---------+

The device has change events configured for all the LRC attributes which clients can use to track
their requests. **The client has the responsibility of subscribing to events to receive changes on
command status and results**.


Input Queue
-----------
The `TaskExecutorComponentManager` (the default queue manager and concurrency mechanism) implements a
`ThreadPoolExecutor` which uses a `SimpleQueue` internally. The component manager exposes the queue size from
the `ThreadPoolExecutor` to determine the number of commands the tango device can accept based on a configurable
size limit. All LRCs are queued and executed in a background process. Each command is evaluated against the state
of the component before executing the task. The `native approach`_ in the TANGO developer guide implements the
check on the device when the command is triggered. On the other hand, the `TaskExecutorComponentManager` performs
the check only when it's dequeued. Methods implemented for component control should be supplied to the component
manager along with an additional method to check whether the command is allowed before executing.

UML Illustration
----------------

Multiple Clients Invoke Multiple Long Running Commands
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. uml:: lrc_scenario.uml

How to implement a long running command using the provided executor
-------------------------------------------------------------------
A task executor has been provisioned to handle the asynchronous execution of tasks
put on the queue. Your sample component manager will be asynchronous if it inherits
from the provisioned executor. You can also swap out the default executor with any
asynchronous mechanism for your component manager.

Create a component manager
^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^

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

Class diagram
-------------

.. uml:: lrc_class_diagram.uml


.. _native approach: https://pytango.readthedocs.io/en/stable/server_api/server.html?highlight=allowed#tango.server.command
