# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#

"""
This module implements a generic base model and device for SKA.

It exposes the generic attributes, properties and commands of an SKA
device.
"""
# PROTECTED REGION ID(SKABaseDevice.additionnal_import) ENABLED START #
# Standard imports
import enum
import inspect
import logging
import logging.handlers
import socket
import sys
import threading
import typing
import warnings

from functools import partial
from urllib.parse import urlparse
from urllib.request import url2pathname

# Tango imports
from tango import AttrWriteType, DebugIt, DevState
from tango.server import run, Device, attribute, command, device_property

# SKA specific imports
import debugpy
import ska_ser_logging
from ska_tango_base import release
from ska_tango_base.base import AdminModeModel, OpStateModel, BaseComponentManager
from ska_tango_base.commands import (
    BaseCommand,
    CompletionCommand,
    StateModelCommand,
    ResponseCommand,
    ResultCode,
)
from ska_tango_base.control_model import (
    AdminMode,
    ControlMode,
    SimulationMode,
    TestMode,
    HealthState,
    LoggingLevel,
)

from ska_tango_base.utils import get_groups_from_json
from ska_tango_base.faults import (
    GroupDefinitionsError,
    LoggingTargetError,
    LoggingLevelError,
)

LOG_FILE_SIZE = 1024 * 1024  # Log file size 1MB.
_DEBUGGER_PORT = 5678


class _Log4TangoLoggingLevel(enum.IntEnum):
    """
    Python enumerated type for Tango log4tango logging levels.

    This is different to tango.LogLevel, and is required if using
    a device's set_log_level() method.  It is not currently exported
    via PyTango, so we hard code it here in the interim.

    Source:
       https://gitlab.com/tango-controls/cppTango/blob/
       4feffd7c8e24b51c9597a40b9ef9982dd6e99cdf/log4tango/include/log4tango/Level.hh#L86-93
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
        return "<{} {} (Python {}, Tango {})>".format(
            self.__class__.__name__, name, python_level, tango_level
        )


class LoggingUtils:
    """
    Utility functions to aid logger configuration.

    These functions are encapsulated in class to aid testing - it
    allows dependent functions to be mocked.
    """

    @staticmethod
    def sanitise_logging_targets(targets, device_name):
        """
        Validate and return logging targets '<type>::<name>' strings.

        :param targets:
            List of candidate logging target strings, like '<type>[::<name>]'
            Empty and whitespace-only strings are ignored.  Can also be None.

        :param device_name:
            Tango device name, like 'domain/family/member', used
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
                            target_type, list(default_target_names.keys())
                        )
                    )
                if not target_name:
                    target_name = default_target_names[target_type]
                if not target_name:
                    raise LoggingTargetError(
                        "Target name required for type {}".format(target_type)
                    )
                valid_target = "{}::{}".format(target_type, target_name)
                valid_targets.append(valid_target)

        return valid_targets

    @staticmethod
    def get_syslog_address_and_socktype(url):
        """
        Parse syslog URL and extract address and socktype parameters for SysLogHandler.

        :param url: Universal resource locator string for syslog target.
            Three types are supported: file path, remote UDP server,
            remote TCP server.

            - Output to a file: 'file://<path to file>'. For example,
              'file:///dev/log' will write to '/dev/log'.

            - Output to remote server over UDP:
              'udp://<hostname>:<port>'. For example,
              'udp://syslog.com:514' will send to host 'syslog.com' on
              UDP port 514

            - Output to remote server over TCP:
              'tcp://<hostname>:<port>'. For example,
              'tcp://rsyslog.com:601' will send to host 'rsyslog.com' on
              TCP port 601

            For backwards compatibility, if the protocol prefix is
            missing, the type is interpreted as file. This is
            deprecated. For example, '/dev/log' is equivalent to
            'file:///dev/log'.

        :return: An (address, socktype) tuple.

            For file types:

            - the address is the file path as as string

            - socktype is None

            For UDP and TCP:

            - the address is tuple of (hostname, port), with hostname a
              string, and port an integer.

            - socktype is socket.SOCK_DGRAM for UDP, or
              socket.SOCK_STREAM for TCP.

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
                    "Invalid syslog URL - could not extract hostname from '{}'".format(
                        url
                    )
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
            socktype = (
                socket.SOCK_DGRAM if parsed.scheme == "udp" else socket.SOCK_STREAM
            )
        else:
            raise LoggingTargetError(
                "Invalid syslog URL - expected file, udp or tcp protocol scheme in '{}'".format(
                    url
                )
            )
        return address, socktype

    @staticmethod
    def create_logging_handler(target, tango_logger=None):
        """
        Create a Python log handler based on the target type.

        Supported target types are "console", "file", "syslog", "tango".

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
                "Invalid target requested - missing '::' separator: {}".format(target)
            )
        if target_type == "console":
            handler = logging.StreamHandler(sys.stdout)
        elif target_type == "file":
            log_file_name = target_name
            handler = logging.handlers.RotatingFileHandler(
                log_file_name, "a", LOG_FILE_SIZE, 2, None, False
            )
        elif target_type == "syslog":
            address, socktype = LoggingUtils.get_syslog_address_and_socktype(
                target_name
            )
            handler = logging.handlers.SysLogHandler(
                address=address,
                facility=logging.handlers.SysLogHandler.LOG_SYSLOG,
                socktype=socktype,
            )
        elif target_type == "tango":
            if tango_logger:
                handler = TangoLoggingServiceHandler(tango_logger)
            else:
                raise LoggingTargetError(
                    "Missing tango_logger instance for 'tango' target type"
                )
        else:
            raise LoggingTargetError(
                "Invalid target type requested: '{}' in '{}'".format(
                    target_type, target
                )
            )
        formatter = ska_ser_logging.get_default_formatter(tags=True)
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
                handler = LoggingUtils.create_logging_handler(
                    target, logger.tango_logger
                )
                logger.addHandler(handler)

        logger.info("Logging targets set to %s", targets)


