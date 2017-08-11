# -*- coding: utf-8 -*-
#
# This file is part of the SKAMaster project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""SKAMaster

A master test
"""

from . import release
from .SKAMaster import SKAMaster, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
