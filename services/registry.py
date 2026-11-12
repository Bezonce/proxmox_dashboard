"""Where every homelab service lives.

A *link* is what the browser opens, an *API base* is what the dashboard itself calls.
Everything comes from .env (see .env.example); the defaults are the addresses in CLAUDE.md.
"""

import os
import re
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# Direct API bases, used when <APP>_URL is not set in .env
_API_DEFAULTS = {
    "JELLYFIN": "http://192.168.0.110:8096",
    "RADARR": "http://192.168.0.111:7878",
    "PROWLARR": "http://192.168.0.112:9696",
    "SONARR": "http://192.168.0.113:8989",
    "JELLYSEERR": "http://192.168.0.114:5055",
    "IMMICH": "http://192.168.0.115:2283",
    "PIHOLE": "http://192.168.0.102",
}


def env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


def base_url(value: str, scheme: str = "http") -> str:
    """Turn 'host:port' or a URL (with or without an /api/vN suffix) into 'scheme://host:port'."""
    value = value.strip().rstrip("/")
    if value and "://" not in value:
        value = f"{scheme}://{value}"
    return re.sub(r"/api(/v\d+)?$", "", value)


def api_base(app: str) -> str:
    """Root URL of an app's API, e.g. api_base("RADARR") -> http://192.168.0.111:7878"""
    return base_url(env(f"{app}_URL", _API_DEFAULTS[app]))


def api_key(app: str) -> str:
    return env(f"{app}_API_KEY")


def proxmox_host() -> str:
    """'host:port' of the Proxmox API, the form proxmoxer expects."""
    host = re.sub(r"^https?://", "", env("PROXMOX_HOST")).rstrip("/")
    if host and ":" not in host:
        host = f"{host}:8006"
    return host


@dataclass(frozen=True)
class Service:
    key: str  # stable id: health lookups and CSS keys
    name: str  # label on the home grid
    icon: str  # glyph in front of the label
    link: str  # what the button opens
    health_url: str  # polled for up/down, "" = not checked


def _service(key: str, name: str, icon: str, link: str, health_url: str = "") -> Service:
    if not health_url and link.startswith(("http://", "https://")):
        health_url = link  # no API to ping: check the page the button opens
    return Service(key, name, icon, link, health_url)


_qbittorrent = base_url(env("QBITTORRENT_NAME"))
_proxmox = proxmox_host()

# Order = order on the home grid (three per row). A service without a link is left out.
SERVICES = [
    svc
    for svc in (
        _service("jellyfin", "Jellyfin", "◈", env("MEDIA_LINK", "http://watch.home.arpa"), f"{api_base('JELLYFIN')}/health"),
        _service(
            "torrent",
            "Torrent",
            "✧",
            env("TORRENT_LINK", "http://torrent.home.arpa"),
            f"{_qbittorrent}/api/v2/app/version" if _qbittorrent else "",  # 403 without login still means "up"
        ),
        _service("nas", "Rozi", "✦", env("NAS_LINK", "http://rozi.home.arpa")),
        _service("camera", "Camera", "◎", env("CAMERA_LINK", "https://192.168.0.2:5001")),
        _service("folders", "Folders", "◮", env("TORRENT_FOLDERS_LINK")),
        _service(
            "jellyseerr", "Requests", "❖", env("JELLYSEERR_LINK", "http://requests.home.arpa"), f"{api_base('JELLYSEERR')}/api/v1/status"
        ),
        _service("immich", "Photos", "✺", env("IMMICH_LINK", "http://photos.home.arpa"), f"{api_base('IMMICH')}/api/server/ping"),
        _service("radarr", "Radarr", "◬", env("RADARR_LINK", "http://radarr.home.arpa"), f"{api_base('RADARR')}/ping"),
        _service("sonarr", "Sonarr", "◐", env("SONARR_LINK", "http://sonarr.home.arpa"), f"{api_base('SONARR')}/ping"),
        _service("prowlarr", "Prowlarr", "✥", env("PROWLARR_LINK", "http://prowlarr.home.arpa"), f"{api_base('PROWLARR')}/ping"),
        # /api/auth answers 401 without a session, which still means "up" and costs no API seat
        _service("pihole", "Pi-hole", "⊘", env("PIHOLE_LINK", "http://pihole.home.arpa"), f"{api_base('PIHOLE')}/api/auth"),
        # The web UI root answers at once; unauthenticated API calls are delayed 3 s by Proxmox
        _service("proxmox", "Proxmox", "▣", env("PROXMOX_LINK", "http://proxmox.home.arpa"), f"https://{_proxmox}/" if _proxmox else ""),
    )
    if svc.link
]

_BY_KEY = {svc.key: svc for svc in SERVICES}


def service(key: str) -> Service | None:
    return _BY_KEY.get(key)
