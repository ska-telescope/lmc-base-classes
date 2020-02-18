# -*- coding: utf-8 -*-
"""
Module for SKA Control Model (SCM) related code.

For further details see the SKA1 CONTROL SYSTEM GUIDELINES (CS_GUIDELINES MAIN VOLUME)
Document number:  000-000000-010 GDL

The enumerated types mapping to the states and modes are included here, as well as
other useful enumerations.

"""

import enum

# ---------------------------------
# Core SKA Control Model attributes
# ---------------------------------


class HealthState(enum.IntEnum):
    """Python enumerated type for HealthState attribute."""

    OK = 0
    DEGRADED = 1
    FAILED = 2
    UNKNOWN = 3


class AdminMode(enum.IntEnum):
    """Python enumerated type for AdminMode attribute."""

    ONLINE = 0
    OFFLINE = 1
    MAINTENANCE = 2
    NOT_FITTED = 3
    RESERVED = 4


class ObsState(enum.IntEnum):
    """Python enumerated type for ObsState attribute."""

    IDLE = 0
    CONFIGURING = 1
    READY = 2
    SCANNING = 3
    PAUSED = 4
    ABORTED = 5
    FAULT = 6


class ObsMode(enum.IntEnum):
    """Python enumerated type for ObsMode attribute."""

    IDLE = 0
    IMAGING = 1
    PULSAR_SEARCH = 2
    PULSAR_TIMING = 3
    DYNAMIC_SPECTRUM = 4
    TRANSIENT_SEARCH = 5
    VLBI = 6
    CALIBRATION = 7


# ---------------------------------------
# Additional SKA Control Model attributes
# ---------------------------------------


class ControlMode(enum.IntEnum):
    """Python enumerated type for ControlMode attribute."""

    REMOTE = 0
    LOCAL = 1


# -------------
# Miscellaneous
# -------------


class LoggingLevel(enum.IntEnum):
    """Python enumerated type for LoggingLevel attribute."""

    OFF = 0
    FATAL = 1
    ERROR = 2
    WARNING = 3
    INFO = 4
    DEBUG = 5
