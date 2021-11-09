====================================================
Asynchronous Implementation of Long Running Commands
====================================================

Some SKA commands interact with hardware systems that have some inherent delays
in their responses. Such commands block concurrent access to TANGO devices and
affect the overall performance (responsiveness) of the device to other requests.
To address this, the base device has a worker thread/queue implementation for
long running commands (LRCs) to allow concurrent access to TANGO devices.

.. note:: Long Running Command: A TANGO command for which the execution time
   is in the order of seconds (CS Guidelines recommends less than 10 ms).
   In this context it also means a command which is implemented to execute
   asynchronously. Long running and asynchronous are used interchangeably in 
   this text and the code base. In the event where the meaning differ it will
   be explained but both mean non-blocking.

This means that devices return immediately with a response while busy with the
actual task in the background or parked on a queue pending the next available worker.
The number of commands which can be received depends on a configurable maximum queue 
size of the device. Clients requests to devices at maximum queue size are rejected and
will need to retry to have their command enqueued.


New attributes and commands have been added to the base device to support the
mechanism to execute long running TANGO commands asynchronously.

Reference Design for the Implementation of Long Running Commands
----------------------------------------------------------------
A message queue solution is the backbone to the implementation of the LRC design. The goal
is to have a hybrid solution which will have the queue usage as an opt in. Note that the
device cannot process short running commands, reply to attribute reads and writes, process
subscription requests or send events with the default option. That said, the SKABaseDevice
meets the following requirements for executing long running commands:

* With no queue (default):
    * start executing LRC if another LRC is not currently executing
    * reject the LRC if another LRC is currently executing
* With queue enabled:
    * enqueue the LRC if the queue is not full
    * reject the LRC if the queue is full
    * execute the LRCs in the order which they have been enqueued (FIFO)
* Interrupt LRCs:
    * abort the execution of currently executing LRCs 
    * flush enqueued LRCs

Monitoring Progress of Long Running Commands
--------------------------------------------
In addition to the listed requirements above, the device should provide monitoring points
to allow clients determine when a LRC is received, executing or completed (success or fail).
LRCs can assume any of the following defined task states: QUEUED, IN_PROGRESS, ABORTED,
COMPLETED, FAILED, NOT_ALLOWED. NOT_FOUND is returned for command IDs that are non-existent.

.. uml:: lrc_command_state.uml

A new set of attributes and commands have been added to the base device to enable
monitoring and reporting of result, status and progress of LRCs.

**LRC Attributes**

+-----------------------------+-------------------------------------------------+----------------------+
| Attribute                   | Example Value                                   |  Description         |
+=============================+=================================================+======================+
| longRunningCommandsInQueue  | ('StandbyCommand', 'OnCommand', 'OffCommand')   | Keeps track of which |
|                             |                                                 | commands are on the  |
|                             |                                                 | queue                |
+-----------------------------+-------------------------------------------------+----------------------+
| longRunningCommandIDsInQueue|('1636437568.0723004_235210334802782_OnCommand', | Keeps track of IDs in|
|                             |1636437789.493874_116219429722764_OffCommand)    | the queue            |
+-----------------------------+-------------------------------------------------+----------------------+
| longRunningCommandStatus    | ('1636437568.0723004_235210334802782_OnCommand',| ID, status pair of   |
|                             | 'IN_PROGRESS',                                  | the currently        |
|                             | '1636437789.493874_116219429722764_OffCommand', | executing commands   |
|                             | 'IN_PROGRESS')                                  |                      |
+-----------------------------+-------------------------------------------------+----------------------+
| longRunningCommandProgress  | ('1636437568.0723004_235210334802782_OnCommand',| ID, progress pair of |
|                             | '12%',                                          | the currently        |
|                             | '1636437789.493874_116219429722764_OffCommand', | executing commands   |
|                             | '1%')                                           |                      |
+-----------------------------+-------------------------------------------------+----------------------+
| longRunningCommandResult    | ('1636438076.6105473_101143779281769_OnCommand',| ID, ResultCode,      |
|                             | '0', 'OK')                                      | result of the        |
|                             |                                                 | completed command    |
+-----------------------------+-------------------------------------------------+----------------------+


**LRC Commands**

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
converted to execute as long running commands (asynchronously), viz: Standby, On, Off,
Reset and GetVersionInfo.

The device has change events configured for all the LRC attributes which clients can use to track
their requests. The client has the responsibility of subscribing to events to receive changes on
command status and results. To make monitoring easier, there's an interface (LongRunningDeviceInterface)
which can be used to track attribute subscriptions and command IDs for a list of devices specified.
More on its usage can be found in `utils <https://gitlab.com/ska-telescope/ska-tango-base/-/blob/main/src/ska_tango_base/utils.py#L566>`_.

UML Illustration
----------------

Multiple Clients Invoke Multiple Long Running Commands
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. uml:: lrc_scenario.uml

Implementing a TANGO Command as Long Running
--------------------------------------------
The LRC update is a drop-in replacement of the current base device implementation.
The base device provisions a QueueManager which has no threads and no queue. Existing device 
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
    def create_component_manager(self):

        return QueueWorkerComponentManager(
            op_state_model=self.op_state_model,
            logger=self.logger,
            max_queue_size=20,
            num_workers=3,
            push_change_event=self.push_change_event,
        )

.. note:: QueueWorkerComponentManager does not have access to the tango layer.
In order to send LRC attribute updates, provide a copy of the device's `push_change_event`
method to its constructor.

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
