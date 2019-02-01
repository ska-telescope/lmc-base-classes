# -*- coding: utf-8 -*-
#
# This file is part of the SKASubarray project
#
#
#

"""SKASubarray

A SubArray handling device. It allows the assigning/releasing of resources into/from Subarray, configuring
capabilities, and exposes the related information like assigned resources, configured capabilities, etc.
"""

__all__ = ["SKASubarray", "main"]

from skabase import release
from .SKASubarray import SKASubarray, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
