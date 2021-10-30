====================================================
Asynchronous Implementation of Long Running Commands
====================================================

The base device has a worker thread/queue implementation for long running
commands (LRCs) to allow concurrent access to TANGO devices. This means that
devices return immediately with a response while busy with the actual task
in the background or parked on a queue pending the next available worker.
The number of commands which can be received depends on a configurable
maximum queue size of the device. Clients requests to devices at maximum
queue size are rejected and will need to retry to have their command enqueued.

.. note:: Long Running Command: A TANGO command for which the execution time
   is in the order of seconds (CS Guidelines recommends less than 10 ms).
   In this context it also means a command which is implemented to execute
   asynchronously. Long running and asynchronous are used interchangeably in 
   this text and the code base. In the event where the meaning differ it will
   be explained but both mean non-blocking.

New attributes and commands have been added to the base device to support the
mechanism to execute long running TANGO commands asynchronously. 

LRC Attributes
--------------
The new set of attributes record the result, status and progress of LRCs running
from a queue.

+-----------------------------+-----------------------+----------------------+
| Attribute                   | Value                 | Description          |
+=============================+=======================+======================+
| longRunningCommandsInQueue  | column 2              | Keeps track of which |
|                             |                       | commands are on the  |
|                             |                       | queue                |
+-----------------------------+-----------------------+----------------------+
| longRunningCommandIDsInQueue| column 2              | Keeps track of IDs in|
|                             |                       | the queue            |
+-----------------------------+-----------------------+----------------------+
| longRunningCommandStatus    | column 2              | ID, status pair of   |
|                             |                       | the currently        |
|                             |                       | executing commands   |
+-----------------------------+-----------------------+----------------------+
| longRunningCommandProgress  | column 2              | ID, progress pair of |
|                             |                       | the currently        |
|                             |                       | executing commands   |
+-----------------------------+-----------------------+----------------------+
| longRunningCommandResult    | column 2              | ID, ResultCode,      |
|                             |                       | result of the        |
|                             |                       | completed command    |
+-----------------------------+-----------------------+----------------------+


LRC Commands
------------
The new set of commands report the content of the LRC attributes or flush the queue.

+-------------------------------+------------------------------+
| Command                       | Description                  |
+===============================+==============================+
| CheckLongRunningCommandStatus | Check the status of a long   |
|                               | running command by ID        |
+-------------------------------+------------------------------+
| AbortCommands                 | Abort the currently executing|
|                               | LRCs and remove all enqueued |
|                               | LRCs                         |
+-------------------------------+------------------------------+

In addition to the set of commands in the table above, a number of candidate SKA
commands in the base device previously implemented as blocking commands have been
converted to execute as long commands (asynchronously), viz: Standby, On, Off,
Reset and GetVersionInfo.


Implementing a TANGO Command as Long Running
--------------------------------------------
The LRC update is a drop-in replacement of the current base device implementation.
The base device provisions a QueueManager which has no threads. Existing device 
implementations will execute commands in the same manner unless your component manager
specifies otherwise. Summarised in a few points, you would do the following to implement
TANGO commands as long running:

1. Create a component manager of type QueueWorkerComponentManager with queue size and thread determined.

2. Create the command class for your tango command.

3. Use the component manager to enqueue your command in the command class.

Example Device Implementing Long Running Command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: py

   class DeviceWithLongRunningCommands(SKABaseDevice):
    ...
    def create_component_manager(self: SKABaseDevice):

        return QueueWorkerComponentManager(
            op_state_model=self.op_state_model,
            logger=self.logger,
            max_queue_size=20,
            num_workers=3,
            push_change_event=self.push_change_event,
        )

then to enqueue your command:

.. code-block:: py

   class PerformLongTaskCommand(ResponseCommand):
        """The command class for PerformLongTask command."""

        def do(self):
            """Download telescope data from the internet"""
            download_tel_data()

    @command(
        dtype_in=None,
        dtype_out="DevVarStringArray",
    )
    @DebugIt()
    def PerformLongTask(self):
        """Command that queues a task that downloads data"""
        handler = self.get_command_object("PerformLongTask")

        # Enqueue here
        (return_code, message) = self.component_manager.enqueue(handler)

        return f"{return_code}", f"{message}"
