# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#

"""
This module implements a generic base model and device for SKA. It
exposes the generic attributes, properties and commands of an SKA
device.
"""
# PROTECTED REGION ID(SKABaseDevice.additionnal_import) ENABLED START #
# Standard imports
import enum
import logging
import logging.handlers
import socket
import sys
import threading
import warnings
from transitions import MachineError
from urllib.parse import urlparse
from urllib.request import url2pathname

# Tango imports
from tango import AttrWriteType, DebugIt, DevState
from tango.server import run, Device, attribute, command, device_property

# SKA specific imports
import ska.logging as ska_logging
from ska.base import release
from ska.base.commands import (
    ActionCommand, BaseCommand, ResultCode
)
from ska.base.control_model import (
    AdminMode, ControlMode, SimulationMode, TestMode, HealthState,
    LoggingLevel
)
from ska.base.faults import StateModelError
from ska.base.state_machine import OperationStateMachine, AdminModeStateMachine

from ska.base.utils import get_groups_from_json, for_testing_only
from ska.base.faults import GroupDefinitionsError, LoggingTargetError, LoggingLevelError

LOG_FILE_SIZE = 1024 * 1024  # Log file size 1MB.


class _Log4TangoLoggingLevel(enum.IntEnum):
    """Python enumerated type for TANGO log4tango logging levels.

    This is different to tango.LogLevel, and is required if using
    a device's set_log_level() method.  It is not currently exported
    via PyTango, so we hard code it here in the interim.

    Source:
       https://github.com/tango-controls/cppTango/blob/
       4feffd7c8e24b51c9597a40b9ef9982dd6e99cdf/log4tango/include/log4tango/Level.hh#L86-L93
    """

    OFF = 100
    FATAL = 200
    ERROR = 300
    WARN = 400
    INFO = 500
    DEBUG = 600


_PYTHON_TO_TANGO_LOGGING_LEVEL = {
    logging.CRITICAL: _Log4TangoLoggingLevel.FATAL,
    logging.ERROR: _Log4TangoLoggingLevel.ERROR,
    logging.WARNING: _Log4TangoLoggingLevel.WARN,
    logging.INFO: _Log4TangoLoggingLevel.INFO,
    logging.DEBUG: _Log4TangoLoggingLevel.DEBUG,
}

_LMC_TO_TANGO_LOGGING_LEVEL = {
    LoggingLevel.OFF: _Log4TangoLoggingLevel.OFF,
    LoggingLevel.FATAL: _Log4TangoLoggingLevel.FATAL,
    LoggingLevel.ERROR: _Log4TangoLoggingLevel.ERROR,
    LoggingLevel.WARNING: _Log4TangoLoggingLevel.WARN,
    LoggingLevel.INFO: _Log4TangoLoggingLevel.INFO,
    LoggingLevel.DEBUG: _Log4TangoLoggingLevel.DEBUG,
}

_LMC_TO_PYTHON_LOGGING_LEVEL = {
    LoggingLevel.OFF: logging.CRITICAL,  # there is no "off"
    LoggingLevel.FATAL: logging.CRITICAL,
    LoggingLevel.ERROR: logging.ERROR,
    LoggingLevel.WARNING: logging.WARNING,
    LoggingLevel.INFO: logging.INFO,
    LoggingLevel.DEBUG: logging.DEBUG,
}


class TangoLoggingServiceHandler(logging.Handler):
    """Handler that emit logs via Tango device's logger to TLS."""

    def __init__(self, tango_logger):
        super().__init__()
        self.tango_logger = tango_logger

    def emit(self, record):
        try:
            msg = self.format(record)
            tango_level = _PYTHON_TO_TANGO_LOGGING_LEVEL[record.levelno]
            self.acquire()
            try:
                self.tango_logger.log(tango_level, msg)
            finally:
                self.release()
        except Exception:
            self.handleError(record)

    def __repr__(self):
        python_level = logging.getLevelName(self.level)
        if self.tango_logger:
            tango_level = _Log4TangoLoggingLevel(self.tango_logger.get_level()).name
            name = self.tango_logger.get_name()
        else:
            tango_level = "UNKNOWN"
            name = "!No Tango logger!"
        return '<{} {} (Python {}, Tango {})>'.format(
            self.__class__.__name__, name, python_level, tango_level)


