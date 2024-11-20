# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""
Test of the ska_tango_base.poller subpackage.

There's just one test here. We provide a fake poll model that calls
"""
from __future__ import annotations

from threading import Barrier

import pytest
from ska_tango_testing.mock import MockCallableGroup

from ska_tango_base.poller import Poller, PollModel


@pytest.fixture(name="config")
def fixture_config() -> dict[str, int]:
    """
    Return a dictionary of config information.

    The "fail_per" entry contains an integer value indicating how often
    the poll model should raise an exception, causing the poll to fail.
    For example, if "fail_per" is set to 10, then the 10th, 20th, 30th,
    etc., poll will fail. This allows us to test failure handling.

    The "hang_after" entry contains an integer value indicating how
    often the poll model should hang behind a barrier that it shares
    with the test thread. This allows the test to coordinate timings,
    and thus avoid race conditions.

    :return: a dictionary of config information
    """
    return {
        "fail_per": 10,
        "hang_after": 25,
    }


@pytest.fixture(name="callbacks")
def fixture_callbacks() -> MockCallableGroup:
    """
    Return a group of callbacks with asynchrony support.

    :return: a group of callbacks with asynchrony support.
    """
    return MockCallableGroup(
        "failed", "polled", "requested", "started", "stopped", "succeeded"
    )


@pytest.fixture(name="barrier")
def fixture_barrier() -> Barrier:
    """
    Return the barrier that coordinates timings between polling and test thread.

    :return: the barrier that coordinats timings between polling and
        test thread.
    """
    return Barrier(2)


@pytest.fixture(name="poll_model")
def fixture_poll_model(
    callbacks: MockCallableGroup,
    barrier: Barrier,
    config: dict[str, int],
) -> PollModel[int, int]:
    """
    Return a poll model for the poller under test to drive.

    :param callbacks: a callback group that is called by the poll model
        whenever one of the poll model's hooks is called
    :param barrier: a barrier, shared by the poll model and this test,
        used to coordinate timings.
    :param config: configuration for this test.

    :return: a poll model for the poller under test to drive.
    """

    class _FakePollModel(PollModel[int, int]):
        def __init__(
            self: _FakePollModel,
            callbacks: MockCallableGroup,
            barrier: Barrier,
            config: dict[str, int],
        ):
            self._callbacks = callbacks
            self._barrier = barrier

            self._poll_count = 0

            self._fail_per = config["fail_per"]
            self._hang_after = config["hang_after"]

        def get_request(self: _FakePollModel) -> int:
            self._poll_count += 1
            self._callbacks["requested"](self._poll_count)
            return self._poll_count

        def poll(self: _FakePollModel, poll_request: int) -> int:
            self._callbacks["polled"](poll_request)
            if poll_request % self._fail_per == 0:
                raise ValueError(f"poll_request is a multiple of {self._fail_per}.")
            return -poll_request

        def polling_started(self: _FakePollModel) -> None:
            self._callbacks["started"]()

        def polling_stopped(self: _FakePollModel) -> None:
            self._callbacks["stopped"]()

        def poll_succeeded(self: _FakePollModel, poll_response: int) -> None:
            self._callbacks["succeeded"](poll_response)

            if -poll_response % self._hang_after == 0:
                self._barrier.wait()

        def poll_failed(self: _FakePollModel, exception: Exception) -> None:
            self._callbacks["failed"](exception)
            raise RuntimeError("poll_failed exception.")

    return _FakePollModel(callbacks, barrier, config)


@pytest.fixture(name="poller")
def fixture_poller(poll_model: PollModel[int, int]) -> Poller[int, int]:
    """
    Return the poller under test.

    :param poll_model: the model that is driven by the poller.

    :return: the poller under test.
    """
    return Poller(poll_model, poll_rate=0.01)


def test_poller(
    poller: Poller[int, int],
    callbacks: MockCallableGroup,
    barrier: Barrier,
    config: dict[str, int],
) -> None:  # noqa: DAR401
    """
    Test the poller.

    The poller is already hooked up to a poll model that calls a
    callback whenever one of its hooks is called. Thus we essentially
    have a trace of what the poller is doing. This test works by
    asserting against that trace.

    :param poller: the poller under test.
    :param callbacks: a callback group that is called by the poll model
        whenever one of the poll model's hooks is called
    :param barrier: a barrier, shared by the poll model and this test,
        used to coordinate timings.
    :param config: configuration for this test.
    """
    callbacks.assert_not_called()
    poller.start_polling()
    callbacks.assert_call("started")
    for iteration in range(1, config["hang_after"] + 1):
        callbacks.assert_call("requested", iteration)
        callbacks.assert_call("polled", iteration)
        if iteration % config["fail_per"] == 0:
            call_details = callbacks.assert_against_call("failed")
            with pytest.raises(ValueError, match="poll_request is a multiple of 10."):
                raise call_details["call_args"][0]
        else:
            callbacks.assert_call("succeeded", -iteration)

    poller.stop_polling()
    barrier.wait()
    callbacks.assert_call("stopped")
    callbacks.assert_not_called()

    poller.start_polling()
    callbacks.assert_call("started")
    for iteration in range(config["hang_after"] + 1, config["hang_after"] + 4):
        callbacks.assert_call("requested", iteration)
        callbacks.assert_call("polled", iteration)
        if iteration % config["fail_per"] == 0:
            call_details = callbacks.assert_against_call("failed")
            with pytest.raises(ValueError, match="poll_request is a multiple of 10."):
                raise call_details["call_args"][0]
        else:
            callbacks.assert_call("succeeded", -iteration)
