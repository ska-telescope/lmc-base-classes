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
3. Run 'sudo pip3 install .'

## Testing
The LMC base classes can be tested locally my invoking *make CI_JOB_ID=some_id test* command. 
This invokes a chain of commands from the makefile which builds the lmc base classes
python package, creates a docker image with lmc base classes, instantiates separate 
container for each of the base class and runs unit test cases of each class. Additionally,
code analysis is also done and code coverage report is prepared.
After testing is done, the containers are taken down.    

## Usage
The base classes are installed as python package in the system. The intended usage of the base classes is to inherit the class according to the requirement. The class needs to be imported in the module. e.g.
```
from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice

class DishLeafNode(with_metaclass(DeviceMeta, SKABaseDevice)):
.
.
.
```

**Note: The lmc-base-classes repository will be repackaged soon. That will change the way of importing it.**

## Docs
- SKA Control System guidelines:  [Google docs folder](https://drive.google.com/drive/folders/0B8fhAW5QnZQWQ2ZlcjhVS0NmRms)
- Old LEvPro work area: [Google docs folder](https://drive.google.com/drive/folders/0B8fhAW5QnZQWVHVFVGVXT2Via28)



## Contribute
Contributions are always welcome! Please ensure that you adhere to our coding standards [CAM_Style_guide](https://docs.google.com/document/d/1aZoIyR9tz5rCWr2qJKuMTmKp2IzHlFjrCFrpDDHFypM/edit?usp=sharing).  Use [flake8](http://flake8.pycqa.org/en/latest/) for linting (default settings, except maximum line length of 90 characters).
