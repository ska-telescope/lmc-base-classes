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

In ska-tango-base 1.2.0, the :func:`SKABaseDevice.AbortCommands
<ska_tango_base.base.base_device.SKABaseDevice.AbortCommands>` command has been
deprecated in favor of the :func:`SKABaseDevice.Abort
<ska_tango_base.base.base_device.SKABaseDevice.Abort>` command.  In addition
:func:`BaseComponentManager.abort_commands
<ska_tango_base.base.base_component_manager.BaseComponentManager.abort_commands>`
method has been deprecated in favor of either the
:func:`BaseComponentManager.abort
<ska_tango_base.base.base_component_manager.BaseComponentManager.abort>`
method or the
:func:`BaseComponentManager.abort_tasks
<ska_tango_base.base.base_component_manager.BaseComponentManager.abort_tasks>`
method.

Rationale
^^^^^^^^^

Prior to ska-tango-base 1.2.0, the following default commands are
provided by the base classes.

- :class:`~ska_tango_base.base.base_device.SKABaseDevice` provides an
  :func:`~ska_tango_base.base.base_device.SKABaseDevice.AbortCommands` command
  which calls the
  :func:`~ska_tango_base.base.base_component_manager.BaseComponentManager.abort_commands`
  method of the component manager.  This command is supposed to abort all the
  currently queued and executing long running commands and is **not**
  itself a long running command.

- :class:`~ska_tango_base.subarray.subarray_device.SKASubarray` provides an
  ``Abort()`` command which calls the ``abort()`` method of the component
  manager. This command is supposed to transition the device's
  :class:`~ska_control_model.ObsState` to
  :obj:`~ska_control_model.ObsState.ABORTED` via the
  :obj:`~ska_control_model.ObsState.ABORTING` state.  The device should cease
  all activities when it receives an ``Abort()`` command, including any other
  long running commands.  The command **is** itself a long running command.

Recall that the ``SKASubarray`` class inherits from the ``SKABaseDevice``,
so it also has an ``AbortCommands()`` command.  It is not clear how the
``AbortCommands()`` command should interact with the ``Abort()`` command.  For
example, if we invoke ``AbortCommands()`` while the ``Abort()`` command is in
progress, should the device transition to :obj:`obsState.ABORTED
<ska_control_model.ObsState.ABORTED>`?  If we call the ``AbortCommands()``
command while the ``On()`` command is in progress, what ``ObsState`` should we
end up in?

The difficulty in answering these questions suggests that there is an issue with
the design and the solution chosen is to simplify the API.  To this end, in
ska-tango-base 1.2.0 an
:func:`~ska_tango_base.base.base_device.SKABaseDevice.Abort()` command has been
added to the :class:`~ska_tango_base.base.base_device.SKABaseDevice`. Like the
``Abort()`` command of the
:class:`~ska_tango_base.subarray.subarray_device.SKASubarray`, this is a long
running command and must be started immediately without being queued.

Other than it being a long running command, the ``SKABaseDevice.Abort()`` command
is intended to have the same behaviour as ``SKABaseDevice.AbortCommands()``, that
is it should interrupt all the executing and queued long running commands.

There are two reasons a subclass of
:class:`~ska_tango_base.base.base_component_manager.BaseComponentManager`
might override the
:func:`~ska_tango_base.base.base_component_manager.BaseComponentManager.abort_commands`
method:

1. The subclass could need to override how to stop all the executing and queued
   tasks.
2. The subclass could need to override the behaviour of the ``AbortCommands()``
   command.

In order to separate these two concerns, the ``abort_commands()`` method has been
deprecated in favor of either:

- :func:`~ska_tango_base.base.base_component_manager.BaseComponentManager.abort_tasks()` -- providing a hook for a subclass to override how tasks are stopped (use case 1 above); or
- :func:`~ska_tango_base.base.base_component_manager.BaseComponentManager.abort()` -- providing a hook for a subclass to override how the ``Abort()`` command behaves (use case 2 above).

