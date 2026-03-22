import os

import streamlit as st
from dotenv import load_dotenv

from styles.styles import apply_crystal_style

apply_crystal_style()

load_dotenv()

# --- Service Definitions --- git commit -m "First version of the dashboard with working
services = [
    {"name": "Torrent", "url": os.getenv("MEDIA_LINK"), "icon": "✧"},
    {"name": "Jellyfin", "url": os.getenv("TORRENT_LINK"), "icon": "◈"},
    {"name": "Rozi", "url": os.getenv("NAS_LINK"), "icon": "✦"},
    {"name": "Camera", "url": os.getenv("CAMERA_LINK"), "icon": "◎"},
    {"name": "Folders", "url": os.getenv("TORRENT_FOLDERS_LINK"), "icon": "◮"},
]

# --- Grid Layout ---
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.link_button(
        label=f"{services[0]['icon']} {services[0]['name']}", url=services[0]["url"], use_container_width=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button(
        label=f"{services[3]['icon']} {services[3]['name']}", url=services[3]["url"], use_container_width=True
    )

with col2:
    st.link_button(
        label=f"{services[1]['icon']} {services[1]['name']}", url=services[1]["url"], use_container_width=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button(
        label=f"{services[4]['icon']} {services[4]['name']}", url=services[4]["url"], use_container_width=True
    )

with col3:
    st.link_button(
        label=f"{services[2]['icon']} {services[2]['name']}", url=services[2]["url"], use_container_width=True
    )

# --- Thin Ethereal Divider ---
st.markdown(
    """
    <div style='height: 1px; width: 100%; margin-bottom: 40px; 
    background: linear-gradient(90deg, transparent, rgba(127, 255, 212, 0.8), rgba(255, 153, 204, 0.8), rgba(127, 255, 212, 0.8), transparent); 
    box-shadow: 0 0 10px #7FFFD4;'></div>
    """,
    unsafe_allow_html=True,
)
