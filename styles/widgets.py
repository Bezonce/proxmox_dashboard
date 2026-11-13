"""Small building blocks in the Crystal style, shared by the pages (CSS lives in styles.py)."""

import datetime as dt
import time
from html import escape
from pathlib import Path

import streamlit as st

REPO = Path(__file__).resolve().parent.parent


# --- Formatting -----------------------------------------------------------------


def fmt_bytes(value: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(value) < 1024 or unit == "TB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return ""


def fmt_duration(seconds: float) -> str:
    seconds = int(max(seconds, 0))
    days, rest = divmod(seconds, 86400)
    hours, rest = divmod(rest, 3600)
    minutes = rest // 60
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def fmt_ago(timestamp: float) -> str:
    return f"{fmt_duration(time.time() - timestamp)} ago" if timestamp else "never"


def fmt_count(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def fmt_day(when: dt.datetime) -> str:
    today = dt.date.today()
    if when.date() == today:
        return "Today"
    if when.date() == today + dt.timedelta(days=1):
        return "Tomorrow"
    return when.strftime("%a %d %b")


def percent(used: float, total: float) -> float:
    return min(max(used / total, 0.0), 1.0) * 100 if total else 0.0


# --- Elements -------------------------------------------------------------------


def _html(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def panel(key: str):
    """A dark glass panel; use as `with panel("name"):`."""
    return st.container(key=f"panel_{key}")


def label(text: str, center: bool = False) -> None:
    _html(f'<div class="crystal-label{" crystal-center" if center else ""}">{escape(text)}</div>')


def muted(text: str, center: bool = False) -> None:
    _html(f'<div class="crystal-muted{" crystal-center" if center else ""}">{escape(text)}</div>')


def offline(name: str, error: str) -> None:
    """How a service that can't be read shows up: one line, never a traceback."""
    _html(f'<div class="crystal-offline">◌ {escape(name)} · {escape(error)}</div>')


def _bar(pct: float) -> str:
    level = "crit" if pct >= 90 else "warn" if pct >= 80 else ""
    return f'<div class="crystal-bar {level}"><div style="width:{pct:.1f}%"></div></div>'


def usage_bar(name: str, used: float, total: float, detail: str | None = None) -> None:
    """A labelled usage bar; turns pink above 80 % and red above 90 %."""
    pct = percent(used, total)
    detail = detail or f"{fmt_bytes(used)} / {fmt_bytes(total)} · {pct:.0f}%"
    _html(f'<div class="crystal-bar-head"><span>{escape(name)}</span><span>{escape(detail)}</span></div>{_bar(pct)}')


def rows(items: list[dict]) -> None:
    """A list of rows: title, optional meta line, value on the right and progress bar (0-100)."""
    markup = []
    for item in items:
        meta = f'<div class="meta">{escape(item["meta"])}</div>' if item.get("meta") else ""
        progress = _bar(item["progress"]) if item.get("progress") is not None else ""
        value_class = "value alert" if item.get("alert") else "value"
        markup.append(
            '<div class="crystal-row">'
            f'<div style="flex:1;min-width:0"><div class="title">{escape(item["title"])}</div>{meta}{progress}</div>'
            f'<div class="{value_class}">{escape(item.get("value", ""))}</div>'
            "</div>"
        )
    _html("".join(markup))


def metric(name: str, value, detail: str | None = None, error: str | None = None) -> None:
    """A glass metric tile; shows "—" with the reason as a tooltip when the data is missing."""
    if error:
        st.metric(name, "—", help=f"Unavailable: {error}")
    else:
        st.metric(name, value, delta=detail, delta_color="off", delta_arrow="off")


def tile(name: str, value: str, detail: str = "", used_pct: float | None = None) -> None:
    """A status card that looks like metric(), with an optional usage bar under the value."""
    progress = _bar(used_pct) if used_pct is not None else ""
    _html(
        '<div class="crystal-tile">'
        f'<div class="crystal-tile-label">{escape(name)}</div>'
        f'<div class="crystal-tile-value">{escape(value)}</div>{progress}'
        f'<div class="crystal-tile-detail">{escape(detail)}</div>'
        "</div>"
    )


def divider() -> None:
    """The thin ethereal divider from the home page."""
    _html(
        "<div style='height: 1px; width: 100%; margin-bottom: 40px;"
        " background: linear-gradient(90deg, transparent, rgba(127, 255, 212, 0.8), rgba(255, 153, 204, 0.8),"
        " rgba(127, 255, 212, 0.8), transparent); box-shadow: 0 0 10px #7FFFD4;'></div>"
    )


# --- Build info -----------------------------------------------------------------


@st.cache_resource
def app_version() -> str:
    """Short git commit of the running code, read from .git without needing the git binary."""
    git = REPO / ".git"
    try:
        head = (git / "HEAD").read_text().strip()
        if not head.startswith("ref: "):
            return head[:7]
        ref = head[5:]
        if (git / ref).exists():
            return (git / ref).read_text().strip()[:7]
        for line in (git / "packed-refs").read_text().splitlines():
            if line.endswith(" " + ref):
                return line[:7]
    except OSError:
        pass
    return "unknown"
