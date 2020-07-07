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
from ska.base.faults import StateModelError

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


class DeviceStateModel:
    """
    Base class for the state model used by SKA devices.
    """

    def __init__(self, transitions, initial_state):
        """
        Create a new device state model.

        :param transitions: a dictionary for which each key is a (state,
            event) tuple, and each value is a (state, side-effect)
            tuple. When the device is in state `IN-STATE`, and action
            `ACTION` is attempted, the transitions table will be checked
            for an entry under key `(IN-STATE, EVENT)`. If no such key
            exists, the action will be denied and a model will raise a
            `StateModelError`. If the key does exist, then its value
            `(OUT-STATE, SIDE-EFFECT)` will result in the model
            transitioning to state `OUT-STATE`, and executing
            `SIDE-EFFECT`, which must be a function or lambda that
            takes a single parameter - a model instance.
        :type transitions: dict
        :param initial_state: the starting state of the model
        :type initial_state: a state with an entry in the transitions
            table
        """
        # instances may update transitions dict, so need a copy
        self._transitions = transitions.copy()
        self._state = initial_state

    @property
    def state(self):
        """Return current state as a string."""
        return self._state

    def update_transitions(self, transitions):
        """
        Update the transitions table with new transitions.

        :param transitions: new transitions to be included in the
            transitions table. Transitions with pre-existing keys will
            replace the transitions for that key. Transitions with novel
            keys will be added. There is no provision for removing
            transitions
        :type transitions: dict
        """
        self._transitions.update(transitions)

    def is_action_allowed(self, action):
        """
        Whether a given action is allowed in the current state.

        :param action: an action, as given in the transitions table
        :type action: ANY
        """
        return (self._state, action) in self._transitions

    def try_action(self, action):
        """
        Checks whether a given action is allowed in the current state,
        and raises a StateModelError if it is not.

        :param action: an action, as given in the transitions table
        :type action: ANY
        :raises StateModelError: if the action is not allowed in the
            current state
        :returns: True if the action is allowed
        :rtype: boolean
        """
        if not self.is_action_allowed(action):
            raise StateModelError(
                f"Action '{action}' not allowed in current state ({self._state})."
            )
        return True

    def perform_action(self, action):
        """
        Performs an action on the state model

        :param action: an action, as given in the transitions table
        :type action: ANY
        :raises StateModelError: if the action is not allowed in the
            current state

        """
        self.try_action(action)

        (self._state, side_effect) = self._transitions[(self._state, action)]
        if side_effect is not None:
            side_effect(self)
