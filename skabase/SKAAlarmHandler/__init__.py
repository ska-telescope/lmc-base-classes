# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#

"""SKABASE

A generic base device for SKA.
"""

from . import release
from .SKAAlarmHandler import SKAAlarmHandler, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
