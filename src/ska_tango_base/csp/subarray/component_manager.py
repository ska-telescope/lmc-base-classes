"""
This module models component management for CSP subarrays.
"""
from ska_tango_base.subarray import SubarrayComponentManager


class CspSubarrayComponentManager(SubarrayComponentManager):
    """
    A component manager for SKA CSP subarray Tango devices:

    The current implementation is intended to
    * illustrate the model
    * enable testing of the base classes

    It should not generally be used in concrete devices; instead, write
    a subclass specific to the component managed by the device.
    """

    def __init__(self, op_state_model, obs_state_model, *args, **kwargs):
        super().__init__(
            op_state_model,
            obs_state_model,
            *args,
            **kwargs,
        )

    @property
    def config_id(self):
        return NotImplementedError("CspSubarrayComponentManager is abstract.")

    @property
    def scan_id(self):
        return NotImplementedError("CspSubarrayComponentManager is abstract.")
