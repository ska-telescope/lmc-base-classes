===============================================
commandedState and commandedObsState attributes
===============================================

In order to provide information about the state of a Tango device the
*commandedState* and *commandedObsState* attributes are provided by the
:class:`ska_tango_base.base.base_device.SKABaseDevice` and
:class:`ska_tango_base.subarray.subarray_device.SKASubarray` classes
respectively.

These attributes indicate the expected stable operating or observation state
after the last long running command that has started is completed.

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