The default implementation of ``abort()`` calls ``abort_tasks()`` and by default
``abort_tasks()`` raises a ``NotImplementedError``.  The
:class:`~ska_tango_base.executor.executor_component_manager.TaskExecutorComponentManager`
provides an override of
:func:`~ska_tango_base.executor.executor_component_manager.TaskExecutorComponentManager.abort_tasks()`
that aborts the task executor queue as ``abort_commands()`` did prior to
ska_tango_base 1.2.0.

Preparing for removal
^^^^^^^^^^^^^^^^^^^^^

Deprecation warnings may be issued for code which does either of the following:

- invoke the ``AbortCommands()`` command; or
- override the ``abort_commands()`` method of the component manager

Modules which do **not** do either of the above do **not** need updating to
prepare for the removal of the ``AbortCommands()`` command.

If a client invokes the ``AbortCommands()`` command on a device server using
ska-tango-base 1.2.0, the **server** may emit a deprecation warning, directing
the client to instead invoke the ``Abort()`` command.  Clients should follow
this advice to resolve the warning.  The ``SKABaseDevice`` is conservative about
emitting this warning, so if there is any possibility that the device server
might have overridden the behaviour of ``AbortCommands()``, it will not emit a
deprecation warning as the ``Abort()`` command might need to be updated first.

If the ``SKABaseDevice`` detects that a component manager is overriding the
``abort_commands()`` method, it will emit a deprecation warning at device
startup, instructing the developer to either override the ``abort()`` method or
the ``abort_tasks()`` method instead. How to resolve this deprecation warning
depends on the device implementation in question and will require judgement from
the developer.  The following general guidance might serve as a useful starting
point:

- If the reason for overriding ``abort_commands()`` was to change the behaviour of
  the ``AbortCommands()`` command then the ``abort()`` method should probably be
  overridden instead, in order to override the behaviour of the ``Abort()``
  command.
- If instead the reason for overriding ``abort_commands()`` was to override how
  tasks are stopped then overriding the ``abort_tasks()`` method is probably
  more appropriate.

It is, of course, possible that the reason for overriding ``abort_commands()``
is some combination of the above, in which case both ``abort()`` and
``abort_tasks()`` may need to be overridden.

If after resolving the deprecation warnings, a component manager now has an
overridden ``abort()`` method when it previously had an overridden
``abort_commands()`` method, developers may want to keep the overridden
``abort_commands()`` method to avoid breaking clients downstream.  In this case it
is recommended to add a deprecation warning advising clients to call the ``Abort()``
command instead of the ``AbortCommands()`` command.  When the ``abort_commands()`` method
is overridden the ``SKABaseDevice`` will not emit such a deprecation warning itself.

If instead the component manager is now overriding the ``abort_tasks()`` method
when previously it was overriding the ``abort_commands()`` method then the
``abort_commands()`` method can be safely removed.  The default implementation
of the ``abort_commands()`` method calls ``abort_tasks()`` and in this case the
``SKABaseDevice`` will emit a deprecation warning to call the ``Abort()``
command if a client calls the ``AbortCommands()`` command.

Long Running Command attributes
-------------------------------

The following Tango attributes have been deprecated from the SKABaseDevice:

- ``longRunningCommandResult``
- ``longRunningCommandStatus``
- ``longRunningCommandProgress``
- ``longRunningCommandInProgress``
- ``longRunningCommandIdsInQueue``
- ``longRunningCommandsInQueue``


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
``lrcQueue``, ``lrcExecuting`` or ``lrcFinished`` attributes.  If there are some
use cases which are not covered by these new attributes please file a bug
report.

If you are subscribing to the above attributes to monitor the status of an LRC,
then use the new :func:`~ska_tango_base.long_running_commands_api.invoke_lrc()`
function instead to initiate the command and provide a callback which will be
used to notify you when there are updates (see :doc:`../how-to/invoke-an-lrc`).

When available, ``invoke_lrc`` will use a new private attribute ``_lrcEvent`` to
monitor the progress of an LRC. Direct use of the attribute is not supported and
the changes to the behaviour of this attribute will not be considered breaking.

.. note

   The new ``_lrcEvent`` private attribute is considered to be version 2 of the
   client/server LRC protocol.  The version of the protocol is considered to be
   an implementation detail and is hidden from the users of ska-tango-base.
