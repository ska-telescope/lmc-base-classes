========================================================
Guidelines on reporting failure of long running commands
========================================================

.. warning::

   These guidelines are still under consideration by the wider SKA community and
   may be changed in the future.

In general, long running commands are fallible. ska-tango-base provides several
different mechanisms for reporting such failures, this corresponds to the
several ways that an LRC can fail. This subsection provides guidelines of when
to use which mechanism. It is important to remember that these are just
guidelines and not hard and fast rules. The important thing is that the error
reporting mechanism is *natural* for the command in question. The goal of the
discussion below is to try and articulate what makes an error reporting
mechanism *natural* in the context of an LRC.

A taxonomy of failures
----------------------

Before we discuss the specifics of how an LRC can fail, it is useful to
introduce some terminology. For our purposes, we define a normal failure as a
failure where a command did not manage to achieve its goal due to some condition
which falls inside the specification of the command - i.e. it has failed because
of some situation that the command is supposed to handle gracefully. For
example, the following are all failures which a command should be specified to
handle gracefully:

- The arguments that a user has passed to a command are invalid.
- A file that is required is missing.
- A subordinate device is not reachable on the network.
- A sub-command invoked on a subordinate device failed (either abnormally or normally).

In contrast to a normal failure, we define an abnormal failure as a failure
where the command failed to achieve its goal because of some unanticipated
situation. When an abnormal failure occurs there is, by definition, a bug in the
software. For example, the following are all failures which are reasonable for
the software developer to assume cannot happen, but could still happen because
their assumption was incorrect:

- Some (hopefully documented) precondition for the command is violated.
- A python variable that does not exist is accessed and the resulting exception is unhandled.
- An array is accessed out of bounds and the resulting exception is unhandled.

Why do we draw the distinction between these two kinds of failures? Because the
entity which must be informed about the failure differs for each type of
failure, and depending on who the "target audience" is,
influences how we report the failure.

The client code must be informed about normal failures. It must anticipate that a 
failure is possible and react accordingly. The reaction might just be "pass
the error up to the code that called me" or "report the error to a user", but it
is the client code which has the context needed to decide what to do.

In contrast, an abnormal failure cannot be recovered from by code. In the
presence of a bug, the best the code can do is throw away what it is doing and
hope that the process is in a coherent state after doing this. Initially, an
abnormal failure needs to be reported to an operator so that that they can
address the fact that the Tango device is misbehaving. However, as the presence
of an abnormal failure means there is a bug, it must ultimately be reported to a 
developer so that they can fix the bug! In this situation we should prefer 
"failing fast" and reporting the failure ideally with a stack trace so that the 
developer who needs to fix this has some clues as to what is going wrong.

A rule of thumb for LRC failure
-------------------------------

As a general rule of thumb for an LRC, for normal failures, using a
:class:`~ska_control_model.ResultCode` is preferred. Whereas, for abnormal
failures, using a python ``Exception`` is preferred. There are four reasons for this:

1. Use of a ``ResultCode`` makes it clear via the API that the command is fallible.
   The API of a python function does not make it clear when/if it can throw an
   ``Exception``, so it is easy to miss in the client code that invokes the command.
2. An ``Exception`` holds a "traceback" which is useful for a developer debugging an
   issue, making it ideal for reporting bugs (i.e. abnormal failures) in code.
3. When python encounters a bug in the code by default it raises ``Exception``, e.g.
   it will raise an ``AttributeError`` when accessing a non-existent attribute on an
   object. It is a good idea not to fight the language on this.
4. An ``Exception`` "unwinds" the stack, making it the ideal mechanism for failing
   fast. We can catch and report the failure at a well defined recovery point.

Reporting a failure from the initial Tango command
--------------------------------------------------

An LRC is initiated by a client invoking a Tango command of the same name. The
Tango command can fail to either start or enqueue the task corresponding to the
LRC. In our taxonomy this would be a normal failure. A Tango command must return a 
:obj:`ResultCode.REJECTED <ska_control_model.ResultCode.REJECTED>` in this case, 
which is following our rule of thumb above.

In the presence of a bug in a Tango command, python will raise an ``Exception``
and Tango will forward this on to the client and raise an exception there. This
follows the guidelines above without intervention from the developer.

If the command accepts a JSON encoded string as a parameter, but the argument it
receives is not a valid JSON string or does not match the required schema, we can
say that the client has violated a precondition of the command - meaning there is
a bug in the client. The default :class:`~ska_tango_base.commands.JsonValidator`
provided by ska_tango_base will raise an ``Exception`` in this case, following
our rule of thumb.

It is useful to contrast the invalid JSON failure, with an invalid value for the
argument. A client program is often not in a position to determine if the value for an 
argument is valid, because this value could come from a user and the client program
might not have the context to know if the user has made a mistake or not. As such,
in general, it cannot be a bug for the client program to invoke a
command with an invalid value for the argument. In this case, the initial Tango
command should accept the LRC command and the task should report the normal
failure with a :class:`~ska_control_model.ResultCode` as described in the next
subsection.

Reporting a failure from the task
---------------------------------

Once the initial Tango command has returned, there is no mechanism for the LRC
to send a python ``Exception`` to the client. All that can be sent to the client is
the result associated with the task via the ``longRunningCommandResult``
attribute. In this case, it is recommended to use the task's associated status
to distinguish between normal and abnormal failures. When following this
recommendation, in the presence of any failure (abnormal or otherwise) the
:class:`~ska_control_model.ResultCode` associated with the task should be
:obj:`ResultCode.FAILED <ska_control_model.ResultCode.FAILED>`. If the failure
is normal, the status of the task itself should be :obj:`TaskStatus.COMPLETED
<ska_control_model.TaskStatus.COMPLETED>`, otherwise it should be
:obj:`TaskStatus.FAILED <ska_control_model.TaskStatus.FAILED>`.

In the case of an abnormal failure, if there is an associated ``Exception``, it
should be logged before the task is completed. The ``task_callback`` provides an
exception convenience argument which logs the ``Exception``, :code:`ex`, that
is passed in and sets the task's associated result to the tuple
:code:`(ResultCode.FAILED, str(ex))`. If you want a different result, 
there is no requirement to use the ``task_callback`` with the exception
argument. However, it is still recommended to always log the exception for
abnormal failures, even if supplying a different result.

