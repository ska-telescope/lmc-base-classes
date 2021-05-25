"""
This module models component management for CSP subelement observation devices.
"""
import functools

from ska_tango_base.base import check_communicating
from ska_tango_base.csp.subarray import CspSubarrayComponentManager
from ska_tango_base.subarray import ReferenceSubarrayComponentManager
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


class ReferenceCspSubarrayComponentManager(
    CspSubarrayComponentManager,
    ReferenceSubarrayComponentManager,
):
    """
    A component manager for SKA CSP subelement observation Tango devices:

    The current implementation is intended to
    * illustrate the model
    * enable testing of the base classes

    It should not generally be used in concrete devices; instead, write
    a subclass specific to the component managed by the device.
    """

    class _Component(ReferenceSubarrayComponentManager._Component):
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
            self._config_id = ""
            self._scan_id = 0

            super().__init__(capability_types, _power_mode=_power_mode, _faulty=_faulty)

        @property
        @check_on
        def config_id(self):
            return self._config_id

        @property
        @check_on
        def scan_id(self):
            return self._scan_id

        @check_on
        def configure(self, configuration):
            self._config_id = configuration["id"]
            self._update_configured(True)

        @check_on
        def deconfigure(self):
            self._config_id = ""
            super().deconfigure()

        @check_on
        def scan(self, scan_id):
            self._scan_id = scan_id
            super().scan(scan_id)

        @check_on
        def simulate_scan_stopped(self):
            self._scan_id = 0
            super().simulate_scan_stopped()

    def __init__(
        self, op_state_model, obs_state_model, capability_types, logger, _component=None
    ):
        super().__init__(
            op_state_model,
            obs_state_model,
            capability_types,
            logger,
            _component=_component
            or self._Component(capability_types),
        )

    @property
    @check_communicating
    def config_id(self):
        return self._component.config_id

    @property
    @check_on
    def scan_id(self):
        return self._component.scan_id