class LoggingUtils:
    """Utility functions to aid logger configuration.

    These functions are encapsulated in class to aid testing - it
    allows dependent functions to be mocked.
    """

    @staticmethod
    def sanitise_logging_targets(targets, device_name):
        """Validate and return logging targets '<type>::<name>' strings.

        :param targets: 
            List of candidate logging target strings, like '<type>[::<name>]'
            Empty and whitespace-only strings are ignored.  Can also be None.

        :param device_name:
            TANGO device name, like 'domain/family/member', used
            for the default file name

        :return: list of '<type>::<name>' strings, with default name, if applicable

        :raises LoggingTargetError: for invalid target string that cannot be corrected
        """
        default_target_names = {
            "console": "cout",
            "file": "{}.log".format(device_name.replace("/", "_")),
            "syslog": None,
            "tango": "logger",
        }

        valid_targets = []
        if targets:
            for target in targets:
                target = target.strip()
                if not target:
                    continue
                if "::" in target:
                    target_type, target_name = target.split("::", 1)
                else:
                    target_type = target
                    target_name = None
                if target_type not in default_target_names:
                    raise LoggingTargetError(
                        "Invalid target type: {} - options are {}".format(
                            target_type, list(default_target_names.keys())))
                if not target_name:
                    target_name = default_target_names[target_type]
                if not target_name:
                    raise LoggingTargetError(
                        "Target name required for type {}".format(target_type))
                valid_target = "{}::{}".format(target_type, target_name)
                valid_targets.append(valid_target)

        return valid_targets

    @staticmethod
    def get_syslog_address_and_socktype(url):
        """Parse syslog URL and extract address and socktype parameters for SysLogHandler.

        :param url:
            Universal resource locator string for syslog target.  Three types are supported:
            file path, remote UDP server, remote TCP server.
            - Output to a file:  'file://<path to file>'
              Example:  'file:///dev/log' will write to '/dev/log'
            - Output to remote server over UDP:  'udp://<hostname>:<port>'
              Example:  'udp://syslog.com:514' will send to host 'syslog.com' on UDP port 514
            - Output to remote server over TCP:  'tcp://<hostname>:<port>'
              Example:  'tcp://rsyslog.com:601' will send to host 'rsyslog.com' on TCP port 601
            For backwards compatibility, if the protocol prefix is missing, the type is
            interpreted as file.  This is deprecated.
            - Example:  '/dev/log' is equivalent to 'file:///dev/log'

        :return: (address, socktype)
            For file types:
            - address is the file path as as string
            - socktype is None
            For UDP and TCP:
            - address is tuple of (hostname, port), with hostname a string, and port an integer.
            - socktype is socket.SOCK_DGRAM for UDP, or socket.SOCK_STREAM for TCP.

        :raises LoggingTargetError: for invalid url string
        """
        address = None
        socktype = None
        parsed = urlparse(url)
        if parsed.scheme in ["file", ""]:
            address = url2pathname(parsed.netloc + parsed.path)
            socktype = None
            if not address:
                raise LoggingTargetError(
                    "Invalid syslog URL - empty file path from '{}'".format(url)
                )
            if parsed.scheme == "":
                warnings.warn(
                    "Specifying syslog URL without protocol is deprecated, "
                    "use 'file://{}' instead of '{}'".format(url, url),
                    DeprecationWarning,
                )
        elif parsed.scheme in ["udp", "tcp"]:
            if not parsed.hostname:
                raise LoggingTargetError(
                    "Invalid syslog URL - could not extract hostname from '{}'".format(url)
                )
            try:
                port = int(parsed.port)
            except (TypeError, ValueError):
                raise LoggingTargetError(
                    "Invalid syslog URL - could not extract integer port number from '{}'".format(
                        url
                    )
                )
            address = (parsed.hostname, port)
            socktype = socket.SOCK_DGRAM if parsed.scheme == "udp" else socket.SOCK_STREAM
        else:
            raise LoggingTargetError(
                "Invalid syslog URL - expected file, udp or tcp protocol scheme in '{}'".format(url)
            )
        return address, socktype

    @staticmethod
    def create_logging_handler(target, tango_logger=None):
        """Create a Python log handler based on the target type (console, file, syslog, tango)

        :param target:
            Logging target for logger, <type>::<name>

        :param tango_logger:
            Instance of tango.Logger, optional.  Only required if creating
            a target of type "tango".

        :return: StreamHandler, RotatingFileHandler, SysLogHandler, or TangoLoggingServiceHandler

        :raises LoggingTargetError: for invalid target string
        """
        if "::" in target:
            target_type, target_name = target.split("::", 1)
        else:
            raise LoggingTargetError(
                "Invalid target requested - missing '::' separator: {}".format(target))
        if target_type == "console":
            handler = logging.StreamHandler(sys.stdout)
        elif target_type == "file":
            log_file_name = target_name
            handler = logging.handlers.RotatingFileHandler(
                log_file_name, 'a', LOG_FILE_SIZE, 2, None, False)
        elif target_type == "syslog":
            address, socktype = LoggingUtils.get_syslog_address_and_socktype(target_name)
            handler = logging.handlers.SysLogHandler(
                address=address,
                facility=logging.handlers.SysLogHandler.LOG_SYSLOG,
                socktype=socktype)
        elif target_type == "tango":
            if tango_logger:
                handler = TangoLoggingServiceHandler(tango_logger)
            else:
                raise LoggingTargetError("Missing tango_logger instance for 'tango' target type")
        else:
            raise LoggingTargetError(
                "Invalid target type requested: '{}' in '{}'".format(target_type, target))
        formatter = ska_logging.get_default_formatter(tags=True)
        handler.setFormatter(formatter)
        handler.name = target
        return handler

    @staticmethod
    def update_logging_handlers(targets, logger):
        old_targets = [handler.name for handler in logger.handlers]
        added_targets = set(targets) - set(old_targets)
        removed_targets = set(old_targets) - set(targets)

        for handler in list(logger.handlers):
            if handler.name in removed_targets:
                logger.removeHandler(handler)
        for target in targets:
            if target in added_targets:
                handler = LoggingUtils.create_logging_handler(target, logger.tango_logger)
                logger.addHandler(handler)

        logger.info('Logging targets set to %s', targets)


