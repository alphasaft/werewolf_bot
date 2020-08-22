"""
Default logger for this project. We don't use the library logging.py because discord already use it, and we receive a
lot of useless info.
"""

import sys
import os
import enum
import time
import datetime


class Level(enum.Enum):
    """Represents a severity level of a logger"""
    DEBUG = 0
    INFO = 10
    WARNING = 20
    ERROR = 30
    CRITICAL = 40
    OFF = 50


# Base formats

CLASSIC_FMT = "{level} : {message}"
MESSAGE_FMT = "{message}"
DATED_FMT = "{level} : At {datetime} : {message}"


class Logger:
    def __init__(self, level, *, fmt=CLASSIC_FMT, file=sys.stderr, filemode="a", tee=False):
        """
        Initialize self

        Parameters
        ----------

        level - The severity level of the logger
        fmt - The format for the log ; see Logger.set_format() for more info
        file - a string or an IO object for the logs
        filemode - if file is specified and a string, the builtin function open will use this filemode to open it
        tee - if provided and True, prints every logged info in FILE and in sys.stdout
        """
        self._output = None
        self.set_output(file=file, filemode=filemode)

        self._level = level
        self._level_fixed = False
        self._fmt = fmt

        self._tee = tee

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

        try:
            Level(level)
        except ValueError:
            raise ValueError("LEVEL parameter must be a Level enum")

        if level == Level.OFF:
            raise ValueError("OFF level should only be used to prevent the logger to send any message")

        if self.enabled_for(level):
            _fmt = self._fmt.format(
                datetime=datetime.datetime.fromtimestamp(time.time()),
                level=level.name,
                message=message
            )

            # We force the message to be written instantly
            print(_fmt, file=self._output, flush=True)
            if self._tee:
                print(_fmt, flush=True)

            os.sync()

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

    def set_output(self, *, file, filemode='a'):
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

        try:
            Level(level)
        except ValueError:
            raise ValueError("LEVEL parameter must be a Level")

        self._level = Level(level)
        self._level_fixed = True

    def enable_tee(self):
        """Enables the 'tee' option"""
        self._tee = True

    def disable_tee(self):
        """Disables the 'tee' option"""
        self._tee = False


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
enable_tee = _ROOT_LOGGER.enable_tee
disable_tee = _ROOT_LOGGER.disable_tee
