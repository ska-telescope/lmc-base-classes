# flake8: noqa
# type: ignore
# pylint: skip-file  # TODO: Incrementally lint this repo
"""This module models component management for CSP subarrays."""
from ska_tango_base.subarray import SubarrayComponentManager


class CspSubarrayComponentManager(SubarrayComponentManager):
    """
    A component manager for SKA CSP subarray Tango devices.

    The current implementation is intended to
    * illustrate the model
    * enable testing of the base classes

    It should not generally be used in concrete devices; instead, write
    a subclass specific to the component managed by the device.
    """

    @property
    def config_id(self):
        """Return the configuration id."""
        return NotImplementedError("CspSubarrayComponentManager is abstract.")

    @property
    def scan_id(self):
        """Return the scan id."""
        return NotImplementedError("CspSubarrayComponentManager is abstract.")
