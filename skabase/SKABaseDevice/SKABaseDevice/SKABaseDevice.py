# -*- coding: utf-8 -*-
#
# This file is part of the SKABaseDevice project
#
#
#
# Distributed under the terms of the GPL license.
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
import json

from PyTango import DeviceProxy

from skabase.utils import (get_dp_command, exception_manager,
                           tango_type_conversion, coerce_value)

# PROTECTED REGION END #    //  SKABaseDevice.additionnal_import

__all__ = ["SKABaseDevice", "main"]


class SKABaseDevice(Device):
    """
    A generic base device for SKA.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKABaseDevice.class_variable) ENABLED START #

    def __init__(self, *args, **kwargs):
        """Initialize attribute values."""
        super(SKABaseDevice, self).__init__(*args, **kwargs)

        self._build_state = " "
        self._version_id = " "
        self._central_logging_level = 0
        self._element_logging_level = 0
        self._storage_logging_level = 0
        self._health_state = 0
        self._admin_mode = 0
        self._control_mode = 0
        self._simulation_mode = False
        self._test_mode = " "


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
        """ Get device proxy attributes"""
        ### TBD - Why use DeviceProxy?
        ### Can this not be known through self which is a Device

        # Get attribute configuration
        device_proxy = DeviceProxy(self.get_name())
        if attribute_name is not None:
            attr_config = device_proxy.get_attribute_config_ex(attribute_name)
        else:
            attr_config = device_proxy.get_attribute_config_ex(
                device_proxy.get_attribute_list())

        # Get attribute values if required
        if with_value and attribute_name is not None:
            attr_values = device_proxy.read_attributes([attribute_name])
        elif with_value:
            attr_values = device_proxy.read_attributes(device_proxy.get_attribute_list())

        # Process all attributes
        attributes = {}
        for i, attr in enumerate(attr_config):

            # Populate dictionary with attribute configuration conversion
            attr_dict = {
                'name': attr.name,
                'polling_frequency': attr.events.per_event.period,
                'min_value': (attr.min_value if attr.min_value != 'Not specified'
                              else None),
                'max_value': (attr.max_value if attr.min_value != 'Not specified'
                              else None),
                'readonly': attr.writable not in [PyTango.AttrWriteType.READ_WRITE,
                                                  PyTango.AttrWriteType.WRITE,
                                                  PyTango.AttrWriteType.READ_WITH_WRITE]
            }

            # Convert data type
            if attr.data_format == PyTango.AttrDataFormat.SCALAR:
                attr_dict["data_type"] = tango_type_conversion.get(
                    attr.data_type, str(attr.data_type))
            else:
                # Data types we aren't really going to represent
                attr_dict["data_type"] = "other"

            # Add context if required
            if with_context:
                attr_dict['component'] = self.get_name()

            # Add value if required
            if with_value:
                attr_dict['value'] = coerce_value(attr_values[i].value)
                attr_dict['is_alarm'] = attr_values[i].quality == AttrQuality.ATTR_ALARM
                # ts = datetime.fromtimestamp(attr_values[i].time.tv_sec)
                # ts.replace(microsecond=attr_values[i].time.tv_usec)
                # attr_dict['timestamp'] = ts.isoformat()

            # Define attribute type
            if attr.name in self.MetricList:
                attr_dict['attribute_type'] = 'metric'
            else:
                attr_dict['attribute_type'] = 'attribute'

            # Add to return attribute list
            if with_metrics and attr_dict['attribute_type'] == 'metric':
                attributes[attr.name] = attr_dict
            elif with_attributes and attr_dict['attribute_type'] == 'attribute':
                attributes[attr.name] = attr_dict

        return attributes

    # PROTECTED REGION END #    //  SKABaseDevice.class_variable

    # -----------------
    # Device Properties
    # -----------------

    SkaLevel = device_property(
        dtype='int16', default_value=4
    )

    MetricList = device_property(
        dtype='str', default_value="healthState,adminMode,controlMode"
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
        doc="The control mode of the device. REMOTE, LOCAL\nTANGO Device accepts only from a ?local? client and ignores commands and queries received from TM\nor any other ?remote? clients. The Local clients has to release LOCAL control before REMOTE clients\ncan take control again.",
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
    dtype_out='str', 
    )
    @DebugIt()
    def GetMetrics(self):
        # PROTECTED REGION ID(SKABaseDevice.GetMetrics) ENABLED START #
        ### TBD - read the value of each of the attributes in the MetricList
        with exception_manager(self):
            args_dict = {'with_value': False, 'with_commands': False,
                         'with_metrics': True, 'with_attributes': False}
            device_dict = self._get_device_json(args_dict)
            argout = json.dumps(device_dict)

        return argout
        # PROTECTED REGION END #    //  SKABaseDevice.GetMetrics

    @command(
    dtype_in='str', 
    doc_in="Requests the JSON string representing this device, can be filtered \nby with_commands, with_metrics, with_attributes and \nwith_value. Defaults for empty string  argin are:\n{`with_value`:false, `with_commands`:true,\n  `with_metrics`:true, `with_attributes`:false}", 
    dtype_out='str', 
    doc_out="The JSON string representing this device, \nfiltered as per the input argument flags", 
    )
    @DebugIt()
    def ToJson(self, argin):
        # PROTECTED REGION ID(SKABaseDevice.ToJson) ENABLED START #

        # TBD - see how to use fandango's export_device_to_dict
        with exception_manager(self):
            defaults = {'with_value': False, 'with_commands': True,
                        'with_metrics': True, 'with_attributes': False}
            args_dict = self._parse_argin(argin, defaults=defaults)
            device_dict = self._get_device_json(args_dict)
            argout = json.dumps(device_dict)
        return argout
        # PROTECTED REGION END #    //  SKABaseDevice.ToJson

    @command(
    dtype_out=('str',), 
    doc_out="[ name: EltTelState ]", 
    )
    @DebugIt()
    def GetVersionInfo(self):
        # PROTECTED REGION ID(SKABaseDevice.GetVersionInfo) ENABLED START #
        return [""]
        # PROTECTED REGION END #    //  SKABaseDevice.GetVersionInfo

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKABaseDevice.main) ENABLED START #
    return run((SKABaseDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKABaseDevice.main

if __name__ == '__main__':
    main()
