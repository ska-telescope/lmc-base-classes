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

### Tango device controls for logging levels and targets

The logging level and additional logging targets are controlled by two attributes.
These attributes are initialised from two device properties on startup.  An extract
of the definitions from the base class is shown below.

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
        dtype='DevVarStringArray', default_value=[]
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
        max_dim_x=3,
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

Note that the the `loggingTargets` attribute says "excluding ska_logging defaults".
If you want to forward logs to other targets, then you could use this attribute.  It is an
empty list by default, since we only want the logging to stdout that is already provided
by the ska_logging library.

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

# disable all additional targets (empty list breaks, so include an empty string!)
proxy.loggingTargets = ['']
```

Currently there are three types of targets implemented:
- `console`
- `file`
- `syslog`

If you were to set the `proxy.loggingTargets = ["console::cout"]` you would get
all the logs to stdout duplicated.  Once for ska_logging root logger, and once for
the additional console logger you just added.  For the "console" option it doesn't matter
what text comes after the `::` - we always use stdout.

For file output, provide the path after the `::`.  If the path is ommitted, then a
file is created in the device server's current directory, with a name based on the
the Tango name.  E.g., "my/test/device" would get the file "my_test_device.log".
Currently, we using a `logging.handlers.RotatingFileHandler` with a 1 MB limit and
just 2 backups.  This could be modified in future.

For syslog, the syslog target address details must be provided after the `::`.
This string is what ever you would pass to `logging.handlers.SysLogHandler`'s `address`
argument.  E.g. `proxy.loggingTargets = ["syslog::/dev/log"]`.

If you want file and syslog targets, you could do something like:
`proxy.loggingTargets = ["file::/tmp/my.log", "syslog::/dev/log"]`.

**Note:**  There is a limit of 3 additional handlers.  That the maximum length
of the spectrum attribute. We could change this if there is a reasonable use
case for it.

### Can I still send logs to the Tango Logging Service?

Not really.  In `SKABaseDevice._init_logging` we monkey patch the Tango Logging Service (TLS)
methods `debug_stream`, `error_stream`, etc. to point the Python logger methods like
`logger.debug`, `logger.error`, etc.  This means that logs are no longer forwarded
to the Tango Logging Service.

In future, we could add a new target that allows the logs to be forwarded to TLS.
That would be something like `"tls::my/log/consumer"`.

Although, you might get some logs from the admin device, since we cannot override its
behaviour from the Python layer.  PyTango is wrapper around the C++ Tango library, and
the admin device is implemented in C++.

The `tango.DeviceProxy` also has some built in logging control methods which you should
avoid as they only apply to the Tango Logging Service:
- `DeviceProxy.add_logging_target`
- `DeviceProxy.remove_logging_target`
- `DeviceProxy.set_logging_level`

### What code should I write to log from my device?

You should always use the `self.logger` object within methods.  This instance of the
logger is the only one that knows the Tango device name.  You can also use the PyTango
decorators like `DebugIt`, since the monkey patching redirects them to that same logger.

```python
class MyDevice(SKABaseDevice):
    def my_method(self):
        someone = "you"
        self.logger.info("I have a message for %s", someone)

    @tango.DebugIt()
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
