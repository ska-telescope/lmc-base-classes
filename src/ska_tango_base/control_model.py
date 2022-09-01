# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
Module for SKA Control Model (SCM) related code.

For further details see the SKA1 CONTROL SYSTEM GUIDELINES (CS_GUIDELINES MAIN VOLUME)
Document number:  000-000000-010 GDL
And architectural updates:
https://jira.skatelescope.org/browse/ADR-8
https://confluence.skatelescope.org/pages/viewpage.action?pageId=105416556

The enumerated types mapping to the states and modes are included here, as well as
other useful enumerations.
"""
from __future__ import annotations

from ska_control_model import (
    AdminMode,
    CommunicationStatus,
    ControlMode,
    HealthState,
    LoggingLevel,
    ObsMode,
    ObsState,
    PowerState,
    SimulationMode,
    TestMode,
)

__all__ = [
    "AdminMode",
    "CommunicationStatus",
    "ControlMode",
    "HealthState",
    "LoggingLevel",
    "ObsMode",
    "ObsState",
    "PowerState",
    "SimulationMode",
    "TestMode",
]
