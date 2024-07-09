========================
How to configure logging
========================

In order to provide consistent logging across all Python Tango devices in SKA, the
logging is configured in the LMC base class: ``SKABaseDevice``.

Default logging targets
-----------------------
The ``SKABaseDevice`` automatically uses the logging configuration provided by the
`ska_ser_logging <https://gitlab.com/ska-telescope/ska-ser-logging>`__ package. This cannot be
easily disabled, and should not be. It allows us to get consistent logs from all
devices, and to effect system wide change, if necessary. Currently, that library sets up
the root logger to always output to stdout (i.e., the console). This is so that the logs
can be consumed by Fluentd and forwarded to Elastic.

The way the ``SKABaseDevice`` logging formatter and filters are configured, the emitted
logs include a tag field with the Tango device name. This is useful when searching for
logs in tools like Kibana. For example, ``tango-device=ska_mid/tm_leaf_node/d0004``.
This should work even for multiple devices from a single device server.

In addition, the ``SKABaseDevice``'s default ``loggingTargets`` are configured to send
all logs to the `Tango Logging
Service <https://tango-controls.readthedocs.io/en/latest/development/device-api/device-server-writing.html#the-tango-logging-service>`__
(TLS) as well. The sections below explain the Tango device attributes and properties
related to this.

Tango device controls for logging levels and targets
----------------------------------------------------
The logging level and additional logging targets are controlled by two attributes. These
attributes are initialised from two device properties on startup. An extract of the
definitions from the base class is shown below.

As mentioned above, note that the ``LoggingTargetsDefault`` includes ``"tango::logger"``
which means Python logs are forwarded to the Tango Logging Service as well. This can be
overridden in the Tango database, however disabling the ``"tango::logger"`` target is
strongly discouraged, as other devices in the telescope or test infrastructure may rely
on this.

.. code:: python

   class SKABaseDevice(Device):
      ...
      # -----------------
      # Device Properties
      # -----------------
      LoggingLevelDefault = device_property(
          dtype="uint16", default_value=LoggingLevel.INFO
      )

      LoggingTargetsDefault = device_property(
          dtype="DevVarStringArray", default_value=["tango::logger"]
      )
      ...
      # ----------
      # Attributes
      # ----------
      @attribute(dtype=LoggingLevel)
      def loggingLevel(self: SKABaseDevice[ComponentManagerT]) -> LoggingLevel:
         """
         Read the logging level of the device.

         Initialises to LoggingLevelDefault on startup.
         See :py:class:`~ska_control_model.LoggingLevel`

         :return:  Logging level of the device.
         """
         return self._logging_level

      @loggingLevel.write
      def loggingLevel(
         self: SKABaseDevice[ComponentManagerT], value: LoggingLevel
      ) -> None:
         """
         Set the logging level for the device.

         Both the Python logger and the Tango logger are updated.

         :param value: Logging level for logger
         """
         self.set_logging_level(value)

      @attribute(dtype=("str",), max_dim_x=4)
      def loggingTargets(self: SKABaseDevice[ComponentManagerT]) -> list[str]:
         """
         Read the additional logging targets of the device.

         Note that this excludes the handlers provided by the ska_ser_logging
         library defaults - initialises to LoggingTargetsDefault on startup.

         :return:  Logging level of the device.
         """
         return [str(handler.name) for handler in self.logger.handlers]

      @loggingTargets.write
      def loggingTargets(
         self: SKABaseDevice[ComponentManagerT], value: list[str]
      ) -> None:
         """
         Set the additional logging targets for the device.

         Note that this excludes the handlers provided by the ska_ser_logging
         library defaults.

         :param value: Logging targets for logger
         """
         self.set_logging_targets(value)
      ...

Changing the logging level
--------------------------
The ``loggingLevel`` attribute allows us to adjust the severity of logs being emitted.
This attribute is an enumerated type. The default is currently INFO level, but it can be
overridden by setting the ``LoggingLevelDefault`` property in the Tango database.

Example:

.. code:: python

   proxy = tango.DeviceProxy('my/test/device')

   # change to debug level using an enum
   proxy.loggingLevel = ska.base.control_model.LoggingLevel.DEBUG

   # change to info level using a string
   proxy.loggingLevel = "INFO"

Do not use ``proxy.set_logging_level()``. That method only applies to the Tango Logging
Service (see section below). However, note that when the ``loggingLevel`` attribute is
set, we internally update the TLS logging level as well.

Additional logging targets
--------------------------
Note that the ``loggingTargets`` attribute says “excluding ska_ser_logging defaults”. Even
when empty, you will still have the logging to stdout that is already provided by the
ska_ser_logging library. If you want to forward logs to other targets, then you can use this
attribute. Since we also want logging to TLS, it should include the ``"tango::logger"``
item by default.

The format and usage of this attribute is not that intuitive, but it was not expected to
be used much, and was kept similar to the existing SKA control system guidelines
proposal. The string format of each target is chosen to match that used by the Tango
Logging Service: ``"<type>::<location>"``.

