#!/usr/bin/env python

import os
import sys

import setuptools

setup_dir = os.path.dirname(os.path.abspath(__file__))
release_filename = os.path.join(setup_dir, "src", "ska", "base", "release.py")
exec(open(release_filename).read())

# prevent unnecessary installation of pytest-runner
needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
pytest_runner = ["pytest-runner"] if needs_pytest else []

setuptools.setup(
    name=name,
    description=description,
    version=version,
    author=author,
    author_email=author_email,
    license=license,
    packages=setuptools.find_namespace_packages(where="src", include=["ska.*"]),
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
    install_requires=["future", "transitions", "ska_logging >= 0.3.0"],
    tests_require=["pytest", "coverage", "pytest-json-report", "pytest-forked"],
    entry_points={
        "console_scripts": [
            "SKAAlarmHandler=ska.base.alarm_handler_device:main",
            "SKABaseDevice=ska.base.base_device:main",
            "SKACapability=ska.base.capability_device:main",
            "SKAExampleDevice=ska.base.example_device:main",
            "SKALogger=ska.base.logger_device:main",
            "SKAMaster=ska.base.master_device:main",
            "SKAObsDevice=ska.base.obs_device:main",
            "SKASubarray=ska.base.subarray_device:main",
            "SKATelState=ska.base.tel_state_device:main",
            "CspSubelementMaster=ska.base.csp_subelement_master:main",
            "CspSubelementObsDevice=ska.base.csp_subelement_obsdevice:main",
            "CspSubelementSubarray=ska.base.csp_subelement_subarray:main",
        ]
    },
    keywords="lmc base classes ska",
    zip_safe=False,
)
