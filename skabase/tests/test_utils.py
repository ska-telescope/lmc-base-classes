"""Tests for skabase.utils."""

import json
import pytest

from skabase.utils import get_groups_from_json
from skabase.utils import GroupDefinitionsError


TEST_GROUPS = {
    # Valid groups
    'basic_no_subgroups': {
        'group_name': 'g1',
        'devices': ['my/dev/1'],
    },
    'basic_empty_subgroups': {
        'group_name': 'g2',
        'devices': ['my/dev/2'],
        'subgroups': []
    },
    'dual_level': {
        'group_name': 'g3',
        'subgroups': [
            {'group_name': 'g3-1',
             'devices': ['my/dev/3-1']}
        ]
    },
    'multi_level': {
        'group_name': 'data_centre_1',
        'devices': ['dc1/aircon/1', 'dc1/aircon/2'],
        'subgroups': [
            {'group_name': 'racks',
             'subgroups': [
                {'group_name': 'rackA',
                 'devices': ['dc1/server/1', 'dc1/server/2',
                             'dc1/switch/A', 'dc1/pdu/rackA']},
                {'group_name': 'rackB',
                 'devices': ['dc1/server/3', 'dc1/server/4',
                             'dc1/switch/B', 'dc1/pdu/rackB'],
                 'subgroups': []},
                ]},
        ]
    },

    # Invalid groups (bad keys)
    'bk1_bad_keys': {
    },
    'bk2_bad_keys': {
        'group_name': 'bk2',
        'bad_devices_key': ['my/dev/01', 'my/dev/02']
    },
    'bk3_bad_keys': {
        'group_name': 'bk3',
        'bad_subgroups_key': []
    },
    'bk4_bad_keys': {
        'bad_group_name_key': 'bk4',
        'devices': ['my/dev/41']
    },
    'bk5_bad_nested_keys': {
        'group_name': 'bk5',
        'subgroups': [
            {'group_name': 'bk5-1',
             'bad_devices_key': ['my/dev/3-1']}
        ]
    },
    'bk6_bad_nested_keys': {
        'group_name': 'bk6',
        'subgroups': [
            {'bad_group_name_key': 'bk6-1',
             'devices': ['my/dev/3-1']}
        ]
    },

    # Invalid groups (bad values)
    'bv1_bad_device_names': {
        'group_name': 'bv1',
        'devices': ['my\dev-11']
    },
    'bv2_bad_device_names': {
        'group_name': 'bv2',
        'devices': ['1', '2', 'bad']
    },
    'bv3_bad_device_names': {
        'group_name': 'bv3',
        'devices': ['  ']
    },
    'bv4_bad_subgroups_value': {
        'group_name': 'bv4',
        'subgroups': ['  ']
    },
    'bv5_bad_nested_device_names': {
        'group_name': 'bv5',
        'subgroups': [
            {'group_name': 'bv5-1',
             'devices': ['my\dev-11']}
        ]
    },
}

VALID_GROUP_KEYS = [
    ('basic_no_subgroups', ),
    ('basic_no_subgroups', 'basic_empty_subgroups', ),
    ('basic_no_subgroups', 'basic_empty_subgroups', 'dual_level', ),
    ('basic_no_subgroups', 'basic_empty_subgroups', 'dual_level', 'multi_level'),
]

BAD_GROUP_KEYS = [
    ('bk1_bad_keys', ),
    ('bk2_bad_keys', ),
    ('bk3_bad_keys', ),
    ('bk4_bad_keys', ),
    ('bk5_bad_nested_keys', ),
    ('bk6_bad_nested_keys', ),
    ('bv1_bad_device_names', ),
    ('bv2_bad_device_names', ),
    ('bv3_bad_device_names', ),
    ('bv4_bad_subgroups_value', ),
    ('bv5_bad_nested_device_names', ),
    # Include a valid group, g2 with an invalid group
    ('basic_no_subgroups', 'bk1_bad_keys', ),
]


def _jsonify_group_configs(group_configs):
    """Returns list of JSON definitions for groups."""
    definitions = []
    for group_config in group_configs:
        definitions.append(json.dumps(group_config))
    return definitions


def _get_group_configs_from_keys(group_keys):
    """Provides list of group configs based on keys for TEST_GROUPS."""
    group_configs = []
    for group_key in group_keys:
        group_config = TEST_GROUPS[group_key]
        group_configs.append(group_config)
    return group_configs


def _group_id_name(keys):
    """Helper function to give tests nicer names."""
    return ','.join(keys)


@pytest.fixture(scope="module", params=VALID_GROUP_KEYS, ids=_group_id_name)
def valid_group_configs(request):
    """Provides valid lists of groups configs, one at a time."""
    return _get_group_configs_from_keys(request.param)


@pytest.fixture(scope="module", params=BAD_GROUP_KEYS, ids=_group_id_name)
def bad_group_configs(request):
    """Provides bad lists of groups configs, one at a time."""
    return _get_group_configs_from_keys(request.param)


def test_get_groups_from_json_empty_list():
    groups = get_groups_from_json([])
    assert groups == {}
    # empty or whitespace strings should also be ignored
    groups = get_groups_from_json([''])
    assert groups == {}
    groups = get_groups_from_json(['  ', '', ' '])
    assert groups == {}


def _validate_group(definition, group):
    """Compare groups test definition dict to actual tango.Group."""
    expected_group_name = definition['group_name']  # key must exist
    expected_devices = definition.get('devices', [])  # key may exist
    expected_subgroups = definition.get('subgroups', [])  # key may exist

    print "Checking group:", expected_group_name, group
    assert group is not None
    assert expected_group_name == group.get_name()
    device_list = group.get_device_list(forward=False)
    assert expected_devices == list(device_list)

    for expected_subgroup in expected_subgroups:
        print "\tsubgroup def", expected_subgroup
        subgroup = group.get_group(expected_subgroup['group_name'])
        assert subgroup is not None
        # recurse the tree
        _validate_group(expected_subgroup, subgroup)


def test_get_groups_from_json_valid(valid_group_configs):
    json_definitions = _jsonify_group_configs(valid_group_configs)
    groups = get_groups_from_json(json_definitions)

    # Check result
    assert len(groups) == len(valid_group_configs)
    for group_config in valid_group_configs:
        name = group_config['group_name']
        group = groups[name]
        _validate_group(group_config, group)


def test_get_groups_from_json_invalid(bad_group_configs):
    json_definitions = _jsonify_group_configs(bad_group_configs)
    with pytest.raises(GroupDefinitionsError):
        get_groups_from_json(json_definitions)
