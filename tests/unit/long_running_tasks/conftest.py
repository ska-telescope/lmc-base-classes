"""Fixtures for tests."""
import pytest
import socket

import tango

from tango.test_context import get_host_ip, MultiDeviceTestContext


@pytest.fixture(scope="module")
def devices_to_test(request):
    """Fixture for devices to test."""
    yield getattr(request.module, "devices_to_test")


@pytest.fixture(scope="function")
def multi_device_tango_context(
    mocker, devices_to_test  # pylint: disable=redefined-outer-name
):
    """
    Create and return a TANGO MultiDeviceTestContext object.

    tango.DeviceProxy patched to work around a name-resolving issue.
    """

    def _get_open_port():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port

    HOST = get_host_ip()
    PORT = _get_open_port()
    _DeviceProxy = tango.DeviceProxy
    mocker.patch(
        "tango.DeviceProxy",
        wraps=lambda fqdn, *args, **kwargs: _DeviceProxy(
            "tango://{0}:{1}/{2}#dbase=no".format(HOST, PORT, fqdn), *args, **kwargs
        ),
    )
    with MultiDeviceTestContext(
        devices_to_test, host=HOST, port=PORT, process=True
    ) as context:
        yield context
