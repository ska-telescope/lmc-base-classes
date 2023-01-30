"""This module models component management for CSP subarrays."""
from ...subarray import SubarrayComponentManager


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
    def config_id(self) -> str:
        """
        Return the configuration id.

        :return: the configuration id.

        :raises NotImplementedError: because this class is abstract
        """  # noqa DAR202
        raise NotImplementedError("CspSubarrayComponentManager is abstract.")

    @property
    def scan_id(self) -> int:
        """
        Return the scan id.

        :return: the scan id.

        :raises NotImplementedError: because this class is abstract
        """  # noqa DAR202
        raise NotImplementedError("CspSubarrayComponentManager is abstract.")
