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
import time

from future.utils import with_metaclass
from logging import StreamHandler
from logging.handlers import SysLogHandler
from logging.handlers import RotatingFileHandler

# Tango imports
import tango
from tango import DebugIt
from tango.server import run, Device, DeviceMeta, attribute, command, device_property
from tango import AttrQuality, AttrWriteType
from tango import DeviceProxy, DevFailed

# SKA specific imports
from skabase import release
file_path = os.path.dirname(os.path.abspath(__file__))
auxiliary_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/auxiliary"
sys.path.insert(0, auxiliary_path)

from utils import (get_dp_command,
                   coerce_value,
                   get_groups_from_json,
                   get_tango_device_type_id)

from faults import GroupDefinitionsError

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


def _create_logging_handler(target, device_name):
    """Create a Python log handler based on the target type (console, file, syslog)

    :param target: Logging target for logger, <type>::<name>

    :param device_name: TANGO device name

    :return: StreamHandler, RotatingFileHandler, or SysLogHandler
    """
    target_type, target_name = target.split("::", 1)

    class UTCFormatter(logging.Formatter):
        converter = time.gmtime

    # Format defined here:
    #   https://developer.skatelescope.org/en/latest/development/logging-format.html
    # VERSION "|" TIMESTAMP "|" SEVERITY "|" [THREAD-ID] "|" [FUNCTION] "|" [LINE-LOC] "|"
    #   [TAGS] "|" MESSAGE LF
    formatter = UTCFormatter(
        fmt="1|%(asctime)s.%(msecs)03dZ|"
            "%(levelname)s|%(threadName)s|"
            "%(module)s.%(funcName)s|"
            "%(filename)s#%(lineno)d|tango-device:{}|"
            "%(message)s".format(device_name),
        datefmt='%Y-%m-%dT%H:%M:%S')

    if target_type == "console":
        handler = StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
    elif target_type == "file":
        log_file_name = target_name
        handler = RotatingFileHandler(log_file_name, 'a', LOG_FILE_SIZE, 2, None, False)
        handler.setFormatter(formatter)
    elif target_type == "syslog":
        handler = SysLogHandler(address=target_name, facility='syslog')
        handler.setFormatter(formatter)
    return handler


# PROTECTED REGION END #    //  SKABaseDevice.additionnal_import


__all__ = ["SKABaseDevice", "TangoLoggingLevel", "main"]


