# -*- coding: utf-8 -*-
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

import enum


# ---------------------------------
# Core SKA Control Model attributes
# ---------------------------------
class HealthState(enum.IntEnum):
    """Python enumerated type for ``healthState`` attribute."""

    OK = 0
    """
    Tango Device reports this state when ready for use, or when entity ``adminMode``
    is ``NOT_FITTED`` or ``RESERVED``.

    The rationale for reporting health as OK when an entity is ``NOT_FITTED`` or
    ``RESERVED`` is to ensure that it does not pop-up unnecessarily on drill-down fault
    displays with healthState ``UNKNOWN``, ``DEGRADED`` or ``FAILED`` while it is
    expected to not be available.
    """

    DEGRADED = 1
    """
    Tango Device reports this state when only part of functionality is available. This
    value is optional and shall be implemented only where it is useful.

    For example, a subarray may report healthState as ``DEGRADED`` if one of the dishes
    that belongs to a subarray is unresponsive, or may report healthState as ``FAILED``.

    Difference between ``DEGRADED`` and ``FAILED`` health shall be clearly identified
    (quantified) and documented. For example, the difference between ``DEGRADED`` and ``FAILED``
    subarray can be defined as the number or percent of the dishes available, the number or
    percent of the baselines available,   sensitivity, or some other criterion. More than one
    criteria may be defined for a Tango Device.
    """

    FAILED = 2
    """
    Tango Device reports this state when unable to perform core functionality and
    produce valid output.
    """

    UNKNOWN = 3
    """
    Initial state when health state of entity could not yet be determined.
    """


class AdminMode(enum.IntEnum):
    """Python enumerated type for ``adminMode`` attribute."""

    ONLINE = 0
    """
    The component can be used for normal operations, such as observing.
    While in this mode, the Tango device is actively monitoring and
    controlling its component. Tango devices that implement
    ``adminMode`` as a read-only attribute shall always report
    ``adminMode=ONLINE``.
    """

    OFFLINE = 1
    """
    The component is not to be used for any operations. While in this
    mode, Tango devices report ``state=DISABLE``, and do not communicate
    with their component. Monitoring and control of the component does
    not occur, so alarms, alerts and events are not received.
    """

    MAINTENANCE = 2
    """
    SKA operations declares that the component cannot be used for normal
    operations, but can be used for maintenance purposes such as testing
    and debugging, as part of a "maintenance subarray". While in this
    mode, Tango devices are actively monitoring and controlling their
    component, but may only support a subset of normal functionality.

    ``MAINTENANCE`` mode has different meaning for different components,
    depending on the context and functionality. Some entities may
    implement different behaviour when in ``MAINTENANCE`` mode. For each
    Tango device, the difference in behaviour and functionality in
    ``MAINTENANCE`` mode shall be documented.
    """

    NOT_FITTED = 3
    """
    The component cannot be used for any purposes because it is not
    fitted; for example, faulty equipment has been removed and not
    yet replaced, leaving nothing `in situ` to monitor. While in this
    mode, Tango devices report ``state=DISABLED``. All monitoring and
    control functionality is disabled because there is no component to
    monitor.
    """

    RESERVED = 4
    """
    The component is fitted, but only for redundancy purposes. It is
    additional equipment that does not take part in operations at this
    time, but is ready to take over when the operational
    equipment fails. While in this mode, Tango devices report
    ``state=DISABLED``. All monitoring and control functionality is
    disabled.
    """


class ObsState(enum.IntEnum):
    """Python enumerated type for ``obsState`` attribute - the observing state."""

    EMPTY = 0
    """
    The sub-array is ready to observe, but is in an undefined
    configuration and has no resources allocated.
    """

    RESOURCING = 1
    """
    The system is allocating resources to, or deallocating resources
    from, the subarray. This may be a complete de/allocation, or it may
    be incremental. In both cases it is a transient state and will
    automatically transition to IDLE when complete. For some subsystems
    this may be a very brief state if resourcing is a quick activity.
    """

    IDLE = 2
    """
    The subarray has resources allocated and is ready to be used for
    observing. In normal science operations these will be the resources
    required for the upcoming SBI execution.
    """

    CONFIGURING = 3
    """
    The subarray is being configured ready to scan. On entry to the
    state no assumptions can be made about the previous conditions. It
    is a transient state and will automatically transition to READY when
    it completes normally.
    """

    READY = 4
    """
    The subarray is fully prepared to scan, but is not actually taking
    data or moving in the observed coordinate system (it may be
    tracking, but not moving relative to the coordinate system).
    """

    SCANNING = 5
    """
    The subarray is taking data and, if needed, all components are
    synchronously moving in the observed coordinate system. Any changes
    to the sub-systems are happening automatically (this allows for a
    scan to cover the case where the phase centre is moved in a
    pre-defined pattern).
    """

    ABORTING = 6
    """
    The subarray is trying to abort what it was doing due to having been
    interrupted by the controller.
    """

    ABORTED = 7
    """
    The subarray has had its previous state interrupted by the
    controller, and is now in an aborted state.
    """

    RESETTING = 8
    """
    The subarray device is resetting to the IDLE state.
    """

    FAULT = 9
    """
    The subarray has detected an error in its observing state making it
    impossible to remain in the previous state.
    """

    RESTARTING = 10
    """
    The subarray device is restarting, as the last known stable state is
    where no resources were allocated and the configuration undefined.
    """


