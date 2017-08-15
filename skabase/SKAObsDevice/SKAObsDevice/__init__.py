# -*- coding: utf-8 -*-
#
# This file is part of the SKAObsDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""SKAObsDevice

A generic base device for Observations for SKA.
"""

from . import release
from .SKAObsDevice import SKAObsDevice, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
