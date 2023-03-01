"""
This subpackage implements reference component managers.

These are example component managers for use in testing, and as
explanatory material.
"""

__all__ = (
    "FakeBaseComponent",
    "FakeSubarrayComponent",
    "ReferenceBaseComponentManager",
    "ReferenceSubarrayComponentManager",
)

from .reference_base_component_manager import (
    FakeBaseComponent,
    ReferenceBaseComponentManager,
)
from .reference_subarray_component_manager import (
    FakeSubarrayComponent,
    ReferenceSubarrayComponentManager,
)
