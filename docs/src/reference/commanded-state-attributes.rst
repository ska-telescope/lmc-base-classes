===============================================
commandedState and commandedObsState attributes
===============================================

In order to provide information about the state of a Tango device the
:obj:`~ska_tango_base.base.base_device.SKABaseDevice.commandedState` and 
:obj:`~ska_tango_base.obs.obs_device.SKAObsDevice.commandedObsState` attributes 
are provided by the :class:`~ska_tango_base.base.base_device.SKABaseDevice` and
:class:`~ska_tango_base.obs.obs_device.SKAObsDevice` classes
respectively.

These attributes indicate the expected stable operating or observation state
after the last long running command that has started is completed.

The :obj:`~ska_tango_base.base.base_device.SKABaseDevice.commandedState` string 
initialises to ``None``. The only other strings it can change to is ``OFF``,
``STANDBY`` or ``ON``, following the start of the ``Off``, ``Standby``, ``On`` 
or ``Reset`` long running commands. The following table shows the 
:obj:`~ska_tango_base.base.base_device.SKABaseDevice.commandedState` given current 
device state and issued command in progress: 

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

The :obj:`~ska_tango_base.obs.obs_device.SKAObsDevice.commandedObsState` 
initial value is :obj:`ObsState.EMPTY <ska_control_model.ObsState.EMPTY>`. 
The only stable (non-transitional) state values it can change to is 
:obj:`~ska_control_model.ObsState.EMPTY`, :obj:`~ska_control_model.ObsState.IDLE`, 
:obj:`~ska_control_model.ObsState.READY` or :obj:`~ska_control_model.ObsState.ABORTED` 
following the start of any of the :obj:`~ska_tango_base.obs.obs_device.SKAObsDevice`'s 
long running commands. The following table shows the 
:obj:`~ska_tango_base.obs.obs_device.SKAObsDevice.commandedObsState` given 
current :obj:`~ska_tango_base.obs.obs_device.SKAObsDevice.obsState` and issued command in progress: 

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

