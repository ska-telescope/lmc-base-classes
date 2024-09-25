# -*- coding: utf-8 -*-
#
# This file is part of the SKA Tango Base project
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.
"""This module contains the tests for the SKABaseDevice's CommandTracker."""
from __future__ import annotations

import time
from unittest.mock import Mock

import pytest
from ska_control_model import ResultCode, TaskStatus

from ska_tango_base.base import CommandTracker


class TestCommandTracker:
    """Tests of the CommandTracker class."""

    @pytest.fixture
    def callbacks(self: TestCommandTracker, mocker: Mock) -> dict[str, Mock]:
        """
        Return a dictionary of mocks for use as callbacks.

        These callbacks will be passed to the command tracker under
        test, and can then be used in testing to check that callbacks
        are called as expected.

        :param mocker: pytest fixture that wraps
            :py:mod:`unittest.mock`.

        :return: a dictionary of mocks for use as callbacks
        """
        return {
            "queue": mocker.Mock(),
            "status": mocker.Mock(),
            "progress": mocker.Mock(),
            "result": mocker.Mock(),
            "exception": mocker.Mock(),
            "event": mocker.Mock(),
        }

    @pytest.fixture
    def removal_time(self: TestCommandTracker) -> float:
        """
        Return how long the command tracker should retain memory of a completed command.

        :return: amount of time, in seconds.
        """
        return 0.1

    @pytest.fixture
    def command_tracker(
        self: TestCommandTracker,
        callbacks: dict[str, Mock],
        removal_time: float,
    ) -> CommandTracker:
        """
        Return the command tracker under test.

        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        :param removal_time: how long completed command is retained

        :return: the command tracker under test
        """
        return CommandTracker(
            queue_changed_callback=callbacks["queue"],
            status_changed_callback=callbacks["status"],
            progress_changed_callback=callbacks["progress"],
            result_callback=callbacks["result"],
            exception_callback=callbacks["exception"],
            event_callback=callbacks["event"],
            removal_time=removal_time,
        )

    # TODO pylint: disable=too-many-statements
    def test_command_tracker(
        self: TestCommandTracker,
        command_tracker: CommandTracker,
        removal_time: float,
        callbacks: dict[str, Mock],
    ) -> None:
        """
        Test that the command tracker correctly tracks commands.

        :param command_tracker: the command tracker under test
        :param removal_time: how long completed command is retained
        :param callbacks: a dictionary of mocks, passed as callbacks to
            the command tracker under test
        """
        assert command_tracker.commands_in_queue == []
        assert command_tracker.command_statuses == []
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result is None
        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_not_called()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()
        callbacks["event"].assert_not_called()

        # 1st new command
        first_command_id = command_tracker.new_command("first_command")
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command")
        ]
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.STAGING)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result is None
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_called_once_with(
            [(first_command_id, "first_command")]
        )
        callbacks["status"].assert_called_once_with(
            [(first_command_id, TaskStatus.STAGING)]
        )
        callbacks["queue"].reset_mock()
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()
        callbacks["event"].assert_called_once()
        callbacks["event"].reset_mock()

        # 1st command is queued
        command_tracker.update_command_info(first_command_id, status=TaskStatus.QUEUED)
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command")
        ]
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.QUEUED)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result is None
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_called_once_with(
            [(first_command_id, TaskStatus.QUEUED)]
        )
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()
        callbacks["event"].assert_called_once()
        callbacks["event"].reset_mock()

        # 1st command starts
        command_tracker.update_command_info(
            first_command_id, status=TaskStatus.IN_PROGRESS
        )
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command")
        ]
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.IN_PROGRESS)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result is None
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_called_once_with(
            [(first_command_id, TaskStatus.IN_PROGRESS)]
        )
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()
        callbacks["event"].assert_called_once()
        callbacks["event"].reset_mock()

        # 2nd new command
        second_command_id = command_tracker.new_command("second_command")
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command"),
            (second_command_id, "second_command"),
        ]
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.IN_PROGRESS),
            (second_command_id, TaskStatus.STAGING),
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result is None
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_called_once_with(
            [
                (first_command_id, "first_command"),
                (second_command_id, "second_command"),
            ]
        )
        callbacks["status"].assert_called_once_with(
            [
                (first_command_id, TaskStatus.IN_PROGRESS),
                (second_command_id, TaskStatus.STAGING),
            ]
        )
        callbacks["queue"].reset_mock()
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()
        callbacks["event"].assert_called_once()
        callbacks["event"].reset_mock()

        # 1st command reports progress
        command_tracker.update_command_info(first_command_id, progress=50)
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command"),
            (second_command_id, "second_command"),
        ]
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.IN_PROGRESS),
            (second_command_id, TaskStatus.STAGING),
        ]
        assert command_tracker.command_progresses == [(first_command_id, 50)]
        assert command_tracker.command_result is None
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_not_called()
        callbacks["progress"].assert_called_once_with([(first_command_id, 50)])
        callbacks["progress"].reset_mock()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()
        callbacks["event"].assert_called_once()
        callbacks["event"].reset_mock()

        # 1st command reports result
        command_tracker.update_command_info(
            first_command_id, result=(ResultCode.OK, "a message string")
        )
        assert command_tracker.command_statuses == [
            (first_command_id, TaskStatus.IN_PROGRESS),
            (second_command_id, TaskStatus.STAGING),
        ]
        assert command_tracker.command_progresses == [(first_command_id, 50)]
        assert command_tracker.command_result == (
            first_command_id,
            (ResultCode.OK, "a message string"),
        )
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_not_called()
        callbacks["progress"].assert_not_called()
        callbacks["progress"].reset_mock()
        callbacks["result"].assert_called_once_with(
            first_command_id, (ResultCode.OK, "a message string")
        )
        callbacks["result"].reset_mock()
        callbacks["exception"].assert_not_called()

        # 1st command is completed
        command_tracker.update_command_info(
            first_command_id, status=TaskStatus.COMPLETED
        )
        assert command_tracker.commands_in_queue == [
            (first_command_id, "first_command"),
            (second_command_id, "second_command"),
        ]
        time.sleep(removal_time + 0.1)
        assert command_tracker.commands_in_queue == [
            (second_command_id, "second_command")
        ]
        assert command_tracker.command_statuses == [
            (second_command_id, TaskStatus.STAGING)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result == (
            first_command_id,
            (ResultCode.OK, "a message string"),
        )
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_called_once_with(
            [(second_command_id, "second_command")]
        )
        callbacks["queue"].reset_mock()
        callbacks["status"].assert_called_once_with(
            [
                (first_command_id, TaskStatus.COMPLETED),
                (second_command_id, TaskStatus.STAGING),
            ]
        )
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        # 2nd command starts
        command_tracker.update_command_info(
            second_command_id, status=TaskStatus.IN_PROGRESS
        )
        assert command_tracker.commands_in_queue == [
            (second_command_id, "second_command")
        ]
        assert command_tracker.command_statuses == [
            (second_command_id, TaskStatus.IN_PROGRESS)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result == (
            first_command_id,
            (ResultCode.OK, "a message string"),
        )
        assert command_tracker.command_exception is None

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_called_once_with(
            [
                (second_command_id, TaskStatus.IN_PROGRESS),
            ]
        )
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_not_called()
        callbacks["exception"].assert_not_called()

        exception_to_raise = ValueError("Exception under test")

        # 2nd command fails
        command_tracker.update_command_info(
            second_command_id,
            status=TaskStatus.FAILED,
            exception=exception_to_raise,
        )
        assert command_tracker.commands_in_queue == [
            (second_command_id, "second_command")
        ]
        assert command_tracker.command_statuses == [
            (second_command_id, TaskStatus.FAILED)
        ]
        assert command_tracker.command_progresses == []
        assert command_tracker.command_result == (
            second_command_id,
            (ResultCode.FAILED, str(exception_to_raise)),
        )
        assert command_tracker.command_exception == (
            second_command_id,
            exception_to_raise,
        )

        callbacks["queue"].assert_not_called()
        callbacks["status"].assert_called_once_with(
            [
                (second_command_id, TaskStatus.FAILED),
            ]
        )
        callbacks["status"].reset_mock()
        callbacks["progress"].assert_not_called()
        callbacks["result"].assert_called_once_with(
            second_command_id, (ResultCode.FAILED, str(exception_to_raise))
        )
        callbacks["exception"].assert_called_once_with(
            second_command_id, exception_to_raise
        )
