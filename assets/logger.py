"""
Default logger for this project. We don't use the library logging.py because discord already use it, and we receive a
lot of useless info.
"""

import sys
import enum
import time
import datetime
import logging


class Level(enum.Enum):
    """Represents a severity level of a logger"""
    DEBUG = 0
    INFO = 10
    WARNING = 20
    ERROR = 30
    CRITICAL = 40


class Logger:
    def __init__(self, level, *, fmt="{level} : {message}", file=sys.stderr, filemode="a"):
        """
        Initialize self

        Parameters
        ----------

        level - The severity level of the logger
        fmt - The format for the log
        """
        self._output = None
        self.set_output(file, filemode)

        self._level = level
        self._level_fixed = False
        self._fmt = fmt

    def enabled_for(self, level):
        """
        Returns True if self is enabled for the level LEVEL or below, False otherwise.
        e.g. this will also return True if self is enabled for DEBUG and the passed LEVEL is WARN.
        """
        return level.value >= self._level.value

    def log(self, level: Level, message: str):
        """
        Log MESSAGE with severity LEVEL.
        In fact, this prints the message (using the chosen format) with print() into the output file of the logger
        (sys.stderr by default)
        """
        if self.enabled_for(level):
            _fmt = self._fmt.format(
                datetime=datetime.datetime.fromtimestamp(time.time()),
                level=level.name,
                message=message
            )

            print(_fmt, file=self._output)

    def debug(self, message: str):
        """Log MESSAGE with severity 'DEBUG'"""
        self.log(Level.DEBUG, message)

    def info(self, message: str):
        """Log MESSAGE with severity 'INFO'"""
        self.log(Level.INFO, message)

    def warn(self, message: str):
        """Log MESSAGE with severity 'WARNING'"""
        self.log(Level.WARNING, message)

    def error(self, message: str):
        """Log MESSAGE with severity 'ERROR'"""
        self.log(Level.ERROR, message)

    def critical(self, message: str):
        """Log MESSAGE with severity 'CRITICAL'"""
        self.log(Level.CRITICAL, message)

    def set_output(self, file, filemode='a'):
        """
        Sets self.output to file. Notice that if FILE is a string, self.output gets the value open(file, filemode)
        instead
        """
        self._output = open(file, filemode) if isinstance(file, str) else file

    def set_format(self, fmt):
        """
        Sets the current log format to FMT
        FMT must be a str object that could contain :

        {message} (MANDATORY) : will be replaced by the log message
        {datetime} : will be replaced by the current datetime at every log
        {level} : will be replaced by the message severity level
        """

        if "{message}" not in fmt:
            raise ValueError("Defining a log format (%s) that doesn't contain '{message}'" % fmt)

        self._fmt = fmt

    def set_level(self, level):
        """Sets the severity level of the logger to LEVEL. This can only be called once."""
        if self._level_fixed:
            raise NameError("set_level() can be called only once !")

        self._level = level
        self._level_fixed = True


# Export
_ROOT_LOGGER = Logger(Level.WARNING)

enabled_for = _ROOT_LOGGER.enabled_for
log = _ROOT_LOGGER.log
debug = _ROOT_LOGGER.debug
info = _ROOT_LOGGER.info
warn = _ROOT_LOGGER.warn
error = _ROOT_LOGGER.error
critical = _ROOT_LOGGER.critical

set_output = _ROOT_LOGGER.set_output
set_format = _ROOT_LOGGER.set_format
set_level = _ROOT_LOGGER.set_level
