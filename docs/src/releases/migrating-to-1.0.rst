================
Migrating to 1.0
================

This migration guide lists all the breaking changes introduced by ska-tango-base
release 1.0.0.   Depending on the Tango Device implementation, some of the
changes may require developers’ intervention, i.e. may require updates in the
custom developed code.  In this guide the changes are ordered according to the
likelihood that a developer intervention is required, starting with the change
most likely to require developer intervention.

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: none

Dependencies
------------

ska-control-model
^^^^^^^^^^^^^^^^^

ska-tango-base 1.0.0 requires ska-control-model >= 1.0.0 < 2.0.0.  It is
recommended for packages to not explicitly reference ska-control-model in their
pyproject.toml and instead allow ska-tango-base to select the appropriate
ska-control-model version.

As most packages consume ska-control-model via ska-tango-base and ska-tango-base
and ska-control-model are so tightly coupled this document contains guidance for
migrating to both ska-tango-base 1.0.0 and ska-control-model 1.0.0.

PyTango
^^^^^^^

ska-tango-base 1.0.0 requires PyTango >= 9.4.2 < 10.0.0.  This is due to a combination of
two reasons:

* The Tango event system does not work in between Kubernetes namespaces for
  PyTango versions before 9.4.2.
* The PyTango releases 9.3.x are more difficult to work with because the
  Tango collaboration do not provide wheels for them.

Although ska-tango-base 1.0.0 supports PyTango 9.4.2 it is recommended to update
to the latest PyTango 9.5.1.

It is possible to update both ska-tango-base to 1.0.0 and PyTango to 9.5.1
simultaneously, and it is expected that this will be straight forward for most
packages.  See the remainder of this document and the `PyTango migration guide
<https://pytango.readthedocs.io/en/latest/versions/migration/index.html>`_
for help updating.

If a lot of changes are required, the upgrade may be performed incrementally.
Below is a plan to migrate a package from an "old" ska-tango-base release (pre
0.19.2) and PyTango 9.3.x to ska-tango-base 1.0.0 and PyTango 9.5.1.

#. Update ska-tango-base to 0.20.2 -- this version supports PyTango 9.5.1 and
   provides deprecation warnings for the changes in ska-tango-base 1.0.0.
#. Update PyTango to 9.5.1 -- see the `PyTango migration guide
   <https://pytango.readthedocs.io/en/latest/versions/migration/index.html>`_ for
   help doing this.
#. Update ska-tango-base to 1.0.0 -- see the remainder of this document for help
   doing this.

AdminMode.MAINTENANCE has been removed
--------------------------------------

In the ska-control-model release 0.3.4 introduced the following changes:

- Replaced :obj:`!AdminMode.MAINTENANCE` with  :obj:`AdminMode.ENGINEERING <ska_control_model.AdminMode.ENGINEERING>`.
- Replaced the :class:`~ska_control_model.AdminModeModel` action :code:`"to_maintenance"`  with :code:`"to_engineering"`.

These changes were introduced to avoid confusion with the DISH MAINTENANCE mode
(see SP-3868 for details).

To maintain backwards compatibility, ska-control-model 0.3.4 allowed for the use
of the old names :obj:`!AdminMode.MAINTENANCE` and :code:`"to_maintenance"`,
generating deprecation warnings on use.

With the ska-control-model release 1.0.0 :obj:`!AdminMode.MAINTENANCE` has been
removed as has the :code:`"to_maintenance"` action.  This might require changes
when updating to ska-control-model 1.0.0.

When updating you must replace any reference to :obj:`!AdminMode.MAINTENANCE`
with :obj:`AdminMode.ENGINEERING <ska_control_model.AdminMode.ENGINEERING>`.
Recall that :obj:`!AdminMode.MAINTENANCE` might be being referenced by a string
variable by either indexing or calling :class:`~ska_control_model.AdminMode`,
for example::

   mode_str = "MAINTENANCE"
   mode = AdminMode[mode_str]
   mode2 = AdminMode(mode_str)

