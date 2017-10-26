# -*- coding: utf-8 -*-
#
# This file is part of the PDU project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" PDU

Ref (Reference Elt) PDU device
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
from SKABaseDevice import SKABaseDevice
# Additional import
# PROTECTED REGION ID(PDU.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  PDU.additionnal_import

__all__ = ["PDU", "main"]


class PDU(SKABaseDevice):
    """
    Ref (Reference Elt) PDU device
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(PDU.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  PDU.class_variable

    # -----------------
    # Device Properties
    # -----------------










    # ----------
    # Attributes
    # ----------

    system_voltage = attribute(
        dtype='float',
    )

    system_current = attribute(
        dtype='float',
    )

    port_1_name = attribute(
        dtype='str',
    )

    port_2_name = attribute(
        dtype='str',
    )

    port_3_name = attribute(
        dtype='str',
    )

    port_4_name = attribute(
        dtype='str',
    )

    port_5_name = attribute(
        dtype='str',
    )

    port_6_name = attribute(
        dtype='str',
    )

    port_8_name = attribute(
        dtype='str',
    )

    port_9_name = attribute(
        dtype='str',
    )

    port_10_name = attribute(
        dtype='str',
    )

    port_11_name = attribute(
        dtype='str',
    )

    port_12_name = attribute(
        dtype='str',
    )

    port_12_current = attribute(
        dtype='float',
    )

    port_1_current = attribute(
        dtype='float',
    )

    port_2_current = attribute(
        dtype='float',
    )

    port_3_current = attribute(
        dtype='float',
    )

    port_4_current = attribute(
        dtype='float',
    )

    port_5_current = attribute(
        dtype='float',
    )

    port_6_current = attribute(
        dtype='float',
    )

    port_7_current = attribute(
        dtype='float',
    )

    port_8_current = attribute(
        dtype='float',
    )

    port_9_current = attribute(
        dtype='float',
    )

    port_10_current = attribute(
        dtype='float',
    )

    port_11_current = attribute(
        dtype='float',
    )

    port_7_name = attribute(
        dtype='str',
    )

    port_1_enabled = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
    )

    port_2_enabled = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
    )

    port_3_enabled = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
    )

    port_4_enabled = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
    )

    port_5_enabled = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
    )

    port_6_enabled = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
    )

    port_7_enabled = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
    )

    port_8_enabled = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
    )

    port_9_enabled = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
    )

    port_10_enabled = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
    )

    port_11_enabled = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
    )

    port_12_enabled = attribute(
        dtype='bool',
        access=AttrWriteType.READ_WRITE,
    )











    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(PDU.init_device) ENABLED START #
        # PROTECTED REGION END #    //  PDU.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(PDU.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(PDU.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_system_voltage(self):
        # PROTECTED REGION ID(PDU.system_voltage_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.system_voltage_read

    def read_system_current(self):
        # PROTECTED REGION ID(PDU.system_current_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.system_current_read

    def read_port_1_name(self):
        # PROTECTED REGION ID(PDU.port_1_name_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  PDU.port_1_name_read

    def read_port_2_name(self):
        # PROTECTED REGION ID(PDU.port_2_name_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  PDU.port_2_name_read

    def read_port_3_name(self):
        # PROTECTED REGION ID(PDU.port_3_name_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  PDU.port_3_name_read

    def read_port_4_name(self):
        # PROTECTED REGION ID(PDU.port_4_name_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  PDU.port_4_name_read

    def read_port_5_name(self):
        # PROTECTED REGION ID(PDU.port_5_name_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  PDU.port_5_name_read

    def read_port_6_name(self):
        # PROTECTED REGION ID(PDU.port_6_name_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  PDU.port_6_name_read

    def read_port_8_name(self):
        # PROTECTED REGION ID(PDU.port_8_name_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  PDU.port_8_name_read

    def read_port_9_name(self):
        # PROTECTED REGION ID(PDU.port_9_name_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  PDU.port_9_name_read

    def read_port_10_name(self):
        # PROTECTED REGION ID(PDU.port_10_name_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  PDU.port_10_name_read

    def read_port_11_name(self):
        # PROTECTED REGION ID(PDU.port_11_name_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  PDU.port_11_name_read

    def read_port_12_name(self):
        # PROTECTED REGION ID(PDU.port_12_name_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  PDU.port_12_name_read

    def read_port_12_current(self):
        # PROTECTED REGION ID(PDU.port_12_current_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.port_12_current_read

    def read_port_1_current(self):
        # PROTECTED REGION ID(PDU.port_1_current_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.port_1_current_read

    def read_port_2_current(self):
        # PROTECTED REGION ID(PDU.port_2_current_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.port_2_current_read

    def read_port_3_current(self):
        # PROTECTED REGION ID(PDU.port_3_current_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.port_3_current_read

    def read_port_4_current(self):
        # PROTECTED REGION ID(PDU.port_4_current_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.port_4_current_read

    def read_port_5_current(self):
        # PROTECTED REGION ID(PDU.port_5_current_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.port_5_current_read

    def read_port_6_current(self):
        # PROTECTED REGION ID(PDU.port_6_current_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.port_6_current_read

    def read_port_7_current(self):
        # PROTECTED REGION ID(PDU.port_7_current_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.port_7_current_read

    def read_port_8_current(self):
        # PROTECTED REGION ID(PDU.port_8_current_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.port_8_current_read

    def read_port_9_current(self):
        # PROTECTED REGION ID(PDU.port_9_current_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.port_9_current_read

    def read_port_10_current(self):
        # PROTECTED REGION ID(PDU.port_10_current_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.port_10_current_read

    def read_port_11_current(self):
        # PROTECTED REGION ID(PDU.port_11_current_read) ENABLED START #
        return 0.0
        # PROTECTED REGION END #    //  PDU.port_11_current_read

    def read_port_7_name(self):
        # PROTECTED REGION ID(PDU.port_7_name_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  PDU.port_7_name_read

    def read_port_1_enabled(self):
        # PROTECTED REGION ID(PDU.port_1_enabled_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  PDU.port_1_enabled_read

    def write_port_1_enabled(self, value):
        # PROTECTED REGION ID(PDU.port_1_enabled_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.port_1_enabled_write

    def read_port_2_enabled(self):
        # PROTECTED REGION ID(PDU.port_2_enabled_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  PDU.port_2_enabled_read

    def write_port_2_enabled(self, value):
        # PROTECTED REGION ID(PDU.port_2_enabled_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.port_2_enabled_write

    def read_port_3_enabled(self):
        # PROTECTED REGION ID(PDU.port_3_enabled_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  PDU.port_3_enabled_read

    def write_port_3_enabled(self, value):
        # PROTECTED REGION ID(PDU.port_3_enabled_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.port_3_enabled_write

    def read_port_4_enabled(self):
        # PROTECTED REGION ID(PDU.port_4_enabled_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  PDU.port_4_enabled_read

    def write_port_4_enabled(self, value):
        # PROTECTED REGION ID(PDU.port_4_enabled_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.port_4_enabled_write

    def read_port_5_enabled(self):
        # PROTECTED REGION ID(PDU.port_5_enabled_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  PDU.port_5_enabled_read

    def write_port_5_enabled(self, value):
        # PROTECTED REGION ID(PDU.port_5_enabled_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.port_5_enabled_write

    def read_port_6_enabled(self):
        # PROTECTED REGION ID(PDU.port_6_enabled_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  PDU.port_6_enabled_read

    def write_port_6_enabled(self, value):
        # PROTECTED REGION ID(PDU.port_6_enabled_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.port_6_enabled_write

    def read_port_7_enabled(self):
        # PROTECTED REGION ID(PDU.port_7_enabled_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  PDU.port_7_enabled_read

    def write_port_7_enabled(self, value):
        # PROTECTED REGION ID(PDU.port_7_enabled_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.port_7_enabled_write

    def read_port_8_enabled(self):
        # PROTECTED REGION ID(PDU.port_8_enabled_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  PDU.port_8_enabled_read

    def write_port_8_enabled(self, value):
        # PROTECTED REGION ID(PDU.port_8_enabled_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.port_8_enabled_write

    def read_port_9_enabled(self):
        # PROTECTED REGION ID(PDU.port_9_enabled_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  PDU.port_9_enabled_read

    def write_port_9_enabled(self, value):
        # PROTECTED REGION ID(PDU.port_9_enabled_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.port_9_enabled_write

    def read_port_10_enabled(self):
        # PROTECTED REGION ID(PDU.port_10_enabled_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  PDU.port_10_enabled_read

    def write_port_10_enabled(self, value):
        # PROTECTED REGION ID(PDU.port_10_enabled_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.port_10_enabled_write

    def read_port_11_enabled(self):
        # PROTECTED REGION ID(PDU.port_11_enabled_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  PDU.port_11_enabled_read

    def write_port_11_enabled(self, value):
        # PROTECTED REGION ID(PDU.port_11_enabled_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.port_11_enabled_write

    def read_port_12_enabled(self):
        # PROTECTED REGION ID(PDU.port_12_enabled_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  PDU.port_12_enabled_read

    def write_port_12_enabled(self, value):
        # PROTECTED REGION ID(PDU.port_12_enabled_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.port_12_enabled_write


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def Reset(self):
        # PROTECTED REGION ID(PDU.Reset) ENABLED START #
        pass
        # PROTECTED REGION END #    //  PDU.Reset

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(PDU.main) ENABLED START #
    return run((PDU,), args=args, **kwargs)
    # PROTECTED REGION END #    //  PDU.main

if __name__ == '__main__':
    main()
