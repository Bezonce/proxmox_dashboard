import streamlit as st


def apply_crystal_style():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Jura:wght@500;700&display=swap');

        /* 1. The Original Sky-to-City Gradient Background */
        .stApp {
            background: linear-gradient(180deg, #121A3B 0%, #305A8A 35%, #7FFFD4 75%, #E6E6FA 100%) !important;
            font-family: 'Jura', sans-serif;
            color: #E0FFFF;
        }

        /* 2. Original Floating Bokeh Orbs */
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

        /* 3. Original Tiny Stars */
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

        /* 4. Original Glass-Building Buttons (Applying to BOTH Link and Normal Buttons) */
        .stLinkButton a, .stButton > button {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(8px) !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            border-bottom: 3px solid #7FFFD4 !important; /* Cyan building glow */
            border-radius: 4px !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 3px;
            transition: all 0.3s ease-in-out !important;
            box-shadow: 0 8px 32px rgba(30, 144, 255, 0.2), inset 0 0 15px rgba(127, 255, 212, 0.1) !important;
            width: 100% !important;
        }

        /* Original Hover State: Magenta Glow */
        .stLinkButton a:hover, .stButton > button:hover {
            transform: translateY(-5px) !important;
            background: rgba(255, 255, 255, 0.2) !important;
            border-color: #FF99CC !important; 
            border-bottom: 3px solid #FF99CC !important;
            color: #FFFFFF !important;
            box-shadow: 0 10px 30px rgba(255, 153, 204, 0.4), inset 0 0 20px rgba(255, 153, 204, 0.2) !important;
            text-shadow: 0 0 10px #FFFFFF, 0 0 20px #FF99CC;
        }

        /* 5. NEW: The Magenta Heartbeat (Integrated into Original Style) */
        @keyframes heartbeat {
            0% { transform: scale(1); text-shadow: 0 0 10px #FF99CC; }
            14% { transform: scale(1.15); text-shadow: 0 0 20px #FF99CC, 0 0 30px rgba(255, 153, 204, 0.6); }
            28% { transform: scale(1); text-shadow: 0 0 10px #FF99CC; }
            42% { transform: scale(1.25); text-shadow: 0 0 25px #FF99CC, 0 0 45px rgba(255, 153, 204, 0.8); }
            70% { transform: scale(1); text-shadow: 0 0 10px #FF99CC; }
        }

        .stButton button p::first-letter, .stLinkButton a span::first-letter {
            color: #FF99CC !important;
            display: inline-block !important;
            transition: all 0.3s ease;
            text-shadow: 0 0 10px #FF99CC;
            margin-right: 5px;
        }

        .stButton button:hover p::first-letter, .stLinkButton a:hover span::first-letter {
            animation: heartbeat 1.5s ease-in-out infinite !important;
        }

        /* 6. NEW: The HUD Table (Matching your Glassmorphism) */
        div[data-testid="stDataFrame"] {
            background: rgba(18, 26, 59, 0.3) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(127, 255, 212, 0.3) !important;
            border-radius: 8px !important;
        }

        div[data-testid="stDataFrame"] th {
            background-color: rgba(127, 255, 212, 0.1) !important;
            color: #7FFFD4 !important;
        }

        /* 7. Original Titles Styling */
        .crystal-title {
            font-size: 3.5rem;
            font-weight: 700;
            text-align: center;
            color: #FFFFFF;
            letter-spacing: 8px;
            text-shadow: 0 0 10px #7FFFD4, 0 0 20px #87CEFA, 0 0 30px #FF99CC;
            padding-top: 20px;
        }

        .stSubheader, h1, h2, h3 {
            color: #FFFFFF !important;
            text-shadow: 0 0 10px #7FFFD4 !important;
        }

        /* 8. Status lights on the home grid (containers keyed status_<up|down|unknown>_<service>) */
        [class*="st-key-status_"] .stLinkButton a {
            position: relative !important;
        }
        [class*="st-key-status_"] .stLinkButton a::after {
            content: "";
            position: absolute;
            top: 8px; right: 10px;
            width: 7px; height: 7px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.35);
        }
        [class*="st-key-status_up_"] .stLinkButton a::after {
            background: #7FFFD4;
            box-shadow: 0 0 6px #7FFFD4, 0 0 12px #7FFFD4;
        }
        [class*="st-key-status_down_"] .stLinkButton a {
            border-bottom-color: #FF5C8A !important;
            opacity: 0.75;
        }
        [class*="st-key-status_down_"] .stLinkButton a::after {
            background: #FF5C8A;
            box-shadow: 0 0 6px #FF5C8A, 0 0 14px #FF5C8A;
            animation: blink 1.5s ease-in-out infinite;
        }
        @keyframes blink { 50% { opacity: 0.3; } }

        /* 9. Glass panels and metric tiles: dark glass so text stays readable on the light horizon */
        [class*="st-key-panel_"] {
            background: rgba(18, 26, 59, 0.55);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(127, 255, 212, 0.3);
            border-radius: 8px;
            padding: 18px 22px;
            box-shadow: 0 8px 32px rgba(30, 144, 255, 0.2);
        }

        div[data-testid="stMetric"] {
            background: rgba(18, 26, 59, 0.45);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-bottom: 3px solid #7FFFD4;
            border-radius: 4px;
            padding: 14px 18px;
            box-shadow: 0 8px 32px rgba(30, 144, 255, 0.2), inset 0 0 15px rgba(127, 255, 212, 0.1);
        }
        [data-testid="stMetricLabel"] p {
            color: #7FFFD4 !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-size: 0.75rem !important;
        }
        [data-testid="stMetricValue"] p {
            color: #FFFFFF !important;
            font-family: 'Jura', sans-serif;
            text-shadow: 0 0 10px rgba(127, 255, 212, 0.6);
        }

        [data-testid="stMetricDelta"], [data-testid="stMetricDelta"] * {
            background: transparent !important;
            color: rgba(224, 255, 255, 0.75) !important;
            padding-left: 0 !important;
            letter-spacing: 1px;
        }

        .crystal-label {
            color: #7FFFD4;
            text-transform: uppercase;
            letter-spacing: 3px;
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .crystal-big {
            color: #FFFFFF;
            font-size: 1.9rem;
            line-height: 1.3;
            text-shadow: 0 0 10px rgba(127, 255, 212, 0.6);
        }
        .crystal-muted {
            color: rgba(224, 255, 255, 0.7);
            font-size: 0.85rem;
            letter-spacing: 1px;
        }
        .crystal-center { text-align: center; }

        .crystal-offline {
            color: #FFD1E3;
            background: rgba(255, 92, 138, 0.12);
            border-left: 3px solid #FF5C8A;
            border-radius: 2px;
            padding: 6px 12px;
            font-size: 0.9rem;
            letter-spacing: 1px;
        }

        /* 10. Usage bars and list rows */
        .crystal-bar-head, .crystal-row {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            color: #E0FFFF;
            letter-spacing: 1px;
        }
        .crystal-bar-head { font-size: 0.85rem; margin: 10px 0 4px; }
        .crystal-bar {
            height: 6px;
            background: rgba(255, 255, 255, 0.12);
            border-radius: 3px;
            overflow: hidden;
        }
        .crystal-bar > div {
            height: 100%;
            background: linear-gradient(90deg, #7FFFD4, #87CEFA);
            box-shadow: 0 0 8px #7FFFD4;
        }
        .crystal-bar.warn > div { background: linear-gradient(90deg, #FFFF99, #FF99CC); box-shadow: 0 0 8px #FF99CC; }
        .crystal-bar.crit > div { background: #FF5C8A; box-shadow: 0 0 8px #FF5C8A; }

        .crystal-row {
            padding: 8px 0;
            border-bottom: 1px solid rgba(127, 255, 212, 0.15);
            align-items: baseline;
        }
        .crystal-row:last-child { border-bottom: none; }
        .crystal-row .title { color: #FFFFFF; font-weight: 700; overflow-wrap: anywhere; }
        .crystal-row .meta { color: rgba(224, 255, 255, 0.7); font-size: 0.8rem; }
        .crystal-row .value { color: #7FFFD4; white-space: nowrap; font-size: 0.85rem; }
        .crystal-row .value.alert { color: #FF99CC; }
        .crystal-row .crystal-bar { margin-top: 6px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
