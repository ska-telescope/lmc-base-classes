# SKA Tango Base Classes and Utilities

[![Documentation Status](https://readthedocs.org/projects/ska-telescope-ska-tango-base/badge/?version=latest)](https://developer.skao.int/projects/ska-tango-base/en/latest/?badge=latest)

## About

A shared repository for the Local Monitoring and Control (LMC) Tango Base Classes. The goal is to create a Software Development Kit for the Control System of the [Square Kilometre Array](http://skatelescope.org/) (SKA) radio telescope project. The Telescope Manager provides the Central Control System and each _Element_ provides a Local Control System that all work together as the Control System for the instrument. In the SKA case _Elements_ are subsystems such as the Central Signal Processor (CSP), Science Data Processor (SDP), Dishes (DSH), Low-Frequency Aperture Array (LFAA) etc.  Control is implement using the distributed control system, [Tango](http://www.tango-controls.org), which is accessed from Python using the [PyTango](https://gitlab.com/tango-controls/pytango) package.

Early work in this repo was done as part of the LMC Base Classes Evolutionary Prototype (LEvPro) project, under the INDO-SA collaboration program.

The ska-tango-base repository includes a set of eight classes as mentioned in SKA Control systems guidelines. Following is the list of base classes

- SKABaseDevice: This is generic class that includes common attributes, commands and properties that are required for any SKA tango device.
- SKACapability: This is generic base class for any element to provide common functionality of a capability of an SKA device.
- SKAAlarmHandler: This is the generic class meant to handle the alarms and alerts.
- SKALogger: This is the generic class for logging.
- SKAController: This is the generic base class to provide common functionality required for any SKA Element Controller device.
- SKAObsDevice: This is the generic base class meant to provide common functionality of a device which is directly going to be a part of an observation.
- SKASubarray: This is the generic base class which provides common functionality required in a subarray device.
- SKATelState: This is the generic base class to provide common functionality of a TelState device of any SKA Element.

## Documentation

For detailed instructions on installation and usage, see the [Read The Docs](https://developer.skao.int/projects/ska-tango-base/en/latest/).

## Installation

### Requirements

The basic requirements are:

- Python 3.10
- Pip

### Installation steps

1. Clone the repository on local machine.
2. Navigate to the root directory of the repository from terminal
3. Run ``python3 -m pip install . --extra-index-url https://artefact.skao.int/repository/pypi-internal/simple``

## Development

### Visual Studio Code

VS Code is the recommended IDE for this project. Simply open the root of the project as a workspace and build and load the included Dev Container.

### PyCharm

The Docker integration is recommended.  For development, use the `artefact.skao.int/ska-tango-base:latest` image as the Python Interpreter for the project.

As this project uses a `src` [folder structure](https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure), so under _Preferences > Project Structure_, the `src` folder needs to be marked as "Sources".  That will allow the interpreter to be aware of the package from folders like `tests` that are outside of `src`. When adding Run/Debug configurations, make sure "Add content roots to PYTHONPATH" and "Add source roots to PYTHONPATH" are checked.

## Contribute

Contributions are always welcome! Please refer to the [SKA telescope developer portal](https://developer.skao.int/).

## Version History

See the `CHANGELOG.md` file for version history.
