============================================
Long Running Command Client/Server Interface
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


Monitoring Progress of Long Running Commands
--------------------------------------------

Once a client has initiated an LRC as described above the following LRC
attributes are provided for monitoring the progress of their command.
Associate task data of ``status``, ``progress`` and ``result`` can be obtained
corresponding to the command ID they were returned from the initiating Tango
command.

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
|                             |'1636437789.493874_116219429722764_Off')   |                      |
+-----------------------------+-------------------------------------------+----------------------+
| longRunningCommandStatus    | ('1636437568.0723004_235210334802782_On', | ID, status pair of   |
|                             | 'IN_PROGRESS',                            | the currently        |
|                             |                                           | executing commands   |
|                             | '1636437789.493874_116219429722764_Off',  |                      |
|                             | 'IN_PROGRESS')                            |                      |
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
|                             | ('0', 'OK'))                              | JSON encoded result  |
|                             |                                           | of the               |
|                             |                                           | completed command    |
+-----------------------------+-------------------------------------------+----------------------+

The device has change events configured for all the LRC attributes which clients can use to track
their requests. **The client has the responsibility of subscribing to events to receive changes on
command status and results**.

In addition to the above attributes, the following commands are provided for
interacting with Long Running Commands.

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

UML Illustration
----------------

Multiple Clients Invoke Multiple Long Running Commands
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. uml:: lrc-scenario.uml

Class diagram
-------------

.. uml:: lrc-class-diagram.uml

.. _native approach: https://pytango.readthedocs.io/en/stable/server_api/server.html?highlight=allowed#tango.server.command
