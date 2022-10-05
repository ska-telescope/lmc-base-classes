# -*- coding: utf-8 -*-
#
# (c) 2022 CSIRO.
#
# Distributed under the terms of the BSD 3-clause new license.
# See LICENSE.txt for more info.

"""This module provides a polling component manager."""
from __future__ import annotations

from logging import Logger
from typing import Any, Callable

from ska_tango_base.base import BaseComponentManager
from ska_tango_base.control_model import CommunicationStatus, PowerState

from .poller import Poller, PollModel, PollRequestT, PollResponseT


class PollingComponentManager(
    BaseComponentManager, PollModel[PollRequestT, PollResponseT]
):
    """Abstract base class for a component manager that polls its component."""

    def __init__(
        self: PollingComponentManager,
        logger: Logger,
        communication_state_callback: Callable,
        component_state_callback: Callable,
        poll_rate: float = 0.1,
        **kwargs: Any,
    ) -> None:
        """
        Initialise a new base component manager instance.

        :param logger: a logger for this component manager to use for
            logging
        :param communication_state_callback: callback to be called when
            the status of communications between the component manager
            and its component changes.
        :param component_state_callback: callback to be called when the
            state of the component changes.
        :param poll_rate: how often to poll, in seconds
        :param kwargs: initial values for additional attributes.
        """
        self._poller = Poller(self, poll_rate)

        super().__init__(
            logger,
            communication_state_callback,
            component_state_callback,
            power=PowerState.UNKNOWN,
            fault=None,
            **kwargs,
        )

    def start_communicating(self) -> None:
        """Start polling the component."""
        if self.communication_state == CommunicationStatus.ESTABLISHED:
            return
        if self.communication_state == CommunicationStatus.DISABLED:
            self._update_communication_state(CommunicationStatus.NOT_ESTABLISHED)
        # and we remain in NOT_ESTABLISHED until the polling loop is
        # actually talking to the spectrum analyser. It will tell us this
        # is the case by calling our `poll_succeeded` method.
        self._poller.start_polling()

    def polling_started(self) -> None:
        """
        Respond to polling having started.

        This is a hook called by the poller when it starts polling.
        """
        # There's no need to do anything here. We wait to receive some polled
        # values before we declare communication to be established.

    def stop_communicating(self) -> None:
        """Stop polling the spectrum analyser."""
        if self.communication_state == CommunicationStatus.DISABLED:
            return
        # communication remains ESTABLISHED until the polling loop actually
        # stops polling. It will tell us that it has stopped by calling the
        # `polling_stopped` method.

        self._poller.stop_polling()

    def polling_stopped(self) -> None:
        """
        Respond to polling having stopped.

        This is a hook called by the poller when it stops polling.
        """
        self._update_component_state(power=PowerState.UNKNOWN, fault=None)
        self._update_communication_state(CommunicationStatus.DISABLED)

    def poll_failed(self, exception: Exception) -> None:
        """
        Respond to an exception being raised by a poll attempt.

        This is a hook called by the poller when an exception occurs.

        :param exception: the exception that was raised by a recent poll
            attempt.
        """
        self._update_communication_state(CommunicationStatus.NOT_ESTABLISHED)
        self.logger.error(f"Poll failed: {repr(exception)}")

    def poll_succeeded(self, poll_response: PollResponseT) -> None:
        """
        Handle a successful poll, including any values received.

        This is a hook called by the poller at the end of each
        successful poll.

        :param poll_response: response to the poll, including any values
            received.
        """
        # Reiterate that communication is established, just in case it
        # had dropped out.
        self.logger.debug("Setting communications ESTABLISHED")
        self._update_communication_state(CommunicationStatus.ESTABLISHED)

    def get_request(self) -> PollRequestT:
        """
        Return the reads and writes to be executed in the next poll.

        :raises NotImplementedError: because this class is abstract.

        :returns: reads and writes to be executed in the next poll.
        """  # noqa: DAR202
        raise NotImplementedError("PollingComponentManager is abstract.")

    def poll(
        self,
        poll_request: PollRequestT,
    ) -> PollResponseT:
        """
        Poll the hardware.

        Connect to the hardware, write any values that are to be
        written, and then read all values.

        :param poll_request: specification of the reads and writes
            to be performed in this poll.

        :raises NotImplementedError: because this class is abstract.

        :return: responses to queries in this poll
        """  # noqa: DAR202
        raise NotImplementedError("PollingComponentManager is abstract.")
