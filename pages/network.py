import polars as pl
import streamlit as st

from services import pihole
from services.health import DOWN, UP, check_all, fetch_if_up
from services.registry import SERVICES
from styles.widgets import fmt_count, label, metric, offline, panel, percent, rows


@st.fragment(run_every="60s")
def dns():
    stats, error = fetch_if_up("pihole", pihole.stats)

    st.subheader("DNS · Pi-hole")
    tiles = st.columns(4)
    with tiles[0]:
        metric("Queries", fmt_count(stats["queries"]) if stats else None, "last 24 h", error)
    with tiles[1]:
        metric("Blocked", fmt_count(stats["blocked"]) if stats else None, f"{stats['percent_blocked']:.1f}%" if stats else None, error)
    with tiles[2]:
        metric("Clients", stats["clients"] if stats else None, "active", error)
    with tiles[3]:
        metric("Blocklist", fmt_count(stats["blocklist"]) if stats else None, "domains", error)

    with panel("top_clients"):
        label("Busiest clients")
        if error:
            offline("Pi-hole", error)
        else:
            top = max((client["queries"] for client in stats["top_clients"]), default=0)
            rows(
                [
                    {
                        "title": client["name"],
                        "meta": client["ip"] if client["ip"] != client["name"] else "",
                        "value": fmt_count(client["queries"]),
                        "progress": percent(client["queries"], top),
                    }
                    for client in stats["top_clients"]
                ]
            )


@st.fragment(run_every="30s")
def services():
    st.subheader("Services")
    health = check_all()

    def status(key: str) -> str:
        state, detail = health.get(key, ("", ""))
        if state == UP:
            return "● online"
        if state == DOWN:
            return f"○ down · {detail}"
        return "◌ not checked"

    table = pl.DataFrame([{"Service": f"{svc.icon} {svc.name}", "Status": status(svc.key), "Address": svc.link} for svc in SERVICES])
    st.dataframe(
        table,
        column_config={"Address": st.column_config.LinkColumn("Address", display_text=r"^\w+://([^/#]+)")},
        hide_index=True,
        height="content",
    )


dns()
services()
