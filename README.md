# lmc-base-classes



[![Documentation Status](https://readthedocs.org/projects/lmc-base-classes/badge/?version=latest)](https://developerskatelescopeorg.readthedocs.io/projects/lmc-base-classes/en/latest/?badge=latest)



## About

A shared repository for the Local Monitoring and Control (LMC) Base Classes. The goal is to create a Software Development Kit for the Control System of the [Square Kilometre Array](http://skatelescope.org/) (SKA) radio telescope project. The Telescope Manager provides the Central Control System and each _Element_ provides a Local Control System that all work together as the Control System for the instrument. In the SKA case _Elements_ are subsystems such as the Central Signal Processor (CSP), Science Data Processor (SDP), Dishes (DSH), Low-Frequency Apperture Array (LFAA) etc.  Control is implement using the distributed control system, [TANGO](http://www.tango-controls.org), which is accessed from Python using the [PyTango](https://github.com/tango-controls/pytango) package.


Early work in this repo was done as part of the LMC Base Classes Evolutionary Prototype (LEvPro) project, under the INDO-SA collaboration program.

The lmc-base-classe repository contains set of eight classes as mentioned in SKA Control systems guidelines. Following is the list of base classes
- SKABaseDevice: This is generic class that includes common attributes, commands and properties that are required for any SKA tango device.
- SKACapability: This is generic base class for any element to provide common functionality of a capability of an SKA device.
- SKAAlarmHandler: This is the generic class meant to handle the alarms and alerts.
- SKALogger: This is the generic class for logging.
- SKAMaster: This is the generic base class to provide common functionality required for any SKA Element Master device.
- SKAObsDevice: This is the generic base classs meant to provide common functionality of a device which is directly going to be a part of an observation.
- SKASubarray: This is the generic base class which provides common functionality required in a subarray device.
- SKATelState: This is the generic base class to provide common functionality of a TelState device of any SKA Element.

## Version History

#### 0.6.1
- Add ON state to SKABaseDeviceStateModel.
- Move On() and Off() commands to SKABaseDevice.
- Add event pushing for device state, device status, admin mode and obs state
  (change and archive events).
- Disable all attribute polling.

#### 0.6.0
- Breaking change: State management
  - SKABaseDevice implements a simple state machine with states
    `DISABLED`, `OFF`, `ON`, `INIT` and `FAULT`, along with transitions
    between them.
  - SKASubarray implements full subarray state machine in accordance
    with ADR-8 (the underlying state model supports all states and
    transitions, including transitions through transient states; the
    subarray device uses this state model but currently provide a
    simple, purely synchronous implementation)
  - Base classes provide subclassing code hooks that separate management
    of device state from other device functionality. Thus, subclasses
    are encouraged to leave state management in the care of the base
    classes by:
    - leaving `init_device()` alone and placing their (stateless)
      initialisation code in the `do()` method of the `InitCommand` object instead. The base `init_device()` implementation will ensure that
      the `do()` method is called, whilst ensuring state is managed e.g.
      the device is put into state `IDLE` beforehand, and put into the
      right state afterwards.
    - leaving commands like `Configure()` alone and placing their
      (stateless) implementation code in `ConfigureCommand.do()`
      instead. This applies to all commands that affect device state:
       `Off()`, `On()`, `AssignResources()`, `ReleaseResources()`,
       `ReleaseAllResources()`, `Configure()`, `Scan()`, `EndScan()`,
       `End()`, `Abort()`, `Reset()`, `Restart()`.
    - leaving the base device to handle reads from and writes to the
      state attributes `adminMode`, `obsState` and device `state`. For
      example, do not call `Device.set_state()` directly; and do not
      override methods like `write_adminMode()`.

#### 0.5.4
- Remove `ObsState` command from SKACapability, SKAObsDevice and SKASubarray Pogo XMI files.  It should not
  have been included - the `obsState` attribute provides this information. The command was not in the Python
  files, so no change to usage.  It only affects future Pogo code generation.
- Add new logging target, `"tango::logger"`, that forwards Python logs to the Tango Logging Service.  This
  is enabled by default in code, but could be overridden by existing Tango Database device properties.
- Maximum number of logging targets increased from 3 to 4.

#### 0.5.3
- Setting `loggingTargets` attribute to empty list no longer raises exception.
- Change syslog targets in `loggingTargets` attribute to a full URL so that remote syslog servers can be specified.
  For example, `"syslog::udp://server.domain:514"`, would send logs to `server.domain` via UDP port 514.
  Specifying a path without a protocol, like `"syslog::/var/log"`, is deprecated.

#### 0.5.2
- Change ska_logger dependency to use ska-namespaced package (v0.3.0).  No change to usage.

#### 0.5.1
- Make 'ska' a [native namespace package](https://packaging.python.org/guides/packaging-namespace-packages/#native-namespace-packages).
  No change to usage.

#### 0.5.0
- Breaking change:  Major restructuring of the package to simplify imports and reduce confusion.  
  - The single word `skabase` module has now changed to two words: `ska.base`.
  - Instead of `from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice` to import the
    class, just use `from ska.base import SKABaseDevice`.  
  - Instead of `skabase.control_model` use `ska.base.control_model`.
  - The `SKATestDevice` was removed.  Note that this class was only intended
    for internal use in lmc-base-classes and is no longer needed.
  - Removed unused scripts and modules.
- Removed `TangoLoggingLevel` which was deprecated in 0.4.0.  Use `ska.base.control_model.LoggingLevel`
  instead.

#### 0.4.1
- Fix lost properties when re-initialising test device (remove `get_name` mock).
- Fix Sphinx doc building.
- Move `ObsDevice` variable initialisation from `__init__` to `init_device`.
- Run scripts with `python3` instead of `python` and update pip usage.

#### 0.4.0
- Changed all `DevEnum` attributes to use Python `enum.IntEnum` classes.  These can be imported from the
  new `control_model` namespace, e.g., `skabase.control_model import AdminMode`.
- The names of some of the enumeration labels were changed to better match the Control Systems Guidelines.
  - `ON-LINE` changed to `ONLINE`.
  - `OFF-LINE` changed to `OFFLINE`.
  - All dashes were changed to underscores to allow usage as Python variables.
- Changed `simulationMode` attribute from `bool` to enumerated type: `SimulationMode`.
- Changed `testMode` attribute from `str` to enumerated type: `TestMode`.
- Deprecated `TangoLoggingLevel`.  Will be removed in version 0.5.0.  Use `skabase.control_model.LoggingLevel`
  instead.
- Remove unnecessary usage of `DeviceMeta` class.

#### 0.3.1
- Used `ska_logging` library instead of defining logging format and handlers locally.
- `LoggingTargetDefault` property is now empty instead of `"console::cout"`, since the
  the `ska_logging` library will automatically output to stdout.
- Fixed device name field in log message if a device server includes multiple devices.
- Removed a number of unused files in the `ansible` and `refelt` folders.

#### 0.3.0
- Not released

#### 0.2.0
- Changed logging to use SKA format
- Simplified element, storage and central logging to just a single target.  Default writes to stdout.
  This is in line with the move to Elastic for all logs instead of using the Tango Logging Service
  for some cases.
- Deprecated `dev_logging` method.  Will be removed in 0.3.0.  Use direct calls the `self.logger` instead.

#### 0.1.3
- Storage logs are written to a file if Syslog service is not available.
- Added exception handling
- Improved code coverage
- Improved compliance to coding standards
- Improvement in documentation
- Other minor improvements

#### 0.1.2
 - Internal release

#### 0.1.1
- Logging functionality
- Python3 migration
- Repackaging of all the classes into a single Python package
- Changes to folder structure,
- Integration in CI environment

## Installation
### Requirements
The basic requirements are:
- Python 3.5
- Pip

The requirements for installation of the lmc bas classes are:
- enum34
- argparse
- future

The requirements for testing are:
- coverage
- pytest
- pytest-cov
- pytest-xdist
- mock

### Installation steps
1. Clone the repository on local machine.
2. Navigate to the root directory of the repository from terminal
3. Run 'python3 -m pip install . --extra-index-url https://nexus.engageska-portugal.pt/repository/pypi/simple'

## Testing
The LMC base classes can be tested locally my invoking *make CI_JOB_ID=some_id test* command.
This invokes a chain of commands from the makefile which builds the lmc base classes
python package, creates a docker image with lmc base classes, instantiates separate
container for each of the base class and runs unit test cases of each class. Additionally,
code analysis is also done and code coverage report is prepared.
After testing is done, the containers are taken down.

## Usage
The base classes are installed as a Python package in the system. The intended usage of the base classes is to inherit the class according to the requirement. The class needs to be imported in the module. e.g.
```
from ska.base import SKABaseDevice

class DishLeafNode(SKABaseDevice):
.
.
.
```

## Logging explained

In order to provided consistent logging across all Python Tango devices in SKA,
the logging is configured in the LMC base class: `SKABaseDevice`.

### Default logging targets

The `SKABaseDevice` automatically uses the logging configuration provided by the
[ska_logging](https://gitlab.com/ska-telescope/ska-logging) package.  This cannot
be easily disabled, and should not be.  It allows us to get consistent logs from all
devices, and to effect system wide change, if necessary.  Currently,
that library sets up the root logger to always output to stdout (i.e., the console).
This is so that the logs can be consumed by Fluentd and forwarded to Elastic.

The way the `SKABaseDevice` logging formatter and filters are configured, the emitted
logs include a tag field with the Tango device name.  This is useful when searching
for logs in tools like Kibana.  For example, `tango-device=ska_mid/tm_leaf_node/d0004`.
This should work even for multiple devices from a single device server.

In addition, the `SKABaseDevice`'s default `loggingTargets` are configured to send all
logs to the [Tango Logging Service](https://tango-controls.readthedocs.io/en/latest/development/device-api/device-server-writing.html#the-tango-logging-service)
(TLS) as well.  The sections below explain the Tango device attributes and properties
related to this.

### Tango device controls for logging levels and targets

The logging level and additional logging targets are controlled by two attributes.
These attributes are initialised from two device properties on startup.  An extract
of the definitions from the base class is shown below.

As mentioned above, note that the `LoggingTargetsDefault` includes `"tango::logger"` which
means Python logs are forwarded to the Tango Logging Service as well.  This can be overridden
in the Tango database, however disabling the `"tango::logger"` target is strongly discouraged,
as other devices in the telescope or test infrastructure may rely on this.

```python
class SKABaseDevice(Device):

    ...

    # -----------------
    # Device Properties
    # -----------------

    LoggingLevelDefault = device_property(
        dtype='uint16', default_value=LoggingLevel.INFO
    )

    LoggingTargetsDefault = device_property(
        dtype='DevVarStringArray', default_value=["tango::logger"]
    )

    # ----------
    # Attributes
    # ----------

    loggingLevel = attribute(
        dtype=LoggingLevel,
        access=AttrWriteType.READ_WRITE,
        doc="Current logging level for this device - "
            "initialises to LoggingLevelDefault on startup",
    )

    loggingTargets = attribute(
        dtype=('str',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4,
        doc="Logging targets for this device, excluding ska_logging defaults"
            " - initialises to LoggingTargetsDefault on startup",
    )

   ...

```

### Changing the logging level

The `loggingLevel` attribute allows us to adjust the severity of logs being emitted.
This attribute is an enumerated type.  The default is currently INFO level, but it
can be overridden by setting the `LoggingLevelDefault` property in the Tango database.

Example:
```python
proxy = tango.DeviceProxy('my/test/device')

# change to debug level using an enum
proxy.loggingLevel = ska.base.control_model.LoggingLevel.DEBUG

# change to info level using a string
proxy.loggingLevel = "INFO"
```

Do not use `proxy.set_logging_level()`.  That method only applies to the Tango Logging
Service (see section below).  However, note that when the `loggingLevel` attribute
is set, we internally update the TLS logging level as well.

### Additional logging targets

Note that the `loggingTargets` attribute says "excluding ska_logging defaults".
Even when empty, you will still have the logging to stdout that is already provided
by the ska_logging library.  If you want to forward logs to other targets, then you can use
this attribute.  Since we also want logging to TLS, it should include the `"tango::logger"`
item by default.

The format and usage of this attribute is not that intuitive, but it was not expected to
be used much, and was kept similar to the existing SKA control system guidelines proposal.
The string format of each target is chosen to match that used by the
Tango Logging Service: `"<type>::<location>"`.

It is a spectrum string attribute.  In PyTango we read it back as a tuple of strings,
and we can write it with either a list or tuple of strings.

```python
proxy = tango.DeviceProxy('my/test/device')

# read back additional targets (as a tuple)
current_targets = proxy.loggingTargets

# add a new file target
new_targets = list(current_targets) + ["file::/tmp/my.log"]
proxy.loggingTargets = new_targets

# disable all additional targets
proxy.loggingTargets = []
```

Currently there are four types of targets implemented:
- `console`
- `file`
- `syslog`
- `tango`

#### console target
If you were to set the `proxy.loggingTargets = ["console::cout"]` you would get
all the logs to stdout duplicated.  Once for ska_logging root logger, and once for
the additional console logger you just added.  For the "console" option it doesn't matter
what text comes after the `::` - we always use stdout.  While it may not seem useful
now, the option is kept in case the ska_logging default configuration changes, and no
longer outputs to stdout.

#### file target
For file output, provide the path after the `::`.  If the path is omitted, then a
file is created in the device server's current directory, with a name based on the
the Tango name.  E.g., "my/test/device" would get the file "my_test_device.log".
Currently, we using a `logging.handlers.RotatingFileHandler` with a 1 MB limit and
just 2 backups.  This could be modified in future.

#### syslog target
For syslog, the syslog target address details must be provided after the `::` as a URL.
The following types are supported:
- File, `file://<path>`
  - E.g., for `/dev/log` use `file:///dev/log`.
  - If the protocol is omitted, it is assumed to be `file://`.  Note: this is deprecated.
    Support will be removed in v0.6.0.
- Remote UDP server, `udp://<hostname>:<port>`
  -  E.g., for `server.domain` on UDP port 514 use `udp://server.domain:514`.
- Remote TCP server, `tcp://<hostname>:<port>`
  -  E.g., for `server.domain` on TCP port 601 use `tcp://server.domain:601`.

Example of usage:  `proxy.loggingTargets = ["syslog::udp://server.domain:514"]`.

#### tango target
All Python logs can be forwarded to the Tango Logging Service by adding the `"tango::logger"`
target.  This will use the device's log4tango logger object to emit logs into TLS.  The
TLS targets still need to be added in the usual way.  Typically, using the `add_logging_target`
method from an instance of a `tango.DeviceProxy` object.

#### multiple targets
If you want file and syslog targets, you could do something like:
`proxy.loggingTargets = ["file::/tmp/my.log", "syslog::udp://server.domain:514"]`.

**Note:**  There is a limit of 4 additional handlers.  That is the maximum length
of the spectrum attribute. We could change this if there is a reasonable use
case for it.

### Can I still send logs to the Tango Logging Service?

Yes.  In `SKABaseDevice._init_logging` we monkey patch the log4tango logger
methods `debug_stream`, `error_stream`, etc. to point the Python logger methods like
`logger.debug`, `logger.error`, etc.  This means that logs are no longer forwarded
to the Tango Logging Service automatically.  However, by including a `"tango::logger"`
item in the `loggingTarget` attribute, the Python logs are sent to TLS.

The `tango.DeviceProxy` also has some built in logging control methods that only apply
to the Tango Logging Service:
- `DeviceProxy.add_logging_target`
  - Can be used to add a log consumer device.
  - Can be used to log to file (in the TLS format).
  - Should not be used to turn on console logging, as that will result in duplicate logs.
- `DeviceProxy.remove_logging_target`
  - Can be used to remove any TLS logging target.
- `DeviceProxy.set_logging_level`
  - Should not be used as it only applies to TLS.  The Python logger level will be out
    of sync.  Rather use the device attribute `loggingLevel` which sets both.

### Where are the logs from the admin device (dserver)?

PyTango is wrapper around the C++ Tango library, and the admin device is implemented in C++. 
The admin device does not inherit from the SKABaseDevice and we cannot override its behaviour
from the Python layer.  Its logs can only be seen by configuring the TLS appropriately.

### What code should I write to log from my device?

You should always use the `self.logger` object within methods.  This instance of the
logger is the only one that knows the Tango device name.  You can also use the PyTango
[logging decorators](https://pytango.readthedocs.io/en/stable/server_api/logging.html#logging-decorators)
like `DebugIt`, since the monkey patching redirects them to that same logger.

```python
class MyDevice(SKABaseDevice):
    def my_method(self):
        someone = "you"
        self.logger.info("I have a message for %s", someone)

    @tango.DebugIt(show_args=True, show_ret=True)
    def my_handler(self):
        # great, entry and exit of this method is automatically logged
        # at debug level!
        pass

```

Yes, you could use f-strings. `f"I have a message for {someone}"`.  The only benefit
of the `%s` type formatting is that the full string does not need to be created unless
the log message will be emitted.  This could provide a small performance gain, depending
on what is being logged, and how often.


### When I set the logging level via command line it doesn't work

Tango devices can be launched with a `-v` parameter to set the logging level. For example,
'MyDeviceServer instance -v5' for debug level.  Currently, the `SKABaseDevice` does not
consider this command line option, so it will just use the Tango device property instead.
In future, it would be useful to override the property with the command line option.

## Development

### PyCharm

The Docker integration is recommended.  For development, use the
`nexus.engageska-portugal.pt/tango-example/lmcbaseclasses:latest` image
as the Python Interpreter for the project.  Note that if `make` is
run with targets like `build`, `up`, or `test`, that image will be
rebuilt by Docker using the local code, and tagged as `latest`.  

As this project uses a `src` [folder structure](https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure),
so under _Preferences > Project Structure_, the `src` folder needs to be marked as "Sources".  That will
allow the interpreter to be aware of the package from folders like `tests` that are outside of `src`.
When adding Run/Debug configurations, make sure "Add content roots to PYTHONPATH" and
"Add source roots to PYTHONPATH" are checked.

## Docs
- Online:  [Read The Docs](https://developerskatelescopeorg.readthedocs.io/projects/lmc-base-classes/en/latest)
- SKA Control System guidelines:  [Google docs folder](https://drive.google.com/drive/folders/0B8fhAW5QnZQWQ2ZlcjhVS0NmRms)
- Old LEvPro work area: [Google docs folder](https://drive.google.com/drive/folders/0B8fhAW5QnZQWVHVFVGVXT2Via28)



## Contribute
Contributions are always welcome! Please refer to the [SKA Developer Portal](https://developer.skatelescope.org/en/latest/).
