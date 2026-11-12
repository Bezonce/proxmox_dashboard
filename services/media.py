"""Read-only clients for the media stack: Jellyfin, Jellyseerr, Radarr, Sonarr, Prowlarr, Immich."""

import datetime as dt

import streamlit as st

from services.client import ServiceError, cached, get_json
from services.registry import api_base, api_key

UPCOMING_DAYS = 14


def _connect(app: str) -> tuple[str, str]:
    key = api_key(app)
    if not key:
        raise ServiceError(f"not configured – set {app}_API_KEY in .env")
    return api_base(app), key


def _parse_time(value: str | None) -> dt.datetime | None:
    """An API timestamp (UTC, ISO 8601) as an aware datetime."""
    if not value:
        return None
    try:
        when = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return when if when.tzinfo else when.replace(tzinfo=dt.timezone.utc)


def _percent(done: float, total: float) -> float:
    return round(min(max(done / total, 0.0), 1.0) * 100, 1) if total else 0.0


# --- Radarr / Sonarr / Prowlarr -------------------------------------------------


def _calendar_window() -> tuple[dt.datetime, dt.datetime]:
    """From local midnight today to UPCOMING_DAYS later."""
    start = dt.datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + dt.timedelta(days=UPCOMING_DAYS)


def _utc(when: dt.datetime) -> str:
    return when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _arr_get(app: str, version: str, path: str, **params):
    base, key = _connect(app)
    return get_json(f"{base}/api/{version}/{path}", headers={"X-Api-Key": key}, params=params)


def _queue_row(app: str, title: str, record: dict) -> dict:
    size = record.get("size") or 0
    return {
        "app": app,
        "title": title or record.get("title", ""),
        "status": record.get("trackedDownloadState") or record.get("status", ""),
        "progress": _percent(size - (record.get("sizeleft") or 0), size),
        "time_left": record.get("timeleft") or "",
    }


def _warnings(app: str, checks: list[dict]) -> list[dict]:
    return [
        {"app": app, "level": check.get("type", ""), "message": check.get("message", "")}
        for check in checks
        if check.get("type") in ("warning", "error")
    ]


@cached(ttl=60)
def radarr() -> dict:
    """Movie downloads in progress, releases of the next two weeks and Radarr's own health warnings."""
    start, end = _calendar_window()
    queue = _arr_get("RADARR", "v3", "queue", pageSize=50, includeMovie="true")
    calendar = _arr_get("RADARR", "v3", "calendar", start=_utc(start), end=_utc(end))
    health = _arr_get("RADARR", "v3", "health")

    upcoming = []
    for movie in calendar:
        # A movie has up to three release dates (no time of day); show the first one inside the window
        releases = [
            (when, kind)
            for kind, field in (("Cinema", "inCinemas"), ("Digital", "digitalRelease"), ("Disc", "physicalRelease"))
            if (when := _parse_time(movie.get(field))) and start.date() <= when.date() <= end.date()
        ]
        if releases:
            when, kind = min(releases)
            title = movie.get("title", "")
            upcoming.append(
                {
                    "when": when.replace(tzinfo=None),
                    "timed": False,
                    "kind": f"Movie · {kind}",
                    "title": f"{title} ({movie['year']})" if movie.get("year") else title,
                    "have": bool(movie.get("hasFile")),
                }
            )

    return {
        "queue": [_queue_row("Radarr", record.get("movie", {}).get("title", ""), record) for record in queue.get("records", [])],
        "upcoming": upcoming,
        "warnings": _warnings("Radarr", health),
    }


@cached(ttl=300)
def disks() -> list[dict]:
    """Large disks Radarr can see (the mergerfs media pool), each listed once."""
    seen, result = set(), []
    for disk in _arr_get("RADARR", "v3", "diskspace"):
        total, free = disk.get("totalSpace") or 0, disk.get("freeSpace") or 0
        # skip the container's own small root disk, and bind mounts of the same pool
        if total < 100 * 1024**3 or (total, free) in seen:
            continue
        seen.add((total, free))
        result.append({"path": disk.get("path", ""), "free": free, "total": total})
    return result


@cached(ttl=60)
def sonarr() -> dict:
    """Episode downloads in progress, episodes airing in the next two weeks and Sonarr's health warnings."""
    start, end = _calendar_window()
    queue = _arr_get("SONARR", "v3", "queue", pageSize=50, includeSeries="true", includeEpisode="true")
    calendar = _arr_get("SONARR", "v3", "calendar", start=_utc(start), end=_utc(end), includeSeries="true")
    health = _arr_get("SONARR", "v3", "health")

    def episode_title(series: dict, episode: dict) -> str:
        number = f"S{episode.get('seasonNumber', 0):02d}E{episode.get('episodeNumber', 0):02d}"
        return " ".join(part for part in (series.get("title", ""), number, episode.get("title", "")) if part)

    upcoming = []
    for episode in calendar:
        when = _parse_time(episode.get("airDateUtc"))
        if when:
            upcoming.append(
                {
                    "when": when.astimezone().replace(tzinfo=None),
                    "timed": True,
                    "kind": "Episode",
                    "title": episode_title(episode.get("series", {}), episode),
                    "have": bool(episode.get("hasFile")),
                }
            )

    return {
        "queue": [
            # a season pack has no single episode: fall back to the release name
            _queue_row("Sonarr", episode_title(record.get("series", {}), record["episode"]) if record.get("episode") else "", record)
            for record in queue.get("records", [])
        ],
        "upcoming": upcoming,
        "warnings": _warnings("Sonarr", health),
    }


