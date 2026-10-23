"""Custom exceptions raised by the log_analyzer package."""


class LogAnalyzerError(Exception):
    """Base class for all errors raised by log_analyzer.

    Catch this to handle any error from the package in one place.
    """


class LogFileError(LogAnalyzerError):
    """Raised when a log file cannot be found, read or written."""
