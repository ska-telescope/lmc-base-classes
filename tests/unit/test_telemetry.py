# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module contains tests for using OpenTelemetry in SKABaseDevice."""
import importlib.util
import os
import signal
import subprocess
import time

from packaging import version
from tango import __version__ as tango_version


def test_open_telemetry() -> None:
    """Run the device server and client in separate processes with telemetry enabled."""
    env = os.environ.copy()
    env["TANGO_TELEMETRY_ENABLE"] = "on"
    server_log_path = "tests/device_server.log"
    client_log_path = "tests/device_proxy.log"

    with open(server_log_path, "w", encoding="utf-8") as server_log, open(
        client_log_path, "w", encoding="utf-8"
    ) as client_log:
        # Run the device server in a separate process
        server_p = subprocess.Popen(  # pylint: disable=consider-using-with
            [
                "python",
                "src/ska_tango_base/testing/reference/reference_base_device.py",
                "test",
                "-nodb",
                "-port",
                "45678",
                "-dlist",
                "foo/bar/1",
            ],
            stdout=server_log,
            stderr=subprocess.STDOUT,  # Redirect stderr to the same file
            env=env,
            start_new_session=True,  # Start in a new process group
        )
        time.sleep(2)  # Wait for device server to initialise

        env["PYTANGO_TELEMETRY_CLIENT_SERVICE_NAME"] = "test.client"
        # Run the client script in a separate process
        client_p = subprocess.Popen(  # pylint: disable=consider-using-with
            [
                "python",
                "src/ska_tango_base/testing/telemetry_client_script.py",
            ],
            stdout=client_log,
            stderr=subprocess.STDOUT,
            env=env,
        )
        client_p.wait()  # Wait for the client script to complete
        time.sleep(0.5)  # Wait for any LRCs to complete (not strictly necessary)
        os.killpg(os.getpgid(server_p.pid), signal.SIGTERM)  # Kill the device server

    if (
        version.parse(tango_version) >= version.parse("10.0.0")
        and importlib.util.find_spec("opentelemetry") is not None
    ):
        # Compare the telemetry logs of the server and client
        with open(server_log_path, "r", encoding="utf-8") as server_log, open(
            client_log_path, "r", encoding="utf-8"
        ) as client_log:
            server_out = server_log.readlines()
            client_out = client_log.readlines()
            for i, line in enumerate(server_out):
                if "SKABaseDevice.On" in line:
                    trace_id = server_out[i + 2].split('"')[3][2:]
                    span_id = server_out[i + 3].split('"')[3][2:]
                    break

            print("Trace ID of On command:", trace_id)
            print("Server span ID:", span_id)

            for i, line in enumerate(client_out):
                if trace_id in line:
                    print(
                        "Client span ID:",
                        client_out[i + 1].split()[-1].strip('",').strip("0x"),
                    )
                    print(
                        "Client span parent ID:",
                        client_out[i + 3].split()[-1].strip('",'),
                    )
