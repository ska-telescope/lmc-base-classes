"""This subpackage models a SKA Tango observing device."""

__all__ = (
    "ObsStateModel",
    "SKAObsDevice",
)

from .obs_device import SKAObsDevice
from .obs_state_model import ObsStateModel
