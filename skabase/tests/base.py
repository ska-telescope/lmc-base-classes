from eltbase.library.helpers import get_dev_info
from time import sleep
from unittest import TestCase
from subprocess import Popen
from PyTango import Database, DbDevInfo, DbDatum
from os.path import join, dirname, realpath
import sys

db = Database()


# service tango-db status
# service tango-starter status

class DeviceServerBaseTest(TestCase):
    DOMAIN_NAME = 'test'
    REQUIRED_DEVICE_SERVERS = []
    running_device_servers = {}
    device_server_path = join(dirname(realpath(__file__)), '../../run')

    @classmethod
    def add_device(cls, device_server_name, device_ref):
        dev_info = get_dev_info(cls.DOMAIN_NAME, device_server_name, device_ref)
        db.add_device(dev_info)
        return dev_info.name

    @classmethod
    def remove_device(cls, device_ref):
        db.delete_device('%s/%s' % (cls.DOMAIN_NAME, device_ref))

    @classmethod
    def add_devices(self):
        pass

    @classmethod
    def remove_devices(self):
        pass

    @classmethod
    def stop_device_server(cls, device_server_name):
        process = cls.running_device_servers[device_server_name]
        process.kill()

    @classmethod
    def start_device_server(cls, device_server_name):
        # Running in Pycharm debugger, Popen uses the system python not the virtualenv python.
        # sys.executable gives the full path of current interpreter from the virtual env
        python = sys.executable
        process = Popen(["nohup", python, device_server_name, cls.DOMAIN_NAME, '-v1'],
                        cwd=cls.device_server_path)
        sleep(5)
        cls.running_device_servers[device_server_name] = process

    @classmethod
    def setUpClass(cls):
        cls.add_devices()
        sleep(2)
        for device_server in cls.REQUIRED_DEVICE_SERVERS:
            cls.start_device_server(device_server)
        sleep(2)

    @classmethod
    def tearDownClass(cls):
        cls.remove_devices()
        for device_server in cls.REQUIRED_DEVICE_SERVERS:
            cls.stop_device_server(device_server)

    @classmethod
    def add_device_prop(cls,device_ref,properties):

        for name,value in properties.iteritems():
            db = Database()
            db_datum = DbDatum()
            db_datum.name = name
            db_datum.value_string.append(value)
            device_name = '%s/%s' % (cls.DOMAIN_NAME, device_ref)

            db.put_device_property(device_name, db_datum)
