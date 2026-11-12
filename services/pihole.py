"""Pi-hole v6 statistics.

Pi-hole hands out at most 16 API sessions, so the session id is kept for the whole
process and renewed only when Pi-hole says it has expired, never per page load.
"""

import threading

import streamlit as st

from services.client import ServiceError, cached, parse_json, request
from services.registry import api_base, env


class _Session:
    def __init__(self):
        self.sid = ""
        self.lock = threading.Lock()


@st.cache_resource(show_spinner=False)
def _session() -> _Session:
    return _Session()


def _login(base: str, password: str) -> str:
    response = request("POST", f"{base}/api/auth", json={"password": password})
    if response.status_code == 401:
        raise ServiceError("login refused – check PIHOLE_APP_PASSWORD")
    if response.status_code == 429:
        raise ServiceError("too many sessions or login attempts (HTTP 429)")
    sid = parse_json(response).get("session", {}).get("sid")
    if not sid:
        raise ServiceError("login gave no session id")
    return sid


def _get(path: str, params: dict | None = None) -> dict:
    base, password = api_base("PIHOLE"), env("PIHOLE_APP_PASSWORD")
    if not password:
        raise ServiceError("not configured – set PIHOLE_APP_PASSWORD in .env")
    session = _session()

    def fetch(renew: bool):
        with session.lock:
            if renew or not session.sid:
                session.sid = _login(base, password)
            sid = session.sid
        return request("GET", f"{base}/api/{path}", headers={"X-FTL-SID": sid}, params=params)

    response = fetch(renew=False)
    if response.status_code == 401:  # the session expired: log in once more and retry
        response = fetch(renew=True)
    return parse_json(response)


@cached(ttl=60)
def stats() -> dict:
    """Today's query totals and the busiest clients."""
    summary = _get("stats/summary")
    clients = _get("stats/top_clients", {"count": 5})
    queries = summary.get("queries", {})
    return {
        "queries": queries.get("total", 0),
        "blocked": queries.get("blocked", 0),
        "percent_blocked": queries.get("percent_blocked", 0.0),
        "clients": summary.get("clients", {}).get("active", 0),
        "blocklist": summary.get("gravity", {}).get("domains_being_blocked", 0),
        "top_clients": [
            {"name": client.get("name") or client.get("ip", ""), "ip": client.get("ip", ""), "queries": client.get("count", 0)}
            for client in clients.get("clients", [])
        ],
    }
