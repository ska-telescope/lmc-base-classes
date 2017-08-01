#!/usr/bin/env python
###############################################################################
# SKA South Africa (http://ska.ac.za/)                                        #
# Author: cam@ska.ac.za                                                       #
# Copyright @ 2013 SKA SA. All rights reserved.                               #
#                                                                             #
# THIS SOFTWARE MAY NOT BE COPIED OR DISTRIBUTED IN ANY FORM WITHOUT THE      #
# WRITTEN PERMISSION OF SKA SA.                                               #
###############################################################################

from setuptools import setup, find_packages

setup(name="skabase",
      description="Element Base Classes - Evolutionary Prototype",
      author="MeerKAT CAM Team",
      author_email="cam@ska.ac.za",
      packages=find_packages(),
      include_package_data=True,
      scripts=["scripts/gen_csv_info.py",
               "scripts/elt_ctl.py",
               "run/eltlogger_DS",
               "run/eltmaster_DS",
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
      setup_requires=[],
      install_requires=[
          "enum34",
          "argparse"
      ],
      tests_require=[
          "nose",
          "coverage",
          "nosexcover",
          "unittest2"
      ],
      keywords="elt lmc ska",
      test_suite="nose.collector",
      zip_safe=False)
