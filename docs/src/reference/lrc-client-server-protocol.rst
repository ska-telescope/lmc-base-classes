.. _lrc-client-server-protocol:

============================================
Long Running Command client/server interface
============================================

This page describes the protocol built on top of Tango used by ska-tango-base to
implement Long Running Commands.

Initiating Long Running Commands
--------------------------------

To initiate an LRC, a client must invoke the corresponding Tango command. This
Tango command either returns a :code:`(ResultCode, str)` pair or raises an
exception if argument validation fails.  The return value is to be interpreted
depending on the value of the ResultCode as follows:

- :obj:`ResultCode.QUEUED <ska_control_model.ResultCode.QUEUED>` -- The command
  has been queued, the second return value contains the generated command ID for
  the LRC.
- :obj:`ResultCode.STARTED <ska_control_model.ResultCode.STARTED>` -- The
  command has been started immediately, the second return value contains the
  generated command ID for the LRC.
- :obj:`ResultCode.REJECTED <ska_control_model.ResultCode.REJECTED>` -- The
  command has been rejected (because, for example there is no room in the Input
  Queue).  The second return value contains a reason string.


Monitoring progress of Long Running Commands
--------------------------------------------

Once a client has initiated an LRC as described above the following LRC
attributes are provided for monitoring the progress of their command.
Associate task data of ``status``, ``progress`` and ``result`` can be obtained
corresponding to the command ID they were returned from the initiating Tango
command.

LRC Attributes
~~~~~~~~~~~~~~

+-----------------------------+-------------------------------------------+----------------------+
| Attribute                   | Example Value                             |  Description         |
+=============================+===========================================+======================+
| longRunningCommandsInQueue  | ('Standby', 'On', 'Off')                  | Keeps track of which |
|                             |                                           | commands are known.  |
|                             |                                           | Note the name is     |
|                             |                                           | misleading as it     |
|                             |                                           | includes LRC         |
|                             |                                           | IN_PROGRESS and LRC  |
|                             |                                           | that are             |
|                             |                                           | COMPLETED/ABORTED/   |
|                             |                                           | REJECTED/FAILED      |
+-----------------------------+-------------------------------------------+----------------------+
| longRunningCommandIDsInQueue|('1636437568.0723004_235210334802782_On',  | Keeps track of IDs in|
|                             |'1636437789.493874_116219429722764_Off')   | that have been       |
|                             |                                           | allocated.           |
|                             |                                           | Note the name is     |
|                             |                                           | misleading as it     |
|                             |                                           | includes LRC         |
|                             |                                           | IN_PROGRESS and LRC  |
|                             |                                           | that are             |
|                             |                                           | COMPLETED/ABORTED/   |
|                             |                                           | REJECTED/FAILED      |
+-----------------------------+-------------------------------------------+----------------------+
| longRunningCommandStatus    | ('1636437568.0723004_235210334802782_On', | ID, status pair of   |
|                             | 'IN_PROGRESS',                            | the currently        |
|                             |                                           | allocated commands   |
|                             | '1636437789.493874_116219429722764_Off',  |                      |
|                             | 'QUEUED')                                 |                      |
+-----------------------------+-------------------------------------------+----------------------+
| longRunningCommandInProgress| ('On')                                    | Name of all commands |
|                             |                                           | currently executing  |
|                             | ('Configure', 'Abort')                    |                      |
|                             |                                           |                      |
|                             | ()                                        |                      |
+-----------------------------+-------------------------------------------+----------------------+
| longRunningCommandProgress  | ('1636437568.0723004_235210334802782_On', | ID, progress pair of |
|                             | '12',                                     | the currently        |
|                             |                                           | executing commands   |
|                             | '1636437789.493874_116219429722764_Off',  |                      |
|                             | '1')                                      |                      |
+-----------------------------+-------------------------------------------+----------------------+
| longRunningCommandResult    | ('1636438076.6105473_101143779281769_On', | ID,                  |
|                             | '[0, "On command completed OK"]')         | JSON encoded result  |
|                             |                                           | of the               |
|                             |                                           | completed command    |
+-----------------------------+-------------------------------------------+----------------------+
| _lrcEvents                  | ('1636438076.6105473_101143779281769_On', | ID, JSON encoded dict|
|                             | '{"status": 5, "result":                  | of status, progress  |
|                             | [0, "On command completed OK"]}')         | and/or result of all |
|                             |                                           | executing commands   |
+-----------------------------+-------------------------------------------+----------------------+

Associated data for a command will remain present in the above attributes for
(by default) at most 10 seconds after it has reached a terminal
:class:`~ska_control_model.TaskStatus` (one of
:obj:`TaskStatus.COMPLETED <ska_control_model.TaskStatus.COMPLETED>`
:obj:`TaskStatus.FAILED <ska_control_model.TaskStatus.FAILED>`
:obj:`TaskStatus.ABORTED <ska_control_model.TaskStatus.ABORTED>`
:obj:`TaskStatus.REJECTED <ska_control_model.TaskStatus.REJECTED>`) .  This is
controlled by the ``removal_time`` passed to the
:class:`~ska_tango_base.base.command_tracker.CommandTracker` initialiser. Note
that associated data for a command may be evicted earlier than 10 seconds after
reaching a terminal :class:`~ska_control_model.TaskStatus` to make room for
other commands.

The device has change events configured for all the LRC attributes which clients can use to track
their requests. **The client has the responsibility of subscribing to events to receive changes on
command status and results**, unless using the new
:func:`~ska_tango_base.long_running_commands_api.invoke_lrc` function, which handles the
events for you. The ``longRunningCommandStatus``, ``longRunningCommandProgress`` and 
``longRunningCommandResult`` is considered as v1 of the LRC client-server protocol.

New LRC client-server protocol (v2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``_lrcEvents`` attribute is only meant for internal use by the 
:func:`~ska_tango_base.long_running_commands_api.invoke_lrc` function. Reading it 
directly just returns an empty list. For each currently executing command, ``_lrcEvents`` 
pushes a change event containing the command ID and a json encoded dictionary of the 
status and/or progress and/or result received by the 
:func:`CommandTracker.update_command_info() <ska_tango_base.base.command_tracker.CommandTracker.update_command_info>` 
callback in a single call. Now 
:func:`~ska_tango_base.long_running_commands_api.invoke_lrc` rather subscribes to 
``_lrcEvents`` (if it's available on the device server) and then a client can know if a 
change to the status and result of a command are related via the callback the client 
passed to :func:`~ska_tango_base.long_running_commands_api.invoke_lrc`.

LRC commands
~~~~~~~~~~~~

In addition to the above attributes, the following commands are provided for
interacting with Long Running Commands.

+-------------------------------+------------------------------+
| Command                       | Description                  |
+===============================+==============================+
| CheckLongRunningCommandStatus | Check the status of a long   |
|                               | running command by ID        |
+-------------------------------+------------------------------+
| Abort                         | Abort the currently executing|
|                               | LRC and remove all enqueued  |
|                               | LRCs                         |
+-------------------------------+------------------------------+

UML illustration
----------------

Multiple clients invoke multiple Long Running Commands:

.. uml:: lrc-scenario.uml

Class diagram
-------------

.. uml:: lrc-class-diagram.uml

.. _native approach: https://pytango.readthedocs.io/en/stable/server_api/server.html?highlight=allowed#tango.server.command
