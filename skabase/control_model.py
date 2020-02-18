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
    """Python enumerated type for ``healthState`` attribute."""

    OK = 0
    """
    TANGO Device reports this state when ready for use, or when entity ``adminMode``
    is ``NOT_FITTED`` or ``RESERVED``.

    The rationale for reporting health as OK when an entity is ``NOT_FITTED`` or
    ``RESERVED`` is to ensure that it does not pop-up unnecessarily on drill-down fault
    displays with healthState ``UNKNOWN``, ``DEGRADED`` or ``FAILED`` while it is
    expected to not be available.
    """

    DEGRADED = 1
    """
    TANGO Device reports this state when only part of functionality is available. This
    value is optional and shall be implemented only where it is useful.

    For example, a subarray may report healthState as ``DEGRADED`` if one of the dishes
    that belongs to a subarray is unresponsive, or may report healthState as ``FAILED``.

    Difference between ``DEGRADED`` and ``FAILED`` health shall be clearly identified
    (quantified) and documented. For example, the difference between ``DEGRADED`` and ``FAILED`` 
    subarray can be defined as the number or percent of the dishes available, the number or 
    percent of the baselines available,   sensitivity, or some other criterion. More than one 
    criteria may be defined for a TANGO Device.
    """

    FAILED = 2
    """
    TANGO Device reports this state when unable to perform core functionality and
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
    SKA operations declared that the entity can be used for observing (or other
    function it implements). During normal operations Elements and subarrays
    (and all other entities) shall be in this mode. TANGO Devices that implement
    ``adminMode`` as read-only attribute shall always report ``adminMode=ONLINE``.
    ``adminMode=ONLINE`` is also used to indicate active Subarrays or Capabilities.
    """

    OFFLINE = 1
    """SKA operations declared that the entity is not used for observing or other function it 
    provides. A subset of the monitor and control functionality may be supported in this mode. 
    ``adminMode=OFFLINE`` is also used to indicate unused Subarrays and unused Capabilities.
    TANGO devices report ``state=DISABLED`` when ``adminMode=OFFLINE``.
    """

    MAINTENANCE = 2
    """
    SKA operations declared that the entity is reserved for maintenance and cannot
    be part of scientific observations, but can be used for observing in a ‘Maintenance Subarray’. 
    
    ``MAINTENANCE`` mode has different meaning for different entities, depending on the context
    and functionality. Some entities may implement different behaviour when in ``MAINTENANCE``
    mode.
    
    For each TANGO Device, the difference in behaviour and functionality in ``MAINTENANCE`` mode 
    shall be documented. ``MAINTENANCE`` is the factory default for ``adminMode``. Transition
    out of ``adminMode=NOT_FITTED`` is always via ``MAINTENANCE``; an engineer/operator has to
    verify that the  entity is operational as expected before it is set to ``ONLINE``
    (or ``OFFLINE``).
    """

    NOT_FITTED = 3
    """
    SKA operations declared the entity as ``NOT_FITTED`` (and therefore cannot be used for 
    observing or other function it provides). TM shall not send commands or queries to the 
    Element (entity) while in this mode.
    
    TANGO devices shall report ``state=DISABLE`` when ``adminMode=NOT_FITTED``; higher level 
    entities (Element, Sub-element, component, Subarray and/or Capability) which ‘use’ 
    ``NOT_FITTED`` equipment shall report operational ``state`` as ``DISABLE``.  If only a subset 
    of higher-level functionality is affected, overall ``state`` of the higher-level entity that 
    uses ``NOT_FITTED`` equipment may be reported as ``ON``, but with ``healthState=DEGRADED``. 
    Additional queries may be necessary to identify which functionality and capabilities are 
    available. 
    
    Higher-level entities shall intelligently exclude ``NOT_FITTED`` items from ``healthState`` and 
    Element Alerts/Telescope Alarms; e.g. if a receiver band in DSH is ``NOT_FITTED`` and there 
    is no communication to that receiver band, then DSH shall not raise Element Alerts for that 
    entity and it should not report ``healthState=FAILED`` because of an entity that is 
    ``NOT_FITTED``.
    """

    RESERVED = 4
    """This mode is used to identify additional equipment that is ready to take over when the 
    operational equipment fails. This equipment does not take part in the operations at this 
    point in time. TANGO devices report ``state=DISABLED`` when ``adminMode=RESERVED``.
    """


class ObsState(enum.IntEnum):
    """Python enumerated type for ``obsState`` attribute - the observing state."""

    IDLE = 0
    """
    Subarray, resource, Capability is not used for observing, it does not produce output
    products.  The exact implementation is [TBD4] for each Element/Sub-element that
    implements subarrays.
    """

    CONFIGURING = 1
    """
    Subarray is being prepared for a specific scan. On entry to the state no assumptions
    can be made about the previous conditions. This is a transient state. Subarray/Capability
    are supposed to automatically transitions to ``obsState=READY`` when configuration is
    successfully completed. If an error is encountered, TANGO Device may:
    
    * report failure and abort the configuration, waiting for additional input;
    * proceed with reconfiguration, transition to ``obsState=READY`` and set
      ``healthState=DEGRADED`` (if possible notify the originator of the request that
      configuration is not 100% successful);
    * if serious failure is encountered, transition to ``obsState=FAULT``,
      ``healthState=FAILED``.
    """

    READY = 2
    """
    Subarray is fully prepared for the next scan, but not actually taking data or moving
    in the observed coordinate system (i.e. it may be tracking, but not moving relative
    to the coordinate system). 
    """

    SCANNING = 3
    """
    Subarray is taking data and, if needed, all components are synchronously moving in the
    observed coordinate system. All the M&C flows to the sub-systems are happening
    automatically (e.g. DISHes are receiving pointing updates, CSP is receiving updates for
    delay tracking).
    """

    PAUSED = 4
    """
    [TBC11 by SKAO SW Architects] Subarray is fully prepared for the next observation, but
    not actually taking data or moving in the observed system. Similar to ``READY`` state.
    If required, then functionality required by DISHes, LFAA, CSP is [TBD5]
    (do they keep signal processing and stop transmitting output data? What happens to
    observations that are time/position sensitive and cannot resume after a pause?) 
    """

    ABORTED = 5
    """
    The subarray has had its previous state interrupted by the controller. Exit from
    the ``ABORTED`` state requires the ``Reset`` command.
    """

    FAULT = 6
    """
    Subarray has detected an internal error making it impossible to remain in the previous
    state.
 
    **Note:** This shall trigger a ``healthState`` update of the Subarray/Capability.
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
    TANGO Device accepts commands from all clients.
    """

    LOCAL = 1
    """
    TANGO Device accepts only from a ‘local’ client and ignores commands and queries received 
    from TM or any other ‘remote’ clients. This is typically activated by a switch, 
    or a connection on the local control interface. The intention is to support early
    integration of DISHes and stations. The equipment has to be put back in ``REMOTE``
    before clients can take  control again. ``controlMode`` may be removed from the
    SCM if unused/not needed.
    
    **Note:** Setting `controlMode` to `LOCAL` **is not a safe feature**, but rather a
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
    """Python enumerated type for ``testMode`` attribute.

    This enumeration may be replaced and extended in derived classes to
    add additional custom test modes.  That would require overriding the base
    class ``testMode`` attribute definition.
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
