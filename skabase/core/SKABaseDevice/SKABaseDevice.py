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
# PROTECTED REGION END #    //  SKABaseDevice.additionnal_import

__all__ = ["SKABaseDevice", "main"]


class SKABaseDevice(Device):
    """
    A generic base device for SKA.
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKABaseDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKABaseDevice.class_variable

    # -----------------
    # Device Properties
    # -----------------

    SkaLevel = device_property(
        dtype='int16', default_value=4
    )

    ManagedDevices = device_property(
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

    CentralLoggingLevelDefault = device_property(
        dtype='int',
        mandatory=True
    )

    ElementLoggingLevelDefault = device_property(
        dtype='int',
        mandatory=True
    )

    StorageLoggingLevelStorage = device_property(
        dtype='int',
        mandatory=True
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
        dtype='int',
        doc="Current logging level to Central logging target for this device - \ninitialises to CentralLoggingLevelDefault on startup",
    )

    elementLoggingLevel = attribute(
        dtype='int',
        doc="Current logging level to Element logging target for this device - \ninitialises to ElementLoggingLevelDefault on startup",
    )

    storageLoggingLevel = attribute(
        dtype='int',
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

    testadd = attribute(
        dtype='double',
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
        return ''
        # PROTECTED REGION END #    //  SKABaseDevice.buildState_read

    def read_versionId(self):
        # PROTECTED REGION ID(SKABaseDevice.versionId_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  SKABaseDevice.versionId_read

    def read_centralLoggingLevel(self):
        # PROTECTED REGION ID(SKABaseDevice.centralLoggingLevel_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKABaseDevice.centralLoggingLevel_read

    def read_elementLoggingLevel(self):
        # PROTECTED REGION ID(SKABaseDevice.elementLoggingLevel_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKABaseDevice.elementLoggingLevel_read

    def read_storageLoggingLevel(self):
        # PROTECTED REGION ID(SKABaseDevice.storageLoggingLevel_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKABaseDevice.storageLoggingLevel_read

    def write_storageLoggingLevel(self, value):
        # PROTECTED REGION ID(SKABaseDevice.storageLoggingLevel_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKABaseDevice.storageLoggingLevel_write

    def read_healthState(self):
        # PROTECTED REGION ID(SKABaseDevice.healthState_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKABaseDevice.healthState_read

    def read_adminMode(self):
        # PROTECTED REGION ID(SKABaseDevice.adminMode_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKABaseDevice.adminMode_read

    def write_adminMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.adminMode_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKABaseDevice.adminMode_write

    def read_controlMode(self):
        # PROTECTED REGION ID(SKABaseDevice.controlMode_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKABaseDevice.controlMode_read

    def write_controlMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.controlMode_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKABaseDevice.controlMode_write

    def read_simulationMode(self):
        # PROTECTED REGION ID(SKABaseDevice.simulationMode_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  SKABaseDevice.simulationMode_read

    def write_simulationMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.simulationMode_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKABaseDevice.simulationMode_write

    def read_testMode(self):
        # PROTECTED REGION ID(SKABaseDevice.testMode_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  SKABaseDevice.testMode_read

    def write_testMode(self, value):
        # PROTECTED REGION ID(SKABaseDevice.testMode_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKABaseDevice.testMode_write

    def read_testadd(self):
        # PROTECTED REGION ID(SKABaseDevice.testadd_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  SKABaseDevice.testadd_read


    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKABaseDevice.main) ENABLED START #
    return run((SKABaseDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKABaseDevice.main

if __name__ == '__main__':
    main()
