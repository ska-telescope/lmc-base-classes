"""
This subpackage contains base devices specific to CSP.
"""

__all__ = (
    "CspSubElementObsStateModel",
    "CspObsComponentManager",
    "CspSubarrayComponentManager",
    "ReferenceCspObsComponentManager",
    "ReferenceCspSubarrayComponentManager",
    "CspSubElementMaster",
    "CspSubElementObsDevice",
    "CspSubElementSubarray",
)

from .master_device import CspSubElementMaster

from .obs import (
    CspSubElementObsStateModel,
    CspObsComponentManager,
    ReferenceCspObsComponentManager,
    CspSubElementObsDevice,
)

from .subarray import (
    CspSubarrayComponentManager,
    ReferenceCspSubarrayComponentManager,
    CspSubElementSubarray,
)
