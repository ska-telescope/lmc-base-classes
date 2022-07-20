"""This subpackage models a SKA subarray Tango device."""

__all__ = (
    "SKASubarray",
    "SubarrayObsStateModel",
    "SubarrayComponentManager",
)

from .component_manager import SubarrayComponentManager
from .subarray_device import SKASubarray
from .subarray_obs_state_model import SubarrayObsStateModel
