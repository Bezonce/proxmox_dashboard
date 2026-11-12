import time

import polars as pl
import streamlit as st

from services import media, proxmox
from services.health import fetch_if_up
from styles.widgets import fmt_ago, fmt_bytes, fmt_duration, label, metric, offline, panel, percent, rows, usage_bar

BACKUP_STALE_AFTER = 36 * 3600  # the job runs nightly; older than this means one was missed


@st.fragment(run_every="60s")
def server():
    node, error = proxmox.overview()
    if error:
        offline("Proxmox", error)
        return
    backups, backup_error = proxmox.backups()

    st.subheader(f"Node {node['node']} · Proxmox VE {node['version']}")
    running = sum(guest["running"] for guest in node["guests"])
    tiles = st.columns(4)
    with tiles[0]:
        metric("CPU", f"{node['cpu'] * 100:.0f}%", f"{node['cpus']} cores")
    with tiles[1]:
        load = node["load"] + [0.0] * (3 - len(node["load"]))
        metric("Load", f"{load[0]:.1f}", f"5 min {load[1]:.1f} · 15 min {load[2]:.1f}")
    with tiles[2]:
        metric(
            "Memory",
            f"{percent(node['mem_used'], node['mem_total']):.0f}%",
            f"{fmt_bytes(node['mem_used'])} / {fmt_bytes(node['mem_total'])}",
        )
    with tiles[3]:
        metric("Uptime", fmt_duration(node["uptime"]), f"{running}/{len(node['guests'])} containers running")

    # --- Containers ---
    st.subheader("Containers")
    latest = backups["latest"] if backups else {}
    table = pl.DataFrame(
        [
            {
                "ID": guest["id"],
                "Name": guest["name"],
                "Status": "● running" if guest["running"] else "○ stopped",
                "CPU": guest["cpu"] * 100,
                "Memory": percent(guest["mem"], guest["maxmem"]),
                "RAM": f"{fmt_bytes(guest['mem'])} / {fmt_bytes(guest['maxmem'])}",
                "Disk": percent(guest["disk"], guest["maxdisk"]),
                "Uptime": fmt_duration(guest["uptime"]) if guest["running"] else "",
                "Last backup": fmt_ago(latest[guest["id"]]["when"]) if guest["id"] in latest else "none",
            }
            for guest in node["guests"]
        ]
    )
    bar = {"min_value": 0, "max_value": 100, "format": "%.0f%%", "color": "#7FFFD4"}
    st.dataframe(
        table,
        column_config={
            "ID": st.column_config.NumberColumn("ID", format="%d", width="small"),
            "CPU": st.column_config.ProgressColumn("CPU", **bar),
            "Memory": st.column_config.ProgressColumn("Memory", **bar),
            "Disk": st.column_config.ProgressColumn("Disk", **bar),
        },
        hide_index=True,
        height="content",
    )

    left, right = st.columns(2, gap="large")

    # --- Storage ---
    with left, panel("storage"):
        label("Storage")
        for pool in node["storage"]:
            usage_bar(f"{pool['name']} ({pool['type']})", pool["used"], pool["total"])
        # The media pool is not a Proxmox storage; Radarr sees it through its root folder
        disks, _ = fetch_if_up("radarr", media.disks)
        for disk in disks or []:
            usage_bar(f"{disk['path']} (media)", disk["total"] - disk["free"], disk["total"])

    # --- Backups ---
    with right, panel("backups"):
        label("Backups")
        if backup_error:
            offline("Backups", backup_error)
        else:
            now = time.time()
            names = {guest["id"]: guest["name"] for guest in node["guests"]}
            stale = [
                guest for guest in node["guests"] if guest["id"] not in latest or now - latest[guest["id"]]["when"] > BACKUP_STALE_AFTER
            ]
            items = [
                {
                    "title": "Backup jobs, last 7 days",
                    "meta": f"{backups['runs']} runs · {fmt_bytes(backups['total_size'])} stored",
                    "value": f"{len(backups['failed'])} failed" if backups["failed"] else "all OK",
                    "alert": bool(backups["failed"]),
                }
            ]
            items += [
                {
                    "title": f"Failed: {failure['guest']} {names.get(_as_int(failure['guest']), '')}".strip(),
                    "meta": failure["status"],
                    "value": fmt_ago(failure["when"]),
                    "alert": True,
                }
                for failure in backups["failed"][:5]
            ]
            items += [
                {
                    "title": f"No recent backup: {guest['id']} {guest['name']}",
                    "meta": "last one " + (fmt_ago(latest[guest["id"]]["when"]) if guest["id"] in latest else "never"),
                    "value": "stale",
                    "alert": True,
                }
                for guest in stale
            ]
            rows(items)


def _as_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


server()
