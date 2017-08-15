# -*- coding: utf-8 -*-
#
# This file is part of the SKATestDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""SKATestDevice

A generic base device for Testing SKA base class features.
"""

from . import release
from .SKATestDevice import SKATestDevice, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
