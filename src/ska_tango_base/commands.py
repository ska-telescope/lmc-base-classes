"""
This module provides abstract base classes for device commands, and a
ResultCode enum.

Device commands are implement as a collection of mixins, as follows:

* **BaseCommand**: that implements the common pattern for commands;
  implement the do() method, and invoke the command class by *calling*
  it.

* **OperationalCommand**: implements a command that drives the operation
  state of the device; for example, "On()", "Standby()", "Off()".

* **ObservationCommand**: implements a command that drives the
  observation state of an obsDevice, such as a subarray; for example,
  AssignResources(), Configure(), Scan().

* **ResponseCommand**: for commands that return a (ResultCode, message)
  tuple.
  
* **CompletionCommand**: for commands that need to let their state
  machine know when they have completed; that is, long-running commands
  with transitional states, such as AssignResources() and Configure().

To use these commands: subclass from the mixins needed, then implement
the ``__init__`` and ``do`` methods. For example:

.. code-block:: py

    class AssignResourcesCommand(
        ObservationCommand, ResponseCommand, CompletionCommand
    ):
        def __init__(self, target, op_state_model, obs_state_model, logger=None):
            super().__init__(target, obs_state_model, "assign", op_state_model, logger=logger)

        def do(self, argin):
            # do stuff
            return (ResultCode.OK, "AssignResources command completed OK")

So there.
"""
import enum
import logging

from tango import DevState

from ska_tango_base.faults import CommandError, StateModelError

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
    Abstract base class for Tango device server commands. Checks that
    the command is allowed to run in the current state, and runs the
    command.
    """

    def __init__(self, target, state_model, *args, logger=None, **kwargs):
        """
        Creates a new BaseCommand object for a device.

        :param target: the object that this base command acts upon. For
            example, the device that this BaseCommand implements the
            command for.
        :type target: object
        :param state_model: the state model that this command uses, for
            example to raise a fatal error if the command errors out.
        :type state_model: SKABaseClassStateModel or a subclass of same
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


class OperationalCommand(BaseCommand):
    def __init__(self, target, state_model, action_slug, *args, logger=None, **kwargs):
        """
        A base command for commands that drive the operating state of
        the device.

        :param target: the object that this base command acts upon. For
            example, the device that this BaseCommand implements the
            command for.
        :type target: object
        :param state_model: the state model that this command uses, for
            example to raise a fatal error if the command errors out.
        :type state_model: SKABaseClassStateModel or a subclass of same
        :param action_slug: a slug for this command, used to construct
            actions on the state model corresponding to this command.
            For example, if we set the slug for the Scan() command to
            "scan", then invoking the command would correspond to the
            "scan_invoked" action on the state model.
        :param args: additional positional arguments
        :param logger: the logger to be used by this Command. If not
            provided, then a default module logger will be used.
        :type logger: a logger that implements the standard library
            logger interface
        :param kwargs: additional keyword arguments
        """
        super().__init__(target, state_model, action_slug, *args, logger=logger, **kwargs)
        self._action_slug = action_slug
        self._invoked_action = f"{action_slug}_invoked"

    def __call__(self, argin=None):
        """
        What to do when the command is called. Ensures that we perform
        the "invoked" action on the state machine.

        :param argin: the argument passed to the Tango command, if
            present
        :type argin: ANY

        :return: result of call

        :raises CommandError: if the command is not allowed
        """
        try:
            self.state_model.perform_action(self._invoked_action)
        except StateModelError as sme:
            raise CommandError("Command not permitted") from sme

        return super().__call__(argin)

    def is_allowed(self, raise_if_disallowed=False):
        """
        Whether this command is allowed to run in the current state of
        the state model.

        :param raise_if_disallowed: whether to raise an error or
            simply return False if the command is disallowed

        :returns: whether this command is allowed to run
        :rtype: boolean

        :raises CommandError: if the command is not allowed and
            `raise_if_disallowed` is True
        """
        try:
            return self.state_model.is_action_allowed(
                self._invoked_action,
                raise_if_disallowed=raise_if_disallowed
            )
        except StateModelError as state_model_error:
            raise CommandError(
                f"Error executing command {self.name}"
            ) from state_model_error


