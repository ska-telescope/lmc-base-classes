"""This package provides shared functionality and patterns for SKA TANGO devices."""

__all__ = (
    # subpackages
    "base",
    "csp",
    "obs",
    "subarray",
    # modules
    "commands",
    "control_model",
    "faults",
    "release",
    "utils",
    # direct imports
    "SKAAlarmHandler",
    "SKABaseDevice",
    "SKACapability",
    "SKALogger",
    "SKAController",
    "SKAObsDevice",
    "SKASubarray",
    "SKATelState",
    "CspSubElementController",
    "CspSubElementObsDevice",
    "CspSubElementSubarray",
)

from .alarm_handler_device import SKAAlarmHandler
from .base import SKABaseDevice
from .capability_device import SKACapability
from .controller_device import SKAController
from .csp import (
    CspSubElementController,
    CspSubElementObsDevice,
    CspSubElementSubarray,
)
from .logger_device import SKALogger
from .obs import SKAObsDevice
from .subarray import SKASubarray
from .tel_state_device import SKATelState
