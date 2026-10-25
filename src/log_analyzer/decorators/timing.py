"""@timer: log how long a function takes."""

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger("log_analyzer")


def timer(func: Callable[P, R]) -> Callable[P, R]:
    """Log the wall-clock time of every call at INFO level.

    Only useful on functions that do their work when called. On a function
    that returns a generator or a lazy map/filter, it would only time how
    long it took to create the iterator, which is almost nothing.

    Example:
        >>> @timer
        ... def add(a: int, b: int) -> int:
        ...     return a + b
        >>> add(2, 3)
        5
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.info("%s took %.2f ms", func.__qualname__, elapsed_ms)

    return wrapper
