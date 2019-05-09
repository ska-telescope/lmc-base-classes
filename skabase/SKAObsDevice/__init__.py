# -*- coding: utf-8 -*-
#
# This file is part of the SKAObsDevice project
#
#
#
"""SKAObsDevice

A generic base device for Observations for SKA. It inherits SKABaseDevice class. Any device implementing
and obsMode will inherit from SKAObsDevice instead of just SKABaseDevice.
"""

__all__ = ["SKAObsDevice", "main"]
from skabase import release
from .SKAObsDevice import SKAObsDevice, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
