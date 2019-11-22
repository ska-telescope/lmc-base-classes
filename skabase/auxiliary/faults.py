"""General SKA Tango Device Exceptions."""


class SKABaseError(Exception):
    """Base class for all SKA Tango Device exceptions."""


class GroupDefinitionsError(SKABaseError):
    """Error parsing or creating groups from GroupDefinitions."""


class LoggingLevelError(SKABaseError):
    """Error evaluating logging level."""


class LoggingTargetError(SKABaseError):
    """Error parsing logging target string."""
