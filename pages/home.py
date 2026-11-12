import datetime as dt

import streamlit as st

from services import media, pihole, proxmox
from services.health import DOWN, UP, check_all, fetch_if_up
from services.registry import SERVICES
from styles.styles import apply_crystal_style
from styles.widgets import app_version, divider, fmt_bytes, fmt_count, fmt_duration, metric, muted, percent

apply_crystal_style()


@st.fragment(run_every="60s")
def service_grid():
    health = check_all()

    # --- Grid Layout: three columns, filled column by column ---
    columns = st.columns(3, gap="large")
    for index, svc in enumerate(SERVICES):
        with columns[index % 3]:
            if index >= 3:
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

    top = st.columns(4)
    with top[0]:
        metric(
            "CPU",
            f"{node['cpu'] * 100:.0f}%" if node else None,
            f"load {node['load'][0]:.1f}" if node and node["load"] else None,
            node_error,
        )
    with top[1]:
        metric(
            "Memory",
            f"{percent(node['mem_used'], node['mem_total']):.0f}%" if node else None,
            f"{fmt_bytes(node['mem_used'])} / {fmt_bytes(node['mem_total'])}" if node else None,
            node_error,
        )
    with top[2]:
        running = sum(guest["running"] for guest in node["guests"]) if node else 0
        metric("Containers", f"{running}/{len(node['guests'])}" if node else None, "running", node_error)
    with top[3]:
        metric("Uptime", fmt_duration(node["uptime"]) if node else None, node["node"] if node else None, node_error)

    bottom = st.columns(4)
    with bottom[0]:
        metric("Watching", len(library["streams"]) if library else None, "streams now", library_error)
    with bottom[1]:
        queue = (radarr["queue"] if radarr else []) + (sonarr["queue"] if sonarr else [])
        metric("Downloads", len(queue), "in Radarr / Sonarr", radarr_error and sonarr_error)
    with bottom[2]:
        metric("Requests", wanted["pending"] if wanted else None, "waiting for approval", wanted_error)
    with bottom[3]:
        metric(
            "DNS blocked",
            f"{dns['percent_blocked']:.1f}%" if dns else None,
            f"{fmt_count(dns['blocked'])} of {fmt_count(dns['queries'])}" if dns else None,
            dns_error,
        )


service_grid()
divider()
vitals()
