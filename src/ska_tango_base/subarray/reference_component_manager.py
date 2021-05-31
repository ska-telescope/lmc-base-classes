"""
This module models component management for SKA subarray devices.
"""
import functools

from ska_tango_base.subarray import SubarrayComponentManager
from ska_tango_base.base import (
    check_communicating,
    ReferenceBaseComponentManager,
)
from ska_tango_base.control_model import PowerMode
from ska_tango_base.faults import (
    CapabilityValidationError,
    ComponentError,
    ComponentFault,
)


def check_on(func):
    """
    Decorator that makes a method first checks that the component is
    turned on and not faulty before allowing the command to proceed

    :param func: the wrapped function

    :return: the wrapped function
    """

    @functools.wraps(func)
    def _wrapper(component, *args, **kwargs):
        """
        Wrapper function that checks that the component is turned on and
        not faulty before invoking the wrapped function

        :param component: the component to check
        :param args: positional arguments to the wrapped function
        :param kwargs: keyword arguments to the wrapped function

        :return: whatever the wrapped function returns
        """
        if component.faulty:
            raise ComponentFault()
        if component.power_mode != PowerMode.ON:
            raise ComponentError("Component is not ON")
        return func(component, *args, **kwargs)

    return _wrapper


class ReferenceSubarrayComponentManager(
    ReferenceBaseComponentManager, SubarrayComponentManager
):
    """
    A component manager for SKA subarray Tango devices:

    The current implementation is intended to
    * illustrate the model
    * enable testing of the base classes

    It should not generally be used in concrete devices; instead, write
    a subclass specific to the component managed by the device.
    """

    class _ResourcePool:
        """
        A simple class for managing subarray resources
        """

        def __init__(self, callback=None):
            """
            Initialise a new instance

            :param callback: callback to call when the resource pool
                goes from empty to non-empty or vice-versa
            """
            self._resources = set()

            self._nonempty = False
            self._callback = callback

        def __len__(self):
            """
            Returns the number of resources currently assigned. Note that
            this also functions as a boolean method for whether there are
            any assigned resources: ``if len()``.

            :return: number of resources assigned
            :rtype: int
            """
            return len(self._resources)

        def assign(self, resources):
            """
            Assign some resources

            :param resources: resources to be assigned
            :type resources: set(str)
            """
            self._resources |= set(resources)
            self._update()

        def release(self, resources):
            """
            Release some resources

            :param resources: resources to be released
            :type resources: set(str)
            """
            self._resources -= set(resources)
            self._update()

        def release_all(self):
            """
            Release all resources
            """
            self._resources.clear()
            self._update()

        def get(self):
            """
            Get current resources

            :return: current resources.
            :rtype: set(str)
            """
            return set(self._resources)

        def check(self, resources):
            """
            Check that this pool contains specified resources.

            This is useful for commands like configure(), which might
            need to check that the subarray has the resources needed to
            effect a configuration.

            :return: whether this resource pool contains the specified
                resources
            :rtype bool
            """
            return resources in self._resources

        def _update(self):
            nonempty = bool(len(self))
            if self._nonempty != nonempty:
                self._nonempty = nonempty
                if self._callback is not None:
                    self._callback(nonempty)

    class _Component(ReferenceBaseComponentManager._Component):
        """
        An example subarray component for the component manager to work
        with.

        It can be directly controlled via configure(), scan(),
        end_scan(), end(), abort(), reset() and restart() command
        methods.

        For testing purposes, it can also be told to simulate an
        observation fault via simulate_obsfault() methods.

        When a component changes state, it lets the component manager
        know by calling its ``component_unconfigured``,
        ``component_configured``, ``component_scanning``,
        ``component_not_scanning`` and ``component_obsfault`` methods.
        """

        def __init__(
            self,
            capability_types,
            _power_mode=PowerMode.OFF,
            _faulty=False,
        ):
            """
            Initialise a new instance

            :param capability_types: a list strings representing
                capability types.
            :param _power_mode: initial power mode of this component
                (for testing only)
            :param _faulty: whether this component should initially
                simulate a fault (for testing only)
            """
            self._configured = False

            # self._configured_capabilities is kept as a
            # dictionary internally. The keys and values will represent
            # the capability type name and the number of instances,
            # respectively.
            try:
                self._configured_capabilities = dict.fromkeys(capability_types, 0)
            except TypeError:
                # Might need to have the device property be mandatory in the database.
                self._configured_capabilities = {}

            self._configured_callback = None

            self._scanning = False
            self._scanning_callback = None

            self._obsfault = False
            self._obsfault_callback = None

            super().__init__(_power_mode=_power_mode, _faulty=_faulty)

        def set_obs_callbacks(
            self,
            configured_callback,
            scanning_callback,
            obsfault_callback,
        ):
            """
            Set callbacks for the underlying component

            :param configured_callback: a callback to call with a
                boolean argument when whether the component is
                configured changes
            :param scanning_callback: a callback to call with a boolean
                argument when whether the component is scanning changes
            :param obsfault_callback: a callback to call when the
                component experiences an obs faults
            """
            self._configured_callback = configured_callback
            self._scanning_callback = scanning_callback
            self._obsfault_callback = obsfault_callback

        @property
        @check_on
        def configured(self):
            """
            Whether this component is configured

            :return: whether this component is configured
            :rtype: bool
            """
            return self._configured

        @property
        @check_on
        def configured_capabilities(self):
            """
            Configured capabilities of this component

            :return: list of strings indicating number of configured
                instances of each capability type
            :rtype: list of str
            """
            configured_capabilities = []
            for capability_type, capability_instances in list(
                self._configured_capabilities.items()
            ):
                configured_capabilities.append(
                    "{}:{}".format(capability_type, capability_instances)
                )
            return sorted(configured_capabilities)

        @property
        @check_on
        def scanning(self):
            """
            Whether this component is scanning

            :return: whether this component is scanning
            :rtype: bool
            """
            return self._scanning

        @property
        @check_on
        def obsfault(self):
            """
            Whether this component is obsfaulting

            :return: whether this component is obsfaulting
            :rtype: bool
            """
            return self._obsfault

        def _validate_capability_types(self, capability_types):
            """
            Check the validity of the input parameter passed to the
            Configure command.

            :param capability_types: a list strings representing
                capability types.
            :type capability_types: list

            :raises CapabilityValidationError: If any of the capabilities
                requested are not valid.
            """
            invalid_capabilities = list(
                set(capability_types) - set(self._configured_capabilities)
            )

            if invalid_capabilities:
                raise CapabilityValidationError(
                    "Invalid capability types requested {}".format(invalid_capabilities)
                )

        @check_on
        def configure(self, configuration):
            """
            Configure the component

            :param configuration: the configuration to be configured
            :type configuration: dict
            """
            # In this example implementation, the keys of the dict
            # are the capability types, and the values are the
            # integer number of instances required.
            # E.g., config = {"BAND1": 5, "BAND2": 3}
            capability_types = list(configuration.keys())
            self._validate_capability_types(capability_types)

            # Perform the configuration.
            for capability_type, capability_instances in configuration.items():
                self._configured_capabilities[capability_type] += capability_instances

            self._update_configured(True)

        @check_on
        def deconfigure(self):
            """
            Deconfigure this component.
            """
            self._configured_capabilities = {
                k: 0 for k in self._configured_capabilities
            }
            self._update_configured(False)

        @check_on
        def scan(self, args):
            """
            Start scanning
            """
            self._update_scanning(True)

        @check_on
        def end_scan(self):
            """
            End scanning
            """
            self.simulate_scan_stopped()

        @check_on
        def simulate_scan_stopped(self):
            """
            Tell the component to simulate spontaneous stopping its
            scan.
            """
            self._update_scanning(False)

        @check_on
        def simulate_obsfault(self, obsfault):
            """
            Tell the component to simulate an obsfault
            """
            self._update_obsfault(obsfault)

        def _invoke_configured_callback(self):
            """
            Helper method that invokes the callback when whether the
            component is configured changes.
            """
            if not self.faulty:
                if self._configured_callback is not None:
                    self._configured_callback(self._configured)

        def _update_configured(self, configured):
            """
            Helper method that updates whether the component is
            configured or not, ensuring that callbacks are called as
            required.

            :param configured: new value for whether the component is
                configured or not
            :type configured: bool
            """
            if self._configured != configured:
                self._configured = configured
                self._invoke_configured_callback()

        def _invoke_scanning_callback(self):
            """
            Helper method that invokes the callback when whether the
            component is scanning changes.
            """
            if not self.faulty:
                if self._scanning_callback is not None:
                    self._scanning_callback(self._scanning)

        def _update_scanning(self, scanning):
            """
            Helper method that updates whether the component is
            scanning or not, ensuring that callbacks are called as
            required.

            :param scanning: new value for whether the component is
                scanning or not
            :type scanning: bool
            """
            if self._scanning != scanning:
                self._scanning = scanning
                self._invoke_scanning_callback()

        def _invoke_obsfault_callback(self):
            """
            Helper method that invokes the callback when the component
            experiences an obsfault.
            """
            if not self.faulty:
                if self.obsfault and self._obsfault_callback is not None:
                    self._obsfault_callback()

        def _update_obsfault(self, obsfault):
            """
            Helper method that updates whether the component is
            obsfaulting or not, ensuring that callbacks are called as
            required.

            :param obsfault: new value for whether the component is
                obsfaulting or not
            :type obsfaulting: bool
            """
            if self._obsfault != obsfault:
                self._obsfault = obsfault
                if obsfault:
                    self._invoke_obsfault_callback()

    def __init__(
        self,
        op_state_model,
        obs_state_model,
        capability_types,
        logger=None,
        _component=None,
    ):
        """
        Initialise a new ReferenceSubarrayComponentManager instance

        :param op_state_model: the op state model used by this component
            manager
        :param obs_state_model: the obs state model used by this
            component manager
        :param capability_types: types of capability supported by this
            component manager
        :param logger: a logger for this component manager
        :param _component: allows setting of the component to be
            managed; for testing purposes only
        """
        self.obs_state_model = obs_state_model
        self._resource_pool = self._ResourcePool(self.component_resourced)

        super().__init__(
            op_state_model,
            obs_state_model,
            logger=logger,
            _component=_component or self._Component(capability_types),
        )

    def start_communicating(self):
        """
        Establish communication with the component, then start
        monitoring.
        """
        if self._connected:
            return
        super().start_communicating()

        self._component.set_obs_callbacks(
            self.component_configured,
            self.component_scanning,
            self.component_obsfault,
        )

        if self._component.faulty:
            return
        if self._component.power_mode != PowerMode.ON:
            return

        # we've been disconnected and we might have missed some
        # changes, so we need to check the component's state, and
        # make our state model correspond
        if self._component.obsfault:
            self.obs_state_model.to_OBSFAULT()
        elif not self._component.configured:
            self.obs_state_model.to_IDLE()
        elif not self._component.scanning:
            self.obs_state_model.to_READY()
        else:
            self.obs_state_model.to_SCANNING()

    def stop_communicating(self):
        """
        Cease monitoring the component, and break off all communication
        with it.
        """
        if not self._connected:
            return

        self._component.set_obs_callbacks(None, None, None)
        super().stop_communicating()

    def simulate_communication_failure(self, fail_communicate):
        """
        Simulate (or stop simulating) a component connection failure

        :param fail_communicate: whether the connection to the component
            is failing
        """
        if fail_communicate and self._connected:
            self._component.set_obs_callbacks(None, None, None)
        super().simulate_communication_failure(fail_communicate)

    @check_communicating
    def assign(self, resources):
        """
        Assign resources to the component

        :param resources: resources to be assigned
        :type resources: list(str)
        """
        self.logger.info("Assigning resources to component")
        self._resource_pool.assign(resources)

    @check_communicating
    def release(self, resources):
        """
        Release resources from the component

        :param resources: resources to be released
        :type resources: list(str)
        """
        self.logger.info("Releasing resources in component")
        self._resource_pool.release(resources)

    @check_communicating
    def release_all(self):
        """
        Release all resources
        """
        self.logger.info("Releasing all resources in component")
        self._resource_pool.release_all()

    @check_communicating
    def configure(self, configuration):
        """
        Configure the component

        :param configuration: the configuration to be configured
        :type configuration: dict
        """
        self.logger.info("Configuring component")
        self._component.configure(configuration)

    @check_communicating
    def deconfigure(self):
        """
        Deconfigure this component.
        """
        self.logger.info("Deconfiguring component")
        self._component.deconfigure()

    @check_communicating
    def scan(self, args):
        """
        Start scanning
        """
        self.logger.info("Starting scan in component")
        self._component.scan(args)

    @check_communicating
    def end_scan(self):
        """
        End scanning
        """
        self.logger.info("Stopping scan in component")
        self._component.end_scan()

    @check_communicating
    def abort(self):
        """
        Tell the component to abort whatever it was doing
        """
        self.logger.info("Aborting component")
        if self._component.scanning:
            self._component.end_scan()

    @check_communicating
    def obsreset(self):
        """
        Tell the component to reset to an unconfigured state (but
        without releasing any assigned resources)
        """
        self.logger.info("Resetting component")
        if self._component.configured:
            self._component.deconfigure()

    @check_communicating
    def restart(self):
        """
        Tell the component to return to an empty state (unconfigured and
        without any assigned resources)
        """
        self.logger.info("Restarting component")
        if self._component.configured:
            self._component.deconfigure()
        self._resource_pool.release_all()

    @property
    @check_communicating
    def assigned_resources(self):
        """
        Resources assigned to the component

        :return: the resources assigned to the component
        :rtype: list of str
        """
        return sorted(self._resource_pool.get())

    @property
    @check_communicating
    def configured_capabilities(self):
        """
        Configured capabilities of the component

        :return: list of strings indicating number of configured
            instances of each capability type
        :rtype: list of str
        """
        return self._component.configured_capabilities

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
