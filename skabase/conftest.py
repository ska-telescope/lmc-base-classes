import pytest

from skabase.SKABaseDevice import SKABaseDevice
from tango.test_context import DeviceTestContext


@pytest.fixture(scope="class")
def tango_device_proxy(request):
    """Creates and returns a TANGO DeviceProxy object.
    """

    tango_context = DeviceTestContext(SKABaseDevice)
    tango_context.start()


    def tearDown():
        tango_context.stop()

    request.addfinalizer(tearDown)
    return tango_context.device