# PROTECTED REGION END #    //  SKABaseDevice.additionnal_import


__all__ = ["SKABaseDevice", "main"]


class SKABaseDevice(Device):
    """A generic base device for SKA."""

    _global_debugger_listening = False
    _global_debugger_allocated_port = 0

    class InitCommand(ResponseCommand, CompletionCommand):
        """A class for the SKABaseDevice's init_device() "command"."""

        def __init__(self, target, op_state_model, logger=None):
            """
            Create a new InitCommand.

            :param target: the object that this command acts upon; for
                example, the SKABaseDevice device for which this class
                implements the command
            :type target: object
            :param op_state_model: the state model that this command
                 uses to check that it is allowed to run, and that it
                 drives with actions.
            :type op_state_model: :py:class:`OpStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, op_state_model, "init", logger=logger)

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

            device._build_state = "{}, {}, {}".format(
                release.name, release.version, release.description
            )
            device._version_id = release.version
            device._methods_patched_for_debugger = False

            try:
                # create Tango Groups dict, according to property
                self.logger.debug(
                    "Groups definitions: {}".format(device.GroupDefinitions)
                )
                device.groups = get_groups_from_json(device.GroupDefinitions)
                self.logger.info(
                    "Groups loaded: {}".format(sorted(device.groups.keys()))
                )
            except GroupDefinitionsError:
                self.logger.debug(
                    "No Groups loaded for device: {}".format(device.get_name())
                )

            message = "SKABaseDevice Init command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    _logging_config_lock = threading.Lock()
    _logging_configured = False

    def _init_logging(self):
        """Initialize the logging mechanism, using default properties."""

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
                ska_ser_logging.configure_logging(tags_filter=EnsureTagsFilter)
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
        self.logger.debug("Logger initialised")

        # monkey patch Tango Logging Service streams so they go to the Python
        # logger instead
        def _debug_patch(*args,source,**kwargs):
            self.logger.debug(*args, **kwargs)

        self.debug_stream = _debug_patch

        def _info_patch(*args,source,**kwargs):
            self.logger.info(*args, **kwargs)

        self.info_stream = _info_patch

        def _warn_patch(*args,source,**kwargs):
            self.logger.warning(*args, **kwargs)

        self.warn_stream = _warn_patch

        def _error_patch(*args,source,**kwargs):
            self.logger.error(*args, **kwargs)

        self.error_stream = _error_patch

        def _fatal_patch(*args,source,**kwargs):
            self.logger.critical(*args, **kwargs)

        self.fatal_stream = _fatal_patch

    # PROTECTED REGION END #    //  SKABaseDevice.class_variable

    # -----------------
    # Device Properties
    # -----------------

    SkaLevel = device_property(dtype="int16", default_value=4)
    """
    Device property.

    Indication of importance of the device in the SKA hierarchy
    to support drill-down navigation: 1..6, with 1 highest.
    """

    GroupDefinitions = device_property(
        dtype=("str",),
    )
    """
    Device property.

    Each string in the list is a JSON serialised dict defining the ``group_name``,
    ``devices`` and ``subgroups`` in the group.  A Tango Group object is created
    for each item in the list, according to the hierarchy defined.  This provides
    easy access to the managed devices in bulk, or individually.

    The general format of the list is as follows, with optional ``devices`` and
    ``subgroups`` keys::

        [ {"group_name": "<name>",
           "devices": ["<dev name>", ...]},
          {"group_name": "<name>",
           "devices": ["<dev name>", "<dev name>", ...],
           "subgroups" : [{<nested group>},
                            {<nested group>}, ...]},
          ...
          ]

    For example, a hierarchy of racks, servers and switches::

        [ {"group_name": "servers",
           "devices": ["elt/server/1", "elt/server/2",
                         "elt/server/3", "elt/server/4"]},
          {"group_name": "switches",
           "devices": ["elt/switch/A", "elt/switch/B"]},
          {"group_name": "pdus",
           "devices": ["elt/pdu/rackA", "elt/pdu/rackB"]},
          {"group_name": "racks",
           "subgroups": [
                {"group_name": "rackA",
                 "devices": ["elt/server/1", "elt/server/2",
                               "elt/switch/A", "elt/pdu/rackA"]},
                {"group_name": "rackB",
                 "devices": ["elt/server/3", "elt/server/4",
                               "elt/switch/B", "elt/pdu/rackB"],
                 "subgroups": []}
           ]} ]

    """

    LoggingLevelDefault = device_property(
        dtype="uint16", default_value=LoggingLevel.INFO
    )
    """
    Device property.

    Default logging level at device startup.
    See :py:class:`~ska_tango_base.control_model.LoggingLevel`
    """

    LoggingTargetsDefault = device_property(
        dtype="DevVarStringArray", default_value=["tango::logger"]
    )
    """
    Device property.

    Default logging targets at device startup.
    See the project readme for details.
    """

    # ----------
    # Attributes
    # ----------

    buildState = attribute(
        dtype="str",
        doc="Build state of this device",
    )
    """Device attribute."""

    versionId = attribute(
        dtype="str",
        doc="Version Id of this device",
    )
    """Device attribute."""

    loggingLevel = attribute(
        dtype=LoggingLevel,
        access=AttrWriteType.READ_WRITE,
        doc="Current logging level for this device - "
        "initialises to LoggingLevelDefault on startup",
    )
    """
    Device attribute.

    See :py:class:`~ska_tango_base.control_model.LoggingLevel`
    """

    loggingTargets = attribute(
        dtype=("str",),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4,
        doc="Logging targets for this device, excluding ska_ser_logging defaults"
        " - initialises to LoggingTargetsDefault on startup",
    )
    """Device attribute."""

    healthState = attribute(
        dtype=HealthState,
        doc="The health state reported for this device. "
        "It interprets the current device"
        " condition and condition of all managed devices to set this. "
        "Most possibly an aggregate attribute.",
    )
    """Device attribute."""

    adminMode = attribute(
        dtype=AdminMode,
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        hw_memorized=True,
        doc="The admin mode reported for this device. It may interpret the current "
        "device condition and condition of all managed devices to set this. "
        "Most possibly an aggregate attribute.",
    )
    """Device attribute."""

    controlMode = attribute(
        dtype=ControlMode,
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        hw_memorized=True,
        doc="The control mode of the device. REMOTE, LOCAL"
        "\nTango Device accepts only from a ‘local’ client and ignores commands and "
        "queries received from TM or any other ‘remote’ clients. The Local clients"
        " has to release LOCAL control before REMOTE clients can take control again.",
    )
    """Device attribute."""

    simulationMode = attribute(
        dtype=SimulationMode,
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        hw_memorized=True,
        doc="Reports the simulation mode of the device. \nSome devices may implement "
        "both modes, while others will have simulators that set simulationMode "
        "to True while the real devices always set simulationMode to False.",
    )
    """Device attribute."""

    testMode = attribute(
        dtype=TestMode,
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        hw_memorized=True,
        doc="The test mode of the device. \n"
        "Either no test mode or an "
        "indication of the test mode.",
    )
    """Device attribute."""

    # ---------------
    # General methods
    # ---------------

    def _update_admin_mode(self, admin_mode):
        """
        Perform Tango operations in response to a change in admin mode.

        This helper method is passed to the admin mode model as a
        callback, so that the model can trigger actions in the Tango
        device.

        :param admin_mode: the new admin_mode value
        :type admin_mode: :py:class:`~ska_tango_base.control_model.AdminMode`
        """
        self.push_change_event("adminMode", admin_mode)
        self.push_archive_event("adminMode", admin_mode)

    def _update_state(self, state):
        """
        Perform Tango operations in response to a change in op state.

        This helper method is passed to the op state model as a
        callback, so that the model can trigger actions in the Tango
        device.

        :param state: the new state value
        :type state: :py:class:`tango.DevState`
        """
        if state != self.get_state():
            self.logger.info(f"Device state changed from {self.get_state()} to {state}")
            self.set_state(state)
            self.set_status(f"The device is in {state} state.")

    def set_state(self, state):
        """
        Set the device state, ensuring that change events are pushed.

        :param state: the new state
        :type state: :py:class:`tango.DevState`
        """
        super().set_state(state)
        self.push_change_event("state")
        self.push_archive_event("state")

    def set_status(self, status):
        """
        Set the device status, ensuring that change events are pushed.

        :param status: the new status
        :type status: str
        """
        super().set_status(status)
        self.push_change_event("status")
        self.push_archive_event("status")

    def init_device(self):
        """
        Initialise the tango device after startup.

        Subclasses that have no need to override the default
        implementation of state management may leave ``init_device()``
        alone.  Override the ``do()`` method on the nested class
        ``InitCommand`` instead.
        """
        try:
            super().init_device()

            self._init_logging()
            self._init_state_model()
            self.component_manager = self.create_component_manager()
            self.InitCommand(self, self.op_state_model, self.logger)()
            self.init_command_objects()
        except Exception as exc:
            self.set_state(DevState.FAULT)
            self.set_status("The device is in FAULT state - init_device failed.")
            if hasattr(self, "logger"):
                self.logger.exception("init_device() failed.")
            else:
                print(f"ERROR: init_device failed, and no logger: {exc}.")

    def _init_state_model(self):
        """Initialise the state model for the device."""
        self.op_state_model = OpStateModel(
            logger=self.logger,
            callback=self._update_state,
        )
        self.admin_mode_model = AdminModeModel(
            logger=self.logger,
            callback=self._update_admin_mode,
        )

    def create_component_manager(self):
        """Create and return a component manager for this device."""
        return BaseComponentManager(self.op_state_model)

    def register_command_object(self, command_name, command_object):
        """
        Register an object as a handler for a command.

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
        Return the command object (handler) for a given command.

        :param command_name: name of the command for which a command
            object (handler) is sought
        :type command_name: str

        :return: the registered command object (handler) for the command
        :rtype: Command instance
        """
        return self._command_objects[command_name]

    def init_command_objects(self):
        """Register command objects (handlers) for this device's commands."""
        self._command_objects = {}

        component_args = (self.component_manager, self.op_state_model, self.logger)
        self.register_command_object("Standby", self.StandbyCommand(*component_args))
        self.register_command_object("Off", self.OffCommand(*component_args))
        self.register_command_object("On", self.OnCommand(*component_args))
        self.register_command_object("Reset", self.ResetCommand(*component_args))

        device_args = (self, self.op_state_model, self.logger)
        self.register_command_object(
            "GetVersionInfo", self.GetVersionInfoCommand(*device_args)
        )
        self.register_command_object(
            "DebugDevice", self.DebugDeviceCommand(*device_args)
        )

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKABaseDevice.always_executed_hook) ENABLED START #
        """
        Perform actions that are executed before every device command.

        This is a Tango hook.
        """
        # PROTECTED REGION END #    //  SKABaseDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKABaseDevice.delete_device) ENABLED START #
        """
        Clean up any resources prior to device deletion.

        This method is a Tango hook that is called by the device
        destructor and by the device Init command. It allows for any
        memory or other resources allocated in the init_device method to
        be released prior to device deletion.
        """
        # PROTECTED REGION END #    //  SKABaseDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_buildState(self):
        # PROTECTED REGION ID(SKABaseDevice.buildState_read) ENABLED START #
        """
        Read the Build State of the device.

        :return: the build state of the device
        """
        return self._build_state
        # PROTECTED REGION END #    //  SKABaseDevice.buildState_read

    def read_versionId(self):
        # PROTECTED REGION ID(SKABaseDevice.versionId_read) ENABLED START #
        """
        Read the Version Id of the device.

        :return: the version id of the device
        """
        return self._version_id
        # PROTECTED REGION END #    //  SKABaseDevice.versionId_read

    def read_loggingLevel(self):
        # PROTECTED REGION ID(SKABaseDevice.loggingLevel_read) ENABLED START #
        """
        Read the logging level of the device.

        :return:  Logging level of the device.
        """
        return self._logging_level
        # PROTECTED REGION END #    //  SKABaseDevice.loggingLevel_read

    def write_loggingLevel(self, value):
        # PROTECTED REGION ID(SKABaseDevice.loggingLevel_write) ENABLED START #
        """
        Set the logging level for the device.

        Both the Python logger and the Tango logger are updated.

        :param value: Logging level for logger

        :raises LoggingLevelError: for invalid value
        """
        try:
            lmc_logging_level = LoggingLevel(value)
        except ValueError:
            raise LoggingLevelError(
                "Invalid level - {} - must be one of {} ".format(
                    value, [v for v in LoggingLevel.__members__.values()]
                )
            )

        self._logging_level = lmc_logging_level
        self.logger.setLevel(_LMC_TO_PYTHON_LOGGING_LEVEL[lmc_logging_level])
        self.logger.tango_logger.set_level(
            _LMC_TO_TANGO_LOGGING_LEVEL[lmc_logging_level]
        )
        self.logger.info(
            "Logging level set to %s on Python and Tango loggers", lmc_logging_level
        )
        # PROTECTED REGION END #    //  SKABaseDevice.loggingLevel_write

    def read_loggingTargets(self):
        # PROTECTED REGION ID(SKABaseDevice.loggingTargets_read) ENABLED START #
        """
        Read the additional logging targets of the device.

        Note that this excludes the handlers provided by the ska_ser_logging
        library defaults.

        :return:  Logging level of the device.
        """
        return [str(handler.name) for handler in self.logger.handlers]
        # PROTECTED REGION END #    //  SKABaseDevice.loggingTargets_read

    def write_loggingTargets(self, value):
        # PROTECTED REGION ID(SKABaseDevice.loggingTargets_write) ENABLED START #
        """
        Set the additional logging targets for the device.

        Note that this excludes the handlers provided by the ska_ser_logging
        library defaults.

        :param value: Logging targets for logger
        """
        device_name = self.get_name()
        valid_targets = LoggingUtils.sanitise_logging_targets(value, device_name)
        LoggingUtils.update_logging_handlers(valid_targets, self.logger)
        # PROTECTED REGION END #    //  SKABaseDevice.loggingTargets_write

    def read_healthState(self):
        # PROTECTED REGION ID(SKABaseDevice.healthState_read) ENABLED START #
        """
        Read the Health State of the device.

        :return: Health State of the device
        """
        return self._health_state
        # PROTECTED REGION END #    //  SKABaseDevice.healthState_read

    def read_adminMode(self):
        # PROTECTED REGION ID(SKABaseDevice.adminMode_read) ENABLED START #
        """
        Read the Admin Mode of the device.

        :return: Admin Mode of the device
        :rtype: AdminMode
        """
        return self.admin_mode_model.admin_mode
        # PROTECTED REGION END #    //  SKABaseDevice.adminMode_read

    def write_adminMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.adminMode_write) ENABLED START #
        """
        Set the Admin Mode of the device.

        :param value: Admin Mode of the device.
        :type value: :py:class:`~ska_tango_base.control_model.AdminMode`

        :raises ValueError: for unknown adminMode
        """
        if value == AdminMode.NOT_FITTED:
            self.admin_mode_model.perform_action("to_notfitted")
        elif value == AdminMode.OFFLINE:
            self.admin_mode_model.perform_action("to_offline")
            if self.component_manager.is_communicating:
                self.component_manager.stop_communicating()
        elif value == AdminMode.MAINTENANCE:
            self.admin_mode_model.perform_action("to_maintenance")
            if not self.component_manager.is_communicating:
                self.component_manager.start_communicating()
        elif value == AdminMode.ONLINE:
            self.admin_mode_model.perform_action("to_online")
            if not self.component_manager.is_communicating:
                self.component_manager.start_communicating()
        elif value == AdminMode.RESERVED:
            self.admin_mode_model.perform_action("to_reserved")
        else:
            raise ValueError(f"Unknown adminMode {value}")
        # PROTECTED REGION END #    //  SKABaseDevice.adminMode_write

    def read_controlMode(self):
        # PROTECTED REGION ID(SKABaseDevice.controlMode_read) ENABLED START #
        """
        Read the Control Mode of the device.

        :return: Control Mode of the device
        """
        return self._control_mode
        # PROTECTED REGION END #    //  SKABaseDevice.controlMode_read

    def write_controlMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.controlMode_write) ENABLED START #
        """
        Set the Control Mode of the device.

        :param value: Control mode value
        """
        self._control_mode = value
        # PROTECTED REGION END #    //  SKABaseDevice.controlMode_write

    def read_simulationMode(self):
        # PROTECTED REGION ID(SKABaseDevice.simulationMode_read) ENABLED START #
        """
        Read the Simulation Mode of the device.

        :return: Simulation Mode of the device.
        """
        return self._simulation_mode
        # PROTECTED REGION END #    //  SKABaseDevice.simulationMode_read

    def write_simulationMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.simulationMode_write) ENABLED START #
        """
        Set the Simulation Mode of the device.

        :param value: SimulationMode
        """
        self._simulation_mode = value
        # PROTECTED REGION END #    //  SKABaseDevice.simulationMode_write

    def read_testMode(self):
        # PROTECTED REGION ID(SKABaseDevice.testMode_read) ENABLED START #
        """
        Read the Test Mode of the device.

        :return: Test Mode of the device
        """
        return self._test_mode
        # PROTECTED REGION END #    //  SKABaseDevice.testMode_read

    def write_testMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.testMode_write) ENABLED START #
        """
        Set the Test Mode of the device.

        :param value: Test Mode
        """
        self._test_mode = value
        # PROTECTED REGION END #    //  SKABaseDevice.testMode_write

    # --------
    # Commands
    # --------

    class GetVersionInfoCommand(BaseCommand):
        """A class for the SKABaseDevice's GetVersionInfo() command."""

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

    @command(
        dtype_out=("str",),
        doc_out="Version strings",
    )
    @DebugIt()
    def GetVersionInfo(self):
        # PROTECTED REGION ID(SKABaseDevice.GetVersionInfo) ENABLED START #
        """
        Return the version information of the device.

        To modify behaviour for this command, modify the do() method of
        the command class.

        :return: Version details of the device.
        """
        command = self.get_command_object("GetVersionInfo")
        return command()
        # PROTECTED REGION END #    //  SKABaseDevice.GetVersionInfo

    class ResetCommand(StateModelCommand, ResponseCommand):
        """A class for the SKABaseDevice's Reset() command."""

        def __init__(self, target, op_state_model, logger=None):
            """
            Create a new ResetCommand.

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the state model that this command
                uses to check that it is allowed to run, and that it
                drives with actions.
            :type op_state_model: :py:class:`OpStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, op_state_model, "reset", logger=logger)

        def do(self):
            """
            Stateless hook for device reset.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            self.target.reset()
            message = "Reset command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    def is_Reset_allowed(self):
        """
        Whether the ``Reset()`` command is allowed to be run in the current state.

        :returns: whether the ``Reset()`` command is allowed to be run in the
            current state
        :rtype: boolean
        """
        command = self.get_command_object("Reset")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_out="DevVarLongStringArray",
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

    class StandbyCommand(StateModelCommand, ResponseCommand):
        """A class for the SKABaseDevice's Standby() command."""

        def __init__(self, target, op_state_model, logger=None):
            """
            Initialise a new StandbyCommand instance.

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type op_state_model: :py:class:`OpStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, op_state_model, "standby", logger=logger)

        def do(self):
            """
            Stateless hook for Standby() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            self.target.standby()
            message = "Standby command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    def is_Standby_allowed(self):
        """
        Check if command Standby is allowed in the current device state.

        :raises :py:exc:`CommandError`: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Standby")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def Standby(self):
        """
        Put the device into standby mode.

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

    class OffCommand(StateModelCommand, ResponseCommand):
        """A class for the SKABaseDevice's Off() command."""

        def __init__(self, target, op_state_model, logger=None):
            """
            Initialise a new OffCommand instance.

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type op_state_model: :py:class:`OpStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, op_state_model, "off", logger=logger)

        def do(self):
            """
            Stateless hook for Off() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            self.target.off()
            message = "Off command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    def is_Off_allowed(self):
        """
        Check if command `Off` is allowed in the current device state.

        :raises :py:exc:`CommandError`: if the command is not allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("Off")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def Off(self):
        """
        Turn the device off.

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

    class OnCommand(StateModelCommand, ResponseCommand):
        """A class for the SKABaseDevice's On() command."""

        def __init__(self, target, op_state_model, logger=None):
            """
            Initialise a new OnCommand instance.

            :param target: the object that this command acts upon; for
                example, the device's component manager
            :type target: object
            :param op_state_model: the state model that this command uses
                 to check that it is allowed to run, and that it drives
                 with actions.
            :type op_state_model: :py:class:`OpStateModel`
            :param logger: the logger to be used by this Command. If not
                provided, then a default module logger will be used.
            :type logger: a logger that implements the standard library
                logger interface
            """
            super().__init__(target, op_state_model, "on", logger=logger)

        def do(self):
            """
            Stateless hook for On() command functionality.

            :return: A tuple containing a return code and a string
                message indicating status. The message is for
                information purpose only.
            :rtype: (ResultCode, str)
            """
            self.target.on()
            message = "On command completed OK"
            self.logger.info(message)
            return (ResultCode.OK, message)

    def is_On_allowed(self):
        """
        Check if command `On` is allowed in the current device state.

        :raises :py:exc:`CommandError`: if the command is not
            allowed

        :return: ``True`` if the command is allowed
        :rtype: boolean
        """
        command = self.get_command_object("On")
        return command.is_allowed(raise_if_disallowed=True)

    @command(
        dtype_out="DevVarLongStringArray",
        doc_out="(ReturnType, 'informational message')",
    )
    @DebugIt()
    def On(self):
        """
        Turn device on.

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

    class DebugDeviceCommand(BaseCommand):
        """A class for the SKABaseDevice's DebugDevice() command."""

        def do(self):
            """
            Stateless hook for device DebugDevice() command.

            Starts the ``debugpy`` debugger listening for remote connections
            (via Debugger Adaptor Protocol), and patches all methods so that
            they can be debugged.

            If the debugger is already listening, additional execution of this
            command will trigger a breakpoint.

            :return: The TCP port the debugger is listening on.
            :rtype: DevUShort
            """
            if not SKABaseDevice._global_debugger_listening:
                allocated_port = self.start_debugger_and_get_port(_DEBUGGER_PORT)
                SKABaseDevice._global_debugger_listening = True
                SKABaseDevice._global_debugger_allocated_port = allocated_port
            device = self.target
            if not device._methods_patched_for_debugger:
                self.monkey_patch_all_methods_for_debugger()
                device._methods_patched_for_debugger = True
            else:
                self.logger.warning("Triggering debugger breakpoint...")
                debugpy.breakpoint()
            return SKABaseDevice._global_debugger_allocated_port

        def start_debugger_and_get_port(self, port):
            """Start the debugger and return the allocated port."""
            self.logger.warning("Starting debugger...")
            interface, allocated_port = debugpy.listen(("0.0.0.0", port))
            self.logger.warning(
                f"Debugger listening on {interface}:{allocated_port}. Performance may be degraded."
            )
            return allocated_port

        def monkey_patch_all_methods_for_debugger(self):
            """Monkeypatch methods that need to be patched for the debugger."""
            all_methods = self.get_all_methods()
            patched = []
            for owner, name, method in all_methods:
                if self.method_must_be_patched_for_debugger(owner, method):
                    self.patch_method_for_debugger(owner, name, method)
                    patched.append(
                        f"{owner} {method.__func__.__qualname__} in {method.__func__.__module__}"
                    )
            self.logger.info("Patched %s of %s methods", len(patched), len(all_methods))
            self.logger.debug("Patched methods: %s", sorted(patched))

        def get_all_methods(self):
            """Return a list of the device's methods."""
            methods = []
            device = self.target
            for name, method in inspect.getmembers(device, inspect.ismethod):
                methods.append((device, name, method))
            for command_object in device._command_objects.values():
                for name, method in inspect.getmembers(
                    command_object, inspect.ismethod
                ):
                    methods.append((command_object, name, method))
            return methods

        @staticmethod
        def method_must_be_patched_for_debugger(owner, method):
            """
            Determine if methods are worth debugging.

            The goal is to find all the user's Python methods, but not
            the lower level PyTango device and Boost extension methods.
            The `typing.types.FunctionType` check excludes the Boost
            methods.
            """
            skip_module_names = ["tango.device_server", "tango.server", "logging"]
            skip_owner_types = [SKABaseDevice.DebugDeviceCommand]
            return (
                isinstance(method.__func__, typing.types.FunctionType)
                and method.__func__.__module__ not in skip_module_names
                and type(owner) not in skip_owner_types
            )

        def patch_method_for_debugger(self, owner, name, method):
            """
            Ensure method calls trigger the debugger.

            Most methods in a device are executed by calls from threads
            spawned by the cppTango layer.  These threads are not known
            to Python, so we have to explicitly inform the debugger
            about them.
            """

            def debug_thread_wrapper(orig_method, *args, **kwargs):
                debugpy.debug_this_thread()
                return orig_method(*args, **kwargs)

            patched_method = partial(debug_thread_wrapper, method)
            setattr(owner, name, patched_method)

    @command(
        dtype_out="DevUShort", doc_out="The TCP port the debugger is listening on."
    )
    @DebugIt()
    def DebugDevice(self):
        """
        Enable remote debugging of this device.

        To modify behaviour for this command, modify the do() method of
        the command class: :py:class:`.DebugDeviceCommand`.
        """
        command = self.get_command_object("DebugDevice")
        return command()


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKABaseDevice.main) ENABLED START #
    """
    Launch an SKABaseDevice device.

    :param args: positional args to tango.server.run
    :param kwargs: named args to tango.server.run
    """
    return run((SKABaseDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKABaseDevice.main


if __name__ == "__main__":
    main()
