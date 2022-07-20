# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This subpackage models a SKA subarray Tango device."""

__all__ = (
    "SKASubarray",
    "SubarrayObsStateModel",
    "SubarrayComponentManager",
)

# Note: order of imports is important - start with lowest in the hierarchy
from .subarray_obs_state_model import SubarrayObsStateModel
from .component_manager import SubarrayComponentManager
from .subarray_device import SKASubarray
