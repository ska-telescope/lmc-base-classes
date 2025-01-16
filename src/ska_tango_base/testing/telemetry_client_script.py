# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This contains a script for connecting a client to a test device without a db."""
from time import sleep

from ska_control_model import AdminMode
from tango import DeviceProxy, DevState


def main() -> None:
    """Interact with the test device server."""
    device1 = DeviceProxy("tango://localhost:45678/foo/bar/1#dbase=no")

    # Interact with the server
    device1.adminMode = AdminMode.ONLINE
    device1.TestTelemetryTracing()

    device2 = DeviceProxy("tango://localhost:45679/foo/bar/2#dbase=no")
    while device2.state() != DevState.ON:
        sleep(0.1)
    sleep(0.1)


if __name__ == "__main__":
    main()
