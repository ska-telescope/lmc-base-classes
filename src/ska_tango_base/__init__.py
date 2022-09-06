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

# Note: order of imports is important - start with lowest in the hierarchy

# SKABaseDevice, and then classes that inherit from it
from .base import SKABaseDevice
from .alarm_handler_device import SKAAlarmHandler  # type: ignore[attr-defined]
from .logger_device import SKALogger
from .controller_device import SKAController
from .tel_state_device import SKATelState

# SKAObsDevice, and then classes that inherit from it
from .obs import SKAObsDevice
from .capability_device import SKACapability
from .subarray import SKASubarray

# CspSubElement classes
from .csp import CspSubElementController, CspSubElementSubarray, CspSubElementObsDevice
