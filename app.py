import streamlit as st

from styles.styles import apply_crystal_style

apply_crystal_style()

# MUST BE THE FIRST LINE
st.set_page_config(page_title="Crystal_City_OS", layout="wide")

# Define your pages
home_page = st.Page("pages/home.py", title="Home", icon="💠", default=True)
server_page = st.Page("pages/server.py", title="Server", icon="🖥️")
media_page = st.Page("pages/media.py", title="Media", icon="🎬")
network_page = st.Page("pages/network.py", title="Network", icon="🛡️")
torrent_page = st.Page("pages/torrent.py", title="Torrent", icon="📡")
books_page = st.Page("pages/books.py", title="Books", icon="📡")

# Create the Navigation
pg = st.navigation(
    {
        "Main": [home_page],
        "Homelab": [server_page, media_page, network_page],
        "Services": [torrent_page, books_page],
    }
)

# Run the app
pg.run()
