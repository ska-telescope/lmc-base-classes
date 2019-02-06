# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#

"""SKABaseDevice

A generic base device for SKA. It exposes the attributes, properties and commands of
a device that are common for all the SKA devices.
"""

__all__ = ["SKABaseDevice", "main"]
from skabase import release
from .SKABaseDevice import SKABaseDevice, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
