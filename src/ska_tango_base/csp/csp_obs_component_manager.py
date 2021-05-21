"""
This module models component management for CSP subelement observation devices.
"""
from ska_tango_base.base_device import BaseComponentManager

class CspObsComponentManager(BaseComponentManager):
    """
    A component manager for SKA CSP subelement observation Tango devices:

    The current implementation is intended to
    * illustrate the model
    * enable testing of the base classes

    It should not generally be used in concrete devices; instead, write
    a subclass specific to the component managed by the device.
    """

    def __init__(self, op_state_model, obs_state_model, *args, **kwargs):
        self.obs_state_model = obs_state_model
        super().__init__(op_state_model, *args, **kwargs)

    def configure_scan(self, configuration):
        """
        Configure the component

        :param configuration: the configuration to be configured
        :type configuration: dict
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def deconfigure(self):
        """
        Deconfigure this component.
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def scan(self, args):
        """
        Start scanning
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def end_scan(self):
        """
        End scanning
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def abort(self):
        """
        Tell the component to abort whatever it was doing
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def obsreset(self):
        """
        Tell the component to reset to an unconfigured state (but
        without releasing any assigned resources)
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    @property
    def config_id(self):
        raise NotImplementedError("CspObsComponentManager is abstract.")

    @property
    def scan_id(self):
        raise NotImplementedError("CspObsComponentManager is abstract.")

    @config_id.setter
    def config_id(self, config_id):
        raise NotImplementedError("CspObsComponentManager is abstract.")

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
