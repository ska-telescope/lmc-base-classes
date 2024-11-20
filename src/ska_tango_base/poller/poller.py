# -*- coding: utf-8 -*-
#
# (c) 2022 CSIRO.
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.

"""This module provides a general framework and mechanism for polling."""
from __future__ import annotations

import enum
import logging
import threading
from typing import Generic, TypeVar

__all__ = ["Poller", "PollModel", "PollRequestT", "PollResponseT"]

module_logger = logging.getLogger(__name__)

PollRequestT = TypeVar("PollRequestT")
"""Type variable for object specifying what the poller should do next poll."""

PollResponseT = TypeVar("PollResponseT")
"""Type variable for object containing the result of the previous poll."""


class PollModel(Generic[PollRequestT, PollResponseT]):
    """Abstract base class for a polling model."""

    def get_request(self: PollModel[PollRequestT, PollResponseT]) -> PollRequestT:
        """
        Return the polling request to be executed at the next poll.

        This is a hook called by the poller each polling loop, to obtain
        instructions on what it should do on the next poll.

        :return: attribute request to be executed at the next poll.

        :raises NotImplementedError: because this class is abstract
        """  # noqa: DAR202
        raise NotImplementedError("PollModel is abstract.")

    def poll(
        self: PollModel[PollRequestT, PollResponseT],
        poll_request: PollRequestT,
    ) -> PollResponseT:
        """
        Perform a single poll.

        This is a hook called by the poller each polling loop.

        :param poll_request: specification of what is to be done on the
            poll. It might, for example, contain a list of reads and
            writes to be executed.

        :return: responses from this poll

        :raises NotImplementedError: because this class is abstract.
        """  # noqa: DAR202
        raise NotImplementedError("PollModel is abstract.")

    def polling_started(self: PollModel[PollRequestT, PollResponseT]) -> None:
        """
        Respond to polling having started.

        This is a hook called by the poller when it starts polling.
        """

    def polling_stopped(self: PollModel[PollRequestT, PollResponseT]) -> None:
        """
        Respond to polling having stopped.

        This is a hook called by the poller when it stops polling.
        """

    def poll_succeeded(
        self: PollModel[PollRequestT, PollResponseT], poll_response: PollResponseT
    ) -> None:
        """
        Handle successful completion of a poll.

        This is a hook called by the poller upon the successful
        completion of a poll.

        :param poll_response: The response to the poll, containing for
            example any values read.
        """

    def poll_failed(
        self: PollModel[PollRequestT, PollResponseT], exception: Exception
    ) -> None:
        """
        Respond to an exception being raised by a poll attempt.

        This is a hook called by the poller when an exception occurs.
        The polling loop itself never raises exceptions. It catches
        everything and simply calls this hook to let the polling model
        know what it caught.

        :param exception: the exception that was raised by a recent poll
            attempt.
        """


class Poller(Generic[PollRequestT, PollResponseT]):
    """A generic hardware polling mechanism."""

    class _State(enum.Enum):
        STOPPED = enum.auto()
        POLLING = enum.auto()
        KILLED = enum.auto()

    def __init__(
        self: Poller[PollRequestT, PollResponseT],
        poll_model: PollModel[PollRequestT, PollResponseT],
        poll_rate: float = 1.0,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Initialise a new instance.

        :param poll_model: an object that this poller will call to both
            execute polls and provide with results
        :param poll_rate: how long (in seconds) to wait after polling,
            before polling again
        :param logger: a logger for this poller to use for logging
        """
        self._poll_model = poll_model
        self._poll_rate = poll_rate
        self._logger = logger or module_logger

        self._state = self._State.STOPPED
        self._condition = threading.Condition()

        self._polling_thread = threading.Thread(
            name="Polling thread",
            target=self._polling_loop,
            daemon=True,
        )

        # doesn't start polling, only starts the polling thread!
        self._polling_thread.start()

    def __del__(self: Poller[PollRequestT, PollResponseT]) -> None:
        """Prepare to delete the poller."""
        with self._condition:
            self._state = self._State.KILLED
            self._condition.notify()
        # We could join the thread here, but there's no need.
        # We trust that it will shut down, and it's a daemon anyhow.

    def start_polling(self: Poller[PollRequestT, PollResponseT]) -> None:
        """Start polling."""
        with self._condition:
            self._state = self._State.POLLING
            self._condition.notify()

    def stop_polling(self: Poller[PollRequestT, PollResponseT]) -> None:
        """Stop polling."""
        with self._condition:
            self._state = self._State.STOPPED
            self._condition.notify()

    def _polling_loop(self: Poller[PollRequestT, PollResponseT]) -> None:  # noqa: C901
        """Loop forever, either polling the hardware, or waiting to do so."""
        while self._state != self._State.KILLED:
            # state is STOPPED
            with self._condition:
                self._condition.wait()
                if self._state != self._State.POLLING:
                    continue

            # state is POLLING
            try:
                self._poll_model.polling_started()
            except Exception:  # pylint: disable=broad-except
                self._logger.exception("polling_started raised an exception.")
            while self._state == self._State.POLLING:
                try:
                    request = self._poll_model.get_request()
                    if request:
                        response = self._poll_model.poll(request)
                        self._poll_model.poll_succeeded(response)
                except Exception as exception:  # pylint: disable=broad-except
                    try:
                        self._poll_model.poll_failed(exception)
                    except Exception:  # pylint: disable=broad-except
                        self._logger.exception("poll_failed raised an exception.")

                with self._condition:
                    self._condition.wait(self._poll_rate)

            # "stop" event received; update state, then back to top of
            # loop i.e. block on "start" event
            try:
                self._poll_model.polling_stopped()
            except Exception:  # pylint: disable=broad-except
                self._logger.exception("polling_stopped raised an exception.")
