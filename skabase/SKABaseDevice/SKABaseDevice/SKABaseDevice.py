# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#
# Distributed under the terms of the none license.
# See LICENSE.txt for more info.

""" SKABASE

A generic base device for SKA.
"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango.server import device_property
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
# Additional import
# PROTECTED REGION ID(SKABaseDevice.additionnal_import) ENABLED START #
import logging

from PyTango import DeviceProxy, DevFailed

from skabase.utils import (get_dp_command, exception_manager,
                           tango_type_conversion, coerce_value,
                           get_groups_from_json, get_tango_device_type_id)

from skabase.SKABaseDevice import release

from skabase.faults import GroupDefinitionsError

MODULE_LOGGER = logging.getLogger(__name__)
# PROTECTED REGION END #    //  SKABaseDevice.additionnal_import

__all__ = ["SKABaseDevice", "main"]


class SKABaseDevice(Device):
    """
    A generic base device for SKA.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKABaseDevice.class_variable) ENABLED START #
    def _get_device_json(self, args_dict):
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
            ### TBD - add logging
            raise

    def _parse_argin(self, argin, defaults=None, required=None):
        args_dict = defaults.copy() if defaults else {}
        try:
            if argin:
                args_dict.update(json.loads(argin))
        except ValueError as ex:
            ### TBD - add logging
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
                MODULE_LOGGER.info(str(attr_err), exc_info=True)
            except DevFailed as derr:
                MODULE_LOGGER.info(str(derr), exc_info=True)

            try:
                attr_dict['max_value'] = attrib.get_max_value()
            except AttributeError as attr_err:
                MODULE_LOGGER.info(str(attr_err), exc_info=True)
            except DevFailed as derr:
                MODULE_LOGGER.info(str(derr), exc_info=True)

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
        doc="Build state of this device",
    )

    centralLoggingLevel = attribute(
        dtype='uint16',
        access=AttrWriteType.READ_WRITE,
        doc="Current logging level to Central logging target for this device - \ninitialises to CentralLoggingLevelDefault on startup",
    )

    elementLoggingLevel = attribute(
        dtype='uint16',
        access=AttrWriteType.READ_WRITE,
        doc="Current logging level to Element logging target for this device - \ninitialises to ElementLoggingLevelDefault on startup",
    )

    storageLoggingLevel = attribute(
        dtype='uint16',
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="Current logging level to Syslog for this device - \ninitialises from  StorageLoggingLevelDefault on first execution of device.\nNeeds to be READ_WRITE To make it memorized - but writing this attribute should \ndo the same as command SetStorageLoggingLevel to ensure the targets and adjustments\nare made correctly",
    )

    healthState = attribute(
        dtype='DevEnum',
        doc="The health state reported for this device. It interprets the current device condition \nand condition of all managed devices to set this. Most possibly an aggregate attribute.",
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
    )

    adminMode = attribute(
        dtype='DevEnum',
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="The admin mode reported for this device. It may interpret the current device condition \nand condition of all managed devices to set this. Most possibly an aggregate attribute.",
        enum_labels=["ON-LINE", "OFF-LINE", "MAINTENANCE", "NOT-FITTED", "RESERVED", ],
    )

    controlMode = attribute(
        dtype='DevEnum',
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="The control mode of the device. REMOTE, LOCAL\nTANGO Device accepts only from a ‘local’ client and ignores commands and queries received from TM\nor any other ‘remote’ clients. The Local clients has to release LOCAL control before REMOTE clients\ncan take control again.",
        enum_labels=["REMOTE", "LOCAL", ],
    )

    simulationMode = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="Reports the simulation mode of the device. Some devices may implement both modes,\nwhile others will have simulators that set simulationMode to True while the real\ndevices always set simulationMode to False.",
    )

    testMode = attribute(
        dtype='str',
        access=AttrWriteType.READ_WRITE,
        memorized=True,
        doc="The test mode of the device. \nEither no test mode (empty string) or an indication of the test mode.",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # PROTECTED REGION ID(SKABaseDevice.init_device) ENABLED START #

        # Initialize attribute values.
        self._build_state = '{}, {}, {}'.format(release.name, release.version,
                                                release.description)
        self._version_id = release.version
        self._central_logging_level = 0
        self._element_logging_level = 0
        self._storage_logging_level = 0
        self._health_state = 0
        self._admin_mode = 0
        self._control_mode = 0
        self._simulation_mode = False
        self._test_mode = ""

        # create TANGO Groups objects dict, according to property
        self.debug_stream("Groups definitions: {}".format(self.GroupDefinitions))
        try:
            self.groups = get_groups_from_json(self.GroupDefinitions)
            self.info_stream("Groups loaded: {}".format(sorted(self.groups.keys())))
        except GroupDefinitionsError:
            self.info_stream("No Groups loaded for device: {}".format(
                                 self.get_name()))


        # PROTECTED REGION END #    //  SKABaseDevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKABaseDevice.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKABaseDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKABaseDevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKABaseDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_buildState(self):
        # PROTECTED REGION ID(SKABaseDevice.buildState_read) ENABLED START #
        return self._build_state
        # PROTECTED REGION END #    //  SKABaseDevice.buildState_read

    def read_versionId(self):
        # PROTECTED REGION ID(SKABaseDevice.versionId_read) ENABLED START #
        return self._version_id
        # PROTECTED REGION END #    //  SKABaseDevice.versionId_read

    def read_centralLoggingLevel(self):
        # PROTECTED REGION ID(SKABaseDevice.centralLoggingLevel_read) ENABLED START #
        return self._central_logging_level
        # PROTECTED REGION END #    //  SKABaseDevice.centralLoggingLevel_read

    def write_centralLoggingLevel(self, value):
        # PROTECTED REGION ID(SKABaseDevice.centralLoggingLevel_write) ENABLED START #
        self._central_logging_level = value
        # PROTECTED REGION END #    //  SKABaseDevice.centralLoggingLevel_write

    def read_elementLoggingLevel(self):
        # PROTECTED REGION ID(SKABaseDevice.elementLoggingLevel_read) ENABLED START #
        return self._element_logging_level
        # PROTECTED REGION END #    //  SKABaseDevice.elementLoggingLevel_read

    def write_elementLoggingLevel(self, value):
        # PROTECTED REGION ID(SKABaseDevice.elementLoggingLevel_write) ENABLED START #
        self._element_logging_level = value
        # PROTECTED REGION END #    //  SKABaseDevice.elementLoggingLevel_write

    def read_storageLoggingLevel(self):
        # PROTECTED REGION ID(SKABaseDevice.storageLoggingLevel_read) ENABLED START #
        return self._storage_logging_level
        # PROTECTED REGION END #    //  SKABaseDevice.storageLoggingLevel_read

    def write_storageLoggingLevel(self, value):
        # PROTECTED REGION ID(SKABaseDevice.storageLoggingLevel_write) ENABLED START #
        self._storage_logging_level = value
        # PROTECTED REGION END #    //  SKABaseDevice.storageLoggingLevel_write

    def read_healthState(self):
        # PROTECTED REGION ID(SKABaseDevice.healthState_read) ENABLED START #
        return self._health_state
        # PROTECTED REGION END #    //  SKABaseDevice.healthState_read

    def read_adminMode(self):
        # PROTECTED REGION ID(SKABaseDevice.adminMode_read) ENABLED START #
        return self._admin_mode
        # PROTECTED REGION END #    //  SKABaseDevice.adminMode_read

    def write_adminMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.adminMode_write) ENABLED START #
        self._admin_mode = value
        # PROTECTED REGION END #    //  SKABaseDevice.adminMode_write

    def read_controlMode(self):
        # PROTECTED REGION ID(SKABaseDevice.controlMode_read) ENABLED START #
        return self._control_mode
        # PROTECTED REGION END #    //  SKABaseDevice.controlMode_read

    def write_controlMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.controlMode_write) ENABLED START #
        self._control_mode = value
        # PROTECTED REGION END #    //  SKABaseDevice.controlMode_write

    def read_simulationMode(self):
        # PROTECTED REGION ID(SKABaseDevice.simulationMode_read) ENABLED START #
        return self._simulation_mode
        # PROTECTED REGION END #    //  SKABaseDevice.simulationMode_read

    def write_simulationMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.simulationMode_write) ENABLED START #
        self._simulation_mode = value
        # PROTECTED REGION END #    //  SKABaseDevice.simulationMode_write

    def read_testMode(self):
        # PROTECTED REGION ID(SKABaseDevice.testMode_read) ENABLED START #
        return self._test_mode
        # PROTECTED REGION END #    //  SKABaseDevice.testMode_read

    def write_testMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.testMode_write) ENABLED START #
        self._test_mode = value
        # PROTECTED REGION END #    //  SKABaseDevice.testMode_write


    # --------
    # Commands
    # --------

    @command(
    dtype_out=('str',), 
    doc_out="[ name: EltTelState ]", 
    )
    @DebugIt()
    def GetVersionInfo(self):
        # PROTECTED REGION ID(SKABaseDevice.GetVersionInfo) ENABLED START #
        return ['{}, {}'.format(self.__class__.__name__, self.read_buildState())]
        # PROTECTED REGION END #    //  SKABaseDevice.GetVersionInfo

    @command(
    )
    @DebugIt()
    def Reset(self):
        # PROTECTED REGION ID(SKABaseDevice.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKABaseDevice.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKABaseDevice.main) ENABLED START #
    return run((SKABaseDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKABaseDevice.main

if __name__ == '__main__':
    main()
