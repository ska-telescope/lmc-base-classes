"""This module models component management for CSP subelement observation devices."""
from typing import Callable, Optional, Tuple

from ska_control_model import TaskStatus

from ...base import BaseComponentManager


class CspObsComponentManager(BaseComponentManager):
    """A component manager for SKA CSP subelement observation Tango devices."""

    def configure_scan(
        self,
        configuration: dict,
        task_callback: Optional[Callable] = None,
    ) -> Tuple[TaskStatus, str]:
        """
        Configure the component.

        :param configuration: the configuration to be configured
        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: because this method has not been
            implemented
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def deconfigure(
        self,
        task_callback: Optional[Callable] = None,
    ) -> Tuple[TaskStatus, str]:
        """
        Deconfigure this component.

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: because this method has not been
            implemented
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def scan(
        self,
        args: str,
        task_callback: Optional[Callable] = None,
    ) -> Tuple[TaskStatus, str]:
        """
        Start scanning.

        :param args: argument to the scan command
        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: because this method has not been
            implemented
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def end_scan(
        self,
        task_callback: Optional[Callable] = None,
    ) -> Tuple[TaskStatus, str]:
        """
        End scanning.

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: because this method has not been
            implemented
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def abort(
        self,
        task_callback: Optional[Callable] = None,
    ) -> Tuple[TaskStatus, str]:
        """
        Tell the component to abort whatever it was doing.

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: because this method has not been
            implemented
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    def obsreset(
        self,
        task_callback: Optional[Callable] = None,
    ) -> Tuple[TaskStatus, str]:
        """
        Reset the configuration but do not release resources.

        :param task_callback: callback to be called when the status of
            the command changes

        :raises NotImplementedError: because this method has not been
            implemented
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    @property
    def config_id(self) -> str:
        """
        Return the configuration id.

        :raises NotImplementedError: because this method has not been
            implemented
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    @config_id.setter
    def config_id(self, config_id: str) -> None:
        """
        Set the configuration id.

        :param config_id: the new config id

        :raises NotImplementedError: because this method has not been
            implemented
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")

    @property
    def scan_id(self) -> int:
        """
        Return the scan id.

        :raises NotImplementedError: because this method has not been
            implemented
        """
        raise NotImplementedError("CspObsComponentManager is abstract.")
