###############################################################################
# SKA South Africa (http://ska.ac.za/)                                        #
# Author: cam@ska.ac.za                                                       #
# Copyright @ 2018 SKA SA. All rights reserved.                               #
#                                                                             #
# THIS SOFTWARE MAY NOT BE COPIED OR DISTRIBUTED IN ANY FORM WITHOUT THE      #
# WRITTEN PERMISSION OF SKA SA.                                               #
###############################################################################
"""
A module defining a list of fixture functions that are shared across all the skabase
tests.
"""
import mock
import pytest
import importlib


from tango.test_context import DeviceTestContext


@pytest.fixture(scope="class")
def tango_context(request):
    """Creates and returns a TANGO DeviceTestContext object.

    Parameters
    ----------
    request: _pytest.fixtures.SubRequest
        A request object gives access to the requesting test context. 
    """
    fq_test_class_name = request.cls.__module__
    fq_test_class_name_details = fq_test_class_name.split(".")
    package_name = fq_test_class_name_details[0]
    class_name = module_name = fq_test_class_name_details[1]
    module = importlib.import_module("{}.{}".format(package_name, module_name))
    klass = getattr(module, class_name)

    tango_context = DeviceTestContext(klass)
    tango_context.start()
    klass.get_name = mock.Mock(side_effect=tango_context.get_device_access)

    yield tango_context
    tango_context.stop()

@pytest.fixture(scope="function")
def initialize_device(tango_context):
    """Re-initializes the device.

    Parameters
    ----------
    tango_context: tango.test_context.DeviceTestContext
        Context to run a device without a database.
    """
    yield tango_context.device.Init()
    