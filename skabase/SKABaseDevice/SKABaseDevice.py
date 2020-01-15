# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#

"""A generic base device for SKA. It exposes the generic attributes,
properties and commands of an SKA device.
"""
# PROTECTED REGION ID(SKABaseDevice.additionnal_import) ENABLED START #
# Standard imports
import enum
import json
import logging
import logging.handlers
import os
import sys
import threading

from future.utils import with_metaclass

# Tango imports
import tango
from tango import DebugIt
from tango.server import run, Device, DeviceMeta, attribute, command, device_property
from tango import AttrQuality, AttrWriteType
from tango import DeviceProxy, DevFailed

# SKA specific imports
import ska_logging
from skabase import release
file_path = os.path.dirname(os.path.abspath(__file__))
auxiliary_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/auxiliary"
sys.path.insert(0, auxiliary_path)

from utils import (get_dp_command,
                   coerce_value,
                   get_groups_from_json,
                   get_tango_device_type_id)
from faults import (GroupDefinitionsError,
                    LoggingTargetError,
                    LoggingLevelError)

LOG_FILE_SIZE = 1024 * 1024  # Log file size 1MB.


class TangoLoggingLevel(enum.IntEnum):
    """Python enumerated type for TANGO logging levels.

    There is a tango.LogLevel type already, but this is a wrapper around
    a C++ enum.  The Python IntEnum type is more convenient.
    """
    OFF = int(tango.LogLevel.LOG_OFF)
    FATAL = int(tango.LogLevel.LOG_FATAL)
    ERROR = int(tango.LogLevel.LOG_ERROR)
    WARNING = int(tango.LogLevel.LOG_WARN)
    INFO = int(tango.LogLevel.LOG_INFO)
    DEBUG = int(tango.LogLevel.LOG_DEBUG)


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