# PROTECTED REGION END #    //  SKABaseDevice.additionnal_import


__all__ = ["DeviceStateModel", "SKABaseDevice", "main"]


class DeviceStateModel:
    """
    Implements the state model for the SKABaseDevice.

    This implementation contains separate state machines for adminMode
    and opState. Since the two are slightly but inextricably coupled,
    the opState machine includes "ADMIN" flavours for the "INIT",
    "FAULT" and "DISABLED" states, to represent states where the device
    has been administratively disabled via the adminModes "RESERVED",
    "NOT_FITTED" and "OFFLINE". This model drives the two state machines
    to ensure they remain coherent.
    """

    def __init__(self, logger, op_state_callback=None, admin_mode_callback=None):
        """
        Initialises the state model.

        :param logger: the logger to be used by this state model.
        :type logger: a logger that implements the standard library
            logger interface
        :param op_state_callback: A callback to be called when the state
            machine for op_state reports a change of state
        :type op_state_callback: callable
        :param admin_mode_callback: A callback to be called when the
            state machine for admin_mode reports a change of state
        :type admin_mode_callback: callable
        """
        self.logger = logger

        self._op_state = None
        self._admin_mode = None

        self._op_state_callback = op_state_callback
        self._admin_mode_callback = admin_mode_callback

        self._op_state_machine = OperationStateMachine(callback=self._update_op_state)
        self._admin_mode_state_machine = AdminModeStateMachine(
            callback=self._update_admin_mode
        )

    @property
    def admin_mode(self):
        """
        Returns the admin_mode

        :returns: admin_mode of this state model
        :rtype: AdminMode
        """
        return self._admin_mode

    def _update_admin_mode(self, machine_state):
        """
        Helper method that updates admin_mode whenever the admin_mode
        state machine reports a change of state, ensuring that the
        callback is called if one exists.

        :param machine_state: the new state of the adminMode state
            machine
        :type machine_state: str
        """
        admin_mode = AdminMode[machine_state]
        if self._admin_mode != admin_mode:
            self._admin_mode = admin_mode
            if self._admin_mode_callback is not None:
                self._admin_mode_callback(admin_mode)

    @property
    def op_state(self):
        """
        Returns the op_state of this state model

        :returns: op_state of this state model
        :rtype: tango.DevState
        """
        return self._op_state

    _op_state_mapping = {
        "INIT": DevState.INIT,
        "INIT_ADMIN": DevState.INIT,
        "FAULT": DevState.FAULT,
        "FAULT_ADMIN": DevState.FAULT,
        "DISABLE": DevState.DISABLE,
        "DISABLE_ADMIN": DevState.DISABLE,
        "STANDBY": DevState.STANDBY,
        "OFF": DevState.OFF,
        "ON": DevState.ON,
    }

    def _update_op_state(self, machine_state):
        """
        Helper method that updates op_state whenever the operation
        state machine reports a change of state, ensuring that the
        callback is called if one exists.

        :param machine_state: the new state of the operation state
            machine
        :type machine_state: str
        """
        op_state = self._op_state_mapping[machine_state]
        if self._op_state != op_state:
            self._op_state = op_state
            if self._op_state_callback is not None:
                self._op_state_callback(op_state)

    __action_breakdown = {
        # "action": ("action_on_op_machine", "action_on_admin_mode_machine"),
        "to_reserved": ("admin_on", "to_reserved"),
        "to_notfitted": ("admin_on", "to_notfitted"),
        "to_offline": ("admin_on", "to_offline"),
        "to_maintenance": ("admin_off", "to_maintenance"),
        "to_online": ("admin_off", "to_online"),
        "init_started": ("init_started", None),
        "init_succeeded_disable": ("init_succeeded_disable", None),
        "init_succeeded_standby": ("init_succeeded_standby", None),
        "init_succeeded_off": ("init_succeeded_off", None),
        "init_failed": ("init_failed", None),
        "reset_started": ("reset_started", None),
        "reset_succeeded_disable": ("reset_succeeded_disable", None),
        "reset_succeeded_standby": ("reset_succeeded_standby", None),
        "reset_succeeded_off": ("reset_succeeded_off", None),
        "reset_failed": ("reset_failed", None),
        "disable_succeeded": ("disable_succeeded", None),
        "disable_failed": ("disable_failed", None),
        "standby_succeeded": ("standby_succeeded", None),
        "standby_failed": ("standby_failed", None),
        "off_succeeded": ("off_succeeded", None),
        "off_failed": ("off_failed", None),
        "on_succeeded": ("on_succeeded", None),
        "on_failed": ("on_failed", None),
        "fatal_error": ("fatal_error", None),
    }

    def is_action_allowed(self, action):
        """
        Whether a given action is allowed in the current state.

        :param action: an action, as given in the transitions table
        :type action: str

        :raises StateModelError: if the action is unknown to the state
            machine

        :return: whether the action is allowed in the current state
        :rtype: bool
        """
        try:
            (op_action, admin_action) = self.__action_breakdown[action]
        except KeyError as key_error:
            raise StateModelError(key_error)

        if (
            admin_action is not None
            and admin_action
            not in self._admin_mode_state_machine.get_triggers(
                self._admin_mode_state_machine.state
            )
        ):
            return False
        return op_action in self._op_state_machine.get_triggers(
            self._op_state_machine.state
        )

    def try_action(self, action):
        """
        Checks whether a given action is allowed in the current state,
        and raises a StateModelError if it is not.

        :param action: an action, as given in the transitions table
        :type action: str

        :raises StateModelError: if the action is not allowed in the
            current state

        :returns: True if the action is allowed
        :rtype: boolean
        """
        if not self.is_action_allowed(action):
            raise StateModelError(
                f"Action {action} is not allowed in operational state "
                f"{self.op_state}, admin mode {self.admin_mode}."
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

        (op_action, admin_action) = self.__action_breakdown[action]

        if op_action is not None:
            self._op_state_machine.trigger(op_action)
        if admin_action is not None:
            self._admin_mode_state_machine.trigger(action)

    @for_testing_only
    def _straight_to_state(self, op_state=None, admin_mode=None):
        """
        Takes the DeviceStateModel straight to the specified state / mode. This
        method exists to simplify testing; for example, if testing that a command
        may be run in a given state, one can push the state model straight to that
        state, rather than having to drive it to that state through a sequence
        of actions. It is not intended that this method would be called outside
        of test setups. A warning will be raised if it is.

        Note that this method will allow you to put the device into an incoherent
        combination of admin_mode and op_state (e.g. OFFLINE and ON).

        :param op_state: the target operational state (optional)
        :type op_state: :py:class:`tango.DevState`
        :param admin_mode: the target admin mode (optional)
        :type admin_mode: :py:class:`~ska.base.control_model.AdminMode`
        """
        if admin_mode is None:
            admin_mode = self._admin_mode_state_machine.state
        else:
            admin_mode = admin_mode.name

        if op_state is None:
            op_state = self._op_state_machine.state
        else:
            op_state = op_state.name

        if op_state.endswith("_ADMIN"):
            op_state = op_state[:-6]
        if admin_mode in ["RESERVED", "NOT_FITTED", "OFFLINE"]:
            op_state = f"{op_state}_ADMIN"

        getattr(self._admin_mode_state_machine, f"to_{admin_mode}")()
        getattr(self._op_state_machine, f"to_{op_state}")()


class SKABaseDevice(Device):
    """
    A generic base device for SKA.
    """

    class InitCommand(ActionCommand):
        """
        A class for the SKABaseDevice's init_device() "command".
        """

        def __init__(self, target, state_model, logger=None):
            """
            Create a new InitCommand

            :param target: the object that this command acts upon; for
                example, the SKASubarray device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`DeviceStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(
                target, state_model, "init", start_action=True, logger=logger
            )

        def do(self):
            """
            Stateless hook for device initialisation.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device = self.target

            device.set_change_event("adminMode", True, True)
            device.set_archive_event("adminMode", True, True)
            device.set_change_event("state", True, True)
            device.set_archive_event("state", True, True)
            device.set_change_event("status", True, True)
            device.set_archive_event("status", True, True)

            device._health_state = HealthState.OK
            device._control_mode = ControlMode.REMOTE
            device._simulation_mode = SimulationMode.FALSE
            device._test_mode = TestMode.NONE

            device._build_state = '{}, {}, {}'.format(release.name,
                                                      release.version,
                                                      release.description)
            device._version_id = release.version

            try:
                # create TANGO Groups dict, according to property
                self.logger.debug(
                    "Groups definitions: {}".format(
                        device.GroupDefinitions
                    )
                )
                device.groups = get_groups_from_json(
                    device.GroupDefinitions
                )
                self.logger.info(
                    "Groups loaded: {}".format(
                        sorted(device.groups.keys())
                    )
                )
            except GroupDefinitionsError:
                self.logger.debug(
                    "No Groups loaded for device: {}".format(
                        device.get_name()
                    )
                )

            message = "SKABaseDevice Init command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

        def succeeded(self):
            self.state_model.perform_action("init_succeeded_off")

    _logging_config_lock = threading.Lock()
    _logging_configured = False

    def _init_logging(self):
        """
        This method initializes the logging mechanism, based on default
        properties.
        """

        class EnsureTagsFilter(logging.Filter):
            """Ensure all records have a "tags" field - empty string, if not provided."""
            def filter(self, record):
                if not hasattr(record, "tags"):
                    record.tags = ""
                return True

        # There may be multiple devices in a single device server - these will all be
        # starting at the same time, so use a lock to prevent race conditions, and
        # a flag to ensure the SKA standard logging configuration is only applied once.
        with SKABaseDevice._logging_config_lock:
            if not SKABaseDevice._logging_configured:
                ska_logging.configure_logging(tags_filter=EnsureTagsFilter)
                SKABaseDevice._logging_configured = True

        device_name = self.get_name()
        self.logger = logging.getLogger(device_name)
        # device may be reinitialised, so remove existing handlers and filters
        for handler in list(self.logger.handlers):
            self.logger.removeHandler(handler)
        for filt in list(self.logger.filters):
            self.logger.removeFilter(filt)

        # add a filter with this device's name
        device_name_tag = "tango-device:{}".format(device_name)

        class TangoDeviceTagsFilter(logging.Filter):
            def filter(self, record):
                record.tags = device_name_tag
                return True

        self.logger.addFilter(TangoDeviceTagsFilter())

        # before setting targets, give Python logger a reference to the log4tango logger
        # to support the TangoLoggingServiceHandler target option
        self.logger.tango_logger = self.get_logger()

        # initialise using defaults in device properties
        self._logging_level = None
        self.write_loggingLevel(self.LoggingLevelDefault)
        self.write_loggingTargets(self.LoggingTargetsDefault)
        self.logger.debug('Logger initialised')

        # monkey patch TANGO Logging Service streams so they go to the Python
        # logger instead
        self.debug_stream = self.logger.debug
        self.info_stream = self.logger.info
        self.warn_stream = self.logger.warning
        self.error_stream = self.logger.error
        self.fatal_stream = self.logger.critical

    # PROTECTED REGION END #    //  SKABaseDevice.class_variable

    # -----------------
    # Device Properties
    # -----------------

    SkaLevel = device_property(
        dtype='int16', default_value=4
    )

    GroupDefinitions = device_property(
        dtype=('str',),
    )

    LoggingLevelDefault = device_property(
        dtype='uint16', default_value=LoggingLevel.INFO
    )

    LoggingTargetsDefault = device_property(
        dtype='DevVarStringArray', default_value=["tango::logger"]
    )

    # ----------
    # Attributes
    # ----------

    buildState = attribute(
        dtype='str',
        doc="Build state of this device",
    )

    versionId = attribute(
        dtype='str',
        doc="Version Id of this device",
    )

    loggingLevel = attribute(
        dtype=LoggingLevel,
        access=AttrWriteType.READ_WRITE,
        doc="Current logging level for this device - "
            "initialises to LoggingLevelDefault on startup",
    )

    loggingTargets = attribute(
        dtype=('str',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4,
        doc="Logging targets for this device, excluding ska_logging defaults"
            " - initialises to LoggingTargetsDefault on startup",
    )

    healthState = attribute(
        dtype=HealthState,
        doc="The health state reported for this device. "
            "It interprets the current device"
            " condition and condition of all managed devices to set this. "
            "Most possibly an aggregate attribute.",
    )

    adminMode = attribute(
        dtype=AdminMode,
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="The admin mode reported for this device. It may interpret the current "
            "device condition and condition of all managed devices to set this. "
            "Most possibly an aggregate attribute.",
    )

    controlMode = attribute(
        dtype=ControlMode,
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="The control mode of the device. REMOTE, LOCAL"
            "\nTANGO Device accepts only from a ‘local’ client and ignores commands and "
            "queries received from TM or any other ‘remote’ clients. The Local clients"
            " has to release LOCAL control before REMOTE clients can take control again.",
    )

    simulationMode = attribute(
        dtype=SimulationMode,
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="Reports the simulation mode of the device. \nSome devices may implement "
            "both modes, while others will have simulators that set simulationMode "
            "to True while the real devices always set simulationMode to False.",
    )

    testMode = attribute(
        dtype=TestMode,
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="The test mode of the device. \n"
            "Either no test mode or an "
            "indication of the test mode.",
    )

    # ---------------
    # General methods
    # ---------------

    def _update_admin_mode(self, admin_mode):
        """
        Helper method for changing admin_mode; passed to the state model as a
        callback

        :param admin_mode: the new admin_mode value
        :type admin_mode: :py:class:`~ska.base.control_model.AdminMode`
        """
        self.push_change_event("adminMode", admin_mode)
        self.push_archive_event("adminMode", admin_mode)

    def _update_state(self, state):
        """
        Helper method for changing state; passed to the state model as a
        callback

        :param state: the new state value
        :type state: :py:class:`tango.DevState`
        """
        if state != self.get_state():
            self.logger.info(f"Device state changed from {self.get_state()} to {state}")
            self.set_state(state)
            self.set_status(f"The device is in {state} state.")

    def set_state(self, state):
        """
        Helper method for setting device state, ensuring that change
        events are pushed.

        :param state: the new state
        :type state: :py:class:`tango.DevState`
        """
        super().set_state(state)
        self.push_change_event("state")
        self.push_archive_event("state")

    def set_status(self, status):
        """
        Helper method for setting device status, ensuring that change
        events are pushed.

        :param status: the new status
        :type status: str
        """
        super().set_status(status)
        self.push_change_event("status")
        self.push_archive_event("status")

    def init_device(self):
        """
        Initializes the tango device after startup.

        Subclasses that have no need to override the default
        default implementation of state management may leave
        ``init_device()`` alone.  Override the ``do()`` method
        on the nested class ``InitCommand`` instead.
        """
        try:
            super().init_device()

            self._init_logging()
            self._init_state_model()

            self._command_objects = {}

            self.InitCommand(self, self.state_model, self.logger)()

            self.init_command_objects()
        except Exception as exc:
            self.set_state(DevState.FAULT)
            self.set_status("The device is in FAULT state - init_device failed.")
            if hasattr(self, "logger"):
                self.logger.exception("init_device() failed.")
            else:
                print(f"ERROR: init_device failed, and no logger: {exc}.")

    def _init_state_model(self):
        """
        Creates the state model for the device
        """
        self.state_model = DeviceStateModel(
            logger=self.logger,
            op_state_callback=self._update_state,
            admin_mode_callback=self._update_admin_mode,
        )

    def register_command_object(self, command_name, command_object):
        """
        Registers a command object as the object to handle invocations
        of a given command

        :param command_name: name of the command for which the object is
            being registered
        :type command_name: str
        :param command_object: the object that will handle invocations
            of the given command
        :type command_object: Command instance
        """
        self._command_objects[command_name] = command_object

    def get_command_object(self, command_name):
        """
        Returns the command object (handler) for a given command.

        :param command_name: name of the command for which a command
            object (handler) is sought
        :type command_name: str

        :return: the registered command object (handler) for the command
        :rtype: Command instance
        """
        return self._command_objects[command_name]

    def init_command_objects(self):
        """
        Creates and registers command objects (handlers) for the
        commands supported by this device.
        """
        device_args = (self, self.state_model, self.logger)

        self.register_command_object("Disable", self.DisableCommand(*device_args))
        self.register_command_object("Standby", self.StandbyCommand(*device_args))
        self.register_command_object("Off", self.OffCommand(*device_args))
        self.register_command_object("On", self.OnCommand(*device_args))
        self.register_command_object("Reset", self.ResetCommand(*device_args))
        self.register_command_object(
            "GetVersionInfo", self.GetVersionInfoCommand(*device_args)
        )

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKABaseDevice.always_executed_hook) ENABLED START #
        """
        Method that is always executed before any device command gets executed.
        """
        # PROTECTED REGION END #    //  SKABaseDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKABaseDevice.delete_device) ENABLED START #
        """
        Method to cleanup when device is stopped.
        """
        # PROTECTED REGION END #    //  SKABaseDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_buildState(self):
        # PROTECTED REGION ID(SKABaseDevice.buildState_read) ENABLED START #
        """
        Reads the Build State of the device.

        :return: the build state of the device
        """
        return self._build_state
        # PROTECTED REGION END #    //  SKABaseDevice.buildState_read

    def read_versionId(self):
        # PROTECTED REGION ID(SKABaseDevice.versionId_read) ENABLED START #
        """
        Reads the Version Id of the device.

        :return: the version id of the device
        """
        return self._version_id
        # PROTECTED REGION END #    //  SKABaseDevice.versionId_read

    def read_loggingLevel(self):
        # PROTECTED REGION ID(SKABaseDevice.loggingLevel_read) ENABLED START #
        """
        Reads logging level of the device.

        :return:  Logging level of the device.
        """
        return self._logging_level
        # PROTECTED REGION END #    //  SKABaseDevice.loggingLevel_read

    def write_loggingLevel(self, value):
        # PROTECTED REGION ID(SKABaseDevice.loggingLevel_write) ENABLED START #
        """
        Sets logging level for the device.  Both the Python logger and the
        Tango logger are updated.

        :param value: Logging level for logger

        :raises LoggingLevelError: for invalid value
        """
        try:
            lmc_logging_level = LoggingLevel(value)
        except ValueError:
            raise LoggingLevelError(
                "Invalid level - {} - must be one of {} ".format(
                    value, [v for v in LoggingLevel.__members__.values()]))

        self._logging_level = lmc_logging_level
        self.logger.setLevel(_LMC_TO_PYTHON_LOGGING_LEVEL[lmc_logging_level])
        self.logger.tango_logger.set_level(
            _LMC_TO_TANGO_LOGGING_LEVEL[lmc_logging_level]
        )
        self.logger.info('Logging level set to %s on Python and Tango loggers',
                         lmc_logging_level)
        # PROTECTED REGION END #    //  SKABaseDevice.loggingLevel_write

    def read_loggingTargets(self):
        # PROTECTED REGION ID(SKABaseDevice.loggingTargets_read) ENABLED START #
        """
        Reads the additional logging targets of the device.

        Note that this excludes the handlers provided by the ska_logging
        library defaults.

        :return:  Logging level of the device.
        """
        return [str(handler.name) for handler in self.logger.handlers]
        # PROTECTED REGION END #    //  SKABaseDevice.loggingTargets_read

    def write_loggingTargets(self, value):
        # PROTECTED REGION ID(SKABaseDevice.loggingTargets_write) ENABLED START #
        """
        Sets the additional logging targets for the device.

        Note that this excludes the handlers provided by the ska_logging
        library defaults.

        :param value: Logging targets for logger
        """
        device_name = self.get_name()
        valid_targets = LoggingUtils.sanitise_logging_targets(value,
                                                              device_name)
        LoggingUtils.update_logging_handlers(valid_targets, self.logger)
        # PROTECTED REGION END #    //  SKABaseDevice.loggingTargets_write

    def read_healthState(self):
        # PROTECTED REGION ID(SKABaseDevice.healthState_read) ENABLED START #
        """
        Reads Health State of the device.

        :return: Health State of the device
        """
        return self._health_state
        # PROTECTED REGION END #    //  SKABaseDevice.healthState_read

    def read_adminMode(self):
        # PROTECTED REGION ID(SKABaseDevice.adminMode_read) ENABLED START #
        """
        Reads Admin Mode of the device.

        :return: Admin Mode of the device
        :rtype: AdminMode
        """
        return self.state_model.admin_mode
        # PROTECTED REGION END #    //  SKABaseDevice.adminMode_read

    def write_adminMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.adminMode_write) ENABLED START #
        """
        Sets Admin Mode of the device.

        :param value: Admin Mode of the device.
        :type value: :py:class:`~ska.base.control_model.AdminMode`

        :raises ValueError: for unknown adminMode
        """
        if value == AdminMode.NOT_FITTED:
            self.state_model.perform_action("to_notfitted")
        elif value == AdminMode.OFFLINE:
            self.state_model.perform_action("to_offline")
        elif value == AdminMode.MAINTENANCE:
            self.state_model.perform_action("to_maintenance")
        elif value == AdminMode.ONLINE:
            self.state_model.perform_action("to_online")
        elif value == AdminMode.RESERVED:
            self.state_model.perform_action("to_reserved")
        else:
            raise ValueError(f"Unknown adminMode {value}")
        # PROTECTED REGION END #    //  SKABaseDevice.adminMode_write

    def read_controlMode(self):
        # PROTECTED REGION ID(SKABaseDevice.controlMode_read) ENABLED START #
        """
        Reads Control Mode of the device.

        :return: Control Mode of the device
        """
        return self._control_mode
        # PROTECTED REGION END #    //  SKABaseDevice.controlMode_read

    def write_controlMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.controlMode_write) ENABLED START #
        """
        Sets Control Mode of the device.

        :param value: Control mode value
        """
        self._control_mode = value
        # PROTECTED REGION END #    //  SKABaseDevice.controlMode_write

    def read_simulationMode(self):
        # PROTECTED REGION ID(SKABaseDevice.simulationMode_read) ENABLED START #
        """
        Reads Simulation Mode of the device.

        :return: Simulation Mode of the device.
        """
        return self._simulation_mode
        # PROTECTED REGION END #    //  SKABaseDevice.simulationMode_read

    def write_simulationMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.simulationMode_write) ENABLED START #
        """
        Sets Simulation Mode of the device

        :param value: SimulationMode
        """
        self._simulation_mode = value
        # PROTECTED REGION END #    //  SKABaseDevice.simulationMode_write

    def read_testMode(self):
        # PROTECTED REGION ID(SKABaseDevice.testMode_read) ENABLED START #
        """
        Reads Test Mode of the device.

        :return: Test Mode of the device
        """
        return self._test_mode
        # PROTECTED REGION END #    //  SKABaseDevice.testMode_read

    def write_testMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.testMode_write) ENABLED START #
        """
        Sets Test Mode of the device.

        :param value: Test Mode
        """
        self._test_mode = value
        # PROTECTED REGION END #    //  SKABaseDevice.testMode_write

    # --------
    # Commands
    # --------

    class GetVersionInfoCommand(BaseCommand):
        """
        A class for the SKABaseDevice's Reset() command.
        """
        def do(self):
            """
            Stateless hook for device GetVersionInfo() command.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device = self.target
            return [f"{device.__class__.__name__}, {device.read_buildState()}"]

    @command(dtype_out=('str',), doc_out="Version strings",)
    @DebugIt()
    def GetVersionInfo(self):
        # PROTECTED REGION ID(SKABaseDevice.GetVersionInfo) ENABLED START #
        """
        Returns the version information of the device.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: Version details of the device.
        """
        command = self.get_command_object("GetVersionInfo")
        return command()
        # PROTECTED REGION END #    //  SKABaseDevice.GetVersionInfo

    class ResetCommand(ActionCommand):
        """
        A class for the SKABaseDevice's Reset() command.
        """
        def __init__(self, target, state_model, logger=None):
            """
            Create a new ResetCommand

            :param target: the object that this command acts upon; for
                example, the SKASubarray device for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`DeviceStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, state_model, "reset", logger=logger)

        def do(self):
            """
            Stateless hook for device reset.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            device = self.target
            device._health_state = HealthState.OK
            device._control_mode = ControlMode.REMOTE
            device._simulation_mode = SimulationMode.FALSE
            device._test_mode = TestMode.NONE

            message = "Reset command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    def is_Reset_allowed(self):
        """
        Whether the ``Reset()`` command is allowed to be run in the
        current state

        :returns: whether the ``Reset()`` command is allowed to be run in the
            current state
        :rtype: boolean
        """
        command = self.get_command_object("Reset")
        return command.is_allowed()

    @command(
        dtype_out='DevVarLongStringArray',
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def Reset(self):
        """
        Reset the device from the FAULT state.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("Reset")
        (return_code, message) = command()
        return [[return_code], [message]]

    class DisableCommand(ActionCommand):
        """
        A class for the SKABaseDevice's Disable() command.
        """

        def __init__(self, target, state_model, logger=None):
            """
            Constructor for DisableCommand

            :param target: the object that this command acts upon; for
                example, the SKABaseDevice for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`DeviceStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, state_model, "disable", logger=logger)

        def do(self):
            """
            Stateless hook for Disable() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "Disable command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    def is_Disable_allowed(self):
        """
        Check if command Disable is allowed in the current device state.

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Disable")
        return command.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def Disable(self):
        """
        Put the device into disabled mode

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("Disable")
        (return_code, message) = command()
        return [[return_code], [message]]

    class StandbyCommand(ActionCommand):
        """
        A class for the SKABaseDevice's Standby() command.
        """

        def __init__(self, target, state_model, logger=None):
            """
            Constructor for StandbyCommand

            :param target: the object that this command acts upon; for
                example, the SKABaseDevice for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`DeviceStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, state_model, "standby", logger=logger)

        def do(self):
            """
            Stateless hook for Standby() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "Standby command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    def is_Standby_allowed(self):
        """
        Check if command Standby is allowed in the current device state.

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Standby")
        return command.check_allowed()

    @command(
        dtype_out='DevVarLongStringArray',
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def Standby(self):
        """
        Put the device into standby mode

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("Standby")
        (return_code, message) = command()
        return [[return_code], [message]]

    class OffCommand(ActionCommand):
        """
        A class for the SKABaseDevice's Off() command.
        """

        def __init__(self, target, state_model, logger=None):
            """
            Constructor for OffCommand

            :param target: the object that this command acts upon; for
                example, the SKABaseDevice for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`DeviceStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, state_model, "off", logger=logger)

        def do(self):
            """
            Stateless hook for Off() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "Off command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    def is_Off_allowed(self):
        """
        Check if command `Off` is allowed in the current device state.

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Off")
        return command.check_allowed()

    @command(
        dtype_out='DevVarLongStringArray',
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def Off(self):
        """
        Turn the device off

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("Off")
        (return_code, message) = command()
        return [[return_code], [message]]

    class OnCommand(ActionCommand):
        """
        A class for the SKABaseDevice's On() command.
        """

        def __init__(self, target, state_model, logger=None):
            """
            Constructor for OnCommand

            :param target: the object that this command acts upon; for
                example, the SKABaseDevice for which this class
                implements the command
            :type target: object
            :param state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type state_model: :py:class:`DeviceStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, state_model, "on", logger=logger)

        def do(self):
            """
            Stateless hook for On() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            message = "On command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    def is_On_allowed(self):
        """
        Check if command `On` is allowed in the current device state.

        :raises ``tango.DevFailed``: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("On")
        return command.check_allowed()

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def On(self):
        """
        Turn device on

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        command = self.get_command_object("On")
        (return_code, message) = command()
        return [[return_code], [message]]


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKABaseDevice.main) ENABLED START #
    """
    Main function of the SKABaseDevice module.

    :param args: positional args to tango.server.run
    :param kwargs: named args to tango.server.run
    """
    return run((SKABaseDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKABaseDevice.main


if __name__ == '__main__':
    main()
