# -*- coding: utf-8 -*-
#
# This file is part of the SKACapability project
#
#
#
"""SKACapability

A Subarray handling device. It exposes the instances of configured capabilities.
"""
__all__ = ["SKACapability", "main"]
from skabase import release
from .SKACapability import SKACapability, main

__version__ = release.version
__version_info__ = release.version_info
__author__ = release.author