class LoggingUtils:
    """Utility functions to aid logger configuration.

    These functions are encapsulated in class to aid testing - it
    allows dependent functions to be mocked.
    """

    @staticmethod
    def sanitise_logging_targets(targets, device_name):
        """Validate and return logging targets '<type>::<name>' strings.

        :param target:
            List of candidate logging target strings, like '<type>[::<name>]'
            Empty and whitespace-only strings are ignored.

        :param device_name:
            TANGO device name, like 'domain/family/member', used
            for the default file name

        :return: list of '<type>::<name>' strings, with default name, if applicable

        :raises: LoggingTargetError for invalid target string that cannot be corrected
        """
        default_target_names = {
            "console": "cout",
            "file": "{}.log".format(device_name.replace("/", "_")),
            "syslog": None}

        valid_targets = []
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
    def create_logging_handler(target):
        """Create a Python log handler based on the target type (console, file, syslog)

        :param target: Logging target for logger, <type>::<name>

        :return: StreamHandler, RotatingFileHandler, or SysLogHandler

        :raises: LoggingTargetError for invalid target string
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
            handler = logging.handlers.SysLogHandler(
                    address=target_name, facility=logging.handlers.SysLogHandler.LOG_SYSLOG)
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
                handler = LoggingUtils.create_logging_handler(target)
                logger.addHandler(handler)

        logger.info('Logging targets set to %s', targets)



# PROTECTED REGION END #    //  SKABaseDevice.additionnal_import


__all__ = ["SKABaseDevice", "TangoLoggingLevel", "main"]


class SKABaseDevice(with_metaclass(DeviceMeta, Device)):
    """
    A generic base device for SKA.
    """
    # PROTECTED REGION ID(SKABaseDevice.class_variable) ENABLED START #

    _logging_config_lock = threading.Lock()
    _logging_configured = False

    def _init_logging(self):
        """
        This method initializes the logging mechanism, based on default properties.

        :param: None.

        :return: None.
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

        # initialise using defaults in device properties
        self._logging_level = None
        self.write_loggingLevel(self.LoggingLevelDefault)
        self.write_loggingTargets(self.LoggingTargetsDefault)
        self.logger.debug('Logger initialised')

        # Monkey patch TANGO Logging System streams so they go to the Python
        # logger instead
        self.debug_stream = self.logger.debug
        self.info_stream = self.logger.info
        self.warn_stream = self.logger.warning
        self.error_stream = self.logger.error
        self.fatal_stream = self.logger.critical

    def _parse_argin(self, argin, defaults=None, required=None):
        """
        Parses the argument passed to it and returns them in a dictionary form.

        :param argin: The argument to parse

        :param defaults:

        :param required:

        :return: Dictionary containing passed arguments.
        """
        args_dict = defaults.copy() if defaults else {}
        try:
            if argin:
                args_dict.update(json.loads(argin))
        except ValueError as ex:
            self.logger.fatal(str(ex), exc_info=True)
            raise

        missing_args = []
        if required:
            missing_args = set(required) - set(args_dict.keys())
        if missing_args:
            msg = ("Missing arguments: {}"
                   .format(', '.join([str(m_arg) for m_arg in missing_args])))
            raise Exception(msg)
        return args_dict

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
        dtype='uint16', default_value=4
    )

    LoggingTargetsDefault = device_property(
        dtype='DevVarStringArray', default_value=[]
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
        dtype=TangoLoggingLevel,
        access=AttrWriteType.READ_WRITE,
        doc="Current logging level for this device - "
            "initialises to LoggingLevelDefault on startup",
    )

    loggingTargets = attribute(
        dtype=('str',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=3,
        doc="Logging targets for this device, excluding ska_logging defaults"
            " - initialises to LoggingTargetsDefault on startup",
    )

    healthState = attribute(
        dtype='DevEnum',
        doc="The health state reported for this device. "
            "It interprets the current device"
            " condition and condition of all managed devices to set this. "
            "Most possibly an aggregate attribute.",
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
    )

    adminMode = attribute(
        dtype='DevEnum',
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="The admin mode reported for this device. It may interpret the current "
            "device condition and condition of all managed devices to set this. "
            "Most possibly an aggregate attribute.",
        enum_labels=["ON-LINE", "OFF-LINE", "MAINTENANCE", "NOT-FITTED", "RESERVED", ],
    )

    controlMode = attribute(
        dtype='DevEnum',
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="The control mode of the device. REMOTE, LOCAL"
            "\nTANGO Device accepts only from a ‘local’ client and ignores commands and "
            "queries received from TM or any other ‘remote’ clients. The Local clients"
            " has to release LOCAL control before REMOTE clients can take control again.",
        enum_labels=["REMOTE", "LOCAL", ],
    )

    simulationMode = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="Reports the simulation mode of the device. \nSome devices may implement "
            "both modes, while others will have simulators that set simulationMode "
            "to True while the real devices always set simulationMode to False.",
    )

    testMode = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="The test mode of the device. \n"
            "Either no test mode (empty string) or an "
            "indication of the test mode.",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """
        Method that initializes the tango device after startup.
        :return: None
        """
        Device.init_device(self)
        # PROTECTED REGION ID(SKABaseDevice.init_device) ENABLED START #

        self._init_logging()

        # Initialize attribute values.
        self._build_state = '{}, {}, {}'.format(release.name, release.version,
                                                release.description)
        self._version_id = release.version
        self._health_state = 0
        self._admin_mode = 0
        self._control_mode = 0
        self._simulation_mode = False
        self._test_mode = ""

        try:
            # create TANGO Groups objects dict, according to property
            self.debug_stream("Groups definitions: {}".format(self.GroupDefinitions))
            self.groups = get_groups_from_json(self.GroupDefinitions)
            self.info_stream("Groups loaded: {}".format(sorted(self.groups.keys())))

        except GroupDefinitionsError:
            self.info_stream("No Groups loaded for device: {}".format(self.get_name()))

        self.logger.info("Completed SKABaseDevice.init_device")
        # PROTECTED REGION END #    //  SKABaseDevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKABaseDevice.always_executed_hook) ENABLED START #
        """
        Method that is always executed before any device command gets executed.

        :return: None
        """
        # PROTECTED REGION END #    //  SKABaseDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKABaseDevice.delete_device) ENABLED START #
        """
        Method to cleanup when device is stopped.

        :return: None
        """
        # PROTECTED REGION END #    //  SKABaseDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_buildState(self):
        # PROTECTED REGION ID(SKABaseDevice.buildState_read) ENABLED START #
        """
        Reads the Build State of the device.

        :return: None
        """
        return self._build_state
        # PROTECTED REGION END #    //  SKABaseDevice.buildState_read

    def read_versionId(self):
        # PROTECTED REGION ID(SKABaseDevice.versionId_read) ENABLED START #
        """
        Reads the Version Id of the device.

        :return: None
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

        :return: None.
        """
        self._logging_level = TangoLoggingLevel(value)
        tango_logger = self.get_logger()
        if self._logging_level == TangoLoggingLevel.OFF:
            self.logger.setLevel(logging.CRITICAL)  # not allowed to be "off"
            tango_logger.set_level(_Log4TangoLoggingLevel.OFF)
        elif self._logging_level == TangoLoggingLevel.FATAL:
            self.logger.setLevel(logging.CRITICAL)
            tango_logger.set_level(_Log4TangoLoggingLevel.FATAL)
        elif self._logging_level == TangoLoggingLevel.ERROR:
            self.logger.setLevel(logging.ERROR)
            tango_logger.set_level(_Log4TangoLoggingLevel.ERROR)
        elif self._logging_level == TangoLoggingLevel.WARNING:
            self.logger.setLevel(logging.WARNING)
            tango_logger.set_level(_Log4TangoLoggingLevel.WARN)
        elif self._logging_level == TangoLoggingLevel.INFO:
            self.logger.setLevel(logging.INFO)
            tango_logger.set_level(_Log4TangoLoggingLevel.INFO)
        elif self._logging_level == TangoLoggingLevel.DEBUG:
            self.logger.setLevel(logging.DEBUG)
            tango_logger.set_level(_Log4TangoLoggingLevel.DEBUG)
        else:
            raise LoggingLevelError(
                "Invalid level - {} - must be between {} and {}".format(
                    self._logging_level, TangoLoggingLevel.OFF, TangoLoggingLevel.DEBUG))
        self.logger.info('Logging level set to %s on Python and Tango loggers', self._logging_level)
        # PROTECTED REGION END #    //  SKABaseDevice.loggingLevel_write

    def read_loggingTargets(self):
        # PROTECTED REGION ID(SKABaseDevice.loggingTargets_read) ENABLED START #
        """
        Reads logging level of the device.

        :return:  Logging level of the device.
        """
        return [str(handler.name) for handler in self.logger.handlers]
        # PROTECTED REGION END #    //  SKABaseDevice.loggingTargets_read

    def write_loggingTargets(self, value):
        # PROTECTED REGION ID(SKABaseDevice.loggingTargets_write) ENABLED START #
        """
        Sets logging level for the device.

        :param value: Logging targets for logger

        :return: None.
        """
        device_name = self.get_name()
        valid_targets = LoggingUtils.sanitise_logging_targets(value, device_name)
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
        """
        return self._admin_mode
        # PROTECTED REGION END #    //  SKABaseDevice.adminMode_read

    def write_adminMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.adminMode_write) ENABLED START #
        """
        Sets Admin Mode of the device.

        :param value: Admin Mode of the device.

        :return: None
        """
        self._admin_mode = value
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

        :return: None
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

        :return: None
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

        :return: None
        """
        self._test_mode = value
        # PROTECTED REGION END #    //  SKABaseDevice.testMode_write


    # --------
    # Commands
    # --------

    @command(dtype_out=('str',), doc_out="[ name: EltTelState ]",)
    @DebugIt()
    def GetVersionInfo(self):
        # PROTECTED REGION ID(SKABaseDevice.GetVersionInfo) ENABLED START #
        """
        Returns the version information of the device.

        :return: Version version details of the device.
        """
        return ['{}, {}'.format(self.__class__.__name__, self.read_buildState())]
        # PROTECTED REGION END #    //  SKABaseDevice.GetVersionInfo

    @command(
    )
    @DebugIt()
    def Reset(self):
        # PROTECTED REGION ID(SKABaseDevice.Reset) ENABLED START #
        """
        Reset device to its default state.

        :return: None
        """
        # PROTECTED REGION END #    //  SKABaseDevice.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKABaseDevice.main) ENABLED START #
    """
    Main function of the SKABaseDevice module.

    :param args: None

    :param kwargs:

    :return:
    """
    return run((SKABaseDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKABaseDevice.main

if __name__ == '__main__':
    main()
