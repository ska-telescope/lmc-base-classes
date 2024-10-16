================
Migrating to 1.2
================

This migration guide lists all the deprecations introduced by ska-tango-base
release 1.2.0.  There are no breaking changes for this release so developers
can update from version 1.0.0 or 1.1.0 without having to make any changes.
However, there are several features that have been deprecated with this release
and where ever possible deprecation warnings are emitted whenever they are used.
This guide contains recommendations about how to resolve the deprecation
warnings in order to prepare for the major release of ska-tango-base where
these will be removed.

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: none

AbortCommands() command
-----------------------

In ska-tango-base 1.2.0, the :any:`SKABaseDevice.AbortCommands` command has been
deprecated in favor of the :any:`SKABaseDevice.Abort` command. In addition
:any:`BaseComponentManager.abort_commands` method has been deprecated in favor of either
the :any:`BaseComponentManager.abort` method or the :any:`BaseComponentManager.abort_tasks`
method.

Rationale
^^^^^^^^^

Prior to ska-tango-base 1.2.0, the following default commands are
provided by the base classes.

- :any:`SKABaseDevice` provides an :any:`AbortCommands` command which calls the
  :any:`abort_commands` method of the component manager.  This command is supposed to 
  abort all the currently queued and executing long running commands and is **not**
  itself a long running command.

- :any:`SKASubarray<subarray_device.SKASubarray>` provides an
  :any:`Abort` command which calls the :any:`Abort` method of the component
  manager. This command is supposed to transition the device's
  :obj:`~ska_control_model.ObsState` to
  :obj:`~ska_control_model.ObsState.ABORTED` via the
  :obj:`~ska_control_model.ObsState.ABORTING` state.  The device should cease
  all activities when it receives an :any:`Abort` command, including any other
  long running commands.  The command **is** itself a long running command.

Recall that the :any:`SKASubarray<subarray_device.SKASubarray>` class inherits from the 
:any:`SKABaseDevice`, so it also has an :any:`AbortCommands` command. It is not clear how the 
:any:`AbortCommands` command should interact with the :any:`Abort` command. For example, 
if we invoke :any:`AbortCommands` while the :any:`Abort` command is in progress, should 
the device transition to :obj:`obsState.ABORTED <ska_control_model.ObsState.ABORTED>`?  
If we call the :any:`AbortCommands` command while the :any:`On` command 
is in progress, what :class:`~ska_control_model.ObsState` should we end up in?

The difficulty in answering these questions suggests that there is an issue with
the design and the solution chosen is to simplify the API.  To this end, in
ska-tango-base 1.2.0 an :any:`Abort` command has been added to the :any:`SKABaseDevice`.
Like the :any:`Abort` command of the :any:`SKASubarray<subarray_device.SKASubarray>`, 
this is a long running command and must be started immediately without being queued.

Other than it being a long running command, the :any:`SKABaseDevice.Abort` command
is intended to have the same behaviour as :any:`SKABaseDevice.AbortCommands`, 
that is, it should interrupt all the executing and queued long running commands.

The :any:`BaseComponentManager.max_executing_tasks` property now has a default value of
2 as a device should support :any:`Abort` and at least one other command.

There are two reasons a subclass of :any:`BaseComponentManager` might override the
:any:`abort_commands` method:

1. The subclass could need to override how to stop all the executing and queued
   tasks.
2. The subclass could need to override the behaviour of the :any:`AbortCommands`
   command.

In order to separate these two concerns, the :any:`abort_commands` method has been
deprecated in favor of either:

- :any:`BaseComponentManager.abort_tasks` -- providing a hook for a subclass to override how tasks are stopped (use case 1 above); or
- :any:`BaseComponentManager.abort` -- providing a hook for a subclass to override how the :any:`Abort` command behaves (use case 2 above).

The default implementation of :any:`Abort` calls :any:`BaseComponentManager.abort_tasks`
and by default it raises a :any:`NotImplementedError`.
:any:`TaskExecutorComponentManager.abort_tasks` provides an override
that aborts the task executor queue as :any:`abort_commands` did prior to
ska_tango_base 1.2.0.

Preparing for removal
^^^^^^^^^^^^^^^^^^^^^

Deprecation warnings may be issued for code which does either of the following:

- invoke the :any:`AbortCommands` command; or
- override the :any:`abort_commands` method of the component manager

Modules which do **not** do either of the above do **not** need updating to
prepare for the removal of the :any:`AbortCommands` command.

If a client invokes the :any:`AbortCommands` command on a device server using
ska-tango-base 1.2.0, the **server** may emit a deprecation warning, directing
the client to instead invoke the :any:`Abort` command.  Clients should follow
this advice to resolve the warning.  The :any:`SKABaseDevice` is conservative about
emitting this warning, so if there is any possibility that the device server
might have overridden the behaviour of :any:`AbortCommands`, it will not emit a
deprecation warning as the :any:`Abort` command might need to be updated first.

If the :any:`SKABaseDevice` detects that a component manager is overriding the
:any:`abort_commands` method, it will emit a deprecation warning at device
startup, instructing the developer to either override the :any:`Abort` method or
the :any:`abort_tasks<BaseComponentManager.abort_tasks>` method instead. How to resolve this deprecation warning
depends on the device implementation in question and will require judgement from
the developer.  The following general guidance might serve as a useful starting
point:

