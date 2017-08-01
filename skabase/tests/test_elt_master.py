import json
import sys

from PyTango import DeviceProxy

from base import DeviceServerBaseTest


class DevFailureTest(DeviceServerBaseTest):
    REQUIRED_DEVICE_SERVERS = ['ELT_DS']
    ELT_TANGO = 'unittest/elt/1'
    DOMAIN_NAME = 'unittest'

    @classmethod
    def add_devices(cls):
        cls.add_device('ELT_DS', 'elt/1')
        cls.add_device('Tile_DS', 'tile/1')
        cls.add_device('Tile_DS', 'tile/2')

    @classmethod
    def remove_devices(cls):
        cls.remove_device('elt/1')
        cls.remove_device('tile/1')
        cls.remove_device('tile/2')

    def test_filter_tile(self):
        """
        The tile device server has not been started, (not in REQUIRED_DEVICE_SERVERS)
        thus the response should result in error
        :return:
        """
        elt_dp = DeviceProxy(self.ELT_TANGO)
        argin = json.dumps({
            'device_type': 'tile',
            'with_value': True
        })
        data = elt_dp.command_inout('filter', argin)
        data_dict = json.loads(data)
        self.assertEqual(2, len(data_dict))
        self.assertListEqual(
            data_dict[0].keys(),
            [u'request_status', u'component_id', u'request_state', u'component_type']
        )
        self.assertEqual(data_dict[0]['request_status'], 'ERR')

        self.assertListEqual(
            data_dict[1].keys(),
            [u'request_status', u'component_id', u'request_state', u'component_type']
        )
        self.assertEqual(data_dict[1]['request_status'], 'ERR')


class EltTest(DeviceServerBaseTest):
    REQUIRED_DEVICE_SERVERS = ['ELT_DS', 'Tile_DS']
    ELT_TANGO = 'unittest/elt/1'
    DOMAIN_NAME = 'unittest'

    @classmethod
    def add_devices(cls):
        cls.add_device('ELT_DS', 'elt/1')
        cls.add_device('Tile_DS', 'tile/1')
        cls.add_device('Tile_DS', 'tile/2')

    @classmethod
    def remove_devices(cls):
        cls.remove_device('elt/1')
        cls.remove_device('tile/1')
        cls.remove_device('tile/2')


    def test_get(self):
        elt_dp = DeviceProxy(self.ELT_TANGO)
        argin = json.dumps({
            'device_type': 'tile',
            'device_id': 1,
            'with_value': True
        })
        data = elt_dp.command_inout('get', argin)
        data_dict = json.loads(data)
        self.assertListEqual(
                data_dict.keys(),
                [u'commands', u'component_id', u'firmware', u'component_type', u'properties']
        )

    def test_filter_tile(self):
        elt_dp = DeviceProxy(self.ELT_TANGO)
        argin = json.dumps({
            'device_type': 'tile',
            'with_value': False
        })
        data = elt_dp.command_inout('filter', argin)
        data_dict = json.loads(data)
        self.assertEqual(2, len(data_dict))
        self.assertItemsEqual(
            data_dict[0].keys(),
            [ u'antennas', u'commands', u'component_id', u'firmware', u'component_type', u'properties']
        )
        self.assertItemsEqual(
            data_dict[1].keys(),
            [ u'antennas', u'commands', u'component_id', u'firmware', u'component_type', u'properties']
        )

        self.assertListEqual(
            sorted(data_dict[0]['properties'][0].keys()),
            [u'attribute_type', u'max_value', u'min_value', u'name', u'polling_frequency', u'readonly']
        )

        self.assertListEqual(
            sorted(data_dict[1]['properties'][0].keys()),
            [u'attribute_type', u'max_value', u'min_value', u'name', u'polling_frequency', u'readonly']

        )

    def test_filter_with_value(self):
        elt_dp = DeviceProxy(self.ELT_TANGO)
        argin = json.dumps({
            'device_type': 'tile',
            'with_value': True
        })
        data = elt_dp.command_inout('filter', argin)
        data_dict = json.loads(data)
        self.assertEqual(2, len(data_dict))
        self.assertListEqual(
            data_dict[0].keys(),
            [u'commands', u'component_id', u'firmware', u'component_type', u'properties']
        )
        self.assertListEqual(
            data_dict[1].keys(),
            [u'commands', u'component_id', u'firmware', u'component_type', u'properties']
        )

        self.assertListEqual(
            sorted(data_dict[0]['properties'][0].keys()),
            [u'is_alarm', u'max_value', u'min_value', u'name',  u'readonly', u'value']
        )

        self.assertListEqual(
            sorted(data_dict[1]['properties'][0].keys()),
            [u'is_alarm', u'max_value', u'min_value', u'name',  u'readonly', u'value']
        )

    def test_filter_nonexistant(self):
        elt_dp = DeviceProxy(self.ELT_TANGO)
        argin = json.dumps({
            'device_type': 'nonexistant',
            'with_value': True
        })
        data = elt_dp.command_inout('filter', argin)
        data_dict = json.loads(data)
        self.assertEqual(0, len(data_dict))

    def test_update(self):
        elt_dp = DeviceProxy(self.ELT_TANGO)
        argin = json.dumps({
            'device_type': 'tile',
            'device_attributes': [{
                'device_id': 1,
                'name': 'elt_port',
                'value': 9000
            }, {
                'device_id': 2,
                'name': 'elt_port',
                'value': 8000
            }]
        })
        data = elt_dp.command_inout('set_attributes', argin)
        data_dict = json.loads(data)
        self.assertDictEqual(
                data_dict,
                {'meta': {'updated': {'properties': 2}}}
        )

    # def test_get_properties(self):
    #     elt_dp = DeviceProxy(self.ELT_TANGO)
    #     argin = json.dumps({
    #         'device_type': 'tile',
    #         'device_id': 1,
    #         'with_value': True,
    #         'skip': 0,
    #         'limit': 10
    #     })
    #     data = elt_dp.command_inout('get_attributes', argin)
    #     import ipdb; ipdb.set_trace()
    #     self.assertEqual(len(data), 10)



def init_obs(elt_id):
    obs = {"meta": {

    },
        "jobs": {
            "pointing": {
                "channels": {
                    "start": 123,
                    "count": 40
                },
                "atten": 1.0,
                "altaz": {
                    "alt": 84.0,
                    "az": 270.0
                }
            }
        },
        "mode": "mwa",
    }

    elt_dp = DeviceProxy(elt_id)
    argin = json.dumps(obs)
    data = elt_dp.command_inout('init_observation', argin)
    data_dict = json.loads(data)
    obs_attr = get_attributes(elt_dp,  data_dict["observation_id"])
    assert str(obs_attr["State"]) == str("INIT")
    data = elt_dp.command_inout('start_observation', "")
    obs_attr = get_attributes(elt_dp,  data_dict["observation_id"])
    assert str(obs_attr["State"]) == str("RUNNING")
    data = elt_dp.command_inout('stop_observation', "")
    try:
      obs_attr = get_attributes(elt_dp,  data_dict["observation_id"])
    except Exception as e:
        reason = e.args[0].reason

    assert reason == 'DB_DeviceNotDefined'




def get_attributes(elt_dp, id):

    argin =    {
        "device_type": "observation",
        "device_id":   id,
        "with_value": True
    }
    result = elt_dp.command_inout('get_attributes', json.dumps(argin))
    print result
    init_result = json.loads(result)
    return {attr["name"]: attr["value"] for attr in init_result}
