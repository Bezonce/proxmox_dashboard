"""Render every page against sample data (healthy) and against dead services, without network."""

import pytest
from streamlit.testing.v1 import AppTest

from services import health, media, pihole, proxmox
from services.registry import SERVICES
from tests import fixtures

PAGES = ["pages/home.py", "pages/server.py", "pages/media.py", "pages/network.py"]

FETCHERS = {
    (proxmox, "overview"): fixtures.PROXMOX,
    (proxmox, "backups"): fixtures.BACKUPS,
    (media, "radarr"): fixtures.RADARR,
    (media, "sonarr"): fixtures.SONARR,
    (media, "disks"): fixtures.DISKS,
    (media, "prowlarr"): fixtures.PROWLARR,
    (media, "jellyfin"): fixtures.JELLYFIN,
    (media, "jellyseerr"): fixtures.JELLYSEERR,
    (media, "immich"): fixtures.IMMICH,
    (pihole, "stats"): fixtures.PIHOLE,
}


def _patch(monkeypatch, healthy: bool):
    for (module, name), data in FETCHERS.items():
        result = (data, None) if healthy else (None, "timed out")
        monkeypatch.setattr(module, name, lambda result=result: result)
    state = (health.UP, "online") if healthy else (health.DOWN, "unreachable")
    monkeypatch.setattr(health, "check_all", lambda: {svc.key: state for svc in SERVICES})


def _run(page: str) -> AppTest:
    app = AppTest.from_file(page, default_timeout=30)
    app.run()
    assert not app.exception, [error.value for error in app.exception]
    return app


@pytest.mark.parametrize("page", PAGES)
def test_page_renders_with_data(monkeypatch, page):
    _patch(monkeypatch, healthy=True)
    app = _run(page)
    assert app.metric or app.dataframe


@pytest.mark.parametrize("page", PAGES)
def test_page_survives_dead_services(monkeypatch, page):
    _patch(monkeypatch, healthy=False)
    _run(page)


def test_home_shows_every_service(monkeypatch):
    _patch(monkeypatch, healthy=True)
    app = _run("pages/home.py")
    html = "".join(block.body for block in app.markdown)
    assert f"{len(SERVICES)}/{len(SERVICES)} online" in html


def test_service_names_are_escaped(monkeypatch):
    _patch(monkeypatch, healthy=True)
    app = _run("pages/media.py")
    html = "".join(block.body for block in app.markdown)
    assert "Pilot &lt;b&gt;" in html and "Pilot <b>" not in html
