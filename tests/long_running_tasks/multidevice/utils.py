"""Multi device test utils."""
from queue import Queue
from typing import Any


class LRCAttributesStore:
    """Utility class to keep track of long running command attribute changes."""

    def __init__(self) -> None:
        """Create the queues."""
        self.queues = {}
        self.attributes = [
            "longrunningcommandsinqueue",
            "longrunningcommandstatus",
            "longrunningcommandprogress",
            "longRunningcommandidsinqueue",
            "longrunningcommandresult",
        ]
        for attribute in self.attributes:
            self.queues[attribute] = Queue()

    def push_event(self, ev):
        """Catch and store events.

        :param ev: The event data
        :type ev: EventData
        """
        if ev.attr_value and ev.attr_value.name.lower() in self.attributes:
            if ev.attr_value.value:
                self.store_push_event(ev.attr_value.name.lower(), ev.attr_value.value)

    def store_push_event(self, attribute_name: str, value: Any):
        """Store attribute changes as they change.

        :param attribute_name: a valid LCR attribute
        :type attribute_name: str
        :param value: The value of the attribute
        :type value: Any
        """
        assert attribute_name in self.queues
        self.queues[attribute_name].put_nowait(value)

    def get_attribute_value(self, attribute_name: str, fetch_timeout: float = 2.0):
        """Read a value from the queue.

        :param attribute_name: a valid LCR attribute
        :type attribute_name: str
        :param fetch_timeout: How long to wait for a event, defaults to 2.0
        :type fetch_timeout: float, optional
        :return: An attribute value fromthe queue
        :rtype: Any
        """
        return self.queues[attribute_name.lower()].get(timeout=fetch_timeout)