- If the reason for overriding :any:`abort_commands` was to change the behaviour of
  the :any:`AbortCommands` command then the :any:`Abort` method should probably be
  overridden instead, in order to override the behaviour of the :any:`Abort`
  command.
- If instead the reason for overriding :any:`abort_commands` was to override how
  tasks are stopped then overriding the :any:`abort_tasks<BaseComponentManager.abort_tasks>` method is probably
  more appropriate.

It is, of course, possible that the reason for overriding :any:`abort_commands`
is some combination of the above, in which case both :any:`Abort` and
:any:`abort_tasks<BaseComponentManager.abort_tasks>` may need to be overridden.

If after resolving the deprecation warnings, a component manager now has an
overridden :any:`Abort` method when it previously had an overridden
:any:`abort_commands` method, developers may want to keep the overridden
:any:`abort_commands` method to avoid breaking clients downstream.  In this case it
is recommended to add a deprecation warning advising clients to call the :any:`Abort`
command instead of the :any:`AbortCommands` command.  When the :any:`abort_commands` method
is overridden the :any:`SKABaseDevice` will not emit such a deprecation warning itself.

If instead the component manager is now overriding the :any:`abort_tasks<BaseComponentManager.abort_tasks>` method
when previously it was overriding the :any:`abort_commands` method then the
:any:`abort_commands` method can be safely removed.  The default implementation
of the :any:`abort_commands` method calls :any:`abort_tasks<BaseComponentManager.abort_tasks>` and in this case the
:any:`SKABaseDevice` will emit a deprecation warning to call the :any:`Abort`
command if a client calls the :any:`AbortCommands` command.

When the :any:`AbortCommands` command is removed, :any:`SKABaseDevice` will require
that :any:`BaseComponentManager.max_executing_tasks`
be at least 2.  Component managers which are not overriding the
:any:`max_executing_tasks` property will not have to change, however, if a
component manager is currently overriding :any:`max_executing_tasks` to 1 it will
need to be updated.  ska-tango-base 1.2.0 will emit a :any:`FutureWarning` if
:any:`max_executing_tasks` has been overridden to 1.

Long Running Command attributes
-------------------------------

The following Tango attributes have been deprecated from the 
:class:`~ska_tango_base.base.base_device.SKABaseDevice`:

- :any:`longRunningCommandResult`
- :any:`longRunningCommandStatus`
- :any:`longRunningCommandProgress`
- :any:`longRunningCommandInProgress`
- :any:`longRunningCommandIDsInQueue`
- :any:`longRunningCommandsInQueue`


Rationale
^^^^^^^^^

The above attributes have two separate intended audiences:

1. Users wanting to inspect the state of the LRCs running on the Tango
   Device for introspection purposes.
2. Clients invoking an LRC wanting to be notified of its progress and eventual
   result.

The use of a single set of attributes for two audiences means that they are not
ideal for either audience.  In ska-tango-base 1.2.0, the existing LRC attributes
have been deprecated in favor of a new client API for invoking LRCs, and three
new attributes specifically added for the first use case.

When any of the existing LRC attributes are read or subscribed to, the **server**
will emit a deprecation warning.

Preparing for removal
^^^^^^^^^^^^^^^^^^^^^

If you are using any of the above attributes to provide information to users
about the status of the LRCs in a Tango device, then use the new
:any:`lrcQueue`, :any:`lrcExecuting` or :any:`lrcFinished` attributes.  If there are some
use cases which are not covered by these new attributes please file a bug
report.

If you are subscribing to the above attributes to monitor the status of an LRC,
then use the new :func:`~ska_tango_base.long_running_commands_api.invoke_lrc`
function instead to initiate the command and provide a callback which will be
used to notify you when there are updates (see :doc:`../how-to/invoke-an-lrc`).

When available, :any:`invoke_lrc` will use a new private attribute ``_lrcEvent`` to
monitor the progress of an LRC. Direct use of the attribute is not supported and
the changes to the behaviour of this attribute will not be considered breaking.

.. note::

   The new ``_lrcEvent`` private attribute is considered to be version 2 of the
   client/server LRC protocol.  The version of the protocol is considered to be
   an implementation detail and is hidden from the users of ska-tango-base.

Long Running Command task update checks
---------------------------------------

Progress and result types
^^^^^^^^^^^^^^^^^^^^^^^^^

The :any:`TaskCallbackType` protocol should be used as type annotation for all 
``task_callback`` functions, but this is not strictly enforced. The :any:`CommandTracker`
assumes it will receive the correct types for status, progress and result updates.

Therefore, from ska-tango-base 1.2.0, the :any:`CommandTracker` will emit a 
:any:`FutureWarning` if a command's progress is not an ``int``, or if its result is not
JSON serialisable, and in both cases convert the progress/result to a ``str`` and continue.
It will also raise a :any:`TypeError` if a command's status is not a :any:`TaskStatus` enum.

Task status transitions
^^^^^^^^^^^^^^^^^^^^^^^

The :any:`CommandTracker` does not enforce the :any:`TaskStatus` state machine as 
detailed in :ref:`lrc-concept-tasks`. It is possible for a device to implement a LRC
that sends a status update with its ``task_callback`` that does not follow the state 
machine. Therefore the :any:`CommandTracker` will also emit a :any:`FutureWarning` for
invalid status transitions. The :any:`TaskStatus` state machine may be enforced in a 
future release.

.. note::

   Users must please make a request for new features to support their use case if they 
   are generating any of these warnings.

