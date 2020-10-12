"""
This module provides abstract base classes for device commands, and a
ResultCode enum.
"""
import enum
import logging
from ska.base.faults import CommandError, ResultCodeError, StateModelError

module_logger = logging.getLogger(__name__)


class ResultCode(enum.IntEnum):
    """
    Python enumerated type for command return codes.
    """

    OK = 0
    """
    The command was executed successfully.
    """

    STARTED = 1
    """
    The command has been accepted and will start immediately.
    """

    QUEUED = 2
    """
    The command has been accepted and will be executed at a future time
    """

    FAILED = 3
    """
    The command could not be executed.
    """

    UNKNOWN = 4
    """
    The status of the command is not known.
    """


class BaseCommand:
    """
    Abstract base class for Tango device server commands. Ensures the
    command is run, and that if the command errors, the "fatal_error"
    action will be called on the state model.
    """

    def __init__(self, target, state_model, logger=None):
        """
        Creates a new BaseCommand object for a device.

        :param state_model: the state model that this command uses, for
             example to raise a fatal error if the command errors out.
        :type state_model: SKABaseClassStateModel or a subclass of same
        :param target: the object that this base command acts upon. For
            example, the device that this BaseCommand implements the
            command for.
        :type target: object
        :param logger: the logger to be used by this Command. If not
            provided, then a default module logger will be used.
        :type logger: a logger that implements the standard library
            logger interface
        """
        self.name = self.__class__.__name__
        self.target = target
        self.state_model = state_model
        self.logger = logger or module_logger

    def __call__(self, argin=None):
        """
        What to do when the command is called. This base class simply
        calls ``do()`` or ``do(argin)``, depending on whether the
        ``argin`` argument is provided.

        :param argin: the argument passed to the Tango command, if
            present
        :type argin: ANY
        """
        try:
            return self._call_do(argin)
        except Exception:
            self.logger.exception(
                f"Error executing command {self.name} with argin '{argin}'"
            )
            self.fatal_error()
            raise

    def _call_do(self, argin=None):
        """
        Helper method that ensures the ``do`` method is called with the
        right arguments, and that the call is logged.

        :param argin: the argument passed to the Tango command, if
            present
        :type argin: ANY
        """
        if argin is None:
            returned = self.do()
        else:
            returned = self.do(argin=argin)

        self.logger.info(
            f"Exiting command {self.name}"
        )
        return returned

    def do(self, argin=None):
        """
        Hook for the functionality that the command implements. This
        class provides stub functionality; subclasses should subclass
        this method with their command functionality.

        :param argin: the argument passed to the Tango command, if
            present
        :type argin: ANY
        """
        raise NotImplementedError(
            "BaseCommand is abstract; do() must be subclassed not called."
        )

    def fatal_error(self):
        """
        Callback for a fatal error in the command, such as an unhandled
        exception.
        """
        self._perform_action("fatal_error")

    def _is_action_allowed(self, action):
        """
        Helper method; whether a given action is permitted in the
        current state of the state model.

        :param action: the action on the state model that is being
            scrutinised
        :type action: string
        :returns: whether the action is allowed
        :rtype: boolean
        """
        return self.state_model.is_action_allowed(action)

    def _try_action(self, action):
        """
        Helper method; "tries" an action on the state model.

        :param action: the action to perform on the state model
        :type action: string
        :raises CommandError: if the action is not allowed in current state
        :returns: True is the action is allowed
        """
        try:
            return self.state_model.try_action(action)
        except StateModelError as exc:
            raise CommandError(
                f"Error executing command {self.name}"
            ) from exc

    def _perform_action(self, action):
        """
        Helper method; performs an action on the state model, thus
        driving state

        :param action: the action to perform on the state model
        :type action: string
        """
        self.state_model.perform_action(action)


