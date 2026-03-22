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
        .stLinkButton > a, .stButton > button {
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
        .stLinkButton > a:hover, .stButton > button:hover {
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
        </style>
        """,
        unsafe_allow_html=True,
    )
