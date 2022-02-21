"""This module models component management for CSP subelement observation devices."""
from ska_tango_base.base import BaseComponentManager


class CspObsComponentManager(BaseComponentManager):
    """
    A component manager for SKA CSP subelement observation Tango devices.

    The current implementation is intended to
    * illustrate the model
    * enable testing of the base classes

    It should not generally be used in concrete devices; instead, write
    a subclass specific to the component managed by the device.
    """

    def configure_scan(self, configuration, task_callback):
        """
        Configure the component.

        :param configuration: the configuration to be configured
        :type configuration: dict
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def deconfigure(self, task_callback):
        """Deconfigure this component."""
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def scan(self, args, task_callback):
        """Start scanning."""
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def end_scan(self, task_callback):
        """End scanning."""
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def abort(self, task_callback):
        """Tell the component to abort whatever it was doing."""
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def obsreset(self, task_callback):
        """Reset the configuration but do not release resources."""
        raise NotImplementedError("CspObsComponentManager is abstract.")

    @property
    def config_id(self):
        """Return the configuration id."""
        raise NotImplementedError("CspObsComponentManager is abstract.")

    @property
    def scan_id(self):
        """Return the scan id."""
        raise NotImplementedError("CspObsComponentManager is abstract.")

    @config_id.setter
    def config_id(self, config_id):
        """Set the configuration id."""
        raise NotImplementedError("CspObsComponentManager is abstract.")
