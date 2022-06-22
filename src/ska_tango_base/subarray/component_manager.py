# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module provides an abstract component manager for SKA Tango subarray devices."""
from __future__ import annotations

from typing import Any, Callable, Optional

from ska_tango_base.base import BaseComponentManager
from ska_tango_base.executor import TaskStatus


class SubarrayComponentManager(BaseComponentManager):
    """
    An abstract base class for a component manager for an SKA subarray Tango devices.

    It supports:

    * Maintaining a connection to its component

    * Controlling its component via commands like AssignResources(),
      Configure(), Scan(), etc.

    * Monitoring its component, e.g. detect that a scan has completed
    """

    def assign(
        self: SubarrayComponentManager,
        resources: set[str],
        task_callback: Optional[Callable[[], None]] = None,
    ) -> tuple[TaskStatus, str]:
        """
        Assign resources to the component.

        :param resources: resources to be assigned
        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: This is an abstract class
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def release(
        self: SubarrayComponentManager,
        resources: set[str],
        task_callback: Optional[Callable[[], None]],
    ) -> tuple[TaskStatus, str]:
        """
        Release resources from the component.

        :param resources: resources to be released
        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: This is an abstract class
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def release_all(
        self: SubarrayComponentManager, task_callback: Optional[Callable]
    ) -> tuple[TaskStatus, str]:
        """
        Release all resources.

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: This is an abstract class
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def configure(
        self, configuration: dict[str, Any], task_callback: Optional[Callable[[], None]]
    ) -> tuple[TaskStatus, str]:
        """
        Configure the component.

        :param configuration: the configuration to be configured
        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: This is an abstract class
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def deconfigure(
        self: SubarrayComponentManager, task_callback: Optional[Callable]
    ) -> tuple[TaskStatus, str]:
        """
        Deconfigure this component.

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: This is an abstract class
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def scan(
        self: SubarrayComponentManager, args: str, task_callback: Optional[Callable]
    ) -> tuple[TaskStatus, str]:
        """
        Start scanning.

        :param args: scan parameters encoded in a json string
        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: This is an abstract class
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def end_scan(
        self: SubarrayComponentManager, task_callback: Optional[Callable]
    ) -> tuple[TaskStatus, str]:
        """
        End scanning.

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: This is an abstract class
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def abort(
        self: SubarrayComponentManager, task_callback: Optional[Callable]
    ) -> tuple[TaskStatus, str]:
        """
        Tell the component to abort whatever it was doing.

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: This is an abstract class
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def obsreset(
        self: SubarrayComponentManager, task_callback: Optional[Callable]
    ) -> tuple[TaskStatus, str]:
        """
        Reset the component to unconfigured but do not release resources.

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: This is an abstract class
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    def restart(
        self: SubarrayComponentManager, task_callback: Optional[Callable]
    ) -> tuple[TaskStatus, str]:
        """
        Deconfigure and release all resources.

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: This is an abstract class
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    @property
    def assigned_resources(self):
        """
        Return the resources assigned to the component.

        :return: list of strings indicating the resources assigned to the component
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")

    @property
    def configured_capabilities(self):
        """
        Return the configured capabilities of the component.

        :return: list of strings indicating number of configured
            instances of each capability type
        """
        raise NotImplementedError("SubarrayComponentManager is abstract.")
