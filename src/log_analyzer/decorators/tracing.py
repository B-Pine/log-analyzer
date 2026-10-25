"""@log_call: log every call with its arguments and result."""

import logging
import reprlib
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger("log_analyzer")


def log_call(func: Callable[P, R]) -> Callable[P, R]:
    """Log each call's arguments and return value at DEBUG level.

    reprlib shortens long values, so passing a huge list doesn't flood
    the log.

    Example:
        >>> @log_call
        ... def greet(name: str) -> str:
        ...     return f"hi {name}"
        >>> greet("Aline")
        'hi Aline'
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        arguments = ", ".join(
            [reprlib.repr(arg) for arg in args]
            + [f"{key}={reprlib.repr(value)}" for key, value in kwargs.items()]
        )
        logger.debug("calling %s(%s)", func.__qualname__, arguments)
        result = func(*args, **kwargs)
        logger.debug("%s returned %s", func.__qualname__, reprlib.repr(result))
        return result

    return wrapper