class ResponseCommand(BaseCommand):
    """
    Abstract base class for a tango command handler, for commands that
    execute a procedure/operation and return a (ResultCode, message)
    tuple.
    """

    def __call__(self, argin=None):
        """
        What to do when the command is called. This base class simply
        calls ``do()`` or ``do(argin)``, depending on whether the
        ``argin`` argument is provided.

        :param argin: the argument passed to the Tango command, if
            present
        :type argin: ANY
        """
        try:
            (return_code, message) = self._call_do(argin)
        except Exception:
            self.logger.exception(
                f"Error executing command {self.name} with argin '{argin}'"
            )
            self.fatal_error()
            raise
        return (return_code, message)

    def _call_do(self, argin=None):
        """
        Helper method that ensures the ``do`` method is called with the
        right arguments, and that the call is logged.

        :param argin: the argument passed to the Tango command, if
            present
        :type argin: ANY
        """
        if argin is None:
            (return_code, message) = self.do()
        else:
            (return_code, message) = self.do(argin=argin)

        self.logger.info(
            f"Exiting command {self.name} with return_code {return_code!s}, "
            f"message: '{message}'"
        )
        return (return_code, message)


class ActionCommand(ResponseCommand):
    """
    Abstract base class for a tango command, which checks a state model
    to find out whether the command is allowed to be run, and after
    running, sends an action to that state model, thus driving device
    state.
    """
    def __init__(
        self, target, state_model, action_hook, start_action=False, logger=None
    ):
        """
        Create a new ActionCommand for a device.

        :param target: the object that this base command acts upon. For
            example, the device that this ActionCommand implements the
            command for.
        :type target: object
        :param action_hook: a hook for the command, used to build
            actions that will be sent to the state model; for example,
            if the hook is "scan", then success of the command will
            result in action "scan_succeeded" being sent to the state
            model.
        :type action_hook: string
        :param start_action: whether the state model supports a start
            action (i.e. to put the state model into an transient state
            while the command is running); default False
        :type start_action: boolean
        :param logger: the logger to be used by this Command. If not
            provided, then a default module logger will be used.
        :type logger: a logger that implements the standard library
            logger interface
        """
        super().__init__(target, state_model, logger=logger)
        self._succeeded_hook = f"{action_hook}_succeeded"
        self._failed_hook = f"{action_hook}_failed"

        self._started_hook = None
        if start_action:
            self._started_hook = f"{action_hook}_started"

    def __call__(self, argin=None):
        """
        What to do when the command is called. This is implemented to
        check that the command is allowed to run, then run the command,
        then send an action to the state model advising whether the
        command succeeded or failed.

        :param argin: the argument passed to the Tango command, if
            present
        :type argin: ANY
        """
        self.check_allowed()
        try:
            self.started()
            (return_code, message) = self._call_do(argin)
            self._returned(return_code)
        except Exception:
            self.logger.exception(
                f"Error executing command {self.name} with argin '{argin}'"
            )
            self.fatal_error()
            raise
        return (return_code, message)

    def _returned(self, return_code):
        """
        Helper method that handles the return of the ``do()`` method.
        If the return code is OK or FAILED, then it performs an
        appropriate action on the state model. Otherwise it raises an
        error.

        :param return_code: The return_code returned by the ``do()``
            method
        :type return_code: :py:class:`ResultCode`
        """
        if return_code == ResultCode.OK:
            self.succeeded()
        elif return_code == ResultCode.FAILED:
            self.failed()
        else:
            if self._started_hook is None:
                raise ResultCodeError(
                    f"ActionCommands that do not have a started action may"
                    f"only return with code OK or FAILED, not {return_code!s}."
                )

    def check_allowed(self):
        """
        Checks whether the command is allowed to be run in the current
        state of the state model.

        :returns: True if the command is allowed to be run
        :raises StateModelError: if the command is not allowed to be run
        """
        return self._try_action(self._started_hook or self._succeeded_hook)

    def is_allowed(self):
        """
        Whether this command is allowed to run in the current state of
        the state model.

        :returns: whether this command is allowed to run
        :rtype: boolean
        """
        return self._is_action_allowed(
            self._started_hook or self._succeeded_hook
        )

    def started(self):
        """
        Action to perform upon starting the comand.
        """
        if self._started_hook is not None:
            self._perform_action(self._started_hook)

    def succeeded(self):
        """
        Callback for the successful completion of the command.
        """
        self._perform_action(self._succeeded_hook)

    def failed(self):
        """
        Callback for the failed completion of the command.
        """
        self._perform_action(self._failed_hook)
