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
