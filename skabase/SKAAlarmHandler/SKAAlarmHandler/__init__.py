# -*- coding: utf-8 -*-
#
# This file is part of the SKAAlarmHandler project
#
#
#

"""SKAAlarmHandler

A generic base device for Alarms for SKA. It exposes SKA alarms and SKA alerts as TANGO attributes.
SKA Alarms and SKA/Element Alerts are rules-based configurable conditions that can be defined over multiple
attribute values and quality factors, and are separate from the "built-in" TANGO attribute alarms.
"""

from . import release
from .SKAAlarmHandler import SKAAlarmHandler, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
