"""
This subpackage models a SKA Tango observing device.
"""

__all__ = (
    "ObsStateModel",
    "SKAObsDevice",
)

# Note: order of imports is important - start with lowest in the hierarchy
from .obs_state_model import ObsStateModel

from .obs_device import SKAObsDevice
