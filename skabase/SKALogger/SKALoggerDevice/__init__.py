# -*- coding: utf-8 -*-
#
# This file is part of the SKALoggerDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""SKALoggerDevice

A generic base device for Logging for SKA.
"""

from . import release
from .SKALoggerDevice import SKALoggerDevice, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author