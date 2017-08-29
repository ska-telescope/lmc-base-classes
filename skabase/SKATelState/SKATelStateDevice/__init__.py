# -*- coding: utf-8 -*-
#
# This file is part of the SKATelStateDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""SKATelStateDevice

A generic base device for Telescope State for SKA.
"""

from . import release
from .SKATelStateDevice import SKATelStateDevice, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
