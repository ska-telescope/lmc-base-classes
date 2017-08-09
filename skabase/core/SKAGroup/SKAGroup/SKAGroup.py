# -*- coding: utf-8 -*-
#
# This file is part of the SKAGroup project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

A class which holds a number of proxies to members
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
# PROTECTED REGION ID(SKAGroup.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SKAGroup.additionnal_import

__all__ = ["SKAGroup", "main"]


class SKAGroup(SKABaseDevice):
    """
    A class which holds a number of proxies to members
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKAGroup.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKAGroup.class_variable

    # -----------------
    # Device Properties
    # -----------------

    member_list = device_property(
        dtype=('str',),
        mandatory=True
    )










    # ----------
    # Attributes
    # ----------

    members_state = attribute(
        dtype='DevState',
        access=AttrWriteType.READ_WRITE,
    )















    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKABaseDevice.init_device(self)
        # PROTECTED REGION ID(SKAGroup.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKAGroup.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKAGroup.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAGroup.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKAGroup.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAGroup.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_members_state(self):
        # PROTECTED REGION ID(SKAGroup.members_state_read) ENABLED START #
        return PyTango.DevState.UNKNOWN
        # PROTECTED REGION END #    //  SKAGroup.members_state_read

    def write_members_state(self, value):
        # PROTECTED REGION ID(SKAGroup.members_state_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAGroup.members_state_write


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    doc_in="[{`name`: `device_name`, `type`:`str`},]", 
    )
    @DebugIt()
    def add_member(self, argin):
        # PROTECTED REGION ID(SKAGroup.add_member) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAGroup.add_member

    @command(
    dtype_in='str', 
    doc_in="[{`name`: `device_name`, `type`:`str`} ]", 
    )
    @DebugIt()
    def remove_member(self, argin):
        # PROTECTED REGION ID(SKAGroup.remove_member) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAGroup.remove_member

    @command(
    dtype_in='str', 
    doc_in="[{`name`: `cmd_name`, `type`:`str`},\n{`name`: `cmd_args`, `type`:`json`}, \n{`name`: `device_name`, `type`:`str`} ]", 
    dtype_out='str', 
    )
    @DebugIt()
    def run_command(self, argin):
        # PROTECTED REGION ID(SKAGroup.run_command) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  SKAGroup.run_command

    @command(
    dtype_in='str', 
    doc_in="[{`name`: `component_type`, `type`:`str`, `default`: ``}]", 
    dtype_out='str', 
    )
    @DebugIt()
    def get_member_names(self, argin):
        # PROTECTED REGION ID(SKAGroup.get_member_names) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  SKAGroup.get_member_names

    @command(
    dtype_in='str', 
    doc_in="[{`name`: `attribute_name`, `type`:`str`, `default`: `*`}, \n{`name`: `device_name`, `type`:`str`, `default`: `*`}, \n{`name`: `with_value`, `type`:`bool`, `default`: `False`}]", 
    dtype_out='str', 
    doc_out="json encoded string of attribute configs and values", 
    )
    @DebugIt()
    def get_attribute_list(self, argin):
        # PROTECTED REGION ID(SKAGroup.get_attribute_list) ENABLED START #
        return ""
        # PROTECTED REGION END #    //  SKAGroup.get_attribute_list

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKAGroup.main) ENABLED START #
    return run((SKAGroup,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKAGroup.main

if __name__ == '__main__':
    main()
