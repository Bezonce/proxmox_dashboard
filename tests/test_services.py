"""The pure helpers: URL handling, parsing and formatting."""

import datetime as dt

import pytest
import requests

from services import client, media, proxmox, registry
from styles import widgets


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("192.168.0.111:7878", "http://192.168.0.111:7878"),
        ("http://192.168.0.111:7878/", "http://192.168.0.111:7878"),
        ("http://192.168.0.111:7878/api/v3", "http://192.168.0.111:7878"),
        ("http://192.168.0.115:2283/api", "http://192.168.0.115:2283"),
        ("torrent.local", "http://torrent.local"),
        ("", ""),
    ],
)
def test_base_url(value, expected):
    assert registry.base_url(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [("192.168.0.4:8006", "192.168.0.4:8006"), ("https://192.168.0.4:8006/", "192.168.0.4:8006"), ("192.168.0.4", "192.168.0.4:8006")],
)
def test_proxmox_host(monkeypatch, value, expected):
    monkeypatch.setenv("PROXMOX_HOST", value)
    assert registry.proxmox_host() == expected


def test_api_base_prefers_env(monkeypatch):
    monkeypatch.delenv("RADARR_URL", raising=False)
    assert registry.api_base("RADARR") == "http://192.168.0.111:7878"
    monkeypatch.setenv("RADARR_URL", "http://radarr.home.arpa/api/v3")
    assert registry.api_base("RADARR") == "http://radarr.home.arpa"


def test_services_have_unique_keys():
    keys = [svc.key for svc in registry.SERVICES]
    assert len(keys) == len(set(keys))


def test_proxmox_helpers():
    assert proxmox._version("pve-manager/9.2.26/41a0e2e09b9e6f9d") == "9.2.26"
    assert proxmox._fraction(-0.0125) == 0.0
    assert proxmox._fraction(0.5) == 0.5


def test_media_helpers():
    assert media._percent(50, 200) == 25.0
    assert media._percent(5, 0) == 0.0
    when = media._parse_time("2026-11-12T20:00:00Z")
    assert when == dt.datetime(2026, 11, 12, 20, tzinfo=dt.timezone.utc)
    assert media._parse_time("not a date") is None
    assert media._utc(when) == "2026-11-12T20:00:00Z"


def test_error_messages_hide_details():
    assert client.describe(requests.ConnectTimeout("http://x?apikey=secret")) == "timed out"
    assert client.describe(requests.ConnectionError("http://x?apikey=secret")) == "unreachable"
    assert client.describe(client.ServiceError("HTTP 500")) == "HTTP 500"


def test_formatting():
    assert widgets.fmt_bytes(512) == "512 B"
    assert widgets.fmt_bytes(1.5 * 1024**3) == "1.5 GB"
    assert widgets.fmt_duration(3 * 86400 + 4 * 3600) == "3d 4h"
    assert widgets.fmt_duration(3720) == "1h 2m"
    assert widgets.fmt_count(48000) == "48 000"
    assert widgets.percent(5, 0) == 0.0


def test_every_service_is_in_a_group():
    assert {svc.group for svc in registry.SERVICES} <= set(registry.GROUPS)
    media = [svc.key for svc in registry.SERVICES if svc.group == registry.MEDIA]
    assert media[:5] == ["jellyfin", "immich", "books", "jellyseerr", "camera"]


def test_file_links_are_hidden(monkeypatch):
    import importlib

    try:
        monkeypatch.setenv("TORRENT_FOLDERS_LINK", "file://192.168.0.4/torrent/")
        assert "folders" not in [svc.key for svc in importlib.reload(registry).SERVICES]
        monkeypatch.setenv("TORRENT_FOLDERS_LINK", "http://files.home.arpa")
        infra = [svc.key for svc in importlib.reload(registry).SERVICES if svc.group == registry.INFRA]
        assert infra == ["nas", "proxmox", "folders", "pihole"]
    finally:
        monkeypatch.undo()
        importlib.reload(registry)  # leave the module as the other tests expect it
