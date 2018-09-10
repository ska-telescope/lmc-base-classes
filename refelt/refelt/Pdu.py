# -*- coding: utf-8 -*-
#
# This file is part of the PDU project
#
#
#

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

__all__ = ["PDU", "main"]


class PDU(SKABaseDevice):
    """
    Ref (Reference Elt) PDU device
    """
    __metaclass__ = DeviceMeta

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

    def always_executed_hook(self):
        pass

    def delete_device(self):
        pass

    # ------------------
    # Attributes methods
    # ------------------

    def read_system_voltage(self):
        return 0.0

    def read_system_current(self):
        return 0.0

    def read_port_1_name(self):
        return ""

    def read_port_2_name(self):
        return ""

    def read_port_3_name(self):
        return ""

    def read_port_4_name(self):
        return ""

    def read_port_5_name(self):
        return ""

    def read_port_6_name(self):
        return ""

    def read_port_8_name(self):
        return ""

    def read_port_9_name(self):
        return ""

    def read_port_10_name(self):
        return ""

    def read_port_11_name(self):
        return ""

    def read_port_12_name(self):
        return ""

    def read_port_12_current(self):
        return 0.0

    def read_port_1_current(self):
        return 0.0

    def read_port_2_current(self):
        return 0.0

    def read_port_3_current(self):
        return 0.0

    def read_port_4_current(self):
        return 0.0

    def read_port_5_current(self):
        return 0.0

    def read_port_6_current(self):
        return 0.0

    def read_port_7_current(self):
        return 0.0

    def read_port_8_current(self):
        return 0.0

    def read_port_9_current(self):
        return 0.0

    def read_port_10_current(self):
        return 0.0

    def read_port_11_current(self):
        return 0.0

    def read_port_7_name(self):
        return ""

    def read_port_1_enabled(self):
        return False

    def write_port_1_enabled(self, value):
        pass

    def read_port_2_enabled(self):
        return False

    def write_port_2_enabled(self, value):
        pass

    def read_port_3_enabled(self):
        return False

    def write_port_3_enabled(self, value):
        pass

    def read_port_4_enabled(self):
        return False

    def write_port_4_enabled(self, value):
        pass

    def read_port_5_enabled(self):
        return False

    def write_port_5_enabled(self, value):
        pass

    def read_port_6_enabled(self):
        return False

    def write_port_6_enabled(self, value):
        pass

    def read_port_7_enabled(self):
        return False

    def write_port_7_enabled(self, value):
        pass

    def read_port_8_enabled(self):
        return False

    def write_port_8_enabled(self, value):
        pass

    def read_port_9_enabled(self):
        return False

    def write_port_9_enabled(self, value):
        pass

    def read_port_10_enabled(self):
        return False

    def write_port_10_enabled(self, value):
        pass

    def read_port_11_enabled(self):
        return False

    def write_port_11_enabled(self, value):
        pass

    def read_port_12_enabled(self):
        return False

    def write_port_12_enabled(self, value):
        pass


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def Reset(self):
        pass

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    return run((PDU,), args=args, **kwargs)

if __name__ == '__main__':
    main()
