#!/usr/bin/env python
###############################################################################
# SKA South Africa (http://ska.ac.za/)                                        #
# Author: cam@ska.ac.za                                                       #
# Copyright @ 2013 SKA SA. All rights reserved.                               #
#                                                                             #
# THIS SOFTWARE MAY NOT BE COPIED OR DISTRIBUTED IN ANY FORM WITHOUT THE      #
# WRITTEN PERMISSION OF SKA SA.                                               #
###############################################################################

import sys

from setuptools import setup, find_packages

# prevent unnecessary installation of pytest-runner
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

setup(name="levpro",
      description="Element Base Classes - Evolutionary Prototype",
      author="MeerKAT CAM Team",
      author_email="cam@ska.ac.za",
      packages=find_packages(),
      include_package_data=True,
      scripts=["scripts/gen_csv_info.py",
               "scripts/purge_xmi_tree.py",
               "scripts/elt_ctl.py",
               ],
      url='http://ska.ac.za/',
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
      ],
      tests_require=[
          "coverage",
          "pytest",
          'pytest-xdist',
          "python-devicetest",
          "unittest2"
      ],
      dependency_links=[
          'git+https://github.com/vxgmichel/pytango-devicetest.git#egg=python_devicetest'],
      keywords="levpro lmc ska",
      test_suite="nose.collector",
      zip_safe=False)
