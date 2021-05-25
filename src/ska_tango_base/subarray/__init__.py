"""
This subpackage models a SKA subarray Tango device.
"""

__all__ = (
    "SubarrayObsStateModel",
    "SubarrayComponentManager",
    "ReferenceSubarrayComponentManager",
    "check_on",
    "SKASubarray",
)

# Note: order of imports is important - start with lowest in the hierarchy
from .subarray_obs_state_model import SubarrayObsStateModel

from .component_manager import SubarrayComponentManager
from .reference_component_manager import (
    ReferenceSubarrayComponentManager, check_on
)
from .subarray_device import SKASubarray
