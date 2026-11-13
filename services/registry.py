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
    group: str  # column on the home grid, one of GROUPS
    link: str  # what the button opens
    health_url: str  # polled for up/down, "" = not checked


def _service(key: str, name: str, icon: str, group: str, link: str, health_url: str = "") -> Service:
    if not health_url and link.startswith(("http://", "https://")):
        health_url = link  # no API to ping: check the page the button opens
    return Service(key, name, icon, group, link, health_url)


_qbittorrent = base_url(env("QBITTORRENT_NAME", "torrent.home.arpa"))
_proxmox = proxmox_host()

MEDIA, INFRA, ARR = "Media", "Infrastructure", "Arr stack"
GROUPS = [MEDIA, INFRA, ARR]  # the home grid's columns, left to right

# Links use the Caddy names (http://<name>.home.arpa); .env can override each one.
# Order within a group = order in its column. A service without a web link is left out.
SERVICES = [
    svc
    for svc in (
        # --- Media
        _service("jellyfin", "Jellyfin", "◈", MEDIA, env("MEDIA_LINK", "http://watch.home.arpa"), f"{api_base('JELLYFIN')}/health"),
        _service("immich", "Photos", "✺", MEDIA, env("IMMICH_LINK", "http://photos.home.arpa"), f"{api_base('IMMICH')}/api/server/ping"),
        _service("books", "Books", "▤", MEDIA, env("BOOKS_LINK", "http://books.home.arpa")),  # Calibre-Web
        _service(
            "jellyseerr",
            "Requests",
            "❖",
            MEDIA,
            env("JELLYSEERR_LINK", "http://requests.home.arpa"),
            f"{api_base('JELLYSEERR')}/api/v1/status",
        ),
        # Surveillance Station on the NAS (the camera itself is on an isolated network)
        _service("camera", "Camera", "◎", MEDIA, env("CAMERA_LINK", "http://rozi.home.arpa/webman/3rdparty/SurveillanceStation/")),
        # --- Infrastructure
        _service("nas", "Rozi", "✦", INFRA, env("NAS_LINK", "http://rozi.home.arpa")),
        # The web UI root answers at once; unauthenticated API calls are delayed 3 s by Proxmox
        _service(
            "proxmox", "Proxmox", "▣", INFRA, env("PROXMOX_LINK", "http://proxmox.home.arpa"), f"https://{_proxmox}/" if _proxmox else ""
        ),
        # Only shown for a web address: browsers refuse to open file:// links from a web page
        _service("folders", "Folders", "◮", INFRA, env("TORRENT_FOLDERS_LINK")),
        # /api/auth answers 401 without a session, which still means "up" and costs no API seat
        _service("pihole", "Pi-hole", "⊘", INFRA, env("PIHOLE_LINK", "http://pihole.home.arpa"), f"{api_base('PIHOLE')}/api/auth"),
        # --- Arr stack
        _service("radarr", "Radarr", "◬", ARR, env("RADARR_LINK", "http://radarr.home.arpa"), f"{api_base('RADARR')}/ping"),
        _service("sonarr", "Sonarr", "◐", ARR, env("SONARR_LINK", "http://sonarr.home.arpa"), f"{api_base('SONARR')}/ping"),
        _service("prowlarr", "Prowlarr", "✥", ARR, env("PROWLARR_LINK", "http://prowlarr.home.arpa"), f"{api_base('PROWLARR')}/ping"),
        # 403 without login still means "up"
        _service("torrent", "Torrent", "✧", ARR, env("TORRENT_LINK", "http://torrent.home.arpa"), f"{_qbittorrent}/api/v2/app/version"),
    )
    if svc.link.startswith(("http://", "https://"))
]

_BY_KEY = {svc.key: svc for svc in SERVICES}


def service(key: str) -> Service | None:
    return _BY_KEY.get(key)
