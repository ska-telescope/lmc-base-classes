"""This module models component management for CSP subelement observation devices."""
from ska_tango_base.base import (
    check_communicating,
    check_on,
    TaskExecutorComponentManager,
)
from ska_tango_base.testing import FakeBaseComponent
from ska_tango_base.csp.subarray import CspSubarrayComponentManager

from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import CommunicationStatus, PowerState


class FakeCspSubarrayComponent(FakeBaseComponent):
    """
    A fake component for the component manager to work with.

    NOTE: There is usually no need to implement a component object.
    The "component" is an element of the external system under
    control, such as a piece of hardware or an external service. In the
    case of a subarray device, the "component" is likely a collection of
    Tango devices responsible for monitoring and controlling the
    various resources assigned to the subarray. The component manager
    should be written so that it interacts with those Tango devices. But
    here, we fake up a "component" object to interact with instead.

    It supports the configure`, `scan`, `end_scan`, `end`, `abort`,
    `obsreset` and `restart` methods. For testing purposes, it can also
    be told to simulate a spontaneous state change via
    `simulate_power_state` and `simulate_fault` methods.

    When one of these command methods is invoked, the component
    simulates communications latency by sleeping for a short time. It
    then returns, but simulates any asynchronous work it needs to do by
    delaying updating task and component state for a short time.
    """

    def __init__(
        self,
        time_to_return=0.05,
        time_to_complete=0.1,
        power=PowerState.OFF,
        fault=False,
        resourced=False,
        configured=False,
        scanning=False,
        obsfault=False,
        **kwargs,
    ):
        """
        Initialise a new instance.

        :param capability_types: a list strings representing
            capability types.
        :param _power_mode: initial power mode of this component
            (for testing only)
        :param _faulty: whether this component should initially
            simulate a fault (for testing only)
        """
        self._config_id = ""
        self._scan_id = 0

        super().__init__(
            time_to_return=time_to_return,
            time_to_complete=time_to_complete,
            power=power,
            fault=fault,
            resourced=resourced,
            configured=configured,
            scanning=scanning,
            obsfault=obsfault,
            **kwargs,
        )

    @property
    @check_on
    def config_id(self):
        """
        Return the unique id of this configuration.

        :return: a unique id
        """
        return self._config_id

    @property
    @check_on
    def scan_id(self):
        """
        Return the unique id of this scan.

        :return: a unique id
        """
        return self._scan_id

    @check_on
    def assign(self, resources, task_callback, task_abort_event):
        """
        Assign resources.

        :param resources: the resources to be assigned.
        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self._state["fault"]:
            result = (
                ResultCode.FAILED,
                "Resource assignment failed; component is in fault.",
            )
        else:
            result = (ResultCode.OK, "Resource assignment completed OK")

        self._simulate_task_execution(
            task_callback,
            task_abort_event,
            result,
            resourced=True,
        )

    @check_on
    def release(self, resources, task_callback, task_abort_event):
        """
        Release resources.

        :param resources: resources to be released
        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self._state["fault"]:
            result = (
                ResultCode.FAILED,
                "Resource release failed; component is in fault.",
            )
        else:
            result = (ResultCode.OK, "Resource release completed OK")

        self._simulate_task_execution(
            task_callback,
            task_abort_event,
            result,
            resourced=True,
        )

    @check_on
    def release_all(self, task_callback, task_abort_event):
        """
        Release all resources.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self._state["fault"]:
            result = (
                ResultCode.FAILED,
                "Resource release failed; component is in fault.",
            )
        else:
            result = (ResultCode.OK, "Resource release completed OK")

        self._simulate_task_execution(
            task_callback, task_abort_event, result, resourced=False
        )

    @check_on
    def configure(self, configuration, task_callback, task_abort_event):
        """
        Configure the component.

        :param configuration: the configuration to be configured
        :type configuration: dict
        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self._state["fault"]:
            result = (ResultCode.FAILED, "Configure failed; component is in fault.")
        else:
            self._config_id = configuration["id"]
            result = (ResultCode.OK, "Configure completed OK")

        self._simulate_task_execution(
            task_callback, task_abort_event, result, configured=True
        )

    @check_on
    def deconfigure(self, task_callback, task_abort_event):
        """
        Deconfigure this component.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self._state["fault"]:
            result = (ResultCode.FAILED, "Deconfigure failed; component is in fault.")
        else:
            self._config_id = ""
            result = (ResultCode.OK, "Deconfigure completed OK")
        self._simulate_task_execution(
            task_callback, task_abort_event, result, configured=False
        )

    @check_on
    def scan(self, scan_id, task_callback, task_abort_event):
        """
        Start scanning.

        :param scan_id: unique ID of this scan
        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self._state["fault"]:
            result = (
                ResultCode.FAILED,
                "Scan commencement failed; component is in fault.",
            )
        else:
            self._scan_id = scan_id
            result = (ResultCode.OK, "Scan commencement completed OK")
        self._simulate_task_execution(
            task_callback, task_abort_event, result, scanning=True
        )

    @check_on
    def end_scan(self, task_callback, task_abort_event):
        """
        End scanning.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self._state["fault"]:
            result = (ResultCode.FAILED, "End scan failed; component is in fault.")
        else:
            self._scan_id = 0
            result = (ResultCode.OK, "End scan completed OK")
        self._simulate_task_execution(
            task_callback, task_abort_event, result, scanning=False
        )

    @check_on
    def simulate_scan_stopped(self):
        """Tell the component to simulate spontaneous stopping its scan."""
        self._update_state(scanning=False)

    @check_on
    def simulate_obsfault(self, obsfault):
        """
        Tell the component to simulate (or stop simulating) an obsfault.

        :param obsfault: whether an obsfault has occurred
        """
        self._update_state(obsfault=obsfault)

    @check_on
    def obsreset(self, task_callback, task_abort_event):
        """
        Reset an observation that has faulted or been aborted.

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

    @check_on
    def restart(self, task_callback, task_abort_event):
        """
        Restart the component after it has faulted or been aborted.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        self._scan_id = 0
        self._config_id = ""
        result = (ResultCode.OK, "Restart completed OK")
        self._simulate_task_execution(
            task_callback,
            task_abort_event,
            result,
            obsfault=False,
            scanning=False,
            configured=False,
            resourced=False,
        )


class ReferenceCspSubarrayComponentManager(
    TaskExecutorComponentManager,
    CspSubarrayComponentManager,
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
        """
        Initialise a new ReferenceCspSubarrayComponentManager instance.

        :param logger: the logger for this component manager to log with
        :param communication_state_callback: callback to be called when
            the state of communications with the component changes
        :param component_state_callback: callback to be called when the
            state of the component changes
        """
        self._fail_communicate = False

        self._component = _component or FakeCspSubarrayComponent()

        super().__init__(
            logger,
            communication_state_callback,
            component_state_callback,
            power=PowerState.UNKNOWN,
            fault=False,
            resourced=False,
            configured=False,
            scanning=False,
            obsfault=False,
        )

    def start_communicating(self):
        """Establish communication with the component, then start monitoring."""
        if self.communication_state == CommunicationStatus.ESTABLISHED:
            return
        if self.communication_state == CommunicationStatus.DISABLED:
            self._update_communication_state(CommunicationStatus.NOT_ESTABLISHED)

        # The component would normally be an element of the system under control. In
        # order to establish communication with it, we might need, for example, to
        # establishing a network connection to the component, then start a polling loop
        # to continually poll over that connection.
        # But here, we're faking the component with an object, so all we need to do is
        # register some callbacks.
        # And in order to fake communications failure, we just return without
        # registering them.
        if self._fail_communicate:
            return

        self._update_communication_state(CommunicationStatus.ESTABLISHED)
        self._component.set_state_change_callback(self._update_component_state)

    def stop_communicating(self):
        """Break off communication with the component."""
        if self.communication_state == CommunicationStatus.DISABLED:
            return

        self._component.set_state_change_callback(None)
        self._update_component_state(power=PowerState.UNKNOWN, fault=None)
        self._update_communication_state(CommunicationStatus.DISABLED)

    def simulate_communication_failure(self, fail_communicate):
        """
        Simulate (or stop simulating) a failure to communicate with the component.

        :param fail_communicate: whether the connection to the component
            is failing
        """
        self._fail_communicate = fail_communicate
        if (
            fail_communicate
            and self.communication_state == CommunicationStatus.ESTABLISHED
        ):
            self._component.set_state_change_callback(None)
            self._update_communication_state(CommunicationStatus.NOT_ESTABLISHED)
        elif (
            not fail_communicate
            and self.communication_state == CommunicationStatus.NOT_ESTABLISHED
        ):
            self._update_communication_state(CommunicationStatus.ESTABLISHED)
            self._component.set_state_change_callback(self._update_component_state)

    @property
    def power_state(self):
        """
        Power mode of the component.

        This is just a bit of syntactic sugar for
        `self.component_state["power"]`.

        :return: the power mode of the component
        """
        return self._component_state["power"]

    @property
    def fault_state(self):
        """
        Whether the component is currently faulting.

        :return: whether the component is faulting
        """
        return self._component_state["fault"]

    @check_communicating
    def off(self, task_callback=None):
        """Turn the component off."""
        return self.submit_task(self._component.off, task_callback=task_callback)

    @check_communicating
    def standby(self, task_callback=None):
        """Put the component into low-power standby mode."""
        return self.submit_task(self._component.standby, task_callback=task_callback)

    @check_communicating
    def on(self, task_callback=None):
        """Turn the component on."""
        return self.submit_task(self._component.on, task_callback=task_callback)

    @check_communicating
    def reset(self, task_callback=None):
        """Reset the component (from fault state)."""
        return self.submit_task(self._component.reset, task_callback=task_callback)

    @check_communicating
    def assign(self, resources, task_callback=None):
        """
        Assign resources to the component.

        :param resources: resources to be assigned
        :type resources: list(str)
        """
        return self.submit_task(
            self._component.assign, (resources,), task_callback=task_callback
        )

    @check_communicating
    def release(self, resources, task_callback=None):
        """
        Release resources from the component.

        :param resources: resources to be released
        :type resources: list(str)
        """
        return self.submit_task(
            self._component.release, (resources,), task_callback=task_callback
        )

    @check_communicating
    def release_all(self, task_callback=None):
        """Release all resources."""
        return self.submit_task(
            self._component.release_all, task_callback=task_callback
        )

    @check_communicating
    def configure(self, configuration, task_callback=None):
        """
        Configure the component.

        :param configuration: the configuration to be configured
        :type configuration: dict
        """
        return self.submit_task(
            self._component.configure, (configuration,), task_callback=task_callback
        )

    @check_communicating
    def deconfigure(self, task_callback=None):
        """Deconfigure this component."""
        return self.submit_task(
            self._component.deconfigure, task_callback=task_callback
        )

    @check_communicating
    def scan(self, args, task_callback=None):
        """Start scanning."""
        return self.submit_task(
            self._component.scan, (args,), task_callback=task_callback
        )

    @check_communicating
    def end_scan(self, task_callback=None):
        """End scanning."""
        return self.submit_task(self._component.end_scan, task_callback=task_callback)

    @check_communicating
    def obsreset(self, task_callback=None):
        """Deconfigure the component but do not release resources."""
        return self.submit_task(self._component.obsreset, task_callback=task_callback)

    @check_communicating
    def restart(self, task_callback=None):
        """
        Tell the component to restart.

        It will return to a state in which it is unconfigured and empty
        of assigned resources.
        """
        return self.submit_task(self._component.restart, task_callback=task_callback)

    @property
    @check_communicating
    def config_id(self):
        """Return the configuration id."""
        return self._component.config_id

    @property
    @check_on
    def scan_id(self):
        """Return the scan id."""
        return self._component.scan_id
