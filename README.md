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
  This is in line with the move to Elastic for all logs instead of using the Tango Logging System
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
