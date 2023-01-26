"""This module models component management for CSP subelement observation devices."""
from __future__ import annotations

import logging
from threading import Event
from typing import Any, Callable, Optional, Tuple, cast

from ska_control_model import CommunicationStatus, PowerState, ResultCode, TaskStatus

from ...base import check_communicating, check_on
from ...csp.obs import CspObsComponentManager
from .reference_base_component_manager import (
    FakeBaseComponent,
    ReferenceBaseComponentManager,
)


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

    def __init__(  # pylint: disable=too-many-arguments
        self: FakeCspObsComponent,
        time_to_return: float = 0.05,
        time_to_complete: float = 0.4,
        power: PowerState = PowerState.OFF,
        fault: Optional[bool] = None,
        configured: bool = False,
        scanning: bool = False,
        obsfault: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initialise a new instance.

        :param time_to_return: the amount of time to delay before
            returning from a command method. This simulates latency in
            communication.
        :param time_to_complete: the amount of time to delay before the
            component calls a task callback to let it know that the task
            has been completed
        :param power: initial power state of this component
        :param fault: initial fault state of this component
        :param configured: initial configured state of this component
        :param scanning: initial scanning state of this component
        :param obsfault: initial obsfault state of this component
        :param kwargs: additional keyword arguments
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

    @property  # type: ignore[misc]  # mypy doesn't support decorated properties
    @check_on
    def config_id(self: FakeCspObsComponent) -> str:
        """
        Return the configuration ID.

        :return: the configuration ID.
        """
        return self._config_id

    @property  # type: ignore[misc]  # mypy doesn't support decorated properties
    @check_on
    def scan_id(self: FakeCspObsComponent) -> int:
        """
        Return the scan ID.

        :return: the scan ID.
        """
        return self._scan_id

    def configure_scan(
        self: FakeCspObsComponent,
        configuration: dict,
        task_callback: Optional[Callable],
        task_abort_event: Event,
    ) -> None:
        """
        Configure the component.

        :param configuration: the configuration to be configured
        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self.power_state != PowerState.ON:
            if task_callback is not None:
                task_callback(
                    status=TaskStatus.COMPLETED,
                    result=(
                        ResultCode.FAILED,
                        "Configure failed: component is not ON.",
                    ),
                )
            return

        self._config_id = configuration["id"]
        result = (ResultCode.OK, "Configure completed OK")
        self._simulate_task_execution(
            task_callback, task_abort_event, result, configured=True
        )

    def deconfigure(
        self: FakeCspObsComponent,
        task_callback: Optional[Callable],
        task_abort_event: Event,
    ) -> None:
        """
        Deconfigure this component.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self.power_state != PowerState.ON:
            if task_callback is not None:
                task_callback(
                    status=TaskStatus.COMPLETED,
                    result=(
                        ResultCode.FAILED,
                        "Deconfigure failed: component is not ON.",
                    ),
                )
            return

        self._config_id = ""
        result = (ResultCode.OK, "Deconfigure completed OK")
        self._simulate_task_execution(
            task_callback, task_abort_event, result, configured=False
        )

    def scan(
        self, scan_id: int, task_callback: Optional[Callable], task_abort_event: Event
    ) -> None:
        """
        Start scanning.

        :param scan_id: the unique id of the scan.
        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self.power_state != PowerState.ON:
            if task_callback is not None:
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

    def end_scan(
        self: FakeCspObsComponent,
        task_callback: Optional[Callable],
        task_abort_event: Event,
    ) -> None:
        """
        End scanning.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self.power_state != PowerState.ON:
            if task_callback is not None:
                task_callback(
                    status=TaskStatus.COMPLETED,
                    result=(
                        ResultCode.FAILED,
                        "End scan failed: component is not ON.",
                    ),
                )
            return

        self._scan_id = 0
        result = (ResultCode.OK, "End scan completed OK")
        self._simulate_task_execution(
            task_callback, task_abort_event, result, scanning=False
        )

    @check_on
    def simulate_scan_stopped(self: FakeCspObsComponent) -> None:
        """Tell the component to simulate spontaneous stopping its scan."""
        self._scan_id = 0
        self._update_state(scanning=False)

    @check_on
    def simulate_obsfault(self: FakeCspObsComponent, obsfault: bool) -> None:
        """
        Tell the component to simulate an obsfault, or the absence of one.

        :param obsfault: if true, simulate an obsfault; otherwise,
            simulate the absence of an obsfault.
        """
        self._update_state(obsfault=obsfault)

    @check_on
    def obsreset(
        self: FakeCspObsComponent,
        task_callback: Optional[Callable],
        task_abort_event: Event,
    ) -> None:
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
        self: ReferenceCspObsComponentManager,
        logger: logging.Logger,
        communication_state_callback: Callable[[CommunicationStatus], None],
        component_state_callback: Callable[..., None],
        _component: Optional[FakeCspObsComponent] = None,
    ) -> None:
        """
        Initialise a new ``ReferenceCspObsComponentManager`` instance.

        :param logger: a logger for this component manager
        :param communication_state_callback: callback for communication state
        :param component_state_callback: callback for component state
        """
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
    def configure_scan(
        self: ReferenceCspObsComponentManager,
        configuration: dict,
        task_callback: Optional[Callable] = None,
    ) -> Tuple[TaskStatus, str]:
        """
        Configure the component.

        :param configuration: the configuration to be applied
        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and human-readable status messsage
        """
        self.logger.info("Configuring component")
        return self.submit_task(
            cast(FakeCspObsComponent, self._component).configure_scan,
            (configuration,),
            task_callback=task_callback,
        )

    @check_communicating
    def deconfigure(
        self: ReferenceCspObsComponentManager,
        task_callback: Optional[Callable] = None,
    ) -> Tuple[TaskStatus, str]:
        """
        Tell the component to deconfigure.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and human-readable status messsage
        """
        self.logger.info("Deconfiguring component")
        return self.submit_task(
            cast(FakeCspObsComponent, self._component).deconfigure,
            task_callback=task_callback,
        )

    @check_communicating
    def scan(
        self: ReferenceCspObsComponentManager,
        args: Any,  # TODO: What should this type be?
        task_callback: Optional[Callable] = None,
    ) -> Tuple[TaskStatus, str]:
        """
        Tell the component to start scanning.

        :param args: arguments to the scan command
        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and human-readable status messsage
        """
        self.logger.info("Starting scan in component")
        return self.submit_task(
            cast(FakeCspObsComponent, self._component).scan,
            (args,),
            task_callback=task_callback,
        )

    @check_communicating
    def end_scan(
        self: ReferenceCspObsComponentManager, task_callback: Optional[Callable] = None
    ) -> Tuple[TaskStatus, str]:
        """
        Tell the component to stop scanning.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and human-readable status messsage
        """
        self.logger.info("Stopping scan in component")
        return self.submit_task(
            cast(FakeCspObsComponent, self._component).end_scan,
            task_callback=task_callback,
        )

    @check_communicating
    def abort(
        self: ReferenceCspObsComponentManager, task_callback: Optional[Callable] = None
    ) -> Tuple[TaskStatus, str]:
        """
        Tell the component to stop scanning.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and human-readable status messsage
        """
        self.logger.info("Aborting tasks")
        return self.abort_commands(task_callback=task_callback)

    @check_communicating
    def obsreset(
        self: ReferenceCspObsComponentManager, task_callback: Optional[Callable] = None
    ) -> Tuple[TaskStatus, str]:
        """
        Perform an obsreset on the component.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and human-readable status messsage
        """
        self.logger.info("Resetting component")
        return self.submit_task(
            cast(FakeCspObsComponent, self._component).obsreset,
            task_callback=task_callback,
        )

    @property  # type: ignore[misc]  # mypy doesn't support decorated properties
    @check_communicating
    def config_id(self: ReferenceCspObsComponentManager) -> str:
        """
        Return the configuration id.

        :return: the configuration id.
        """
        return cast(FakeCspObsComponent, self._component).config_id

    # @config_id.setter  # type: ignore[misc]
    # @check_communicating
    # def config_id(self: ReferenceCspObsComponentManager, config_id: str) -> None:
    #     cast(FakeCspObsComponent, self._component).config_id = config_id

    @property  # type: ignore[misc]  # mypy doesn't support decorated properties
    @check_on
    def scan_id(self: ReferenceCspObsComponentManager) -> int:
        """
        Return the scan id.

        :return: the scan id.
        """
        return cast(FakeCspObsComponent, self._component).scan_id
