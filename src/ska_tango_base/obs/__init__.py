# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This subpackage models an SKA Tango observing device."""

__all__ = (
    "ObsDeviceComponentManager",
    "ObsStateModel",
    "SKAObsDevice",
)

from .obs_device import ObsDeviceComponentManager, SKAObsDevice
from .obs_state_model import ObsStateModel
