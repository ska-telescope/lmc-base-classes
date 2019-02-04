# lmc-base-classes

[![Documentation Status](https://readthedocs.org/projects/lmc-base-classes/badge/?version=latest)](https://developerskatelescopeorg.readthedocs.io/projects/lmc-base-classes/en/latest/?badge=latest)

## About
A shared repository for the Local Monitoring and Control (LMC) Base Classes. The goal is to create a Software Development Kit for the Control System of the [Square Kilometre Array](http://skatelescope.org/) (SKA) radio telescope project. The Telescope Manager provides the Central Control System and each _Element_ provides a Local Control System that all work together as the Control System for the instrument. In the SKA case _Elements_ are subsystems such as the Central Signal Processor (CSP), Science Data Processor (SDP), Dishes (DSH), Low-Frequency Apperture Array (LFAA) etc.  Control is implement using the distributed control system, [TANGO](http://www.tango-controls.org), which is accessed from Python using the [PyTango](https://github.com/tango-controls/pytango) package.

Early work in this repo was done as part of the LMC Base Classes Evolutionary Prototype (LEvPro) project, under the INDO-SA collaboration program.

## Docs
- SKA Control System guidelines:  [Google docs folder](https://drive.google.com/drive/folders/0B8fhAW5QnZQWQ2ZlcjhVS0NmRms)
- Old LEvPro work area: [Google docs folder](https://drive.google.com/drive/folders/0B8fhAW5QnZQWVHVFVGVXT2Via28)

## Contribute
Contributions are always welcome! Please ensure that you adhere to our coding standards [CAM_Style_guide](https://docs.google.com/document/d/1aZoIyR9tz5rCWr2qJKuMTmKp2IzHlFjrCFrpDDHFypM/edit?usp=sharing).  Use [flake8](http://flake8.pycqa.org/en/latest/) for linting (default settings, except maximum line length of 90 characters).
