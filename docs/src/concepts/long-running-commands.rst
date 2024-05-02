=====================
Long Running Commands
=====================

Before we introduce the concept of a Long Running Command we will discuss how a
more traditional Tango control system would go about coordinating asynchronous
operations.  Then we demonstrate the Long Running Command is just a
standardisation of the practice used in more traditional Tango control systems.

Asynchronous operations
^^^^^^^^^^^^^^^^^^^^^^^

A typical Tango device in any control system will at times have to monitor and
control operations which take a long time.  For example,

* moving motors to a given position
* bring a piece of equipment to the required temperature
* performing an intensive calculation
* commanding for a set of subordinate Tango devices to undertaken their own
  "slow operations"

All these operations take an incredibly long time from the perspective of a CPU
and a client requesting the Tango device to do this operations does not want to
wait around for them to complete.  Instead they want to start the operations of
asynchronously and get on with other activities only to be notified later when
the operation has completed.

The traditional way this is handled within a Tango control system is as
follows,

#. The client will invoke a Tango command which begins the operation.  This
   command returns almost immediately.
#. The client will subscribe to some ad-hoc Tango attributes to know when the
   operation has completed.
#. At some point the operation will be finished and the Tango device will update
   the attributes.

The attributes the client subscribes to are ad-hoc in the sense that which
attributes to use depend on the operation the client wishes to do.
Additionally, a typical traditional Tango device software won't "know about" the
operation, it simply updates the attributes as a result of its normal monitoring
duties.  For example, suppose we wanted to cool some apparatus to a given
temperature, the sequence of events for a traditional Tango control system might
be as follows:

#. The client invokes the "TurnOnCoolers" Tango command providing a
   set-point temperature.
#. The device does whatever it has to do to turn on the coolers and then the
   "TurnOnCoolers" Tango command returns to the client.
#. The client subscribes to the boolean attribute "AtSetPoint".  This attribute
   is :code:`True` when the temperature is stable and at the requested
   set point.
#. At some point later, the device determines via its normal monitoring that the
   apparatus has reached the set-point temperature and notifies the client by
   setting "AtSetPoint" to :code:`True`.

The definition of a Long Running Command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At SKA we have decided that this pattern is common enough to introduce the
concept of a Long Running Command (LRC) to standardise the practice.

An LRC is defined as an asynchronous command which is fulfilled by some
asynchronous task executed by the Tango device server.

The LRC is initiated by a Tango command which returns a command ID.  The client
subscribes to LRC attributes which provide information about the asynchronous
task fulfilling their command, using the command ID to determine if the
information relates to _their_ task.  Once the task has finished there will be
an associated ``result`` which the client will be notified of via the LRC
attributes, see XXX.

.. TODO Replace XXX with link to "Client/Server LRC protocol" page

With this defintion, coordinating asynchronous operations with LRCs is very
similar to how asynchronous operations are coordinated in a traditional control
system, as described above.  The key differences are the following:

* To know when the asynchronous operation has completed, a client does not
  subscribe to ad-hoc Tango attributes but instead a standardised set of LRC
  attributes.
* The entire asynchronous operation itself is considered to be the LRC.  Unlike
  in the traditional control system, this operation then has a ``result``.
* The Tango device keeps track of a task which corresponds to the LRC.  In a
  traditional control system the Tango device would not be explicitly aware of
  the asynchronous operation taking place.

.. warning::

    There is a potential point of confusion here with regards to the word
    command.  Each Long Running Command is initiated by a Tango command of the
    same name.  This Tango command is in some sense *part* of the LRC.  In this
    document we will not use the word command on its own, instead prefering LRC
    and Tango command to distinguish between the two.

As an example, consider again the example of cooling some apparatus as we looked at
for a traditional Tango control system.  When using LRC's the sequence might
look like the following:

#. The client invokes the "CoolTo" Tango command to initiate the "CoolTo" LRC
   providing a set point temperature.
#. The device kicks off some asynchronous task to start the cooling process then
   returns a freshly generated command ID to the client.
#. The client subscribes to the ``longRunningCommandResult`` attribute to be
   notified when their command has finished.
#. The task running inside the Tango device decides it has finished and informs
   the client by providing a ``result``.  The client inspects the ``result`` to
   determine if the LRC succeeded or failed.

The LRC Input Queue
^^^^^^^^^^^^^^^^^^^

In addition to providing a standardised interface to asynchronous operations,
the idea of a LRC command introduces objects in software which correspond to
these asynchronous operations.  ``ska-tango-base`` takes advantage of this by
introducing an LRC input queue. This allows an operator to queue up a sequence
of asynchronous operations without having to sit an monitor the Tango device.

Typically, when a Tango device receives an LRC it enqueues a task to the input
queue. When that task gets to the front the queue, it is dequeued, the device
checks if the task is allowed the current state of the device (determined via an
"is_allowed callback") and if all is fine, it begins executing the task.

Once the task has completed, successfully or otherwise, the next task is
dequeued and is executed (provided it is allowed).

.. note::

   An exception to the use of the Input Queue is the Abort LRC from the
   :class:`~ska_tango_base.subarray.subarray_device.SKASubarray` class.  This command
   **must** be executed immediately and cannot be queued.

.. warning::

   Like all Tango commands, the Tango command that initiates an LRC also has an
   "is_allowed callback".  This "native" Tango is_allowed callback is
   determining whether the task can be enqueued, this is different from the
   LRC is_allowed callback that is called after the task is dequeued.  The LRC
   is_allowed callback determines if the task can be executed based on the
   current state, which might be different to the state the device was in when
   the task was enqueued.

Long Running Command tasks
^^^^^^^^^^^^^^^^^^^^^^^^^^

As described above, each LRC is fulfilled by a task.  Typically, this task is
some function running in a separate thread, but this is not required.  The task
might be some operation running on a piece of hardware and all the Tango device
is doing is monitoring the hardware and updating clients with information about
the tasks progress.

Regardless of what the task physically is, it has an associated
:class:`~ska_control_model.TaskStatus` which must follow the following state
machine:

.. uml:: lrc-task-status.uml

For each task there is a corresponding ``task_callback`` which must be called to
update the :class:`~ska_control_model.TaskStatus` of the task.  This
``task_callback`` will update the LRC attributes with information about the status
of the task and associate it with appropriate command ID.

In addition to its ``status``, each task has additional data associated with it:

* When the task's status is one of
  :obj:`~ska_control_model.TaskStatus.COMPLETED`,
  :obj:`~ska_control_model.TaskStatus.FAILED`,
  :obj:`~ska_control_model.TaskStatus.ABORTED` or
  :obj:`~ska_control_model.TaskStatus.REJECTED` it must have a ``result``.  This
  result can be any JSON encodable python object.
* When the task's status is
  :obj:`~ska_control_model.TaskStatus.IN_PROGRESS`
  it may have an optional ``progress`` associated with it.  This progress is an
  integer.  It is recommended to be an integer between 0-99 representing an
  percentage, although a task is free to use any values as appropriate.

Just as with the ``status``, the ``task_callback`` must be called to update the
task's ``result`` and ``progress``.  The ``task_callback`` broadcast this data
via the LRC attributes, associating it with the appropriate command ID.
