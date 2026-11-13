"""qBittorrent: free space on the download disk and what the torrents take up (read-only)."""

import qbittorrentapi
import streamlit as st

from services.client import ServiceError, cached
from services.registry import env


@st.cache_resource(show_spinner=False)
def _client() -> qbittorrentapi.Client:
    """One client per process; it logs in on first use and keeps the session cookie."""
    return qbittorrentapi.Client(
        host=env("QBITTORRENT_NAME", "torrent.home.arpa"),
        username=env("QBITTORRENT_USER"),
        password=env("QBITTORRENT_PASSWORD"),
        VERIFY_WEBUI_CERTIFICATE=False,
        REQUESTS_ARGS={"timeout": (2, 5)},
    )


@cached(ttl=60)
def disk() -> dict:
    """Free space where qBittorrent saves downloads (the mergerfs media pool), and the torrents' total size."""
    if not env("QBITTORRENT_USER"):
        raise ServiceError("not configured – set QBITTORRENT_USER and QBITTORRENT_PASSWORD in .env")
    try:
        data = _client().sync_maindata()
    except qbittorrentapi.LoginFailed:
        raise ServiceError("login refused – check QBITTORRENT_USER / QBITTORRENT_PASSWORD") from None
    except qbittorrentapi.APIConnectionError:
        raise ServiceError("unreachable") from None
    except qbittorrentapi.APIError as error:
        raise ServiceError(f"API error ({type(error).__name__})") from None

    torrents = list((data.get("torrents") or {}).values())
    return {
        "free": (data.get("server_state") or {}).get("free_space_on_disk", 0),
        "torrents": len(torrents),
        "torrent_size": sum(torrent.get("size", 0) for torrent in torrents),
    }
