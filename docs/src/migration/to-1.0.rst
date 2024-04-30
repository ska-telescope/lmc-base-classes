==============
Moving to v1.0
==============

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
* The 9.3.x releases of PyTango are more difficult to work with because the
  Tango collaboration do not provide wheels for them.

Although ska-tango-base 1.0.0 supports PyTango 9.4.2 it is recommended to update
to the latest PyTango 9.5.1.

It is possible to update both ska-tango-base to 1.0.0 and PyTango to 9.5.1
simultaneously, and it is expected that this will be straight forward for most
packages.  See the remainder of this document and the `PyTango migration guide
<https://pytango.readthedocs.io/en/latest/versions/migration/index.html>`_
for help updating.

If you find that a lot of changes are required, you might want to do the upgrade
incrementally. Below is a plan to migrate a package from an "old" ska-tango-base
release (pre 0.19.2) and PyTango 9.3.x to ska-tango-base 1.0.0 and PyTango
9.5.1.

#. Update ska-tango-base to 0.20.2 -- this version supports PyTango 9.5.1 and
   provides deprecation warnings for the changes in ska-tango-base 1.0.0.
#. Update PyTango to 9.5.1 -- see the `PyTango migration guide
   <https://pytango.readthedocs.io/en/latest/versions/migration/index.html>`_ for
   help doing this.
#. Update ska-tango-base to 1.0.0 -- see the remainder of this document for help
   doing this.

AdminMode.MAINTENANCE has been removed
--------------------------------------

In the ska-control-model 0.3.4 release :obj:`!AdminMode.MAINTENANCE` was renamed
to :obj:`AdminMode.ENGINEERING <ska_control_model.AdminMode.ENGINEERING>` and
the :code:`"to_maintenance"` action for the
:class:`~ska_control_model.AdminModeModel` was renamed to `"to_engineering"`.
This was to avoid confusion with the DISH MAINTENANCE mode, see SP-3868 for
details. For the ska-control-model 0.3.4 release :obj:`!AdminMode.MAINTENANCE`
and `"to_maintenance"` action remained for backwards compatibility and generated
a deprecation warning.

With the ska-control-model 1.0.0 release :obj:`!AdminMode.MAINTENANCE` has been
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
:code:`"ENGINEERING"`.  The deprecation warnings provided by the 0.20.0 release
can help you track down these cases.

It is unlikely that your package is referencing the :code:`"to_maintenance"`
action of the :class:`ska_control_model.AdminModeModel`, but if it is you will
need to use :code:`"to_engineering"` instead.

max_workers has been removed from the TaskExecutorComponentManager initialiser
------------------------------------------------------------------------------

The default Long Running Commands perform state transitions which cannot be
executed simultaneously.   Setting :obj:`!max_workers` to anything other than 1
results in multiple state transitions being attempted simultaneously without
careful consideration by the component manager developer.

Having the :obj:`!max_workers` parameter for the
:class:`~ska_tango_base.executor.executor_component_manager.TaskExecutorComponentManager`
implies that providing different values for this parameter will "just work".
However, this is not the case so for ska-tango-base 1.0.0.  The parameter has
been removed in favour of mechanisms for supporting multiple executing LRCs which
nudge the developer into addressing the issues that come with this.

In the ska-tango-base 0.20.0 release this parameter was deprecated.  For
the ska-tango-base 1.0.0 release it has been removed.

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

For guidance on how to execute multiple LRCs at once with the careful thought
required see XXX.

.. TODO Write How-to about component managers with multiple queues

Changes to LRC results provided by default by ska-tango-base
------------------------------------------------------------

The new guidelines (XXX) for how to use the LRC attributes suggest that when a
LRC has finished (successfully or otherwise) it should always have a result and
that result should contain a :class:`~ska_control_model.ResultCode` to
indicate the success or failure of the LRC.  This is to allow clients to only
subscribe to the
:attr:`~ska_tango_base.base.base_device.SKABaseDevice.longRunningCommandResult`
attribute and to know when their command has finished, and if it did so
successfully.

.. TODO Link to these guidelines

Prior to ska-tango-base 1.0.0, the base classes themselves did not always follow
these guidelines.  There would be some situations where the ska-tango-base would
transition an LRC to a finished status and either not provide a result for the
LRC, or the result would just contain a message string.  For ska-tango-base
1.0.0, the base classes will always provide a result of type :code:`(ResultCode,
str)` when they transition an LRC to a finished status.

.. note::

   This is only a change for when ska-tango-base sets the result because, for
   example, the command was not allowed.  If the task implementing the command
   sets the result, just as before ska-tango-base 1.0.0, it can have any type
   provided that it is JSON encodable, although it is recommended to include a
   :class:`~ska_control_model.ResultCode`.

Specifically, for the ska-tango-base 1.0.0 release the following changes have
been made:

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
the LRC documentation, however, prior to the ska-tango-base 1.0.0 release it was
never actually used.

For ska-tango-base 1.0.0 its use has been added so that the command is "in the
system" as early as possible - improving the visibility of the command if, for
example, the device gets stuck while deciding whether to enqueue or reject the
command.

This change might require clients to be updated which were expecting the initial
status for a command to be :obj:`TaskStatus.QUEUED
<ska_control_model.TaskStatus.QUEUED>`.
