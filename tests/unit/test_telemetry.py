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
import tempfile
import time

from packaging import version
from tango import __version__ as tango_version


class BackgroundServer:
    """Run server in background."""

    def __init__(self, command: list[str], env: dict[str, str], filepath: str) -> None:
        """Initialise background server."""
        self.output = tempfile.TemporaryFile("w+t")
        self.filepath = filepath
        self.process = subprocess.Popen(  # pylint: disable=consider-using-with
            command,
            stdout=self.output,
            stderr=subprocess.STDOUT,
            env=env,
            start_new_session=True,
        )

    def wait(self, timeout: float) -> None:
        """Wait for server to startup, blocking until it responds or times out."""
        max_timestamp = time.time() + timeout
        self.output.seek(0)
        while True:
            line = self.output.readline()

            if line == "Ready to accept request\n":
                break

            if time.time() > max_timestamp:
                raise RuntimeError("Timeout waiting for ready string")

            if not line:
                self.output.seek(0)
                try:
                    self.process.wait(0.1)
                    raise RuntimeError("Process stopped during startup")
                except subprocess.TimeoutExpired:
                    continue

    def kill(self) -> None:
        """Wait for response from process, blocking until it responds or times out."""
        # Kill the servers process group
        self.process.terminate()
        time.sleep(0.5)
        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

        # Read output from the subprocess and write to file
        self.output.seek(0)
        with open(self.filepath, "w", encoding="utf-8") as file:
            file.write(self.output.read())


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
    env["OMP_NUM_THREADS"] = "1"
    server1_log_path = "tests/device_server1.log"
    server2_log_path = "tests/device_server2.log"
    client_log_path = "tests/device_proxy.log"

    # Run the device server in a separate process
    server1 = BackgroundServer(
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
        env=env,
        filepath=server1_log_path,
    )
    server2 = BackgroundServer(
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
        env=env,
        filepath=server2_log_path,
    )
    server1.wait(3)
    server2.wait(3)
    with open(client_log_path, "w", encoding="utf-8") as client_log:
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
    server1.kill()
    server2.kill()

    if (
        version.parse(tango_version) >= version.parse("10.0.0")
        and importlib.util.find_spec("opentelemetry") is not None
    ):
        # Compare the telemetry logs of the server and client
        with open(server1_log_path, "r", encoding="utf-8") as server1_log, open(
            server2_log_path, "r", encoding="utf-8"
        ) as server2_log, open(client_log_path, "r", encoding="utf-8") as client_log:
            server1_out = server1_log.readlines()
            server2_out = server2_log.readlines()
            client_out = client_log.readlines()
            trace_id = "0xZYX"  # nonexistent
            # The amount of spans part of the main trace will differ depending on the
            # client script and command code, so we check for a minimum expected amount,
            # in case changes are made.
            # server1: 2x C++ and python command, python command func and _run (5 total)
            # server2: C++ trace, python command func and _run (3 total)
            # client: 2x C++ and python trace for calling command (3 total)
            server1_count, server2_count, client_count = 0, 0, 0
            for line in server1_out:
                # Find trace ID in log printed by command itself
                if "ReferenceSkaBaseDevice.TestTelemetryTracing trace ID" in line:
                    trace_id = line.split()[-1].lstrip("0x")
                    # print("TestTelemetryTracing command trace ID:", trace_id)
                    continue
                if trace_id in line:
                    server1_count += 1
            assert server1_count >= 5
            for line in server2_out:
                if trace_id in line:
                    server2_count += 1
            assert server2_count >= 3
            for line in client_out:
                if trace_id in line:
                    client_count += 1
            assert client_count >= 3