It is a spectrum string attribute. In PyTango we read it back as a tuple of strings, and
we can write it with either a list or tuple of strings.

.. code:: python

   proxy = tango.DeviceProxy('my/test/device')

   # read back additional targets (as a tuple)
   current_targets = proxy.loggingTargets

   # add a new file target
   new_targets = list(current_targets) + ["file::/tmp/my.log"]
   proxy.loggingTargets = new_targets

   # disable all additional targets
   proxy.loggingTargets = []

Currently there are four types of targets implemented:

-  ``console``
-  ``file``
-  ``syslog``
-  ``tango``

console target
^^^^^^^^^^^^^^
If you were to set the ``proxy.loggingTargets = ["console::cout"]`` you would get all
the logs to stdout duplicated. Once for ska_ser_logging root logger, and once for the
additional console logger you just added. For the “console” option it doesn't matter
what text comes after the ``::`` - we always use stdout. While it may not seem useful
now, the option is kept in case the ska_ser_logging default configuration changes, and no
longer outputs to stdout.

file target
^^^^^^^^^^^
For file output, provide the path after the ``::``. If the path is omitted, then a file
is created in the device server's current directory, with a name based on the the Tango
name. E.g., “my/test/device” would get the file “my_test_device.log”. Currently, we
using a ``logging.handlers.RotatingFileHandler`` with a 1 MB limit and just 2 backups.
This could be modified in future.

syslog target
^^^^^^^^^^^^^
For syslog, the syslog target address details must be provided after the ``::`` as a
URL. The following types are supported:

-  File, ``file://<path>``

   -  E.g., for ``/dev/log`` use ``file:///dev/log``.
   -  If the protocol is omitted, it is assumed to be ``file://``. Note: this is
      deprecated. Support will be removed in v0.6.0.

-  Remote UDP server, ``udp://<hostname>:<port>``

   -  E.g., for ``server.domain`` on UDP port 514 use ``udp://server.domain:514``.

-  Remote TCP server, ``tcp://<hostname>:<port>``

   -  E.g., for ``server.domain`` on TCP port 601 use ``tcp://server.domain:601``.

Example of usage: ``proxy.loggingTargets = ["syslog::udp://server.domain:514"]``.

tango target
^^^^^^^^^^^^
All Python logs can be forwarded to the Tango Logging Service by adding the
``"tango::logger"`` target. This will use the device's log4tango logger object to emit
logs into TLS. The TLS targets still need to be added in the usual way. Typically, using
the ``add_logging_target`` method from an instance of a ``tango.DeviceProxy`` object.

multiple targets
^^^^^^^^^^^^^^^^
If you want file and syslog targets, you could do something like:
``proxy.loggingTargets = ["file::/tmp/my.log", "syslog::udp://server.domain:514"]``.

**Note:** There is a limit of 4 additional handlers. That is the maximum length of the
spectrum attribute. We could change this if there is a reasonable use case for it.

Can I still send logs to the Tango Logging Service?
---------------------------------------------------
Yes. In ``SKABaseDevice._init_logging`` we monkey patch the log4tango logger methods
``debug_stream``, ``error_stream``, etc. to point the Python logger methods like
``logger.debug``, ``logger.error``, etc. This means that logs are no longer forwarded to
the Tango Logging Service automatically. However, by including a ``"tango::logger"``
item in the ``loggingTarget`` attribute, the Python logs are sent to TLS.

The ``tango.DeviceProxy`` also has some built in logging control methods that only apply
to the Tango Logging Service:

-  ``DeviceProxy.add_logging_target``

   -  Can be used to add a log consumer device.
   -  Can be used to log to file (in the TLS format).
   -  Should not be used to turn on console logging, as that will result in duplicate
      logs.

-  ``DeviceProxy.remove_logging_target``

   -  Can be used to remove any TLS logging target.

-  ``DeviceProxy.set_logging_level``

   -  Should not be used as it only applies to TLS. The Python logger level will be out
      of sync. Rather use the device attribute ``loggingLevel`` which sets both.

Where are the logs from the admin device (dserver)?
---------------------------------------------------
PyTango is a wrapper around the C++ Tango library, and the admin device is implemented in
C++. The admin device does not inherit from the ``SKABaseDevice`` and we cannot override its
behaviour from the Python layer. Its logs can only be seen by configuring the TLS
appropriately.

What code should I write to log from my device?
-----------------------------------------------
You should always use the ``self.logger`` object within methods. This instance of the
logger is the only one that knows the Tango device name. You can also use the PyTango
`logging
decorators <https://pytango.readthedocs.io/en/stable/server_api/logging.html#logging-decorators>`__
like ``DebugIt``, since the monkey patching redirects them to that same logger.

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

When I set the logging level via command line it doesn't work
-------------------------------------------------------------
Tango devices can be launched with a ``-v`` parameter to set the logging level. For
example, ``MyDeviceServer instance -v5`` for debug level. Currently, the ``SKABaseDevice``
does not consider this command line option, so it will just use the Tango device
property instead. In future, it would be useful to override the property with the
command line option.
