"""
This subpackage contains specifications of SKA state machines.
"""

__all__ = (
    "AdminModeModel",
    "OpStateModel",
    "ObsStateModel",
    "SubarrayObsStateModel",
    "CspSubElementObsStateModel",
)

# Note: order of imports is important - start with lowest in the hierarchy
from .admin_mode_model import AdminModeModel
from .op_state_model import OpStateModel
from .obs_state_model import ObsStateModel

from .subarray_obs_state_model import SubarrayObsStateModel
from .csp_subelement_obs_state_model import CspSubElementObsStateModel
