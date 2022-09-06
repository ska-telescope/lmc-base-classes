# pylint: skip-file  # TODO: Incrementally lint this repo
# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""Tests for skabase.utils."""
from __future__ import annotations

import json
from contextlib import nullcontext
from typing import Any, ContextManager, Dict, cast

import pytest
import tango
from _pytest.fixtures import SubRequest

from ska_tango_base.utils import (  # type: ignore[attr-defined]
    GroupDefinitionsError,
    for_testing_only,
    get_groups_from_json,
    get_tango_device_type_id,
)

TEST_GROUPS = {
    # Valid groups
    "basic_no_subgroups": {
        "group_name": "g1",
        "devices": ["my/dev/1"],
    },
    "basic_empty_subgroups": {
        "group_name": "g2",
        "devices": ["my/dev/2"],
        "subgroups": [],
    },
    "dual_level": {
        "group_name": "g3",
        "subgroups": [{"group_name": "g3-1", "devices": ["my/dev/3-1"]}],
    },
    "multi_level": {
        "group_name": "data_centre_1",
        "devices": ["dc1/aircon/1", "dc1/aircon/2"],
        "subgroups": [
            {
                "group_name": "racks",
                "subgroups": [
                    {
                        "group_name": "rackA",
                        "devices": [
                            "dc1/server/1",
                            "dc1/server/2",
                            "dc1/switch/A",
                            "dc1/pdu/rackA",
                        ],
                    },
                    {
                        "group_name": "rackB",
                        "devices": [
                            "dc1/server/3",
                            "dc1/server/4",
                            "dc1/switch/B",
                            "dc1/pdu/rackB",
                        ],
                        "subgroups": [],
                    },
                ],
            },
        ],
    },
    # Invalid groups (bad keys)
    "bk1_bad_keys": {},
    "bk2_bad_keys": {
        "group_name": "bk2",
        "bad_devices_key": ["my/dev/01", "my/dev/02"],
    },
    "bk3_bad_keys": {"group_name": "bk3", "bad_subgroups_key": []},
    "bk4_bad_keys": {"bad_group_name_key": "bk4", "devices": ["my/dev/41"]},
    "bk5_bad_nested_keys": {
        "group_name": "bk5",
        "subgroups": [{"group_name": "bk5-1", "bad_devices_key": ["my/dev/3-1"]}],
    },
    "bk6_bad_nested_keys": {
        "group_name": "bk6",
        "subgroups": [{"bad_group_name_key": "bk6-1", "devices": ["my/dev/3-1"]}],
    },
    # Invalid groups (bad values)
    "bv1_bad_device_names": {"group_name": "bv1", "devices": ["my\\dev-11"]},
    "bv2_bad_device_names": {
        "group_name": "bv2",
        "devices": ["1", "2", "bad"],
    },
    "bv3_bad_device_names": {"group_name": "bv3", "devices": ["  "]},
    "bv4_bad_subgroups_value": {"group_name": "bv4", "subgroups": ["  "]},
    "bv5_bad_nested_device_names": {
        "group_name": "bv5",
        "subgroups": [{"group_name": "bv5-1", "devices": ["my\\dev-11"]}],
    },
}

VALID_GROUP_KEYS = [
    ("basic_no_subgroups",),
    (
        "basic_no_subgroups",
        "basic_empty_subgroups",
    ),
    (
        "basic_no_subgroups",
        "basic_empty_subgroups",
        "dual_level",
    ),
    (
        "basic_no_subgroups",
        "basic_empty_subgroups",
        "dual_level",
        "multi_level",
    ),
]

BAD_GROUP_KEYS = [
    ("bk1_bad_keys",),
    ("bk2_bad_keys",),
    ("bk3_bad_keys",),
    ("bk4_bad_keys",),
    ("bk5_bad_nested_keys",),
    ("bk6_bad_nested_keys",),
    ("bv1_bad_device_names",),
    ("bv2_bad_device_names",),
    ("bv3_bad_device_names",),
    ("bv4_bad_subgroups_value",),
    ("bv5_bad_nested_device_names",),
    # Include a valid group, g2 with an invalid group
    (
        "basic_no_subgroups",
        "bk1_bad_keys",
    ),
]


def _jsonify_group_configs(group_configs: list[Dict[str, Any]]) -> list[str]:
    """
    Return a list of JSON definitions for groups.

    :param group_configs: definitions of groups

    :return: a list of JSON definitions for groups
    """
    definitions = []
    for group_config in group_configs:
        definitions.append(json.dumps(group_config))
    return definitions


def _get_group_configs_from_keys(group_keys: list[str]) -> list[Dict[str, Any]]:
    """
    Provide list of group configs based on keys for TEST_GROUPS.

    :param group_keys: a list of configuration keys

    :return: a list of group configs
    """
    group_configs = []
    for group_key in group_keys:
        group_config = cast(Dict[str, Any], TEST_GROUPS[group_key])
        group_configs.append(group_config)
    return group_configs