In this example, :code:`mode_str` would need to be updated to
:code:`"ENGINEERING"`.  The deprecation warnings provided by ska-control-model
0.3.4 can help you track down these cases.

It is unlikely that your package is referencing the :code:`"to_maintenance"`
action of the :class:`ska_control_model.AdminModeModel`, but if it is you will
need to use :code:`"to_engineering"` instead.

max_workers has been removed from the TaskExecutorComponentManager initialiser
------------------------------------------------------------------------------
Setting max_workers to a value greater then 1 results in multiple LRCs being
executed simultaneously, which may give unpredictable results.  In the case
where simultaneous execution of two or more LRCs is needed,  careful
consideration is required by the component manager developer to avoid multiple
LRCs being executed simultaneously which perform state and/or mode transition(s).

Having the :obj:`!max_workers` parameter for the
:class:`~ska_tango_base.executor.executor_component_manager.TaskExecutorComponentManager`
implies that providing different values for this parameter will "just work".
However, this is not the case so for ska-tango-base 1.0.0.  The parameter has
been removed in favour of mechanisms for supporting multiple executing LRCs which
nudge the developer into addressing the issues that come with this.

In ska-tango-base 0.20.0 this parameter was deprecated.  For
ska-tango-base 1.0.0 it has been removed.

If you are setting :obj:`!max_workers` to 1, you can safely remove the argument
without issue.

If you are setting it to a value other than 1 and put in the careful thought
required to make this work and would like to keep the old behaviour, you can
override the construction of the
:class:`~ska_tango_base.executor.executor.TaskExecutor` in your initialisation
method.  For example::

   class MyComponentManager(TaskExecutorComponentManager):
      def __init__(self, max_workers, ...):
         super().__init__(...)
         self._task_executor = TaskExecutor(max_workers=max_workers)

New BaseComponentManager properties describing LRC capabilities
---------------------------------------------------------------

ska-tango-base 1.0.0 has introduced two new read-only properties to the
:class:`~ska_tango_base.base.component_manager.BaseComponentManager`,
:attr:`~ska_tango_base.base.component_manager.BaseComponentManager.max_executing_tasks`
and
:attr:`~ska_tango_base.base.component_manager.BaseComponentManager.max_queued_tasks`.
These properties describe how many tasks a component manager can be
simultaneously set to
:obj:`TaskStatus.IN_PROGRESS <ska_control_model.TaskStatus.IN_PROGRESS>`
or
:obj:`TaskStatus.QUEUED <ska_control_model.TaskStatus.QUEUED>`
respectively.
:class:`~ska_tango_base.base.component_manager.BaseComponentManager` provides a
default implementation for these properties (hard-coded to the minimums,
:code:`max_executing_tasks=1` and :code:`max_queued_tasks=0`) and the intention is that
derived classes override these properties so that the
:class:`~ska_tango_base.base.base_device.SKABaseDevice` can construct the LRC
attributes with appropriate maximum bounds.

:class:`~ska_tango_base.subarray.component_manager.SubarrayComponentManager`
overrides ``max_executing_tasks`` to 2 as the Abort command must be executed
simultaneously with other commands.
:class:`~ska_tango_base.executor.executor_component_manager.TaskExecutorComponentManager`
overrides ``max_queued_tasks`` to reflect the size of its queue.

If your component manager inherits from either
:class:`~ska_tango_base.subarray.component_manager.SubarrayComponentManager`
or
:class:`~ska_tango_base.executor.executor_component_manager.TaskExecutorComponentManager`
(or both) you do not have to do anything unless your component manager can
execute more than 2 tasks at the same time or has an additional queue over the
queue provided by the ``TaskExecutorComponentManager``.

