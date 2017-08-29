# -*- coding: utf-8 -*-
#
# This file is part of the SKAAlarmDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""SKAAlarmDevice

A generic base device for Alarms for SKA.
"""

from . import release
from .SKAAlarmDevice import SKAAlarmDevice, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
