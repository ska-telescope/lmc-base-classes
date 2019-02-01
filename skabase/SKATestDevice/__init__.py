# -*- coding: utf-8 -*-
#
# This file is part of the SKATestDevice project
#
#
#

"""SKATestDevice

A generic Test device for testing SKA base class functionalities.
"""

from skabase import release
from .SKATestDevice import SKATestDevice, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
