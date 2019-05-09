# -*- coding: utf-8 -*-
#
# This file is part of the SKAMaster project
#
#
#
"""SKAMaster

A generic master device for SKA Element Master.
"""

__all__ = ["SKAMaster", "main"]

from skabase import release
from .SKAMaster import SKAMaster, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