class ObsMode(enum.IntEnum):
    """Python enumerated type for ``obsMode`` attribute - the observing mode."""

    IDLE = 0
    """
    The ``obsMode`` shall be reported as ``IDLE`` when ``obsState`` is ``IDLE``;
    else, it will correctly report the appropriate value.
    More than one observing mode can be active in the same subarray at the same time.
    """

    IMAGING = 1
    """
    Imaging observation is active.
    """

    PULSAR_SEARCH = 2
    """
    Pulsar search observation is active.
    """

    PULSAR_TIMING = 3
    """
    Pulsar timing observation is active.
    """

    DYNAMIC_SPECTRUM = 4
    """
    Dynamic spectrum observation is active.
    """

    TRANSIENT_SEARCH = 5
    """
    Transient search observation is active.
    """

    VLBI = 6
    """
    Very long baseline interferometry observation is active.
    """

    CALIBRATION = 7
    """
    Calibration observation is active.
    """


# ---------------------------------------
# Additional SKA Control Model attributes
# ---------------------------------------


class ControlMode(enum.IntEnum):
    """Python enumerated type for ``controlMode`` attribute."""

    REMOTE = 0
    """
    Tango Device accepts commands from all clients.
    """

    LOCAL = 1
    """
    Tango Device accepts only from a ‘local’ client and ignores commands and queries received
    from TM or any other ‘remote’ clients. This is typically activated by a switch,
    or a connection on the local control interface. The intention is to support early
    integration of DISHes and stations. The equipment has to be put back in ``REMOTE``
    before clients can take  control again. ``controlMode`` may be removed from the
    SCM if unused/not needed.

    **Note:** Setting `controlMode` to `LOCAL` **is not a safety feature**, but rather a
    usability feature.  Safety has to be implemented separately to the control paths.
    """


class SimulationMode(enum.IntEnum):
    """Python enumerated type for ``simulationMode`` attribute."""

    FALSE = 0
    """
    A real entity is connected to the control system.
    """

    TRUE = 1
    """
    A simulator is connected to the control system, or the real entity acts as a simulator.
    """


class TestMode(enum.IntEnum):
    """
    Python enumerated type for ``testMode`` attribute.

    This enumeration may be replaced and extended in derived classes to
    add additional custom test modes.  That would require overriding the
    base class ``testMode`` attribute definition.
    """

    __test__ = False  # disable pytest discovery for this class

    NONE = 0
    """
    Normal mode of operation. No test mode active.
    """

    TEST = 1
    """
    Element (entity) behaviour and/or set of commands differ for the normal operating mode. To
    be implemented only by devices that implement one or more test modes. The Element
    documentation shall provide detailed description.
    """


# -------------
# Miscellaneous
# -------------


class LoggingLevel(enum.IntEnum):
    """Python enumerated type for ``loggingLevel`` attribute."""

    OFF = 0
    FATAL = 1
    ERROR = 2
    WARNING = 3
    INFO = 4
    DEBUG = 5


class PowerMode(enum.IntEnum):
    """
    Enumerated type for power mode.

    Used by components that rely upon a power supply, such as hardware.
    """

    UNKNOWN = 1
    """The power mode is not known."""

    NO_SUPPLY = 2
    """
    The component is unsupplied with power and cannot be commanded on.

    For example, the power mode of a TPM will be NO_SUPPLY if the
    subrack that powers the TPM is turned off: not only is the TPM
    off, but it cannot even be turned on (until the subrack has been
    turned on).
    """

    OFF = 3
    """The component is turned off but can be commanded on."""

    STANDBY = 4
    """The component is powered on and running in low-power standby mode."""

    ON = 5
    """The component is powered on and running in fully-operational mode."""
