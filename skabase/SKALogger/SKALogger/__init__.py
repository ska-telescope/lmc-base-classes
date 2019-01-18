# -*- coding: utf-8 -*-
#
# This file is part of the SKALogger project
#
#
#


"""SKALogger

A generic base device for Logging for SKA. It enables to view on-line logs through the TANGO Logging Services
and to store logs using Python logging. It configures the log levels of remote logging for selected devices.
"""

from . import release
from .SKALogger import SKALogger, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
