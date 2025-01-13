# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This contains a script for connecting a client to a test device without a db."""
from ska_control_model import AdminMode
from tango import DeviceProxy


def main() -> None:
    """Interact with the test device server."""
    device = DeviceProxy("tango://localhost:45678/foo/bar/1#dbase=no")

    # Interact with the server
    print("Device name:", device.name())
    print("Device state:", device.state())
    device.adminMode = AdminMode.ONLINE
    print("Device state:", device.state())
    device.TestTelemetryTracing()


if __name__ == "__main__":
    main()
