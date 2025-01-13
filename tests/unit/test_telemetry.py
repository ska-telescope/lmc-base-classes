# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module contains tests for using OpenTelemetry in SKABaseDevice."""
import importlib.util
import json
import os
import signal
import subprocess
import time

from packaging import version
from tango import __version__ as tango_version


# pylint: disable=too-many-locals
def test_open_telemetry() -> None:
    """
    Run device servers and client in separate processes with telemetry enabled.

    The stdout of the servers/client is captured in a file and the subprocesses are
    properly terminated before checking the OpenTelemetry traces in the captured output.

    The test checks for the traces of a cascading LRC in the server logs called by the
    client, and asserts that the spans' parent IDs match. It also check the command
    function args passed as 'attributes' to the custom span in TaskExecutor._run().
    """
    env = os.environ.copy()
    env["TANGO_TELEMETRY_ENABLE"] = "on"
    server_log_path = "tests/device_server.log"
    client_log_path = "tests/device_proxy.log"

    with open(server_log_path, "w", encoding="utf-8") as server_log, open(
        client_log_path, "w", encoding="utf-8"
    ) as client_log:
        # Run the device server in a separate process
        server1_p = subprocess.Popen(  # pylint: disable=consider-using-with
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
        server2_p = subprocess.Popen(  # pylint: disable=consider-using-with
            [
                "python",
                "src/ska_tango_base/testing/reference/reference_base_device.py",
                "test",
                "-nodb",
                "-port",
                "45679",
                "-dlist",
                "foo/bar/2",
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
        time.sleep(1)  # Wait for any LRCs to complete (not strictly necessary)
        os.killpg(os.getpgid(server1_p.pid), signal.SIGTERM)  # Kill the device server
        os.killpg(os.getpgid(server2_p.pid), signal.SIGTERM)  # Kill the device server

    if (
        version.parse(tango_version) >= version.parse("10.0.0")
        and importlib.util.find_spec("opentelemetry") is not None
    ):
        # Compare the telemetry logs of the server and client
        with open(server_log_path, "r", encoding="utf-8") as server_log:
            server_out = server_log.readlines()
            trace_id = ""
            on_span_id = ""
            on_parent_id = ""
            asserts = 0
            for i, line in enumerate(server_out):
                if "ReferenceSkaBaseDevice.TestTelemetryTracing" in line:
                    trace_id = server_out[i + 3].split(":")[1].strip(' ",\n')
                if "TaskExecutor._run.call_command_on_device" in line:
                    # assert command span ID matches parent ID of command func
                    assert trace_id == server_out[i + 7].split(":")[1].strip(' ",\n')
                    nextline, attr_str = "", ""
                    j = 0
                    while "}" not in nextline:
                        nextline = server_out[i + 13 + j]
                        attr_str += nextline[:-1]
                        j += 1
                    attributes = json.loads(
                        attr_str.strip(" ,").removeprefix('"attributes":')
                    )
                    assert attributes["function_args"][0] == "On"
                    assert (
                        attributes["function_args"][1]
                        == "tango://localhost:45679/foo/bar/2"
                    )
                    assert attributes["function_kwargs"][0] == "database=False"
                    asserts += 1
                if "SKABaseDevice.On" in line:
                    on_span_id = server_out[i + 3].split(":")[1].strip(' ",\n')
                    on_parent_id = server_out[i + 7].split(":")[1].strip(' ",\n')
                if "TaskExecutor._run.on" in line:
                    # assert command span ID matches parent ID of command func
                    assert on_span_id == server_out[i + 7].split(":")[1].strip(' ",\n')
                    asserts += 1
                    break
            for i, line in enumerate(server_out):
                if "span_id" in line and on_parent_id[2:] in line:
                    # assert matching parent tango operation
                    assert (
                        server_out[i + 9].split(":")[1].strip()
                        == "TestTelemetryTracing"
                    )
                    asserts += 1
                    break
            assert asserts == 3
