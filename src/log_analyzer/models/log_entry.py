"""LogEntry model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class LogEntry:
    """One parsed request from an access log.

    Attributes:
        timestamp: When the request was received.
        ip: Client IP address.
        method: HTTP method, e.g. "GET".
        path: Requested path, e.g. "/home".
        status: HTTP status code, e.g. 200.
    """

    timestamp: datetime
    ip: str
    method: str
    path: str
    status: int

    @property
    def status_class(self) -> str:
        """Status family, e.g. "2xx" for 200 or "4xx" for 404."""
        return f"{self.status // 100}xx"

    @property
    def is_error(self) -> bool:
        """True for client (4xx) and server (5xx) errors."""
        return self.status >= 400