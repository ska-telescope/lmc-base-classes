"""Tests for ska.base.control_model."""
import pytest

from collections import Counter

from ska.base.control_model import DeviceStateModel
from ska.base.faults import StateModelError


class OnOffModel(DeviceStateModel):
    __transitions = {
        ("ON", "off"): (
            "OFF",
            lambda self: self.count_transition("on->off"),
        ),
        ("OFF", "on"): (
            "ON",
            lambda self: self.count_transition("off->on"),
        ),
    }

    def __init__(self):
        super().__init__(self.__transitions, "ON")
        self.counter = Counter()

    def count_transition(self, name):
        self.counter[name] += 1


def test_initial_state():
    on_off = OnOffModel()
    assert on_off.state == "ON"


def test_try_valid_action_returns_true_and_does_not_change_state():
    on_off = OnOffModel()
    assert on_off.try_action("off")
    assert on_off.state == "ON"


def test_try_invalid_action_raises_and_does_not_change_state():
    on_off = OnOffModel()
    with pytest.raises(StateModelError):
        on_off.try_action("on")
    assert on_off.state == "ON"


def test_valid_state_transitions_succeed():
    on_off = OnOffModel()

    on_off.perform_action("off")
    assert on_off.state == "OFF"
    on_off.perform_action("on")
    assert on_off.state == "ON"


def test_invalid_state_transitions_fail():
    on_off = OnOffModel()

    with pytest.raises(StateModelError):
        on_off.perform_action("on")
    on_off.perform_action("off")
    with pytest.raises(StateModelError):
        on_off.perform_action("off")
    with pytest.raises(StateModelError):
        on_off.perform_action("invalid")


def test_side_effect_is_called():
    on_off = OnOffModel()

    on_off.perform_action("off")
    on_off.perform_action("on")
    on_off.perform_action("off")

    assert on_off.counter["on->off"] == 2
    assert on_off.counter["off->on"] == 1


def test_update_transitions_only_applies_to_instances():
    on_off = OnOffModel()

    on_off_updated = OnOffModel()
    on_off_updated.update_transitions({("ON", "break"): ("BROKEN", None)})

    assert on_off.is_action_allowed("off")
    assert not on_off.is_action_allowed("break")
    assert on_off_updated.is_action_allowed("off")
    assert on_off_updated.is_action_allowed("break")
