"""General SKA Tango Device Exceptions."""


class SKABaseError(Exception):
    """Base class for all SKA Tango Device exceptions."""


class GroupDefinitionsError(SKABaseError):
    """Error parsing or creating groups from GroupDefinitions."""


class LoggingLevelError(SKABaseError):
    """Error evaluating logging level."""


class LoggingTargetError(SKABaseError):
    """Error parsing logging target string."""


class ResultCodeError(ValueError):
    """A method has returned an invalid return code."""


class StateModelError(ValueError):
    """Error in state machine model related to transitions or state."""


class CommandError(RuntimeError):
    """Error executing a BaseCommand or similar."""


class CapabilityValidationError(ValueError):
    """Error in validating capability input against capability types."""

class ComponentError(Exception):
    """Component cannot perform as requested."""

class ComponentFault(ComponentError):
    """Component is in FAULT state and cannot perform as requested."""
