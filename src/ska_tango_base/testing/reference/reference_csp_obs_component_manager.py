"""This module models component management for CSP subelement observation devices."""
from ska_tango_base.csp.obs import CspObsComponentManager
from ska_tango_base.base import check_communicating, check_on
from ska_tango_base.testing.reference import (
    FakeBaseComponent,
    ReferenceBaseComponentManager,
)

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import PowerState
from ska_tango_base.executor import TaskStatus


class FakeCspObsComponent(FakeBaseComponent):
    """
    An example CSP subelement obs component for the component manager to work with.

    NOTE: There is usually no need to implement a component object.
    The "component" is an element of the external system under
    control, such as a piece of hardware or an external service. In the
    case of a subarray device, the "component" is likely a collection of
    Tango devices responsible for monitoring and controlling the
    various resources assigned to the subarray. The component manager
    should be written so that it interacts with those Tango devices. But
    here, we fake up a "component" object to interact with instead.

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
        time_to_return=0.05,
        time_to_complete=0.1,
        power=PowerState.OFF,
        fault=False,
        configured=False,
        scanning=False,
        obsfault=False,
        **kwargs,
    ):
        """
        Initialise a new instance.

        :param _power_mode: initial power mode of this component
            (for testing only)
        :param _faulty: whether this component should initially
            simulate a fault (for testing only)
        """
        self._scan_id = 0
        self._config_id = ""

        super().__init__(
            time_to_return=time_to_return,
            time_to_complete=time_to_complete,
            power=power,
            fault=fault,
            configured=configured,
            scanning=scanning,
            obsfault=obsfault,
            **kwargs,
        )

    @property
    @check_on
    def config_id(self):
        """Return the configuration id."""
        return self._config_id

    @property
    @check_on
    def scan_id(self):
        """Return the scan id."""
        return self._scan_id

    def configure_scan(self, configuration, task_callback, task_abort_event):
        """
        Configure the component.

        :param configuration: the configuration to be configured
        :type configuration: dict
        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self.power_state != PowerState.ON:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=(ResultCode.FAILED, "Configure failed: component is not ON."),
            )
            return

        self._config_id = configuration["id"]
        result = (ResultCode.OK, "Configure completed OK")
        self._simulate_task_execution(
            task_callback, task_abort_event, result, configured=True
        )

    def deconfigure(self, task_callback, task_abort_event):
        """
        Deconfigure this component.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self.power_state != PowerState.ON:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=(ResultCode.FAILED, "Deconfigure failed: component is not ON."),
            )
            return

        self._config_id = ""
        result = (ResultCode.OK, "Deconfigure completed OK")
        self._simulate_task_execution(
            task_callback, task_abort_event, result, configured=False
        )

    def scan(self, scan_id, task_callback, task_abort_event):
        """
        Start scanning.

        :param scan_id: the unique id of the scan.
        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self.power_state != PowerState.ON:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=(
                    ResultCode.FAILED,
                    "Scan commencement failed: component is not ON.",
                ),
            )
            return

        self._scan_id = scan_id
        result = (ResultCode.OK, "Scan commencement completed OK")
        self._simulate_task_execution(
            task_callback, task_abort_event, result, scanning=True
        )

    def end_scan(self, task_callback, task_abort_event):
        """
        End scanning.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self.power_state != PowerState.ON:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=(ResultCode.FAILED, "End scan failed: component is not ON."),
            )
            return

        self._scan_id = 0
        result = (ResultCode.OK, "End scan completed OK")
        self._simulate_task_execution(
            task_callback, task_abort_event, result, scanning=False
        )

    @check_on
    def simulate_scan_stopped(self):
        """Tell the component to simulate spontaneous stopping its scan."""
        self._scan_id = 0
        self._update_state(scanning=False)

    @check_on
    def simulate_obsfault(self, obsfault):
        """Tell the component to simulate an obsfault."""
        self._update_state(obsfault=obsfault)

    @check_on
    def obsreset(self, task_callback, task_abort_event):
        """
        Reset the observation after it has faulted or been aborted.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        self._scan_id = 0
        self._config_id = ""
        result = (ResultCode.OK, "Obs reset completed OK")
        self._simulate_task_execution(
            task_callback,
            task_abort_event,
            result,
            obsfault=False,
            scanning=False,
            configured=False,
        )


class ReferenceCspObsComponentManager(
    ReferenceBaseComponentManager,
    CspObsComponentManager,
):
    """
    A component manager for SKA CSP subelement observation Tango devices.

    The current implementation is intended to
    * illustrate the model
    * enable testing of the base classes

    It should not generally be used in concrete devices; instead, write
    a subclass specific to the component managed by the device.
    """

    def __init__(
        self,
        logger,
        communication_state_callback,
        component_state_callback,
        _component=None,
    ):
        """Initialise a new ``ReferenceCspObsComponentManager`` instance."""
        # self._fail_communicate = False

        super().__init__(
            logger,
            communication_state_callback,
            component_state_callback,
            _component=_component or FakeCspObsComponent(),
            configured=False,
            scanning=False,
            obsfault=False,
        )

    @check_communicating
    @check_on
    def configure_scan(self, configuration, task_callback=None):
        """Configure the component."""
        self.logger.info("Configuring component")
        return self.submit_task(
            self._component.configure_scan,
            (configuration,),
            task_callback=task_callback,
        )

    @check_communicating
    def deconfigure(self, task_callback=None):
        """Tell the component to deconfigure."""
        self.logger.info("Deconfiguring component")
        return self.submit_task(
            self._component.deconfigure, task_callback=task_callback
        )

    @check_communicating
    def scan(self, args, task_callback=None):
        """Tell the component to start scanning."""
        self.logger.info("Starting scan in component")
        return self.submit_task(
            self._component.scan, (args,), task_callback=task_callback
        )

    @check_communicating
    def end_scan(self, task_callback=None):
        """Tell the component to stop scanning."""
        self.logger.info("Stopping scan in component")
        return self.submit_task(self._component.end_scan, task_callback=task_callback)

    @check_communicating
    def abort(self, task_callback=None):
        """Tell the component to stop scanning."""
        self.logger.info("Aborting tasks")
        return self.abort_tasks(task_callback=task_callback)

    @check_communicating
    def obsreset(self, task_callback=None):
        """Perform an obsreset on the component."""
        self.logger.info("Resetting component")
        return self.submit_task(self._component.obsreset, task_callback=task_callback)

    @property
    @check_communicating
    def config_id(self):
        """Return the configuration id."""
        return self._component.config_id

    @config_id.setter
    @check_communicating
    def config_id(self, config_id):
        self._component.config_id = config_id

    @property
    @check_on
    def scan_id(self):
        """Return the scan id."""
        return self._component.scan_id
