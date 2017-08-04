# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""SKABASE

A generic base device for SKA.
"""

from . import release
from .SKABaseDevice import SKABaseDevice, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
