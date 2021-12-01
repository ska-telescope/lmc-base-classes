#!/usr/bin/env python

import os
import sys

import setuptools

setup_dir = os.path.dirname(os.path.abspath(__file__))
release_filename = os.path.join(setup_dir, "src", "ska_tango_base", "release.py")
exec(open(release_filename).read())

# prevent unnecessary installation of pytest-runner
needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
pytest_runner = ["pytest-runner"] if needs_pytest else []

setuptools.setup(
    name=name,
    description=description,
    version='0.12.1',
    author=author,
    author_email=author_email,
    license=license,
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    url="https://www.skatelescope.org/",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
    platforms=["OS Independent"],
    setup_requires=[] + pytest_runner,
    install_requires=[
        "debugpy",
        "numpy",
        "pytango",
        "ska_ser_logging",
        "transitions",
    ],
    tests_require=["pytest", "coverage", "pytest-json-report", "pytest-forked", "pytest-timeout"],
    entry_points={
        "console_scripts": [
            "SKAAlarmHandler=ska_tango_base.alarm_handler_device:main",
            "SKABaseDevice=ska_tango_base.base.base_device:main",
            "SKACapability=ska_tango_base.capability_device:main",
            "SKAExampleDevice=ska_tango_base.example_device:main",
            "SKALogger=ska_tango_base.logger_device:main",
            "SKAController=ska_tango_base.controller_device:main",
            "SKAObsDevice=ska_tango_base.obs.obs_device:main",
            "SKASubarray=ska_tango_base.subarray.subarray_device:main",
            "SKATelState=ska_tango_base.tel_state_device:main",
            "CspSubelementController=ska_tango_base.csp_subelement_controller:main",
            "CspSubelementObsDevice=ska_tango_base.csp_subelement_obsdevice:main",
            "CspSubelementSubarray=ska_tango_base.csp_subelement_subarray:main",
        ]
    },
    keywords="tango lmc base classes ska",
    zip_safe=False,
)
