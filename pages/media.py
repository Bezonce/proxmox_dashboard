from itertools import groupby

import streamlit as st

from services import media
from services.health import fetch_if_up
from styles.widgets import fmt_bytes, fmt_count, fmt_day, label, metric, muted, offline, panel, rows, usage_bar


@st.fragment(run_every="60s")
def library_and_streams():
    library, library_error = fetch_if_up("jellyfin", media.jellyfin)
    wanted, wanted_error = fetch_if_up("jellyseerr", media.jellyseerr)

    tiles = st.columns(4)
    with tiles[0]:
        metric("Movies", fmt_count(library["movies"]) if library else None, "in Jellyfin", library_error)
    with tiles[1]:
        metric(
            "Series",
            fmt_count(library["series"]) if library else None,
            f"{fmt_count(library['episodes'])} episodes" if library else None,
            library_error,
        )
    with tiles[2]:
        metric("Watching", len(library["streams"]) if library else None, "streams now", library_error)
    with tiles[3]:
        metric("Requests", wanted["pending"] if wanted else None, f"{wanted['available']} fulfilled" if wanted else None, wanted_error)

    left, right = st.columns(2, gap="large")
    with left, panel("now_playing"):
        label("Now playing")
        if library_error:
            offline("Jellyfin", library_error)
        elif library["streams"]:
            rows(
                [
                    {
                        "title": stream["title"],
                        "meta": f"{stream['user']} · {stream['device']}",
                        "value": stream["playback"],
                        "alert": stream["playback"].startswith("Transcode"),  # transcoding loads the CPU
                        "progress": stream["progress"],
                    }
                    for stream in library["streams"]
                ]
            )
        else:
            muted("Nobody is watching right now.")

    with right, panel("requests"):
        label("Waiting for approval")
        if wanted_error:
            offline("Jellyseerr", wanted_error)
        elif wanted["waiting"]:
            rows(
                [
                    {
                        "title": item["title"],
                        "meta": f"{item['kind']} · requested by {item['user']}",
                        "value": item["when"].strftime("%d %b") if item["when"] else "",
                    }
                    for item in wanted["waiting"]
                ]
            )
        else:
            muted(f"No open requests · {wanted['approved']} approved, {wanted['processing']} downloading.")


@st.fragment(run_every="60s")
def downloads_and_calendar():
    radarr, radarr_error = fetch_if_up("radarr", media.radarr)
    sonarr, sonarr_error = fetch_if_up("sonarr", media.sonarr)
    sources = [("Radarr", radarr, radarr_error), ("Sonarr", sonarr, sonarr_error)]

    left, right = st.columns(2, gap="large")
    with left, panel("downloads"):
        label("Downloads")
        for name, _, error in sources:
            if error:
                offline(name, error)
        queue = [record for _, data, _ in sources if data for record in data["queue"]]
        if queue:
            rows(
                [
                    {
                        "title": record["title"],
                        "meta": f"{record['app']} · {record['status']}",
                        "value": record["time_left"] or f"{record['progress']:.0f}%",
                        "progress": record["progress"],
                    }
                    for record in sorted(queue, key=lambda record: -record["progress"])
                ]
            )
        elif not (radarr_error and sonarr_error):
            muted("Nothing in the download queue.")

    with right, panel("upcoming"):
        label(f"Coming up · {media.UPCOMING_DAYS} days")
        for name, _, error in sources:
            if error:
                offline(name, error)
        upcoming = sorted(
            (item for _, data, _ in sources if data for item in data["upcoming"]),
            key=lambda item: item["when"],
        )
        if not upcoming and not (radarr_error and sonarr_error):
            muted("Nothing scheduled.")
        for _, group in groupby(upcoming, key=lambda item: item["when"].date()):
            items = list(group)
            muted(fmt_day(items[0]["when"]))
            rows(
                [
                    {
                        "title": item["title"],
                        "meta": item["kind"],
                        "value": ("✓ have it" if item["have"] else item["when"].strftime("%H:%M") if item["timed"] else ""),
                    }
                    for item in items
                ]
            )


@st.fragment(run_every="300s")
def indexers_and_photos():
    prowlarr, prowlarr_error = fetch_if_up("prowlarr", media.prowlarr)
    photos, photos_error = fetch_if_up("immich", media.immich)
    radarr, _ = fetch_if_up("radarr", media.radarr)
    sonarr, _ = fetch_if_up("sonarr", media.sonarr)

    left, right = st.columns(2, gap="large")
    with left, panel("health"):
        label("Indexers & warnings")
        if prowlarr_error:
            offline("Prowlarr", prowlarr_error)
        else:
            rows(
                [
                    {
                        "title": "Indexers",
                        "meta": "enabled in Prowlarr",
                        "value": f"{prowlarr['indexers']} · {prowlarr['failing']} failing"
                        if prowlarr["failing"]
                        else f"{prowlarr['indexers']} · all OK",
                        "alert": bool(prowlarr["failing"]),
                    }
                ]
            )
        warnings = [warning for data in (radarr, sonarr, prowlarr) if data for warning in data["warnings"]]
        rows([{"title": warning["message"], "meta": warning["app"], "value": warning["level"], "alert": True} for warning in warnings])
        if not warnings and not prowlarr_error:
            muted("No health warnings from Radarr, Sonarr or Prowlarr.")

    with right, panel("photos"):
        label("Photos · Immich")
        if photos_error:
            offline("Immich", photos_error)
        else:
            if photos["photos"] is not None:
                rows(
                    [
                        {
                            "title": f"{fmt_count(photos['photos'])} photos · {fmt_count(photos['videos'])} videos",
                            "meta": "whole library",
                            "value": fmt_bytes(photos["library_size"]),
                        }
                    ]
                )
            else:
                muted("Photo counts need an admin API key.")
            usage_bar("Photo storage (NAS)", photos["disk_used"], photos["disk_total"])


library_and_streams()
downloads_and_calendar()
indexers_and_photos()
