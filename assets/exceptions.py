class BotError(Exception):
    """Base exception for the project."""


# command invocation error subclasses
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


# command execution error subclasses
class CommandExecutionError(BotError):
    """An error occurred while processing the command"""


class GameRelatedError(CommandExecutionError):
    """An error occurred while performing a game-related operation"""


class EventRelatedError(CommandExecutionError):
    """An error occurred while performing an event-related operation"""


# internal game error subclasses
class InternalGameError(GameRelatedError):
    """
    An error occurred in a game. This should always be caught, and only raised when you know that someone will catch it
    using a try/except block
    """


class ProtectedPlayer(InternalGameError):
    """Someone tried to wound a player that was protected by the guard"""
