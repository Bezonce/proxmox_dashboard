import streamlit as st

from styles.styles import apply_crystal_style

apply_crystal_style()

# MUST BE THE FIRST LINE
st.set_page_config(page_title="Crystal_City_OS", layout="wide")

# Define your pages
home_page = st.Page("pages/home.py", title="Home", icon="💠", default=True)
torrent_page = st.Page("pages/torrent.py", title="Torrent", icon="📡")

# Create the Navigation
pg = st.navigation({"Main": [home_page], "Services": [torrent_page]})

# Run the app
pg.run()
