#!/usr/bin/env python

import sys

from setuptools import setup, find_packages

# prevent unnecessary installation of pytest-runner
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

setup(name="lmc_base_classes",
      description="Element Base Classes - Evolutionary Prototype",
      author="SKA Team",
      packages=find_packages(),
      include_package_data=True,
      scripts=["scripts/gen_csv_info.py",
               "scripts/purge_xmi_tree.py",
               "scripts/elt_ctl.py",
               ],
      url='https://www.skatelescope.org/',
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: Other/Proprietary License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Scientific/Engineering :: Astronomy"],
      platforms=["OS Independent"],
      setup_requires=[] + pytest_runner,
      install_requires=[
          "enum34",
          "argparse"
          "future"
      ],
      tests_require=[
          "coverage",
          "pytest",
          "pytest-cov",
          "pytest-xdist"
      ],
      keywords="lmc base classes ska",
      zip_safe=False)
