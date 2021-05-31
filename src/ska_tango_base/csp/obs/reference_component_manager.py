"""
This module models component management for CSP subelement observation devices.
"""
import functools

from ska_tango_base.csp.obs import CspObsComponentManager
from ska_tango_base.base import check_communicating, ReferenceBaseComponentManager

from ska_tango_base.control_model import PowerMode
from ska_tango_base.faults import ComponentError, ComponentFault


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


class ReferenceCspObsComponentManager(
    CspObsComponentManager, ReferenceBaseComponentManager
):
    """
    A component manager for SKA CSP subelement observation Tango devices:

    The current implementation is intended to
    * illustrate the model
    * enable testing of the base classes

    It should not generally be used in concrete devices; instead, write
    a subclass specific to the component managed by the device.
    """

    class _Component(ReferenceBaseComponentManager._Component):
        """
        An example CSP subelement obs component for the component
        manager to work with.

        It can be directly controlled via configure(), scan(),
        end_scan(), go_to_idle(), abort() and reset()  command methods.

        For testing purposes, it can also be told to simulate an
        observation fault via simulate_obsfault() methods.

        When a component changes state, it lets the component manager
        know by calling its ``component_unconfigured``,
        ``component_configured``, ``component_scanning``,
        ``component_not_scanning`` and ``component_obsfault`` methods.
        """

        def __init__(
            self,
            _power_mode=PowerMode.OFF,
            _faulty=False,
        ):
            """
                     Initialise a new instance
            State Machine<State_Machine>


                     :param _power_mode: initial power mode of this component
                         (for testing only)
                     :param _faulty: whether this component should initially
                         simulate a fault (for testing only)
            """
            self._configured = False
            self._configured_callback = None
            self._config_id = ""

            self._scanning = False
            self._scanning_callback = None
            self._scan_id = 0

            self._obsfault = False
            self._obsfault_callback = None

            super().__init__(_power_mode=_power_mode, _faulty=_faulty)

        def set_obs_callbacks(
            self, configured_callback, scanning_callback, obsfault_callback
        ):
            self._configured_callback = configured_callback
            self._scanning_callback = scanning_callback
            self._obsfault_callback = obsfault_callback

        @property
        @check_on
        def configured(self):
            return self._configured

        @property
        @check_on
        def config_id(self):
            return self._config_id

        # @config_id.setter
        # @check_on
        # def config_id(self, config_id):
        #     self._config_id = config_id

        @property
        @check_on
        def scanning(self):
            return self._scanning

        @property
        @check_on
        def scan_id(self):
            return self._scan_id

        @property
        @check_on
        def obsfault(self):
            return self._obsfault

        @check_on
        def configure_scan(self, configuration):
            self._config_id = configuration["id"]
            self._update_configured(True)

        @check_on
        def deconfigure(self):
            self._config_id = ""
            self._update_configured(False)

        @check_on
        def scan(self, scan_id):
            self._scan_id = scan_id
            self._update_scanning(True)

        @check_on
        def end_scan(self):
            self.simulate_scan_stopped()

        @check_on
        def simulate_scan_stopped(self):
            self._scan_id = 0
            self._update_scanning(False)

        @check_on
        def simulate_obsfault(self, obsfault):
            self._update_obsfault(obsfault)

        def _invoke_configured_callback(self):
            if not self.faulty:
                if self._configured_callback is not None:
                    self._configured_callback(self._configured)

        def _update_configured(self, configured):
            if self._configured != configured:
                self._configured = configured
                self._invoke_configured_callback()

        def _invoke_scanning_callback(self):
            if not self.faulty:
                if self._scanning_callback is not None:
                    self._scanning_callback(self._scanning)

        def _update_scanning(self, scanning):
            if self._scanning != scanning:
                self._scanning = scanning
                self._invoke_scanning_callback()

        def _invoke_obsfault_callback(self):
            if not self.faulty:
                if self.obsfault and self._obsfault_callback is not None:
                    self._obsfault_callback()

        def _update_obsfault(self, obsfault):
            if self._obsfault != obsfault:
                self._obsfault = obsfault
                if obsfault:
                    self._invoke_obsfault_callback()

    def __init__(self, op_state_model, obs_state_model, logger=None, _component=None):
        super().__init__(
            op_state_model,
            obs_state_model,
            logger=logger,
            _component=_component or self._Component(),
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
            self.op_state_model.to_OBSFAULT()
        elif not self._component.configured:
            self.op_state_model.to_IDLE()
        elif not self._component.scanning:
            self.op_state_model.to_READY()
        else:
            self.op_state_model.to_SCANNING()

    def stop_communicating(self):
        """
        Cease monitoring the component, and break off all communication
        with it.
        """
        if not self._connected:
            return

        self._component.set_obs_callbacks(None, None, None, None)
        super().stop_communicating()

    def simulate_communication_failure(self, fail_communicate):
        """
        Simulate (or stop simulating) a failure to communicate with the
        component

        :param fail_communicate: whether the connection to the component
            is failing
        """
        # Pretend that we have either tried to connect a disconnected
        # device and failed; or realised that our connection to the
        # device has been broken
        if fail_communicate and self._connected:
            self._component.set_obs_callbacks(None, None, None, None)
        super().simulate_communication_failure(fail_communicate)

    @check_communicating
    def configure_scan(self, configuration):
        self.logger.info("Configuring component")
        self._component.configure_scan(configuration)

    @check_communicating
    def deconfigure(self):
        self.logger.info("Deconfiguring component")
        self._component.deconfigure()

    @check_communicating
    def scan(self, args):
        self.logger.info("Starting scan in component")
        self._component.scan(args)

    @check_communicating
    def end_scan(self):
        self.logger.info("Stopping scan in component")
        self._component.end_scan()

    @check_communicating
    def abort(self):
        self.logger.info("Aborting component")
        if self._component.scanning:
            self._component.end_scan()

    @check_communicating
    def obsreset(self):
        self.logger.info("Resetting component")
        if self._component.configured:
            self._component.deconfigure()

    @property
    @check_communicating
    def config_id(self):
        return self._component.config_id

    @property
    @check_on
    def scan_id(self):
        return self._component.scan_id

    @config_id.setter
    @check_communicating
    def config_id(self, config_id):
        self._component.config_id = config_id

    def component_configured(self, configured):
        if configured:
            self.obs_state_model.perform_action("component_configured")
        else:
            self.obs_state_model.perform_action("component_unconfigured")

    def component_scanning(self, scanning):
        if scanning:
            self.obs_state_model.perform_action("component_scanning")
        else:
            self.obs_state_model.perform_action("component_not_scanning")

    def component_obsfault(self):
        self.obs_state_model.perform_action("component_obsfault")
