# -*- coding: utf-8 -*-
#
# This file is part of the RefCapVlbiBeams project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" RefCapVlbiBeams

Ref (Reference Element) device of Type RefCapVlbiBeams
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
from SKACapability import SKACapability
# Additional import
# PROTECTED REGION ID(RefCapVlbiBeams.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  RefCapVlbiBeams.additionnal_import

__all__ = ["RefCapVlbiBeams", "main"]


class RefCapVlbiBeams(SKACapability):
    """
    Ref (Reference Element) device of Type RefCapVlbiBeams
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(RefCapVlbiBeams.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  RefCapVlbiBeams.class_variable

    # -----------------
    # Device Properties
    # -----------------


    # ----------
    # Attributes
    # ----------

    obsState = attribute(
        dtype='DevEnum',
        doc="Observing State",
        enum_labels=["IDLE", "CONFIGURING", "READY", "SCANNING", "PAUSED", "ABORTED", "FAULT", ],
    )

    obsMode = attribute(
        dtype='DevEnum',
        doc="Observing Mode",
        enum_labels=["IDLE", "IMG_CONTINUUM", "IMG_SPECTRAL_LINE", "IMG_ZOOM", "PULSAR_SEARCH", "TRANSIENT_SEARCH_FAST", "TRANSIENT_SEARCH_SLOW", "PULSAR_TIMING", "VLBI", ],
    )

    configurationProgress = attribute(
        dtype='uint16',
        unit="%",
        max_value=100,
        min_value=0,
        doc="Percentage configuration progress",
    )

    configurationDelayExpected = attribute(
        dtype='uint16',
        unit="seconds",
        doc="Configuration delay expected in seconds",
    )











    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKACapability.init_device(self)
        # PROTECTED REGION ID(RefCapVlbiBeams.init_device) ENABLED START #
        # PROTECTED REGION END #    //  RefCapVlbiBeams.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(RefCapVlbiBeams.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefCapVlbiBeams.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(RefCapVlbiBeams.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  RefCapVlbiBeams.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_obsState(self):
        # PROTECTED REGION ID(RefCapVlbiBeams.obsState_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefCapVlbiBeams.obsState_read

    def read_obsMode(self):
        # PROTECTED REGION ID(RefCapVlbiBeams.obsMode_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefCapVlbiBeams.obsMode_read

    def read_configurationProgress(self):
        # PROTECTED REGION ID(RefCapVlbiBeams.configurationProgress_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefCapVlbiBeams.configurationProgress_read

    def read_configurationDelayExpected(self):
        # PROTECTED REGION ID(RefCapVlbiBeams.configurationDelayExpected_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  RefCapVlbiBeams.configurationDelayExpected_read


    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(RefCapVlbiBeams.main) ENABLED START #
    return run((RefCapVlbiBeams,), args=args, **kwargs)
    # PROTECTED REGION END #    //  RefCapVlbiBeams.main

if __name__ == '__main__':
    main()
