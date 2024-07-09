=====================
How to use the logger
=====================

You should always use the ``self.logger`` object of ``SKABaseDevice`` within methods. 
This instance of the logger is the only one that knows the Tango device name. 
You can also use the PyTango
`logging decorators <https://pytango.readthedocs.io/en/stable/server_api/logging.html#logging-decorators>`__
like ``DebugIt``, since the monkey patching in ``SKABaseDevice`` redirects them to that same logger.

.. code:: python

   class MyDevice(SKABaseDevice):
       def my_method(self):
           someone = "you"
           self.logger.info("I have a message for %s", someone)

       @tango.DebugIt(show_args=True, show_ret=True)
       def my_handler(self):
           # great, entry and exit of this method is automatically logged
           # at debug level!
           pass

Yes, you could use f-strings. ``f"I have a message for {someone}"``. The only benefit of
the ``%s`` type formatting is that the full string does not need to be created unless
the log message will be emitted. This could provide a small performance gain, depending
on what is being logged, and how often.

Changing the logging level
--------------------------
The ``loggingLevel`` attribute of ``SKABaseDevice`` allows adjusting the severity of 
logs being emitted. This attribute is an enumerated type. The default is currently INFO 
level, but it can be overridden by setting the ``LoggingLevelDefault`` property in the 
Tango database.

Example:

.. code:: python

   proxy = tango.DeviceProxy('my/test/device')

   # change to debug level using an enum
   proxy.loggingLevel = ska_control_model.LoggingLevel.DEBUG

   # change to info level using a string
   proxy.loggingLevel = "INFO"

Do not use ``proxy.set_logging_level()``. That method only applies to the Tango Logging
Service (TLS) - see :ref:`additional-logging-targets`. However, note that when the 
``loggingLevel`` attribute is set, we internally update the TLS logging level as well.