If your component manager does not inherit from these, you may have to override
one or both of the properties to correctly reflect how many tasks can be 
:obj:`TaskStatus.IN_PROGRESS <ska_control_model.TaskStatus.IN_PROGRESS>`
or
:obj:`TaskStatus.QUEUED <ska_control_model.TaskStatus.QUEUED>`
simultaneously.

If your component manager does not correctly report this information, warnings
will be generated if the LRC attribute maximum size is exceeded for any LRC
attribute and clients may not receive information about your tasks.


Changes to LRC results provided by default by ska-tango-base
------------------------------------------------------------

In ska-tango-base 1.0.0, the Long Running Commands always provide the result of
type :code:`(ResultCode, str)` when they transition an LRC to a finished status.

The new guidelines (see :ref:`lrc-task-guidelines`) for how to use the LRC
attributes prescribe that an LRC shall report the outcome (success or failure)
by providing a ResultCode.  The originator of the command (a client) shall
subscribe to the attribute ``longRunningCommandResult`` to be notified when the
execution of the command ends, and to receive the
:class:`~ska_control_model.ResultCode` (i.e. to be notified regarding the
outcome, success or failure).

Prior to ska-tango-base 1.0.0, the base classes themselves did not always follow
this guideline.  In the earlier versions of the ska-tango-base, in some cases
the result code does not get updated when the command ends, or a message string
is provided, but not the result code.  In ska-tango-base 1.0.0, all the LRCs
always provide a result of type :code:`(ResultCode, str)` when they transition
to a finished status.

.. note::

   This is only a change for when ska-tango-base sets the result because, for
   example, the command was not allowed.  If the task implementing the command
   sets the result, just as before ska-tango-base 1.0.0, it can have any type
   provided that it is JSON encodable, although it is recommended to include a
   :class:`~ska_control_model.ResultCode`.

Specifically, for ska-tango-base 1.0.0 the following changes have been made:

- When the command is aborted after being dequeued its result will be set to
  :code:`(ResultCode.ABORTED, <message>)` instead of :code:`<message>`.
- When the command is rejected after being dequeued because it is not allowed,
  the result will be :code:`(ResultCode.NOT_ALLOWED, <message>)` instead of
  :code:`<message>`.
- When a task raises an exception, the result of the command will be
  :code:`(ResultCode.FAILED, <message>)` instead of :code:`<message>`.

.. TODO WOM-343 should update the above list for any other situations they find

This changes might require clients to change how they match these results.

LRCs are transitioned to TaskStatus.STAGING initially
-----------------------------------------------------

This :obj:`TaskStatus.STAGING <ska_control_model.TaskStatus.STAGING>` status
corresponds to the state the command is in while the device decides whether to
enqueue or reject the command. :obj:`~ska_control_model.TaskStatus.STAGING` has
always been a member of :class:`~ska_control_model.TaskStatus` and appears in
the LRC documentation, however, prior to the ska-tango-base release 1.0.0 it was
never actually used.

For ska-tango-base 1.0.0 its use has been added so that the command is "in the
system" as early as possible - improving the visibility of the command if, for
example, the device gets stuck while deciding whether to enqueue or reject the
command.

This change might require clients to be updated which were expecting the initial
status for a command to be :obj:`TaskStatus.QUEUED
<ska_control_model.TaskStatus.QUEUED>`.

Changes to longRunningCommandInProgress
---------------------------------------

Prior to ska-tango-base 1.0.0, the
:attr:`~ska_tango_base.base.base_device.SKABaseDevice.longRunningCommandInProgress`
attribute would always contain two elements.  For example, when there were no
commands in progress it would contain :code:`["", ""]`.

To align the behaviour with the other LRC attributes for
ska-tango-base 1.0.0, the
:attr:`~ska_tango_base.base.base_device.SKABaseDevice.longRunningCommandInProgress`
attribute will contain as many elements as there are LRCs in progress.  So, for
example, if there are no LRCs in progress the attribute will contain
an empty list (:code:`[]`).

If your client was relying on the previous behaviour of always containing two
elements then it will need updating.
