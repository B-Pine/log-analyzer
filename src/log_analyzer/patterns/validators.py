"""Validation patterns for IP addresses, emails and URLs."""

import re
from functools import lru_cache
from ipaddress import IPv4Address, AddressValueError


IPV4: re.Pattern[str] = re.compile(r"\d{1,3}(\.\d{1,3}){3}")
EMAIL: re.Pattern[str] = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
URL: re.Pattern[str] = re.compile(r"https?://\S+")


@lru_cache(maxsize=1024)
def is_valid_ipv4(text: str) -> bool:
    """True if text is an IPv4 address with every part between 0 and 255.

    The regex checks the shape (four dot-separated numbers), then 
    `ipaddress` checks the value.

    Example:
        >>> is_valid_ipv4("192.168.1.10"), is_valid_ipv4("999.1.1.1"), is_valid_ipv4("abc")
        (True, False, False)
    """
    if IPV4.fullmatch(text) is None:
        return False
    try:
        IPv4Address(text)
    except AddressValueError:
        return False
    return True


def is_valid_email(text: str) -> bool:
    """True if text looks like an email address.

    Example:
        >>> is_valid_email("aline@example.com"), is_valid_email("aline@")
        (True, False)
    """
    return EMAIL.fullmatch(text) is not None


def is_valid_url(text: str) -> bool:
    """True if text is an http or https URL.

    Example:
        >>> is_valid_url("https://example.com/home"), is_valid_url("example.com")
        (True, False)
    """
    return URL.fullmatch(text) is not None