class ObservationCommand(OperationalCommand):
    def __init__(
        self,
        target,
        obs_state_model,
        action_slug,
        op_state_model,
        *args,
        logger=None,
        **kwargs
    ):
        """
        A base class for commands that drive the device's observing
        state.

        :param target: the object that this base command acts upon. For
            example, the device that this BaseCommand implements the
            command for.
        :type target: object
        :param obs_state_model: the observation state model that
                this command uses to check that it is allowed to run,
                and that it drives with actions.
        :type obs_state_model: :py:class:`CspSubElementObsStateModel`
        :param action_slug: a slug for this command, used to construct
            actions on the state model corresponding to this command.
            For example, if we set the slug for the Scan() command to
            "scan", then invoking the command would correspond to the
            "scan_invoked" action on the state model.
        :param op_state_model: the op state model that this command
            uses to check that it is allowed to run
        :type op_state_model: :py:class:`OpStateModel`
        :param logger: the logger to be used by this Command. If not
            provided, then a default module logger will be used.
        :type logger: a logger that implements the standard library
            logger interface
        """
        self._op_state_model = op_state_model
        super().__init__(
            target, obs_state_model, action_slug, *args, logger=logger, **kwargs
        )
        self._action_slug = action_slug
        self._invoked_action = f"{action_slug}_invoked"

    def is_allowed(self, raise_if_disallowed=False):
        """
        Whether this command is allowed to run in the current state of
        the state model.

        :param raise_if_disallowed: whether to raise an error or
            simply return False if the command is disallowed

        :returns: whether this command is allowed to run
        :rtype: boolean

        :raises CommandError: if the command is not allowed and
            `raise_if_disallowed` is True
        """
        if self._op_state_model.op_state != DevState.ON:
            if raise_if_disallowed:
                raise CommandError(
                    "Observation commands are only permitted in Op state ON."
                )
            else:
                return False

        return super().is_allowed(raise_if_disallowed=raise_if_disallowed)
    

class ResponseCommand(BaseCommand):
    """
    Abstract base class for a tango command handler, for commands that
    execute a procedure/operation and return a (ResultCode, message)
    tuple.
    """

    RESULT_LOG_LEVEL = {
        ResultCode.OK: logging.INFO,
        ResultCode.STARTED: logging.INFO,
        ResultCode.QUEUED: logging.INFO,
        ResultCode.FAILED: logging.ERROR,
        ResultCode.UNKNOWN: logging.WARNING
    }

    def _call_do(self, argin=None):
        """
        Helper method that ensures the ``do`` method is called with the
        right arguments, and that the call is logged.

        :param argin: the argument passed to the Tango command, if
            present
        :type argin: ANY

        :return: A tuple containing a return code and a string
            message indicating status. The message is for
            information purpose only.
        :rtype: (ResultCode, str)
        """
        if argin is None:
            (return_code, message) = self.do()
        else:
            (return_code, message) = self.do(argin=argin)

        self.logger.log(
            self.RESULT_LOG_LEVEL.get(return_code, logging.ERROR),
            f"Exiting command {self.name} with return_code "
            f"{return_code!s}, message: '{message}'."
        )
        return (return_code, message)


class CompletionCommand(BaseCommand):
    """
    Abstract base class for a command that sends a "completed" action to
    the state model at command completion.
    """

    def __init__(
        self, target, state_model, action_slug, *args, logger=None, **kwargs
    ):
        """
        Create a new ActionCommand for a device.

        :param target: the object that this base command acts upon. For
            example, the device that this ActionCommand implements the
            command for.
        :type target: object
        :param state_model: the state model that this command uses, for
            example to raise a fatal error if the command errors out.
        :type state_model: SKABaseClassStateModel or a subclass of same
        :param action_slug: a slug for this command, used to construct
            actions on the state model corresponding to this command.
            For example, if we set the slug for the Scan() command to
            "scan", then invokation and completion of the command would
            correspond respectively to the "scan_invoked" and
            "scan_completed" actions on the state model.
        :type action_slug: string
        :param args: additional positional arguments
        :param logger: the logger to be used by this Command. If not
            provided, then a default module logger will be used.
        :type logger: a logger that implements the standard library
            logger interface
        :param kwargs: additional keyword arguments
        """
        super().__init__(target, state_model, action_slug, *args, logger=logger, **kwargs)
        self._completed_hook = f"{action_slug}_completed"

    def __call__(self, argin=None):
        """
        What to do when the command is called. This is implemented to
        check that the command is allowed to run, then run the command,
        then send an action to the state model advising whether the
        command succeeded or failed.

        :param argin: the argument passed to the Tango command, if
            present
        :type argin: ANY

        :return: The result of the call.
        """
        result = super().__call__(argin)
        self.completed()
        return result

    def completed(self):
        """
        Callback for the completion of the command.
        """
        self.state_model.perform_action(self._completed_hook)
