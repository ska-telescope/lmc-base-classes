====================================
How to invoke a long running command
====================================

The recommended way to invoke a long running command on a device is to use the
:func:`~ska_tango_base.long_running_commands_api.invoke_lrc` function.  The
function will initiate the LRC on the device and call the
:class:`~ska_tango_base.long_running_commands_api.LrcCallback` provided whenever
there are updates for the LRC.

.. code-block:: py

    def invoke_lrc_example(self: SKABaseDevice, device: tango.DeviceProxy) -> ResultCode:
        """ An example function invoking the On LRC on device.

        :return: ResultCode.OK if the command succeed, ResultCode.FAILED
          otherwise.
        """

        done = threading.Event()
        results = []

        # We must accept unknown kwargs here as future versions of invoke_lrc
        # may pass additional arguments
        def lrc_callback(result: list[Any] | None = None,
                     **kwargs):
            if result is not None:
                for r in result:
                    results.append(r)

        try:
            # We have to keep this lrc_subscriptions alive for as long as we are
            # interested in this LRC
            lrc_subscriptions = invoke_lrc(self.logger, lrc_callback, device, "On")
        except CommandError:
            # handle rejection
            return ResultCode.FAILED
        except DevFailed:
            # handle error
            return ResultCode.FAILED

        if not done.wait(timeout=10):
            # handle timeout
            return ResultCode.FAILED

        # result has been populated here as done is set
        if ResultCode(result[0]) != ResultCode.OK:
            # handle failure
            return ResultCode.FAILED

        return ResultCode.OK

Behind the scenes :func:`~ska_tango_base.long_running_commands_api.invoke_lrc`
is subscribing to ``CHANGE_EVENT``\ s from the LRC attributes and prior to
ska-tango-base version 1.1 the only way to monitor a long running command was to
subscribe to these attributes directly.  You may see code doing this if it
pre-dates ska-tango-base version 1.1. In future versions of ska-tango-base
beyond 1.1 directly subscribing to these attributes will be deprecated and the
only supported method to monitor the LRC will be via the
:func:`~ska_tango_base.long_running_commands_api.invoke_lrc` function.
