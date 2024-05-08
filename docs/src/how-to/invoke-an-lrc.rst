====================================
How to invoke a long running command
====================================

To initiate the LRC you need to call the corresponding Tango command which
returns a result code indicating whether the command was accepted, and a
unique command id (if the command was not rejected). This command id should be
stored and used to keep track of the LRC's progress and eventual result. To be
notified when the LRC finishes you must subscribe to ``CHANGE_EVENT``'s from
the ``longRunningCommandResult`` attribute, and use this command id to determine
if the event corresponds to your command.

If the LRC implements progress reporting, you can also optionally subscribe to
the ``longRunningCommandProgress`` attribute to receive progress updates,
filtering by command id in the same way.
For example, to invoke the ``On`` LRC using a :class:`tango.DeviceProxy`
and wait for the result, you would do the following:

.. code-block:: py

    def invoke_lrc_example(device: tango.DeviceProxy) -> ResultCode:
        """ An example function invoking the On LRC on device.

        :return: ResultCode.OK if the command succeed, ResultCode.FAILED
          otherwise.
        """

        # Initiate the LRC
        try:
            ret, command_id = device.On()
        except DevFailed as ex:
            # handle error
            return ResultCode.FAILED

        if ret == ResultCode.REJECTED:
            # handle rejection
            return ResultCode.FAILED

        # Subscribe to the "longRunningCommandResult" attribute to get notified
        # when the LRC has completed

        done = threading.Event()
        result = []
        def callback(event):
            if not event.err:
                id = event.attr_value.value[0]
                # Compare the command id in the callback with the unique id
                # returned to us when we invoked the LRC
                if id == command_id:
                    for r in json.loads(event.attr_value.value[1]):
                        result.append(r)
                    done.set()

        device.subscribe_event(
            "longRunningCommandResult",
            tango.EventType.CHANGE_EVENT,
            callback)

        if not done.wait(timeout=10):
            # handle timeout
            return ResultCode.FAILED

        # result has been populated here as done is set
        if ResultCode(result[0]) != ResultCode.OK:
            # handle failure
            return ResultCode.FAILED

        return ResultCode.OK

.. warning::

    The above example has a subtle race condition, the LRC could complete (and
    update) ``longRunningCommandResult`` *before* the Tango command which initiated
    the LRC has completed.  If another LRC also finishes and overwrites the
    ``longRunningCommandResult`` attribute we may never see the result for our
    command.
    
    The issue is that we do not know the command ID until the Tango command has
    returned.
    
    The solution is to subscribe to the ``CHANGE_EVENT`` *before* we
    invoke the initiating Tango command, and queue up any events we receive before
    we know the command ID.  Once we have received the command ID, we can look
    through the queue to check if any of the events are for our command.
    
    In practice, this race condition is unlikely to manifest as it requires
    multiple long running commands to complete very quickly, so for now we
    recommend to not worry about this issue.
    
    A future release of ska-tango-base will include a function for invoking LRCs
    which does not suffer from this race condition.
