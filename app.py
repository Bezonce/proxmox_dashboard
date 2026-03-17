import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Crystal_City_OS", layout="wide")

# --- Ethereal 90s Anime Cityscape CSS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Jura:wght@500;700&display=swap');

    /* 1. The Sky-to-City Gradient Background */
    .stApp {
        background: linear-gradient(180deg, #121A3B 0%, #305A8A 35%, #7FFFD4 75%, #E6E6FA 100%) !important;
        font-family: 'Jura', sans-serif; /* Sleek, slightly sci-fi but elegant font */
        color: #E0FFFF;
    }

    /* 2. The Floating Bokeh Orbs (Lens Flares) */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            radial-gradient(circle at 15% 45%, rgba(255, 153, 204, 0.4) 0%, transparent 80px),
            radial-gradient(circle at 85% 65%, rgba(255, 255, 153, 0.25) 0%, transparent 100px),
            radial-gradient(circle at 50% 80%, rgba(135, 206, 250, 0.5) 0%, transparent 120px),
            radial-gradient(circle at 70% 30%, rgba(255, 153, 204, 0.3) 0%, transparent 90px),
            radial-gradient(circle at 30% 75%, rgba(255, 255, 153, 0.3) 0%, transparent 70px);
        pointer-events: none;
        z-index: 0;
    }

    /* Add some tiny stars at the top */
    .stApp::after {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 40%;
        background-image: 
            radial-gradient(1px 1px at 20px 30px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1px 1px at 90px 80px, #ffffff, rgba(0,0,0,0)),
            radial-gradient(1.5px 1.5px at 150px 45px, rgba(255,255,255,0.8), rgba(0,0,0,0)),
            radial-gradient(1px 1px at 250px 90px, #ffffff, rgba(0,0,0,0));
        background-repeat: repeat;
        background-size: 300px 150px;
        pointer-events: none;
        z-index: 0;
        opacity: 0.6;
    }

    /* 3. Ethereal Glowing Header */
    .crystal-title {
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        color: #FFFFFF;
        letter-spacing: 8px;
        text-shadow: 0 0 10px #7FFFD4, 0 0 20px #87CEFA, 0 0 30px #FF99CC;
        padding-top: 20px;
        position: relative;
        z-index: 1;
    }
    
    .crystal-subtitle {
        text-align: center;
        color: #E0FFFF;
        letter-spacing: 5px;
        font-size: 1.1rem;
        margin-bottom: 40px;
        text-shadow: 0 0 8px rgba(255,255,255,0.5);
        position: relative;
        z-index: 1;
    }

    /* 4. Glass-Building Buttons */
    .stLinkButton > a {
        height: 110px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        background: rgba(255, 255, 255, 0.1) !important; /* Crystal clear glass */
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-bottom: 3px solid #7FFFD4 !important; /* Cyan building glow */
        border-radius: 4px !important; /* Sharper edges like the city buildings */
        color: #FFFFFF !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 3px;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 8px 32px rgba(30, 144, 255, 0.2), inset 0 0 15px rgba(127, 255, 212, 0.1) !important;
        position: relative;
        z-index: 1;
    }

    /* 5. Hover State: Magenta/Cyan Glow */
    .stLinkButton > a:hover {
        transform: translateY(-5px) !important;
        background: rgba(255, 255, 255, 0.2) !important;
        border-color: #FF99CC !important; /* Shifts to the pink flare color */
        border-bottom: 3px solid #FF99CC !important;
        color: #FFFFFF !important;
        box-shadow: 0 10px 30px rgba(255, 153, 204, 0.4), inset 0 0 20px rgba(255, 153, 204, 0.2) !important;
        text-shadow: 0 0 10px #FFFFFF, 0 0 20px #FF99CC;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.markdown('<div class="crystal-title">CRYSTAL_TOKYO_OS</div>', unsafe_allow_html=True)
st.markdown('<div class="crystal-subtitle">CITY GRID: ONLINE // ATMOSPHERE: CLEAR</div>', unsafe_allow_html=True)

# --- Thin Ethereal Divider ---
st.markdown(
    """
    <div style='height: 1px; width: 100%; margin-bottom: 40px; 
    background: linear-gradient(90deg, transparent, rgba(127, 255, 212, 0.8), rgba(255, 153, 204, 0.8), rgba(127, 255, 212, 0.8), transparent); 
    box-shadow: 0 0 10px #7FFFD4;'></div>
    """,
    unsafe_allow_html=True,
)


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