@cached(ttl=60)
def prowlarr() -> dict:
    """How many indexers are enabled, how many are currently failing, and Prowlarr's health warnings."""
    indexers = _arr_get("PROWLARR", "v1", "indexer")
    failing = _arr_get("PROWLARR", "v1", "indexerstatus")
    health = _arr_get("PROWLARR", "v1", "health")
    now = dt.datetime.now(dt.timezone.utc)
    return {
        "indexers": sum(1 for indexer in indexers if indexer.get("enable")),
        "failing": sum(1 for status in failing if (until := _parse_time(status.get("disabledTill"))) and until > now),
        "warnings": _warnings("Prowlarr", health),
    }


# --- Jellyfin -------------------------------------------------------------------

_PLAY_METHODS = {"DirectPlay": "Direct play", "DirectStream": "Direct stream", "Transcode": "Transcode"}


@cached(ttl=30)
def jellyfin() -> dict:
    """Library size and who is watching what right now."""
    base, key = _connect("JELLYFIN")
    headers = {"Authorization": f'MediaBrowser Token="{key}"'}
    counts = get_json(f"{base}/Items/Counts", headers=headers)
    sessions = get_json(f"{base}/Sessions", headers=headers, params={"ActiveWithinSeconds": 300})

    streams = []
    for session in sessions:
        item = session.get("NowPlayingItem")
        if not item:
            continue
        if item.get("Type") == "Episode":
            number = f"S{item.get('ParentIndexNumber') or 0:02d}E{item.get('IndexNumber') or 0:02d}"
            title = " ".join(part for part in (item.get("SeriesName", ""), number, item.get("Name", "")) if part)
        else:
            title = f"{item.get('Name', '')} ({item['ProductionYear']})" if item.get("ProductionYear") else item.get("Name", "")
        state = session.get("PlayState", {})
        method = _PLAY_METHODS.get(state.get("PlayMethod"), state.get("PlayMethod") or "")
        streams.append(
            {
                "user": session.get("UserName", ""),
                "title": title,
                "device": " · ".join(part for part in (session.get("Client"), session.get("DeviceName")) if part),
                "playback": f"{method} (paused)" if state.get("IsPaused") else method,
                "progress": _percent(state.get("PositionTicks") or 0, item.get("RunTimeTicks") or 0),
            }
        )

    return {
        "movies": counts.get("MovieCount", 0),
        "series": counts.get("SeriesCount", 0),
        "episodes": counts.get("EpisodeCount", 0),
        "streams": streams,
    }


# --- Jellyseerr -----------------------------------------------------------------


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def _request_title(media_type: str, tmdb_id: int) -> str:
    """Requests only carry a TMDB id; the title needs a second lookup (cached for a day)."""
    base, key = _connect("JELLYSEERR")
    details = get_json(f"{base}/api/v1/{media_type}/{tmdb_id}", headers={"X-Api-Key": key})
    return details.get("title") or details.get("name") or f"TMDB {tmdb_id}"


@cached(ttl=60)
def jellyseerr() -> dict:
    """Request totals and the requests still waiting for approval."""
    base, key = _connect("JELLYSEERR")
    headers = {"X-Api-Key": key}
    counts = get_json(f"{base}/api/v1/request/count", headers=headers)
    pending = get_json(f"{base}/api/v1/request", headers=headers, params={"filter": "pending", "take": 10, "sort": "added"})

    waiting = []
    titles_available = True
    for item in pending.get("results", []):
        media = item.get("media", {})
        media_type = "tv" if (item.get("type") or media.get("mediaType")) == "tv" else "movie"
        tmdb_id = media.get("tmdbId")
        title = f"TMDB {tmdb_id}"
        if tmdb_id and titles_available:
            try:
                title = _request_title(media_type, tmdb_id)
            except ServiceError:
                titles_available = False  # don't wait for a timeout per request
        requested = _parse_time(item.get("createdAt"))
        waiting.append(
            {
                "title": title,
                "kind": "Series" if media_type == "tv" else "Movie",
                "user": item.get("requestedBy", {}).get("displayName", ""),
                "when": requested.astimezone().replace(tzinfo=None) if requested else None,
            }
        )

    return {
        "pending": counts.get("pending", 0),
        "approved": counts.get("approved", 0),
        "processing": counts.get("processing", 0),
        "available": counts.get("available", 0),
        "waiting": waiting,
    }


# --- Immich ---------------------------------------------------------------------


@cached(ttl=300)
def immich() -> dict:
    """Photo and video counts (needs an admin API key) and the disk behind the library."""
    base, key = _connect("IMMICH")
    headers = {"x-api-key": key}
    storage = get_json(f"{base}/api/server/storage", headers=headers)
    try:
        statistics = get_json(f"{base}/api/server/statistics", headers=headers)
    except ServiceError:
        statistics = None  # a non-admin key can still read the storage
    return {
        "photos": statistics.get("photos", 0) if statistics else None,
        "videos": statistics.get("videos", 0) if statistics else None,
        "library_size": statistics.get("usage", 0) if statistics else None,
        "disk_used": storage.get("diskUseRaw", 0),
        "disk_total": storage.get("diskSizeRaw", 0),
    }
