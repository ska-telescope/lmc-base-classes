"""This module provides an abstract component manager for SKA Tango subarray devices."""
from ska_tango_base.base import BaseComponentManager


class SubarrayComponentManager(BaseComponentManager):
    """
    An abstract base class for a component manager for an SKA subarray Tango devices.

    It supports:

    * Maintaining a connection to its component

    * Controlling its component via commands like AssignResources(),
      Configure(), Scan(), etc.

    * Monitoring its component, e.g. detect that a scan has completed
    """

    def assign(self, resources, task_callback):
        """
        Assign resources to the component.

        :param resources: resources to be assigned
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def release(self, resources, task_callback):
        """
        Release resources from the component.

        :param resources: resources to be released
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def release_all(self, task_callback):
        """Release all resources."""
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def configure(self, configuration, task_callback):
        """
        Configure the component.

        :param configuration: the configuration to be configured
        :type configuration: dict
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def deconfigure(self, task_callback):
        """Deconfigure this component."""
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def scan(self, args, task_callback):
        """Start scanning."""
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def end_scan(self, task_callback):
        """End scanning."""
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def abort(self, task_callback):
        """Tell the component to abort whatever it was doing."""
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def obsreset(self, task_callback):
        """Reset the component to unconfigured but do not release resources."""
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def restart(self, task_callback):
        """Deconfigure and release all resources."""
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    # @property
    # def assigned_resources(self):
    #     """
    #     Return the resources assigned to the component.

    #     :return: the resources assigned to the component
    #     :rtype: list of str
    #     """
    #     raise NotImplementedError("SubarrayComponentManager is abstract.")

    # @property
    # def configured_capabilities(self):
    #     """
    #     Return the configured capabilities of the component.

    #     :return: list of strings indicating number of configured
    #         instances of each capability type
    #     :rtype: list of str
    #     """
    #     raise NotImplementedError("SubarrayComponentManager is abstract.")
