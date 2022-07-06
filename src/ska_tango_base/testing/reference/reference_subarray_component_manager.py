<<<<<<< HEAD
# pylint: skip-file  # TODO: Incrementally lint this repo
"""This module models component management for SKA subarray devices."""
from typing import List

from ska_tango_base.base import check_communicating, check_on
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import PowerState
=======
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Low MCCS project
#
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE for more info.
"""This module models component management for SKA subarray devices."""
from __future__ import annotations

import logging
import threading
from typing import Any, Callable, Optional

from ska_tango_base.base import check_communicating, check_on
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import CommunicationStatus, PowerState
from ska_tango_base.executor import TaskStatus
>>>>>>> 50f357b (MCCS-934 type hints, static type checking & standard templates)
from ska_tango_base.faults import CapabilityValidationError
from ska_tango_base.subarray import SubarrayComponentManager
from ska_tango_base.testing.reference import (
    FakeBaseComponent,
    ReferenceBaseComponentManager,
)


class FakeSubarrayComponent(FakeBaseComponent):
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

    It supports the `assign`, `release`, `release_all`, `configure`,
    `scan`, `end_scan`, `end`, `abort`, `obsreset` and `restart`
    methods. For testing purposes, it can also be told to
    simulate a spontaneous obs_state change via simulate_power_state` and
    `simulate_fault` methods.

    When one of these command method is invoked, the component simulates
    communications latency by sleeping for a short time. It then
    returns, but simulates any asynchronous work it needs to do by
    delaying updating task and component state for a short time.
    """

    class _ResourcePool:
        """A simple class for managing subarray resources."""

        def __init__(self: FakeSubarrayComponent._ResourcePool) -> None:
            """Initialise a new instance."""
            self._resources: set = set()

        def __len__(self: FakeSubarrayComponent._ResourcePool) -> int:
            """
            Return the number of resources currently assigned.

            Note that this also functions as a boolean method for
            whether there are any assigned resources: ``if len()``.

            :return: number of resources assigned
            """
            return len(self._resources)

        def assign(
            self: FakeSubarrayComponent._ResourcePool, resources: set[str]
        ) -> None:
            """
            Assign some resources.

            :param resources: resources to be assigned
            """
            self._resources |= set(resources)

        def release(
            self: FakeSubarrayComponent._ResourcePool, resources: set[str]
        ) -> None:
            """
            Release some resources.

            :param resources: resources to be released
            """
            self._resources -= set(resources)

        def release_all(self: FakeSubarrayComponent._ResourcePool) -> None:
            """Release all resources."""
            self._resources.clear()

        def get(self: FakeSubarrayComponent._ResourcePool) -> set[str]:
            """
            Get current resources.

            :return: current resources.
            """
            return set(self._resources)

        def check(
            self: FakeSubarrayComponent._ResourcePool, resources: set[str]
        ) -> bool:
            """
            Check that this pool contains specified resources.

            This is useful for commands like configure(), which might
            need to check that the subarray has the resources needed to
            effect a configuration.

            :param resources: resources to be checked

            :return: whether this resource pool contains the specified
                resources
            """
            return resources in self._resources

    def __init__(
        self: FakeSubarrayComponent,
        capability_types: list[str],
        time_to_return: float = 0.05,
        time_to_complete: float = 0.4,
        power: PowerState = PowerState.OFF,
        fault: Optional[bool] = None,
        resourced: bool = False,
        configured: bool = False,
        scanning: bool = False,
        obsfault: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initialise a new instance.

        :param capability_types: a list strings representing
            capability types.
        :param time_to_return: time
        :param time_to_complete: time
        :param power: power state
        :param fault: is in fault
        :param resourced: is resourced
        :param configured: is configured
        :param scanning: is scanning
        :param obsfault: is obs in fault
        :param kwargs: additional arguments
        """
        self._resource_pool = self._ResourcePool()

        # self._configured_capabilities is kept as a
        # dictionary internally. The keys and values will represent
        # the capability type name and the number of instances,
        # respectively.
        try:
            self._configured_capabilities = dict.fromkeys(capability_types, 0)
        except TypeError:
            # Might need to have the device property be mandatory in the database.
            self._configured_capabilities = {}

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

    @property  # type: ignore[misc]
    @check_on
<<<<<<< HEAD
    def configured_capabilities(self) -> List[str]:
=======
    def configured_capabilities(self: FakeSubarrayComponent) -> list[str]:
>>>>>>> 7ddac93 (MCCS-934 type hints, static type checking & standard templates)
        """
        Return the configured capabilities of this component.

        :return: list of strings indicating number of configured
            instances of each capability type
        """
        configured_capabilities = []
        for capability_type, capability_instances in list(
            self._configured_capabilities.items()
        ):
            configured_capabilities.append(f"{capability_type}:{capability_instances}")
        return sorted(configured_capabilities)

    def _validate_capability_types(
        self: FakeSubarrayComponent, capability_types: list[str]
    ) -> None:
        """
        Check the validity of the input parameter passed to the Configure command.

        :param capability_types: a list strings representing
            capability types.

        :raises CapabilityValidationError: If any of the capabilities
            requested are not valid.
        """
        invalid_capabilities = list(
            set(capability_types) - set(self._configured_capabilities)
        )

        if invalid_capabilities:
            raise CapabilityValidationError(
<<<<<<< HEAD
                "Invalid capability types requested {}".format(
                    invalid_capabilities
                )
=======
                f"Invalid capability types requested {invalid_capabilities}"
>>>>>>> 50f357b (MCCS-934 type hints, static type checking & standard templates)
            )

    @check_on
    def assign(
        self: FakeSubarrayComponent,
        resources: set[str],
        task_callback: Optional[Callable[[], None]],
        task_abort_event: threading.Event,
    ) -> None:
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
            self._resource_pool.assign(resources)
            result = (ResultCode.OK, "Resource assignment completed OK")

        self._simulate_task_execution(
            task_callback,
            task_abort_event,
            result,
            resourced=bool(len(self._resource_pool)),
        )

    @check_on
    def release(
        self: FakeSubarrayComponent,
        resources: set[str],
        task_callback: Optional[Callable[[], None]],
        task_abort_event: threading.Event,
    ) -> None:
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
            self._resource_pool.release(resources)
            result = (ResultCode.OK, "Resource release completed OK")

        self._simulate_task_execution(
            task_callback,
            task_abort_event,
            result,
            resourced=bool(len(self._resource_pool)),
        )

    @check_on
    def release_all(
        self: FakeSubarrayComponent,
        task_callback: Optional[Callable[[], None]],
        task_abort_event: threading.Event,
    ) -> None:
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
            self._resource_pool.release_all()
            result = (ResultCode.OK, "Resource release completed OK")

        self._simulate_task_execution(
            task_callback, task_abort_event, result, resourced=False
        )

    @check_on
    def configure(
        self: FakeSubarrayComponent,
        configuration: dict,
        task_callback: Optional[Callable[[], None]],
        task_abort_event: threading.Event,
    ) -> None:
        """
        Configure the component.

        :param configuration: the configuration to be configured
        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        # # In this example implementation, the keys of the dict
        # # are the capability types, and the values are the
        # # integer number of instances required.
        # # E.g., config = {"BAND1": 5, "BAND2": 3}
        if self._state["fault"]:
            result = (
                ResultCode.FAILED,
                "Configure failed; component is in fault.",
            )
        else:
            capability_types = list(configuration.keys())
            self._validate_capability_types(capability_types)

            # Perform the configuration.
            for capability_type, capability_instances in configuration.items():
                self._configured_capabilities[
                    capability_type
                ] += capability_instances

            result = (ResultCode.OK, "Configure completed OK")

        self._simulate_task_execution(
            task_callback, task_abort_event, result, configured=True
        )

    @check_on
    def deconfigure(
        self: FakeSubarrayComponent,
        task_callback: Optional[Callable[[], None]],
        task_abort_event: threading.Event,
    ) -> None:
        """
        Deconfigure this component.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self._state["fault"]:
            result = (
                ResultCode.FAILED,
                "Deconfigure failed; component is in fault.",
            )
        else:
            self._configured_capabilities = {
                k: 0 for k in self._configured_capabilities
            }
            result = (ResultCode.OK, "Deconfigure completed OK")
        self._simulate_task_execution(
            task_callback, task_abort_event, result, configured=False
        )

    @check_on
    def scan(
        self: FakeSubarrayComponent,
        args: Any,
        task_callback: Optional[Callable[[], None]],
        task_abort_event: threading.Event,
    ) -> None:
        """
        Start scanning.

        :param args: additional arguments
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
            result = (ResultCode.OK, "Scan commencement completed OK")
        self._simulate_task_execution(
            task_callback, task_abort_event, result, scanning=True
        )

    @check_on
    def end_scan(
        self: FakeSubarrayComponent,
        task_callback: Optional[Callable[[], None]],
        task_abort_event: threading.Event,
    ) -> None:
        """
        End scanning.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        if self._state["fault"]:
            result = (
                ResultCode.FAILED,
                "End scan failed; component is in fault.",
            )
        else:
            result = (ResultCode.OK, "End scan completed OK")
        self._simulate_task_execution(
            task_callback, task_abort_event, result, scanning=False
        )

    @check_on
    def simulate_scan_stopped(self: FakeSubarrayComponent) -> None:
        """Tell the component to simulate spontaneous stopping its scan."""
        self._update_state(scanning=False)

    @check_on
    def simulate_obsfault(self: FakeSubarrayComponent, obsfault: bool) -> None:
        """
        Tell the component to simulate an obsfault.

        :param obsfault: fault indicator
        """
        self._update_state(obsfault=obsfault)

    @check_on
    def obsreset(
        self: FakeSubarrayComponent,
        task_callback: Optional[Callable[[], None]],
        task_abort_event: threading.Event,
    ) -> None:
        """
        Reset an observation that has faulted or been aborted.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        self._configured_capabilities = {
            k: 0 for k in self._configured_capabilities
        }
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
    def restart(
        self: FakeSubarrayComponent,
        task_callback: Optional[Callable[[], None]],
        task_abort_event: threading.Event,
    ) -> None:
        """
        Restart the component after it has faulted or been aborted.

        :param task_callback: a callback to be called whenever the
            status of this task changes.
        :param task_abort_event: a threading.Event that can be checked
            for whether this task has been aborted.
        """
        self._configured_capabilities = {
            k: 0 for k in self._configured_capabilities
        }
        self._resource_pool.release_all()
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


class ReferenceSubarrayComponentManager(
    ReferenceBaseComponentManager, SubarrayComponentManager
):
    """
    A component manager for SKA subarray Tango devices.

    The current implementation is intended to
    * illustrate the model
    * enable testing of the base classes

    It should not generally be used in concrete devices; instead, write
    a subclass specific to the component managed by the device.
    """

    def __init__(
        self: ReferenceSubarrayComponentManager,
        capability_types: list[str],
        logger: logging.Logger,
        communication_state_callback: Optional[
            Callable[[CommunicationStatus], None]
        ] = None,
        component_state_callback: Optional[Callable[[], None]] = None,
        _component: Optional[object] = None,
    ):
        """
        Initialise a new ReferenceSubarrayComponentManager instance.

        :param capability_types: types of capabiltiy supported by this
            subarray
        :param logger: the logger for this component manager to log with
        :param communication_state_callback: callback to be called when
            the state of communications with the component changes
        :param component_state_callback: callback to be called when the
            state of the component changes
        :param _component: an object to use as the component of this
            component manager; for testing purposes only.
        """
        super().__init__(
            logger,
            communication_state_callback,
            component_state_callback,
            _component=_component or FakeSubarrayComponent(capability_types),
            resourced=False,
            configured=False,
            scanning=False,
            obsfault=False,
        )

    @check_communicating
    def assign(
        self: ReferenceSubarrayComponentManager,
        resources: set[str],
        task_callback: Optional[Callable[[], None]] = None,
    ) -> tuple[TaskStatus, str]:
        """
        Assign resources to the component.

        :param resources: resources to be assigned
        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and message
        """
        return self.submit_task(
            self._component.assign, (resources,), task_callback=task_callback
        )

    @check_communicating
    def release(
        self: ReferenceSubarrayComponentManager,
        resources: set[str],
        task_callback: Optional[Callable[[], None]] = None,
    ) -> tuple[TaskStatus, str]:
        """
        Release resources from the component.

        :param resources: resources to be released
        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and message
        """
        return self.submit_task(
            self._component.release, (resources,), task_callback=task_callback
        )

    @check_communicating
    def release_all(
        self: ReferenceSubarrayComponentManager,
        task_callback: Optional[Callable[[], None]] = None,
    ) -> tuple[TaskStatus, str]:
        """
        Release all resources.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and message
        """
        return self.submit_task(
            self._component.release_all, task_callback=task_callback
        )

    @check_communicating
    def configure(
        self: ReferenceSubarrayComponentManager,
        configuration: dict[str, Any],
        task_callback: Optional[Callable[[], None]] = None,
    ) -> tuple[TaskStatus, str]:
        """
        Configure the component.

        :param configuration: the configuration to be configured
        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and message
        """
        return self.submit_task(
            self._component.configure,
            (configuration,),
            task_callback=task_callback,
        )

    @check_communicating
    def deconfigure(
        self: ReferenceSubarrayComponentManager,
        task_callback: Optional[Callable[[], None]] = None,
    ) -> tuple[TaskStatus, str]:
        """
        Deconfigure this component.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and message
        """
        return self.submit_task(
            self._component.deconfigure, task_callback=task_callback
        )

    @check_communicating
    def scan(
        self: ReferenceSubarrayComponentManager,
        args: Any,
        task_callback: Optional[Callable[[], None]] = None,
    ) -> tuple[TaskStatus, str]:
        """
        Start scanning.

        :param args: additional arguments
        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and message
        """
        return self.submit_task(
            self._component.scan, (args,), task_callback=task_callback
        )

    @check_communicating
<<<<<<< HEAD
    def end_scan(self, task_callback=None):
        """End scanning."""
        return self.submit_task(
            self._component.end_scan, task_callback=task_callback
        )
=======
    def end_scan(
        self: ReferenceSubarrayComponentManager,
        task_callback: Optional[Callable[[], None]] = None,
    ) -> tuple[TaskStatus, str]:
        """
        End scanning.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and message
        """
        return self.submit_task(self._component.end_scan, task_callback=task_callback)
>>>>>>> 50f357b (MCCS-934 type hints, static type checking & standard templates)

    @check_communicating
    def abort(
        self: ReferenceSubarrayComponentManager,
        task_callback: Optional[Callable[[], None]] = None,
    ) -> tuple[TaskStatus, str]:
        """
        Tell the component to abort the observation.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and message
        """
        print("£££££££££££££££££££££££££££££££££", self.abort_tasks)
        return self.abort_tasks()

    @check_communicating
<<<<<<< HEAD
    def obsreset(self, task_callback=None):
        """Deconfigure the component but do not release resources."""
        return self.submit_task(
            self._component.obsreset, task_callback=task_callback
        )
=======
    def obsreset(
        self: ReferenceSubarrayComponentManager,
        task_callback: Optional[Callable[[], None]] = None,
    ) -> tuple[TaskStatus, str]:
        """
        Deconfigure the component but do not release resources.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and message
        """
        return self.submit_task(self._component.obsreset, task_callback=task_callback)
>>>>>>> 50f357b (MCCS-934 type hints, static type checking & standard templates)

    @check_communicating
    def restart(
        self: ReferenceSubarrayComponentManager,
        task_callback: Optional[Callable[[], None]] = None,
    ) -> tuple[TaskStatus, str]:
        """
        Tell the component to restart.

        It will return to a state in which it is unconfigured and empty
        of assigned resources.

        :param task_callback: a callback to be called whenever the
            status of this task changes.

        :return: task status and message
        """
        return self.submit_task(
            self._component.restart, task_callback=task_callback
        )

    @property  # type: ignore[misc]
    @check_communicating
<<<<<<< HEAD
    def assigned_resources(self) -> List[str]:
=======
    def assigned_resources(self: ReferenceSubarrayComponentManager) -> list[str]:
>>>>>>> 7ddac93 (MCCS-934 type hints, static type checking & standard templates)
        """
        Return the resources assigned to the component.

        :return: the resources assigned to the component
        """
        return sorted(self._component._resource_pool.get())

    @property  # type: ignore[misc]
    @check_communicating
<<<<<<< HEAD
    def configured_capabilities(self) -> List[str]:
=======
    def configured_capabilities(self: ReferenceSubarrayComponentManager) -> list[str]:
>>>>>>> 7ddac93 (MCCS-934 type hints, static type checking & standard templates)
        """
        Return the configured capabilities of the component.

        :return: list of strings indicating number of configured
            instances of each capability type
        """
        return self._component.configured_capabilities
