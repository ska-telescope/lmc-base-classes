# SKA Tango Base Classes and Utilities

[![Documentation Status](https://readthedocs.org/projects/ska-telescope-ska-tango-base/badge/?version=latest)](https://developer.skao.int/projects/ska-tango-base/en/latest/?badge=latest)

## About

A shared repository for the Local Monitoring and Control (LMC) Tango Base Classes. The goal is to create a Software Development Kit for the Control System of the [Square Kilometre Array](http://skatelescope.org/) (SKA) radio telescope project. The Telescope Manager provides the Central Control System and each _Element_ provides a Local Control System that all work together as the Control System for the instrument. In the SKA case _Elements_ are subsystems such as the Central Signal Processor (CSP), Science Data Processor (SDP), Dishes (DSH), Low-Frequency Apperture Array (LFAA) etc.  Control is implement using the distributed control system, [Tango](http://www.tango-controls.org), which is accessed from Python using the [PyTango](https://gitlab.com/tango-controls/pytango) package.

Early work in this repo was done as part of the LMC Base Classes Evolutionary Prototype (LEvPro) project, under the INDO-SA collaboration program.

The ska-tango-base repository includes a set of eight classes as mentioned in SKA Control systems guidelines. Following is the list of base classes
- SKABaseDevice: This is generic class that includes common attributes, commands and properties that are required for any SKA tango device.
- SKACapability: This is generic base class for any element to provide common functionality of a capability of an SKA device.
- SKAAlarmHandler: This is the generic class meant to handle the alarms and alerts.
- SKALogger: This is the generic class for logging.
- SKAController: This is the generic base class to provide common functionality required for any SKA Element Controller device.
- SKAObsDevice: This is the generic base classs meant to provide common functionality of a device which is directly going to be a part of an observation.
- SKASubarray: This is the generic base class which provides common functionality required in a subarray device.
- SKATelState: This is the generic base class to provide common functionality of a TelState device of any SKA Element.


## Instructions
For detailed instructions on installation and usage, see the [Developers Guide](https://developer.skao.int/projects/ska-tango-base/en/latest/guide/index.html).

### Installation
#### Requirements
The basic requirements are:
- Python 3.5
- Pip

The requirements for installation of the lmc base classes are:
- argparse

The requirements for testing are:
- coverage
- pytest
- pytest-cov
- pytest-xdist
- mock

#### Installation steps
1. Clone the repository on local machine.
2. Navigate to the root directory of the repository from terminal
3. Run 'python3 -m pip install . --extra-index-url https://artefact.skao.int/repository/pypi-internal/simple'

### Testing
The project can be tested locally my invoking *make CI_JOB_ID=some_id test* command. This invokes a chain of commands from the makefile which builds the project's python package, creates a docker image with the project, instantiates separate container for each of the base class and runs unit test cases of each class. Additionally, code analysis is also done and code coverage report is prepared. After testing is done, the containers are taken down.

### Usage
The base classes are installed as a Python package in the system. The intended usage of the base classes is to inherit the class according to the requirement. The class needs to be imported in the module. e.g.
```
from ska.base import SKABaseDevice

class DishLeafNode(SKABaseDevice):
.
.
.
```

### Development

#### PyCharm

The Docker integration is recommended.  For development, use the `artefact.skao.int/ska-tango-base:latest` image as the Python Interpreter for the project.  Note that if `make` is run with targets like `build`, `up`, or `test`, that image will be rebuilt by Docker using the local code, and tagged as `latest`.

As this project uses a `src` [folder structure](https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure), so under _Preferences > Project Structure_, the `src` folder needs to be marked as "Sources".  That will allow the interpreter to be aware of the package from folders like `tests` that are outside of `src`. When adding Run/Debug configurations, make sure "Add content roots to PYTHONPATH" and "Add source roots to PYTHONPATH" are checked.

### Docs
- Online:  [Read The Docs](https://developer.skao.int/projects/ska-tango-base/en/latest/)

### Contribute
Contributions are always welcome! Please refer to the [SKA telescope developer portal](https://developer.skao.int/).

## Logging explained

In order to provided consistent logging across all Python Tango devices in SKA, the logging is configured in the LMC base class: `SKABaseDevice`.

### Default logging targets

The `SKABaseDevice` automatically uses the logging configuration provided by the [ska_logging](https://gitlab.com/ska-telescope/ska-logging) package.  This cannot be easily disabled, and should not be.  It allows us to get consistent logs from all devices, and to effect system wide change, if necessary.  Currently, that library sets up the root logger to always output to stdout (i.e., the console). This is so that the logs can be consumed by Fluentd and forwarded to Elastic.

The way the `SKABaseDevice` logging formatter and filters are configured, the emitted logs include a tag field with the Tango device name.  This is useful when searching for logs in tools like Kibana.  For example, `tango-device=ska_mid/tm_leaf_node/d0004`. This should work even for multiple devices from a single device server.

In addition, the `SKABaseDevice`'s default `loggingTargets` are configured to send all logs to the [Tango Logging Service](https://tango-controls.readthedocs.io/en/latest/development/device-api/device-server-writing.html#the-tango-logging-service) (TLS) as well.  The sections below explain the Tango device attributes and properties related to this.

### Tango device controls for logging levels and targets

The logging level and additional logging targets are controlled by two attributes. These attributes are initialised from two device properties on startup.  An extract of the definitions from the base class is shown below.

As mentioned above, note that the `LoggingTargetsDefault` includes `"tango::logger"` which means Python logs are forwarded to the Tango Logging Service as well.  This can be overridden in the Tango database, however disabling the `"tango::logger"` target is strongly discouraged, as other devices in the telescope or test infrastructure may rely on this.

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

The `loggingLevel` attribute allows us to adjust the severity of logs being emitted. This attribute is an enumerated type.  The default is currently INFO level, but it can be overridden by setting the `LoggingLevelDefault` property in the Tango database.

Example:
```python
proxy = tango.DeviceProxy('my/test/device')

# change to debug level using an enum
proxy.loggingLevel = ska.base.control_model.LoggingLevel.DEBUG

# change to info level using a string
proxy.loggingLevel = "INFO"
```

Do not use `proxy.set_logging_level()`.  That method only applies to the Tango Logging Service (see section below).  However, note that when the `loggingLevel` attribute is set, we internally update the TLS logging level as well.

### Additional logging targets

Note that the `loggingTargets` attribute says "excluding ska_logging defaults". Even when empty, you will still have the logging to stdout that is already provided by the ska_logging library.  If you want to forward logs to other targets, then you can use this attribute.  Since we also want logging to TLS, it should include the `"tango::logger"` item by default.

The format and usage of this attribute is not that intuitive, but it was not expected to be used much, and was kept similar to the existing SKA control system guidelines proposal. The string format of each target is chosen to match that used by the Tango Logging Service: `"<type>::<location>"`.

It is a spectrum string attribute.  In PyTango we read it back as a tuple of strings, and we can write it with either a list or tuple of strings.

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
If you were to set the `proxy.loggingTargets = ["console::cout"]` you would get all the logs to stdout duplicated.  Once for ska_logging root logger, and once for the additional console logger you just added.  For the "console" option it doesn't matter what text comes after the `::` - we always use stdout.  While it may not seem useful now, the option is kept in case the ska_logging default configuration changes, and no longer outputs to stdout.

#### file target
For file output, provide the path after the `::`.  If the path is omitted, then a file is created in the device server's current directory, with a name based on the the Tango name.  E.g., "my/test/device" would get the file "my_test_device.log". Currently, we using a `logging.handlers.RotatingFileHandler` with a 1 MB limit and just 2 backups.  This could be modified in future.

#### syslog target
For syslog, the syslog target address details must be provided after the `::` as a URL. The following types are supported:
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
All Python logs can be forwarded to the Tango Logging Service by adding the `"tango::logger"` target.  This will use the device's log4tango logger object to emit logs into TLS.  The TLS targets still need to be added in the usual way.  Typically, using the `add_logging_target` method from an instance of a `tango.DeviceProxy` object.

#### multiple targets
If you want file and syslog targets, you could do something like: `proxy.loggingTargets = ["file::/tmp/my.log", "syslog::udp://server.domain:514"]`.

**Note:**  There is a limit of 4 additional handlers.  That is the maximum length of the spectrum attribute. We could change this if there is a reasonable use case for it.

### Can I still send logs to the Tango Logging Service?

Yes.  In `SKABaseDevice._init_logging` we monkey patch the log4tango logger methods `debug_stream`, `error_stream`, etc. to point the Python logger methods like `logger.debug`, `logger.error`, etc.  This means that logs are no longer forwarded to the Tango Logging Service automatically.  However, by including a `"tango::logger"` item in the `loggingTarget` attribute, the Python logs are sent to TLS.

The `tango.DeviceProxy` also has some built in logging control methods that only apply to the Tango Logging Service:
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

PyTango is wrapper around the C++ Tango library, and the admin device is implemented in C++. The admin device does not inherit from the SKABaseDevice and we cannot override its behaviour from the Python layer.  Its logs can only be seen by configuring the TLS appropriately.

### What code should I write to log from my device?

You should always use the `self.logger` object within methods.  This instance of the logger is the only one that knows the Tango device name.  You can also use the PyTango [logging decorators](https://pytango.readthedocs.io/en/stable/server_api/logging.html#logging-decorators) like `DebugIt`, since the monkey patching redirects them to that same logger.

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

Yes, you could use f-strings. `f"I have a message for {someone}"`.  The only benefit of the `%s` type formatting is that the full string does not need to be created unless the log message will be emitted.  This could provide a small performance gain, depending on what is being logged, and how often.


### When I set the logging level via command line it doesn't work

Tango devices can be launched with a `-v` parameter to set the logging level. For example, 'MyDeviceServer instance -v5' for debug level.  Currently, the `SKABaseDevice` does not consider this command line option, so it will just use the Tango device property instead. In future, it would be useful to override the property with the command line option.

## Version History

### 0.13.7
- Unpin PyTango version

### 0.13.6
- Updated numpy version

### 0.13.5
- Merge branch 'rel-275-v0-13-5' into 'main'
- [REL-275] Prepare to release 0.13.5
- [REL-275] Fix pipeline

#### 0.13.4
- KAR-466 - Repository maintenance
- MCCS-1072 - Type hint & static type check base class alarm_handler_device & utils
- MCCS-934 - Type hint & Static type check base classes
- LOW-330 Import control model definitions from ska-control-model
- LOW-317 Allow Reset() from STANDBY and ON states, not just FAULT

#### 0.13.3
- KAR-403 Fixed exceptions in LRCs not updating  longRunningCommandResult accordingly
- LOW-299 Fixed docs build in the CI pipeline
- LOW-278 Now using ska-tango-testing
- SAH-1156 Enable assigned_resources property inside SubarrayComponentManager.

#### 0.13.2
- CT-738 fix check long running status
- AT3-140 fix base TANGO xmi files
- MCCS-1053 Fix the problem of device in UNKNOWN state upon test startup
- PERENTIE-1350 Remove misleading `CspSubarrayComponentManager.__init__` function

#### 0.13.1
- KAR-399 Renamed SKAController command isCapabilityAchievable to IsCapabilityAchievable.

#### 0.13.0
- MCCS-876 Updated implementation of long running commands
  - SAR-341 Updated docs
  - SAR-351 Updated tests

#### 0.12.1
- SAR-303
  - Fixed PYPI URL
  - Moved command response message to component manager
- MCCS-845
  - `NO_SUPPLY` added to `PowerMode` enum

#### 0.12.0
- Implemented ST-946 (automation templates)
- Included Long running commands implementation
  - SAR-277, SAR-287, SAR-286, SAR-276, SAR-275, SAR-273

#### 0.11.3
- No change, moving artefacts to a new repository https://artefact.skao.int/.

#### 0.11.2
- Update docstrings for 100% coverage and PEP257 compliance

#### 0.11.1
- Minor breaking change: rename of "Master" devices to "Controller"

#### 0.11.0
- Breaking change: state models and component managers
  - Re-implementation of operational state model to better model
    hardware and support device decoupling.
  - Decoupling of state models from each other
  - Introduction of component managers, to support component monitoring
- Update to latest containers
- Add developer guide to documentation

#### 0.10.1
- Make dependency on `pytango` and `numpy` python packages explicit.
- Add optional "key" parameter to `SKASubarrayResourceManager` to filter JSON for
  assign & release methods.

#### 0.10.0
- Add `DebugDevice` command to `SKABaseDevice`.  This allows remote debugging to be
  enabled on all devices.  It cannot be disabled without restarting the process.
  If there are multiple devices in a device server, debugging is only enabled for
  the requested device (i.e., methods patched for debugging cppTango threads).
  However, all Python threads (not cppTango threads), will also be debuggable,
  even if created by devices other than the one that was used to enable debugging.
  There is only one debugger instance shared by the whole process.
  
#### 0.9.1
- Changed dependency from `ska_logging` to `ska_ser_logging`.

#### 0.9.0
- Breaking change: Package rename
  - Installable package name changed from `lmcbaseclasses` to `ska_tango_base`.
  - Package import `ska.base` has been changed to `ska_tango_base`.  For example, instead of
    `from ska.base import SKABaseDevice` use `from ska_tango_base import SKABaseDevice`.

#### 0.8.1
- Fix broken docs

#### 0.8.0
- Add base classes for CSP SubElements

#### 0.7.2
- Switch to threadsafe state machine

#### 0.7.1
- Bugfix for Reset() command

#### 0.7.0
- Separate adminMode state machine from opState state machine
- Add support for STANDBY opState
- Add Standby() and Disable() commands to SKABaseDevice
- Breaking behavioural changes to adminMode and opState state machines
- Breaking change to `_straight_to_state` method signature

#### 0.6.6
- Documentation bugfix

#### 0.6.5
- Fix to observation state machine: allow Abort() from RESETTING observation
  state

#### 0.6.4
- Refactor state machine to use pytransitions library.
- Minor behavioural change: Off() command is accepted in every obsState, rather
than only EMPTY obsState.
- support `_straight_to_state` shortcuts to simplify test setups
- Refactor of state machine testing to make it more portable

#### 0.6.3
- Fix omission of fatal_error transition from base device state machine.

#### 0.6.2
- Fix issue with incorrect updates to transitions dict from inherited devices.
  Only noticeable if running multiple devices of different types in the same
  process.

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
    for internal use and is no longer needed.
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
