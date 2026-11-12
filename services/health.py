"""Up/down checks for every service on the home grid. None of them needs a login."""

from concurrent.futures import ThreadPoolExecutor

import streamlit as st

from services.client import ServiceError, request
from services.registry import SERVICES

UP, DOWN, UNKNOWN = "up", "down", "unknown"


def _probe(url: str) -> tuple[str, str]:
    if not url:
        return UNKNOWN, "not checked"
    try:
        # stream=True: only the status line matters, don't download the page behind it
        with request("GET", url, timeout=(2, 3), allow_redirects=False, stream=True) as response:
            status = response.status_code
    except ServiceError as error:
        return DOWN, str(error)
    # A redirect or a 401/403 still proves the service is answering
    if status >= 500:
        return DOWN, f"HTTP {status}"
    return UP, "online"


@st.cache_data(ttl=30, show_spinner=False)
def check_all() -> dict[str, tuple[str, str]]:
    """{service key: (state, detail)} for all services, probed in parallel."""
    with ThreadPoolExecutor(max_workers=len(SERVICES)) as pool:
        results = pool.map(_probe, [svc.health_url for svc in SERVICES])
    return {svc.key: result for svc, result in zip(SERVICES, results)}


def fetch_if_up(key: str, fetch):
    """Run a cached fetcher, unless the health check already knows the service is down."""
    state, detail = check_all().get(key, (UNKNOWN, ""))
    if state == DOWN:
        return None, f"offline ({detail})"
    return fetch()
