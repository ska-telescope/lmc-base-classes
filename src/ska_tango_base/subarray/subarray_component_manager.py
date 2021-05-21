"""
This module provides an abstract component manager for SKA Tango
subarray devices.
"""
from ska_tango_base.base_device import BaseComponentManager


class SubarrayComponentManager(BaseComponentManager):
    """
    An abstract base class for a component manager for an SKA subarray
    Tango devices, supporting:

    * Maintaining a connection to its component

    * Controlling its component via commands like AssignResources(),
      Configure(), Scan(), etc.

    * Monitoring its component, e.g. detect that a scan has completed
    """

    def __init__(self, op_state_model, obs_state_model):
        """
        Initialise a new SubarrayComponentManager instance

        :param op_state_model: the op state model used by this component manager
        :param obs_state_model: the obs state model used by this component manager
        """
        self.obs_state_model = obs_state_model

        super().__init__(op_state_model)

    def assign(self, resources):
        """
        Assign resources to the component

        :param resources: resources to be assigned
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def release(self, resources):
        """
        Release resources from the component

        :param resources: resources to be released
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def release_all(self):
        """
        Release all resources
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def configure(self, configuration):
        """
        Configure the component

        :param configuration: the configuration to be configured
        :type configuration: dict
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def deconfigure(self):
        """
        Deconfigure this component.
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def scan(self, args):
        """
        Start scanning
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def end_scan(self):
        """
        End scanning
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def abort(self):
        """
        Tell the component to abort whatever it was doing
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def obsreset(self):
        """
        Tell the component to reset to an unconfigured state (but
        without releasing any assigned resources)
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def restart(self):
        """
        Tell the component to return to an empty state (unconfigured and
        without any assigned resources)
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    @property
    def assigned_resources(self):
        """
        Resources assigned to the component

        :return: the resources assigned to the component
        :rtype: list of str
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    @property
    def configured_capabilities(self):
        """
        Configured capabilities of the component

        :return: list of strings indicating number of configured
            instances of each capability type
        :rtype: list of str
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def component_resourced(self, resourced):
        """
        Callback hook, called when whether the component has any
        resources changes

        :param resourced: whether this component has any resources
        :type resourced: bool
        """
        if resourced:
            self.obs_state_model.perform_action("component_resourced")
        else:
            self.obs_state_model.perform_action("component_unresourced")

    def component_configured(self, configured):
        """
        Callback hook, called when whether the component is configured
        changes

        :param configured: whether this component is configured
        :type configured: bool
        """
        if configured:
            self.obs_state_model.perform_action("component_configured")
        else:
            self.obs_state_model.perform_action("component_unconfigured")

    def component_scanning(self, scanning):
        """
        Callback hook, called when whether the component is scanning
        changes

        :param scanning: whether this component is scanning
        :type scanning: bool
        """
        if scanning:
            self.obs_state_model.perform_action("component_scanning")
        else:
            self.obs_state_model.perform_action("component_not_scanning")

    def component_obsfault(self):
        """
        Callback hook, called when the component obsfaults
        """
        self.obs_state_model.perform_action("component_obsfault")
