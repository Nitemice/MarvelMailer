# Import necessary packages
from enum import Enum
import sys
import requests


class OrderedEnum(Enum):
    """Based on https://docs.python.org/3/library/enum.html"""
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class Verbosity(OrderedEnum):
    """Enum for verbosity of Notifier."""
    silent = -2
    quiet = -1
    normal = 0
    verbose = 1


class OutputMethod(Enum):
    """Enum for output methods for Notifier."""
    console = 1
    telegram = 2


class OutputMethodError(ValueError):
    """Exception raised if specified output method is not recognised."""

    def __init__(self, output_method):
        self.output_method = output_method

    @property
    def message(self) -> str:
        """Generate a basic error message, with the bad output type."""
        return "The specified output method (%(output_method)s) is not supported." \
               % {"output_method": self.output_method}


class Notifier:
    """
    Notifier

    Handles notifying the user of messages and errors.
    """

    def __init__(self, config=None, verbosity=Verbosity):
        """
        Initialise the Notifier.

        If no configuration is specified, the Notifier defaults to the console
        as its output method.

        An OutputMethodError will be raised if the specified notification
        method is not one included in the OutputMethod Enum.
        """
        self._verbosity = verbosity
        self.outputMethod = OutputMethod.console
        if config is not None:
            self.config = config
            if config["method"] == OutputMethod.telegram.name:
                self.outputMethod = OutputMethod.telegram
            elif config["method"] == OutputMethod.console.name:
                self.outputMethod = OutputMethod.console
            else:
                raise OutputMethodError(config["method"])

    # Error Functions
    def _error_console(self, message):
        print(message, file=sys.stderr, end='')

    def _error_telegram(self, message):
        bot_token = self.config["bot_token"]
        user_id = self.config["user_id"]
        url = "https://api.telegram.org/bot%(bot_token)s/" \
              "sendMessage?chat_id=%(user_id)s&text=%(message)s"
        message = "ERROR: " + message
        requests.get(url % locals())

    _errorFunctions = {
        OutputMethod.console: _error_console,
        OutputMethod.telegram: _error_telegram
    }

    def error(self, message):
        """Send the user an error message via the previously specified method."""
        if self._verbosity >= Verbosity.quiet:
            self._errorFunctions[self.outputMethod](self, message)

    # Notification Functions
    def _notify_console(self, message):
        print(message, file=sys.stdout, end='')

    def _notify_telegram(self, message):
        bot_token = self.config["bot_token"]
        user_id = self.config["user_id"]
        url = "https://api.telegram.org/bot%(bot_token)s/" \
              "sendMessage?chat_id=%(user_id)s&text=%(message)s"
        requests.get(url % locals())

    _notifyFunctions = {
        OutputMethod.console: _notify_console,
        OutputMethod.telegram: _notify_telegram
    }

    def notify(self, message):
        """Notify the user via the previously specified method."""
        if self._verbosity >= Verbosity.normal:
            self._notifyFunctions[self.outputMethod](self, message)

    # Log Functions
    def _log_console(self, message):
        print(message, file=sys.stdout, end='')

    def _log_telegram(self, message):
        bot_token = self.config["bot_token"]
        user_id = self.config["user_id"]
        url = "https://api.telegram.org/bot%(bot_token)s/" \
              "sendMessage?chat_id=%(user_id)s&text=%(message)s"
        requests.get(url % locals())

    _logFunctions = {
        OutputMethod.console: _log_console,
        OutputMethod.telegram: _log_telegram
    }

    def log(self, message):
        """Log additional information to the user via the previously specified method."""
        if self._verbosity >= Verbosity.verbose:
            self._logFunctions[self.outputMethod](self, message)
