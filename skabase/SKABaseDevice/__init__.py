# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#

"""SKABASE

__init__.py: A generic base device for SKA. It exposes the generic attributes, properties and commands of an SKA device.
"""
__all__ = ["SKABaseDevice", "main"]

from skabase import release
from .SKABaseDevice import SKABaseDevice, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author