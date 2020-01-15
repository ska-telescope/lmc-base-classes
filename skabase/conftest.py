"""
A module defining a list of fixture functions that are shared across all the skabase
tests.
"""
import os
import time
import importlib
import pytest

from unittest import mock

from tango.test_context import DeviceTestContext


@pytest.fixture(scope="class")
def tango_context(request):
    """Creates and returns a TANGO DeviceTestContext object.

    Parameters
    ----------
    request: _pytest.fixtures.SubRequest
        A request object gives access to the requesting test context.
    """
    ska_master_properties = {
        'SkaLevel': '4',
        'LoggingTargetsDefault': '',
        'GroupDefinitions': '',
        'NrSubarrays': '16',
        'CapabilityTypes': '',
        'MaxCapabilities': ['BAND1:1', 'BAND2:1']
        }

    ska_subarray_properties = {
        'CapabilityTypes': 'BAND1',
        'LoggingTargetsDefault': '',
        'GroupDefinitions': '',
        'SkaLevel': '4',
        'SubID': '1',
    }

    fq_test_class_name = request.cls.__module__
    fq_test_class_name_details = fq_test_class_name.split(".")
    # For future use
    # package_name = fq_test_class_name_details[0]
    # class_name = module_name = fq_test_class_name_details[1]
    class_name = fq_test_class_name_details[1]
    module = importlib.import_module(fq_test_class_name_details[1], fq_test_class_name_details[1])
    klass = getattr(module, class_name)

    if (class_name == 'SKAMaster'):
        tango_context = DeviceTestContext(klass, properties=ska_master_properties)
    elif (class_name == 'SKASubarray'):
        tango_context = DeviceTestContext(klass, properties=ska_subarray_properties)
    else:
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

@pytest.fixture(scope="class")
def setup_log_test_device():
    """
    Executes the SKA test device to test the logger class.
    :return: None
    """
    #TODO: Check if test device is registered in tango db. Register if required. Also check how to execute in docker environment.
    # run test device
    file_path = os.path.dirname(os.path.abspath(__file__))
    testdevice_path = os.path.abspath(os.path.join(file_path, os.curdir)) + "/SKATestDevice/SKATestDevice.py"
    cmdline = 'python3 ' + testdevice_path + ' ' + '01 &'
    os.system(cmdline)
    time.sleep(3)
    yield setup_log_test_device

    #tear down
    cmdline = 'pkill -9 -f .' + testdevice_path + ' &'
    os.system(cmdline)

