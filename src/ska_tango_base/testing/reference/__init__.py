"""
This subpackage implements reference component managers.

These are example component managers for use in testing, and as
explanatory material.
"""

__all__ = (
    "FakeBaseComponent",
    "FakeCspObsComponent",
    "FakeCspSubarrayComponent",
    "FakeSubarrayComponent",
    "ReferenceBaseComponentManager",
    "ReferenceCspObsComponentManager",
    "ReferenceCspSubarrayComponentManager",
    "ReferenceSubarrayComponentManager",
)

# Note: order of imports is important - start with lowest in the hierarchy
from .reference_base_component_manager import (
    FakeBaseComponent,
    ReferenceBaseComponentManager,
)
from .reference_subarray_component_manager import (
    FakeSubarrayComponent,
    ReferenceSubarrayComponentManager,
)
from .reference_csp_obs_component_manager import (
    FakeCspObsComponent,
    ReferenceCspObsComponentManager,
)
from .reference_csp_subarray_component_manager import (
    FakeCspSubarrayComponent,
    ReferenceCspSubarrayComponentManager,
)
