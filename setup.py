#!/usr/bin/env python

import os
import sys

import setuptools

setup_dir = os.path.dirname(os.path.abspath(__file__))
release_filename = os.path.join(setup_dir, 'skabase', 'release.py')
exec(open(release_filename).read())

# prevent unnecessary installation of pytest-runner
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

setuptools.setup(
      name=name,
      description=description,
      version=version,
      author=author,
      author_email=author_email,
      license=license,
      packages=setuptools.find_packages(),
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
          "argparse",
          "future"
      ],
      tests_require=[
      ],
      keywords="lmc base classes ska",
      zip_safe=False)