def _group_id_name(keys: list[str]) -> str:
    """
    Return a comma-separated string of keys.

    This is a helper function to give tests nicer names.

    :param keys: a list of group id names

    :return: nice test names
    """
    return ",".join(keys)


@pytest.fixture(scope="module", params=VALID_GROUP_KEYS, ids=_group_id_name)
def valid_group_configs(request: SubRequest) -> list[Dict[str, Any]]:
    """
    Provide valid lists of groups configs, one at a time.

    :param request: request

    :return: valid lists of groups configs
    """
    return _get_group_configs_from_keys(request.param)


@pytest.fixture(scope="module", params=BAD_GROUP_KEYS, ids=_group_id_name)
def bad_group_configs(request: SubRequest) -> list[Dict[str, Any]]:
    """
    Provide bad lists of groups configs, one at a time.

    :param request: request

    :return: bad lists of groups configs
    """
    return _get_group_configs_from_keys(request.param)


def test_get_groups_from_json_empty_list() -> None:
    """Test the ``get_groups_from_json`` helper functions handling of empty input."""
    groups = get_groups_from_json([])
    assert groups == {}
    # empty or whitespace strings should also be ignored
    groups = get_groups_from_json([""])
    assert groups == {}
    groups = get_groups_from_json(["  ", "", " "])
    assert groups == {}


def _validate_group(definition: Dict[str, Any], group: tango.Group) -> None:
    """
    Compare groups test definition dict to actual tango.Group.

    :param definition: check tango.Group
    :param group: actual group
    """
    expected_group_name = definition["group_name"]  # key must exist
    expected_devices = definition.get("devices", [])  # key may exist
    expected_subgroups = definition.get("subgroups", [])  # key may exist

    print("Checking group:", expected_group_name, group)
    assert group is not None
    assert expected_group_name == group.get_name()
    device_list = group.get_device_list(forward=False)
    assert expected_devices == list(device_list)

    for expected_subgroup in expected_subgroups:
        print("\tsubgroup def", expected_subgroup)
        subgroup = group.get_group(expected_subgroup["group_name"])
        assert subgroup is not None
        # recurse the tree
        _validate_group(expected_subgroup, subgroup)


def test_get_groups_from_json_valid(valid_group_configs: list[Dict[str, Any]]) -> None:
    """
    Test the ``get_groups_from_json`` helper function's handling of valid input.

    :param valid_group_configs: fixture that returns valid group configs
    """
    json_definitions = _jsonify_group_configs(valid_group_configs)
    groups = get_groups_from_json(json_definitions)

    # Check result
    assert len(groups) == len(valid_group_configs)
    for group_config in valid_group_configs:
        name = group_config["group_name"]
        group = groups[name]
        _validate_group(group_config, group)


def test_get_groups_from_json_invalid(bad_group_configs: list[Dict[str, Any]]) -> None:
    """
    Test the ``get_groups_from_json`` helper function's handling of invalid input.

    :param bad_group_configs: fixture that returns invalid group configs
    """
    json_definitions = _jsonify_group_configs(bad_group_configs)
    with pytest.raises(GroupDefinitionsError):
        get_groups_from_json(json_definitions)


def test_get_tango_device_type_id() -> None:
    """Test the ``get_tango_device_type_id`` helper function."""
    device_name = "domain/family/member"
    result = get_tango_device_type_id(device_name)
    assert result == ["family", "member"]


@pytest.mark.parametrize(
    "in_test, context",
    [
        (
            False,
            pytest.warns(
                UserWarning,
                match="foo should only be used for testing purposes",
            ),
        ),
        (True, nullcontext()),
    ],
)
def test_for_testing_only(in_test: bool, context: ContextManager) -> None:
    """
    Test the @for_testing_only decorator.

    Test that a warning is raised if and only if we are NOT testing.
    This is achieved by patching the test, which cannot be done using
    the ``@decorator`` syntax.

    :param in_test: whether we are in a test or not.
    :param context: the testing context: either a pytest.warns, or a
        null_context
    """

    def foo() -> str:
        """
        Return a known value.

        This is a dummy function for the decorator under test to wrap.

        :return: a known value
        """
        return "foo"

    foo = for_testing_only(foo, _testing_check=lambda: in_test)

    with context:
        assert foo() == "foo"


def test_for_testing_only_decorator() -> None:
    """Test the for_testing_only decorator using the usual @decorator syntax."""

    @for_testing_only
    def bah() -> str:
        """
        Return a known value.

        This is a dummy function for the decorator under test to wrap.

        :return: a known value
        """
        return "bah"

    with pytest.warns(None) as warning_record:  # type: ignore[call-overload]
        assert bah() == "bah"
    assert len(warning_record) == 0  # no warning was raised because we are testing
