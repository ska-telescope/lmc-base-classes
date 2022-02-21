"""This subpackage contains modules for test mocking in ska-tango-base."""


__all__ = [
    "MockCallable",
    "MockChangeEventCallback",
]

from .mock_callable import MockCallable, MockChangeEventCallback
