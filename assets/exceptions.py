class BotError(Exception):
    """Base exception for the project."""


class CommandInvocationError(BotError):
    """An user has invoked a command but doesn't meet the requirements"""


class CommandSyntaxError(CommandInvocationError):
    """A syntax error was done when invoking a command"""


class AvailabilityError(CommandInvocationError):
    """
    The user has already invoked an other command that is in conflict with this one event that has the same date and
    time...)
    """


class BelongingError(CommandInvocationError):
    """The user doesn't belong to a specific event/game/etc"""


class CommandPermissionError(CommandInvocationError):
    """The user misses one one more game- or event-related permissions t invoke this command"""


class CommandExecutionError(BotError):
    """An error occurred while processing the command"""


class GameRelatedError(CommandExecutionError):
    """An error occurred while performing a game-related operation"""


class EventRelatedError(CommandExecutionError):
    """An error occurred while performing an event-related operation"""
