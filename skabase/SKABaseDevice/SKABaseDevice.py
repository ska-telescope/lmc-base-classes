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
import os
import sys
import json
import logging
import logging.handlers
from logging.handlers import SysLogHandler
from future.utils import with_metaclass

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

# Initialize logging
logging.basicConfig()
# PROTECTED REGION END #    //  SKABaseDevice.additionnal_imports

__all__ = ["SKABaseDevice", "main"]

class SKABaseDevice(with_metaclass(DeviceMeta, Device)):
    """
    A generic base device for SKA.
    """
    # PROTECTED REGION ID(SKABaseDevice.class_variable) ENABLED START #

    def _init_syslog(self):
        """
        Method to initialize Syslog for logging. If Syslog service is not available
        then logs are stored into a file.

        :parameter: None

        :return: None
        """
        try:
            self.logger = logging.getLogger(__name__)
            #self.syslogs = SysLogHandler(address='/dev/log', facility='syslog')
            self.syslogs = SysLogHandler(address='/var/run/rsyslog/dev/log', facility='syslog')
            self.formatter = logging.Formatter('%(name)s: %(levelname)s %(module)s %(message)r')
            self.syslogs.setFormatter(self.formatter)
            self.logger.addHandler(self.syslogs)
        except Exception:
            self.error_stream("Syslog cannot be initialized:")

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
        args_dict = defaults.copy() if defaults else {}configurepoll
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
        # for index in range(len(attr_list)):
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

        :param dev_log_msg: DevString
            Message to log

        :param dev_log_level: DevEnum
            Logging level of the message. The message can have one of the following
            logging level.
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

    CentralLoggingTarget = device_property(
        dtype='str',
    )

    ElementLoggingTarget = device_property(
        dtype='str',
    )

    StorageLoggingTarget = device_property(
        dtype='str', default_value="localhost"
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

    centralLoggingLevel = attribute(
        dtype='uint16',
        access=AttrWriteType.READ_WRITE,
        doc="Current logging level to Central logging target for this device - "
            "\ninitialises to CentralLoggingLevelDefault on startup",
    )

    elementLoggingLevel = attribute(
        dtype='uint16',
        access=AttrWriteType.READ_WRITE,
        doc="Current logging level to Element logging target for this device - "
            "\ninitialises to ElementLoggingLevelDefault on startup",
    )

    storageLoggingLevel = attribute(
        dtype='uint16',
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="Current logging level to Syslog for this device - "
            "initialises from  StorageLoggingLevelDefault on first "
            "execution of device.Needs to be READ_WRITE To make it"
            " memorized - but writing this attribute should do the "
            "same as command SetStorageLoggingLevel to ensure the "
            "targets and adjustmentsare made correctly",
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

        # Start sysLogHandler
        self._init_syslog()

        # Initialize attribute values.
        self._build_state = '{}, {}, {}'.format(release.name, release.version,
                                                release.description)
        self._version_id = release.version
        self._central_logging_level = int(tango.LogLevel.LOG_OFF)
        self._element_logging_level = int(tango.LogLevel.LOG_OFF)
        self._storage_logging_level = int(tango.LogLevel.LOG_OFF)
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

    def read_centralLoggingLevel(self):
        # PROTECTED REGION ID(SKABaseDevice.centralLoggingLevel_read) ENABLED START #
        """
        Reads the central logging level of the device.
        :return: Central logging level of the device
        """
        return self._central_logging_level
        # PROTECTED REGION END #    //  SKABaseDevice.centralLoggingLevel_read

    def write_centralLoggingLevel(self, value):
        # PROTECTED REGION ID(SKABaseDevice.centralLoggingLevel_write) ENABLED START #
        """
        Sets central logging level of the device
        :param value: Logging level for Central Logger
        :return: None
        """
        self._central_logging_level = value
        # PROTECTED REGION END #    //  SKABaseDevice.centralLoggingLevel_write

    def read_elementLoggingLevel(self):
        # PROTECTED REGION ID(SKABaseDevice.elementLoggingLevel_read) ENABLED START #
        """
        Reads element logging level of the device.
        :return: Element logging level of the device.
        """
        return self._element_logging_level
        # PROTECTED REGION END #    //  SKABaseDevice.elementLoggingLevel_read

    def write_elementLoggingLevel(self, value):
        # PROTECTED REGION ID(SKABaseDevice.elementLoggingLevel_write) ENABLED START #
        """
        Sets element logging level of the device
        :param value: Logging Level for Element Logger
        :return: None
        """
        self._element_logging_level = value
        # PROTECTED REGION END #    //  SKABaseDevice.elementLoggingLevel_write

    def read_storageLoggingLevel(self):
        # PROTECTED REGION ID(SKABaseDevice.storageLoggingLevel_read) ENABLED START #
        """
        Reads storage logging level of the device.
        :return: Storage logging level of the device.
        """
        return self._storage_logging_level
        # PROTECTED REGION END #    //  SKABaseDevice.storageLoggingLevel_read

    def write_storageLoggingLevel(self, value):
        # PROTECTED REGION ID(SKABaseDevice.storageLoggingLevel_write) ENABLED START #
        """
        Sets logging level at storage.
        :param value: Logging Level for storage logger
        :return:
        """
        self._storage_logging_level = value
        if self._storage_logging_level == int(tango.LogLevel.LOG_FATAL):
            self.logger.setLevel(logging.FATAL)
        elif self._storage_logging_level == int(tango.LogLevel.LOG_ERROR):
            self.logger.setLevel(logging.ERROR)
        elif self._storage_logging_level == int(tango.LogLevel.LOG_WARN):
            self.logger.setLevel(logging.WARNING)
        elif self._storage_logging_level == int(tango.LogLevel.LOG_INFO):
            self.logger.setLevel(logging.INFO)
        elif self._storage_logging_level == int(tango.LogLevel.LOG_DEBUG):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.DEBUG)
        # PROTECTED REGION END #    //  SKABaseDevice.storageLoggingLevel_write

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
