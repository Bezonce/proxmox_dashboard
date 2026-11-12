"""Shared plumbing for the service clients: timeouts, readable errors, cached fetchers."""

import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

import requests
import streamlit as st
import urllib3

# Proxmox and the NAS use self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TIMEOUT = (2, 5)  # seconds: connect, read

P = ParamSpec("P")
T = TypeVar("T")


class ServiceError(Exception):
    """A failure with a short message that is safe to show on the page."""


def describe(error: Exception) -> str:
    if isinstance(error, ServiceError):
        return str(error)
    if isinstance(error, requests.Timeout):
        return "timed out"
    if isinstance(error, requests.RequestException):
        return "unreachable"
    return f"unexpected answer ({type(error).__name__})"


def request(method: str, url: str, **kwargs) -> requests.Response:
    """requests.request with the dashboard's timeout; network failures become ServiceError."""
    kwargs.setdefault("timeout", TIMEOUT)
    kwargs.setdefault("verify", False)
    try:
        return requests.request(method, url, **kwargs)
    except requests.RequestException as error:
        raise ServiceError(describe(error)) from None


def parse_json(response: requests.Response):
    if response.status_code in (401, 403):
        raise ServiceError(f"access denied (HTTP {response.status_code}) – check the API key")
    if not response.ok:
        raise ServiceError(f"HTTP {response.status_code}")
    try:
        return response.json()
    except ValueError:
        raise ServiceError("unexpected answer (not JSON)") from None


def get_json(url: str, *, headers: dict | None = None, params: dict | None = None):
    return parse_json(request("GET", url, headers=headers, params=params))


def cached(ttl: int) -> Callable[[Callable[P, T]], Callable[P, tuple[T | None, str | None]]]:
    """Cache a fetcher's result as (data, error).

    Failures are cached too, so a service that is down costs one timeout per `ttl`
    instead of one per page refresh, and a page never sees an exception.
    """

    def decorator(fetch: Callable[P, T]) -> Callable[P, tuple[T | None, str | None]]:
        @st.cache_data(ttl=ttl, show_spinner=False)
        @functools.wraps(fetch)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> tuple[T | None, str | None]:
            try:
                return fetch(*args, **kwargs), None
            except Exception as error:
                return None, describe(error)

        return wrapper

    return decorator
