"""Exceptions helper module.

This module defines the base exception class for any project using this
library. All exception classes should inherit from `DakaraError`:

>>> class MyError(DakaraError):
...     pass

This helps to differentiate known exceptions and unknown ones, which are real
bugs.

It defines `generate_exception_handler` that allows to generate functions which
will catch an exception, add a custom error message and re-raise it. It also
defines `handle_all_exceptions` that can be used on `__main__` module to catch
all program exceptions.
"""

import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DakaraError(Exception):
    """Basic exception class for the project."""


class DakaraHandledError(Exception):
    """Basic exception class for errors that have been handled.

    Must be used in multiple inheritance.
    """


def generate_exception_handler(exception_class, error_message):
    """Generate a context manager to take care of given exception.

    It will add a custom message to an expected exception class. An exception
    derived from the caught exception (that can be a subclass of
    `exception_class`) and from the generic `DakaraHandledError` is then
    raised.

    >>> class MyError(Exception):
    ...     pass
    >>> handle_my_error = generate_exception_handler(MyError, "extra message")
    >>> try:
    ...     with handle_my_error():
    ...         raise MyError("initial message")
    ... except MyError as error:
    ...     pass
    >>> assert str(error).split() == ["initial message", "extra message"]
    >>> assert isinstance(error, MyError)
    >>> assert isinstance(error, DakaraHandledError)

    Args:
        exception_class (Exception or list of Exception): Exception class to
            catch.
        error_message (str): Error message to display. It will be displayed on
            the next line after the exception message.

    Returns:
        function: Context manager function.
    """

    @contextmanager
    def function():
        try:
            yield None

        except exception_class as error:

            class HandledError(error.__class__, DakaraHandledError):
                pass

            raise HandledError("{}\n{}".format(error, error_message)) from error

    return function


class ExitValue:
    """Container for the exit value.

    Attributes:
        value (int): Exit value, default to 0.
    """

    def __init__(self):
        self.value = 0


@contextmanager
def handle_all_exceptions(bugtracker_url, logger=logger, debug=False):
    """Handle all exceptions and yield an exit value.

    Unless in debug mode, no exceptions will be raised.

    >>> import sys
    >>> with handle_all_exceptions(
    ...    "https://www.example.com/bugtracker"
    ... ) as exit_value:
    ...    # your program here
    >>> sys.exit(exit_value.value)

    Args:
        bugtracker_url (str): URL address of the bugtracker, displayed on
            unexpected exceptions.
        logger (logging.Logger): Logger. If not given, will take the current
            module's logger.
        debug (bool): If True, known and unknown exceptions will be directly
            raised.

    Yields:
        ExitValue: Container with the return value, stored in attribute
        `value`. If no error happened, the return value is 0, in case of
        Ctrl+C, it is 255, in case of a known error, it is 1, in case of an
        unknown error, it is 2.
    """
    container = ExitValue()

    try:
        yield container

    except KeyboardInterrupt:
        container.value = 255
        logger.info("Quit by user")

    except DakaraError as error:
        container.value = 1

        # directly re-raise the error in debug mode
        if debug:
            raise

        # just log it otherwise
        logger.critical(error)

    except BaseException as error:
        container.value = 2

        # directly re-raise the error in debug mode
        if debug:
            raise

        # show the error and a special message otherwise
        logger.exception("Unexpected error: %s", error)
        logger.critical("Please fill a bug report at '%s'", bugtracker_url)