class SKABaseDevice(with_metaclass(DeviceMeta, Device)):
    """
    A generic base device for SKA.
    """
    # PROTECTED REGION ID(SKABaseDevice.class_variable) ENABLED START #

    def _init_logging(self):
        """
        This method initializes the logging mechanism, based on default properties.

        :param: None.

        :return: None.
        """
        self.logger = logging.getLogger(__name__)
        # device may be reinitialised, so remove existing handlers
        if hasattr(self, '_logging_handlers'):
            for handler in self._logging_handlers:
                self.logger.removeHandler(handler)
        # initialise using defaults in device properties
        self._logging_level = None
        self._logging_targets = []
        self._logging_handlers = {}
        self.write_loggingLevel(self.LoggingLevelDefault)
        self.write_loggingTargets(self.LoggingTargetsDefault)

        # Monkey patch TANGO Logging System streams so they go to the Python
        # logger instead
        self.debug_stream = self.logger.debug
        self.info_stream = self.logger.info
        self.warn_stream = self.logger.warning
        self.error_stream = self.logger.error
        self.fatal_stream = self.logger.critical

    def _get_device_json(self, args_dict):
        """
        Returns device configuration in JSON format.

        :param args_dict:

        :return: Device configuration parameters in JSON form
        """
        try:

            device_dict = {
                'component': self.get_name(),
            }
            if args_dict.get('with_metrics') or args_dict.get('with_attributes'):
                device_dict['attributes'] = self.get_device_attributes(
                    with_value=args_dict.get('with_value'),
                    with_metrics=args_dict.get('with_metrics'),
                    with_attributes=args_dict.get('with_attributes'),
                    with_context=False
                ),
            if args_dict.get('with_commands') is True:
                device_dict['commands'] = self.get_device_commands(with_context=False)
            return device_dict

        except Exception as ex:
            self.logger.fatal(str(ex), exc_info=True)
            raise

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

    def get_device_commands(self, with_context=True):
        """ Get device proxy commands"""
        ### TBD - Why use DeviceProxy?
        ### Can this not be known through self which is a Device
        commands = []
        device_proxy = DeviceProxy(self.get_name())
        cmd_config_list = device_proxy.command_list_query()
        for device_cmd_config in cmd_config_list:
            commands.append(get_dp_command(
                device_proxy.dev_name(), device_cmd_config, with_context))
        return commands

    def get_device_attributes(self, with_value=False,
                              with_context=True, with_metrics=True,
                              with_attributes=True, attribute_name=None):
        """ Get device attributes"""

        multi_attribute = self.get_device_attr()
        attr_list = multi_attribute.get_attribute_list()

        attributes = {}

        # Cannot loop over the attr_list object (not python-wrapped): raises TypeError:
        # No to_python (by-value) converter found for C++ type: Tango::Attribute*
        for index in range(len(attr_list)):
            attrib = attr_list[index]
            attr_name = attrib.get_name()
            if attribute_name is not None:
                if attr_name != attribute_name:
                    continue

            attr_dict = {
                'name': attr_name,
                'polling_frequency': attrib.get_polling_period()
            }

            try:
                attr_dict['min_value'] = attrib.get_min_value()
            except AttributeError as attr_err:
                self.logger.info(str(attr_err), exc_info=True)
            except DevFailed as derr:
                self.logger.info(str(derr), exc_info=True)

            try:
                attr_dict['max_value'] = attrib.get_max_value()
            except AttributeError as attr_err:
                self.logger.info(str(attr_err), exc_info=True)
            except DevFailed as derr:
                self.logger.info(str(derr), exc_info=True)

            attr_dict['readonly'] = (
                attrib.get_writable() not in [AttrWriteType.READ_WRITE,
                                              AttrWriteType.WRITE,
                                              AttrWriteType.READ_WITH_WRITE])

            # TODO (KM 2017-10-30): Add the data type of the attribute in the dict.

            if with_context:
                device_type, device_id = get_tango_device_type_id(self.get_name())
                attr_dict['component_type'] = device_type
                attr_dict['component_id'] = device_id


            if with_value:
                # To get the values for the State and Status attributes, we need to call
                # their get methods, respectively. The device does not implement the
                # read_<attribute_name> methods for them.
                if attr_name in ['State', 'Status']:
                    attr_dict['value'] = coerce_value(
                        getattr(self, 'get_{}'.format(attr_name.lower()))())
                else:
                    attr_dict['value'] = coerce_value(
                        getattr(self, 'read_{}'.format(attr_name))())

                attr_dict['is_alarm'] = attrib.get_quality == AttrQuality.ATTR_ALARM

            # Define attribute type
            if attr_name in self.MetricList:
                attr_dict['attribute_type'] = 'metric'
            else:
                attr_dict['attribute_type'] = 'attribute'

            # Add to return attribute dict
            if (with_metrics and attr_dict['attribute_type'] == 'metric' or
                    with_attributes and attr_dict['attribute_type'] == 'attribute'):
                attributes[attr_name] = attr_dict

        return attributes

    def dev_logging(self, dev_log_msg, dev_log_level):
        """
        This method logs the message to SKA Element Logger, Central Logger and Storage
        Logger.

        :param dev_log_msg: DevString.

        Message to log

        :param dev_log_level: DevEnum

            Logging level of the message. The message can have one of the following
            logging level:
                LOG_FATAL

                LOG_ERROR

                LOG_WARN

                LOG_INFO

                LOG_DEBUG

        :return: None
        """
        # Element Level Logging
        if self._element_logging_level >= int(tango.LogLevel.LOG_FATAL) and dev_log_level == int(
                tango.LogLevel.LOG_FATAL):
            self.fatal_stream(dev_log_msg)
        elif self._element_logging_level >= int(tango.LogLevel.LOG_ERROR) and dev_log_level == int(
                tango.LogLevel.LOG_ERROR):
            self.error_stream(dev_log_msg)
        elif self._element_logging_level >= int(tango.LogLevel.LOG_WARN) and dev_log_level == int(
                tango.LogLevel.LOG_WARN):
            self.warn_stream(dev_log_msg)
        elif self._element_logging_level >= int(tango.LogLevel.LOG_INFO) and dev_log_level == int(
                tango.LogLevel.LOG_INFO):
            self.info_stream(dev_log_msg)
        elif self._element_logging_level >= int(tango.LogLevel.LOG_DEBUG) and dev_log_level == int(
                tango.LogLevel.LOG_DEBUG):
            self.debug_stream(dev_log_msg)

        # Central Level Logging
        if self._central_logging_level >= int(tango.LogLevel.LOG_FATAL) and dev_log_level == int(
                tango.LogLevel.LOG_FATAL):
            self.fatal_stream(dev_log_msg)
        elif self._central_logging_level >= int(tango.LogLevel.LOG_ERROR) and dev_log_level == int(
                tango.LogLevel.LOG_ERROR):
            self.error_stream(dev_log_msg)
        elif self._central_logging_level >= int(tango.LogLevel.LOG_WARN) and dev_log_level == int(
                tango.LogLevel.LOG_WARN):
            self.warn_stream(dev_log_msg)
        elif self._central_logging_level >= int(tango.LogLevel.LOG_INFO) and dev_log_level == int(
                tango.LogLevel.LOG_INFO):
            self.info_stream(dev_log_msg)
        elif self._central_logging_level >= int(tango.LogLevel.LOG_DEBUG) and dev_log_level == int(
                tango.LogLevel.LOG_DEBUG):
            self.debug_stream(dev_log_msg)

        # Storage Level Logging
        if self._storage_logging_level >= int(tango.LogLevel.LOG_FATAL) and dev_log_level == int(
                tango.LogLevel.LOG_FATAL):
            self.logger.fatal(dev_log_msg)
        elif self._storage_logging_level >= int(tango.LogLevel.LOG_ERROR) and dev_log_level == int(
                tango.LogLevel.LOG_ERROR):
            self.logger.error(dev_log_msg)
        elif self._storage_logging_level >= int(tango.LogLevel.LOG_WARN) and dev_log_level == int(
                tango.LogLevel.LOG_WARN):
            self.logger.warning(dev_log_msg)
        elif self._storage_logging_level >= int(tango.LogLevel.LOG_INFO) and dev_log_level == int(
                tango.LogLevel.LOG_INFO):
            self.logger.info(dev_log_msg)
        elif self._storage_logging_level >= int(tango.LogLevel.LOG_DEBUG) and dev_log_level == int(
                tango.LogLevel.LOG_DEBUG):
            self.logger.debug(dev_log_msg)
        else:
            pass


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
        dtype='uint16', default_value=int(TangoLoggingLevel.INFO)
    )

    LoggingTargetsDefault = device_property(
        dtype='DevVarStringArray', default_value=["console::cout"]
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
        doc="Current logging targets for this device"
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
        print("***INIT DEVICE***")
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

        self.logger.info("Completed init_device")
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
        Sets logging level for the device.

        :param value: Logging level for logger

        :return: None.
        """
        self._logging_level = TangoLoggingLevel(value)
        if self._logging_level == tango.LogLevel.LOG_OFF:
            self.logger.setLevel(logging.CRITICAL)  # not allowed to be "off"
        elif self._logging_level == tango.LogLevel.LOG_FATAL:
            self.logger.setLevel(logging.CRITICAL)
        elif self._logging_level == tango.LogLevel.LOG_ERROR:
            self.logger.setLevel(logging.ERROR)
        elif self._logging_level == tango.LogLevel.LOG_WARN:
            self.logger.setLevel(logging.WARNING)
        elif self._logging_level == tango.LogLevel.LOG_INFO:
            print("set logging level to INFO")
            self.logger.setLevel(logging.INFO)
        elif self._logging_level == tango.LogLevel.LOG_DEBUG:
            self.logger.setLevel(logging.DEBUG)
        else:
            raise ValueError(
                "Invalid level - {} - must be between {} and {}".format(
                    TangoLoggingLevel.OFF, TangoLoggingLevel.DEBUG))
        # PROTECTED REGION END #    //  SKABaseDevice.loggingLevel_write

    def read_loggingTargets(self):
        # PROTECTED REGION ID(SKABaseDevice.loggingTargets_read) ENABLED START #
        """
        Reads logging level of the device.

        :return:  Logging level of the device.
        """
        return self._logging_targets
        # PROTECTED REGION END #    //  SKABaseDevice.loggingTargets_read

    def write_loggingTargets(self, value):
        # PROTECTED REGION ID(SKABaseDevice.loggingTargets_write) ENABLED START #
        """
        Sets logging level for the device.

        :param value: Logging targets for logger

        :return: None.
        """
        new_targets = value
        # validate types
        default_target_names = {
            "console": "cout",
            "file": "{}.log".format(self.get_name().replace("/", "_")),
            "syslog": None}
        for index, target in enumerate(new_targets):
            if "::" in target:
                target_type, target_name = target.split("::", 1)
            else:
                target_type = target
                target_name = default_target_names.get(target_type, None)
                new_targets[index] = "{}::{}".format(target_type, target_name)
            if target_type not in default_target_names:
                raise ValueError(
                    "Invalid target type: {} - options are {}".format(
                        target_type, list(default_target_names.keys())))
            if not target_name:
                raise ValueError(
                    "Target name required for type {}".format(target_type))

        # update logging targets / handlers
        old_targets = self._logging_targets
        added_targets = set(new_targets) - set(old_targets)
        removed_targets = set(old_targets) - set(new_targets)

        for target in removed_targets:
            handler = self._logging_handlers.pop(target)
            self.logger.removeHandler(handler)
        for target in added_targets:
            handler = _create_logging_handler(target, self.get_name())
            self.logger.addHandler(handler)
            self._logging_handlers[target] = handler

        self._logging_targets = new_targets
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
    # Do basic logging config before starting any threads
    logging.basicConfig()
    return run((SKABaseDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKABaseDevice.main

if __name__ == '__main__':
    main()
