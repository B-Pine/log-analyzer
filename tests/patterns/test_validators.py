"""Tests for the IP, email and URL validation patterns."""

import pytest

from log_analyzer.patterns import EMAIL, IPV4, URL, is_valid_email, is_valid_ipv4, is_valid_url


@pytest.mark.parametrize("ip", ["192.168.1.10", "0.0.0.0", "255.255.255.255", "8.8.8.8"])
def test_valid_ipv4(ip: str) -> None:
    assert is_valid_ipv4(ip)


@pytest.mark.parametrize(
    "ip",
    ["256.1.1.1", "999.168.1.10", "192.168.1", "192.168.1.10.5",
     "192.168.1.x", "010.1.1.1", " 192.168.1.10", ""],
)
def test_invalid_ipv4(ip: str) -> None:
    assert not is_valid_ipv4(ip)


def test_ipv4_results_are_cached() -> None:
    is_valid_ipv4.cache_clear()
    for _ in range(5):
        is_valid_ipv4("192.168.1.10")
    info = is_valid_ipv4.cache_info()
    assert (info.misses, info.hits) == (1, 4)


@pytest.mark.parametrize(
    "email", ["aline@example.com", "eric.mugisha+shop@shop.rw", "a_b@sub.example.org"]
)
def test_valid_email(email: str) -> None:
    assert is_valid_email(email)


@pytest.mark.parametrize("email", ["aline@", "@example.com", "aline example.com", "aline@example"])
def test_invalid_email(email: str) -> None:
    assert not is_valid_email(email)


@pytest.mark.parametrize(
    "url", ["https://example.com", "http://example.com/home", "https://shop.rw/search?q=a&page=2"]
)
def test_valid_url(url: str) -> None:
    assert is_valid_url(url)


@pytest.mark.parametrize("url", ["example.com", "ftp://example.com", "https://", "https://a b.com"])
def test_invalid_url(url: str) -> None:
    assert not is_valid_url(url)


#   search() and findall(): finding patterns inside longer text 

def test_search_finds_an_email_anywhere_in_text() -> None:
    match = EMAIL.search("Contact the admin at aline@example.com for access.")
    assert match is not None and match.group() == "aline@example.com"


def test_findall_extracts_every_ip() -> None:
    text = "Blocked 10.0.0.1, then 192.168.1.10 and 172.16.0.5"
    assert IPV4.findall(text) == ["10.0.0.1", "192.168.1.10", "172.16.0.5"]


def test_findall_extracts_every_url() -> None:
    text = "See https://example.com/a and http://shop.rw/b for details"
    assert URL.findall(text) == ["https://example.com/a", "http://shop.rw/b"]
