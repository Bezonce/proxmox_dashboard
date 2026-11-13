import datetime as dt

import streamlit as st

from services import media, pihole, proxmox, torrent
from services.health import DOWN, UP, check_all, fetch_if_up
from services.registry import GROUPS, SERVICES
from styles.styles import apply_crystal_style
from styles.widgets import (
    app_version,
    divider,
    fmt_bytes,
    fmt_count,
    fmt_duration,
    label,
    metric,
    muted,
    percent,
    tile,
)

apply_crystal_style()


def torrent_disk():
    """Free space on the HDD pool the torrents download to, as a status card."""
    disk, error = fetch_if_up("torrent", torrent.disk)
    if error:
        metric("Torrent disk", None, error=error)
        return
    # qBittorrent knows the free space; the pool's size comes from Radarr, which sees the same pool
    pools, _ = fetch_if_up("radarr", media.disks)
    pool = max(pools or [], key=lambda candidate: candidate["total"], default=None)
    tile(
        "Torrent disk",
        f"{fmt_bytes(disk['free'])} free",
        f"{disk['torrents']} torrents · {fmt_bytes(disk['torrent_size'])}",
        used_pct=percent(pool["total"] - disk["free"], pool["total"]) if pool else None,
    )


@st.fragment(run_every="60s")
def service_grid():
    health = check_all()

    # --- Grid Layout: one column per group ---
    columns = st.columns(len(GROUPS), gap="large")
    for column, group in zip(columns, GROUPS):
        with column:
            label(group, center=True)
            for index, svc in enumerate(svc for svc in SERVICES if svc.group == group):
                if index:
                    st.markdown("<br>", unsafe_allow_html=True)
                state, detail = health.get(svc.key, ("unknown", ""))
                with st.container(key=f"status_{state}_{svc.key}"):
                    st.link_button(label=f"{svc.icon} {svc.name}", url=svc.link, help=detail, width="stretch")

    checked = [state for state, _ in health.values() if state in (UP, DOWN)]
    down = [svc.name for svc in SERVICES if health.get(svc.key, ("",))[0] == DOWN]
    summary = f"{checked.count(UP)}/{len(checked)} online"
    if down:
        summary += " · down: " + ", ".join(down)
    muted(f"{summary} · {dt.datetime.now():%H:%M} · build {app_version()}", center=True)


@st.fragment(run_every="60s")
def vitals():
    node, node_error = proxmox.overview()
    library, library_error = fetch_if_up("jellyfin", media.jellyfin)
    radarr, radarr_error = fetch_if_up("radarr", media.radarr)
    sonarr, sonarr_error = fetch_if_up("sonarr", media.sonarr)
    wanted, wanted_error = fetch_if_up("jellyseerr", media.jellyseerr)
    dns, dns_error = fetch_if_up("pihole", pihole.stats)

    running = sum(guest["running"] for guest in node["guests"]) if node else 0
    queue = (radarr["queue"] if radarr else []) + (sonarr["queue"] if sonarr else [])

    # Three per row, lined up with the three button columns above
    server, storage, watching = (st.columns(3, gap="large") for _ in range(3))
    with server[0]:
        metric(
            "CPU",
            f"{node['cpu'] * 100:.0f}%" if node else None,
            f"load {node['load'][0]:.1f}" if node and node["load"] else None,
            node_error,
        )
    with server[1]:
        metric(
            "Memory",
            f"{percent(node['mem_used'], node['mem_total']):.0f}%" if node else None,
            f"{fmt_bytes(node['mem_used'])} / {fmt_bytes(node['mem_total'])}" if node else None,
            node_error,
        )
    with server[2]:
        metric("Containers", f"{running}/{len(node['guests'])}" if node else None, "running", node_error)

    with storage[0]:
        metric("Uptime", fmt_duration(node["uptime"]) if node else None, node["node"] if node else None, node_error)
    with storage[1]:
        torrent_disk()
    with storage[2]:
        metric(
            "DNS blocked",
            f"{dns['percent_blocked']:.1f}%" if dns else None,
            f"{fmt_count(dns['blocked'])} of {fmt_count(dns['queries'])}" if dns else None,
            dns_error,
        )

    with watching[0]:
        metric("Watching", len(library["streams"]) if library else None, "streams now", library_error)
    with watching[1]:
        metric("Downloads", len(queue), "in Radarr / Sonarr", radarr_error and sonarr_error)
    with watching[2]:
        metric("Requests", wanted["pending"] if wanted else None, "waiting for approval", wanted_error)


service_grid()
divider()
vitals()
