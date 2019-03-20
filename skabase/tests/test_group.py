import tango
from tango import DeviceProxy, AttrQuality, AttributeProxy
from .base import DeviceServerBaseTest
import json
from time import sleep

class TestGroup(DeviceServerBaseTest):
    REQUIRED_DEVICE_SERVERS = ['Subarray_DS', 'Capability_DS']

    @classmethod
    def add_devices(cls):
        cls.add_device('Subarray_DS', 'sub/1')
        cls.add_device('Capability_DS', 'cap/sub1cap1')
        cls.add_device('Capability_DS', 'cap/sub1cap2')
        cls.add_device('Device_DS', 'dev/sub1cap1dev1')
        cls.add_device('Device_DS', 'dev/sub1cap1dev2')
        cls.add_device('Device_DS', 'dev/sub1cap2dev1')

    @classmethod
    def remove_devices(cls):
        cls.remove_device('sub/1')
        cls.remove_device('cap/sub1cap1')
        cls.remove_device('cap/sub1cap2')
        cls.remove_device('dev/sub1cap1dev1')
        cls.remove_device('dev/sub1cap1dev2')
        cls.remove_device('dev/sub1cap2dev1')

    def test_add_member(self):
        device_name = '%s/sub/1' % self.DOMAIN_NAME
        group_name = 'capabilities'
        # self.stop_device_server('Subarray_DS')
        # self.start_device_server('Subarray_DS')
        dp = DeviceProxy(device_name)
        dp.set_logging_level(5)
        member_device_name_1 = '%s/capability/sub1cap1' % self.DOMAIN_NAME
        data_1 = json.dumps({'group_name': group_name, 'device_name': member_device_name_1 })
        dp.command_inout('add_member', data_1)
        self.assertTrue(member_device_name_1 in dp.get_property(group_name)[group_name])

        member_device_name_2 = '%s/capability/sub1cap2' % self.DOMAIN_NAME
        data_2 = json.dumps({'group_name': group_name, 'device_name': member_device_name_2 })
        dp.command_inout('add_member', data_2)

        items = dp.get_property(group_name)[group_name]
        self.assertTrue(member_device_name_2 in items)
        self.assertEqual(len(items), 2)
        dp.command_inout('remove_member', data_2)

        items = dp.get_property(group_name)[group_name]
        self.assertFalse(member_device_name_2 in items)
        self.assertEqual(len(items), 1)

        dp.command_inout('remove_member', data_1)
        self.assertFalse(member_device_name_1 in dp.get_property(group_name)[group_name])

    def add_members(self, device_name, group_name, members=None):
        dp = DeviceProxy(device_name)
        for member in members:
            data = json.dumps({'group_name': group_name, 'device_name': member })
            dp.command_inout('add_member', data)

    def test_alarm_propagation(self):
        device_name = '%s/sub1/1' % self.DOMAIN_NAME
        members_template = ['%s/capability/sub1cap1', '%s/capability/sub1cap2']
        members = [member % self.DOMAIN_NAME for member in members_template]

        self.add_members(device_name, 'tiles', members)
        dp = DeviceProxy(device_name)
        self.assertNotEqual(dp.state(), AttrQuality.ATTR_ALARM)
        member_dp = DeviceProxy(members[0])
        alarm_data = json.dumps({'name': 'an_attr', 'min_alarm': '20', 'max_alarm': '50'})
        member_dp.command_inout('set_attribute_alarm', alarm_data)
        member_dp.an_attr = 10
        attr = AttributeProxy(members[0] + '/an_attr')
        self.assertEqual(attr.read().quality, AttrQuality.ATTR_ALARM)
        self.assertEqual(member_dp.state(), tango._tango.DevState.ALARM)
        i = 0
        while (dp.state() != tango._tango.DevState.ALARM) and i < 3:
            sleep(1)
            i+=1

        self.assertEqual(dp.state(), tango._tango.DevState.ALARM)
