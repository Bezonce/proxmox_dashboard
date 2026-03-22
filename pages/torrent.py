import os

import polars as pl
import qbittorrentapi
import streamlit as st
from dotenv import load_dotenv

from styles.styles import apply_crystal_style

load_dotenv()

apply_crystal_style()


st.set_page_config(page_title="Crystal_City_OS", layout="wide")


# --- 1. CONNECTION (CACHED) ---
@st.cache_resource
def get_qbt_client():
    client = qbittorrentapi.Client(
        host=os.getenv("QBITTORRENT_NAME"),
        username=os.getenv("QBITTORRENT_USER"),
        password=os.getenv("QBITTORRENT_PASSWORD"),
    )
    client.auth_log_in()
    return client


# --- 2. DATA FETCHING LOGIC ---
def update_torrent_data(client):
    """Fetches new data and saves it to session state."""
    torrents = client.torrents_info(filter="all")
    if not torrents:
        st.session_state.df = None
        return

    # Calculate ETA components
    hours = pl.col("eta") // 3600
    minutes = (pl.col("eta") % 3600) // 60
    seconds = pl.col("eta") % 60

    st.session_state.df = (
        pl.DataFrame(torrents)
        .select(
            [
                pl.lit(False).alias("Selected"),
                (pl.col("size") / (1024**3)).round(2).alias("Size GB"),
                pl.col("name").alias("Name"),
                pl.col("progress").alias("Progress"),
                pl.col("ratio").round(2).alias("Ratio"),
                (pl.col("uploaded") / (1024**3)).round(2).alias("Uploaded GB"),
                (pl.col("dlspeed") / (1024**2)).round(2).alias("DL (MB/s)"),
                (
                    pl.when(pl.col("eta") >= 8640000)
                    .then(pl.lit("∞"))
                    .otherwise(
                        pl.format(
                            "{}:{}:{}",
                            hours,
                            minutes.cast(pl.String).str.zfill(2),
                            seconds.cast(pl.String).str.zfill(2),
                        )
                    )
                ).alias("ETA"),
                pl.from_epoch(pl.col("added_on")).dt.strftime("%Y-%m-%d %H:%M").alias("Added On"),
                pl.col("hash").alias("ID"),
            ]
        )
        .sort("Added On", descending=False)
    )


# --- 3. DIALOG ---
@st.dialog("Confirm Deletion")
def delete_torrents_dialog(qbt_client, edited_df):
    apply_crystal_style()
    selected = edited_df.filter(pl.col("Selected"))
    if selected.is_empty():
        st.warning("No torrents selected.")
        return

    st.write(f"Delete **{len(selected)}** torrents?")
    delete_files = st.checkbox("Also delete files on disk?", value=True)

    st.write(selected.select(["Name"]))

    total_size = selected.select(pl.col("Size GB").sum()).item()
    st.markdown(f"**Total size:** {total_size:.2f} GB")

    if st.button("⌽Confirm", type="primary"):
        ids = selected["ID"].to_list()
        qbt_client.torrents_delete(torrent_hashes=ids, delete_files=delete_files)
        # Reset everything
        if "torrent_editor" in st.session_state:
            del st.session_state["torrent_editor"]
        update_torrent_data(qbt_client)
        st.rerun()


# --- 4. MAIN APP ---
st.set_page_config(layout="wide")
qbt_client = get_qbt_client()

# Initialize data if it doesn't exist
if "df" not in st.session_state:
    update_torrent_data(qbt_client)

if st.session_state.df is not None:
    st.subheader(
        f"Active Transfers: {len(st.session_state.df)} torrents, {st.session_state.df.select(pl.col('Size GB').sum()).item():.2f} GB"
    )

    # TOOLBAR
    col1, col2, col3 = st.columns([1, 1, 1])

    # IMPORTANT: We define the editor FIRST so we can use its output in the buttons
    edited_df = st.data_editor(
        st.session_state.df,
        column_config={
            "Selected": st.column_config.CheckboxColumn(
                "Select",
                width="small",
            ),
            "Progress": st.column_config.ProgressColumn(
                "Progress", min_value=0, max_value=1, format="%.1f%%", color="#7FFFD4"
            ),
            "ID": None,
        },
        hide_index=True,
        width="stretch",
        key="torrent_editor",
    )

    with col1:
        if st.button(
            "⌽Delete",
            type="primary",
            width="stretch",
        ):
            # Pass edited_df (the one with the checkmarks) to the dialog
            delete_torrents_dialog(qbt_client, edited_df)

    with col2:
        if st.button(
            "⟳Refresh",
            width="stretch",
        ):
            update_torrent_data(qbt_client)
            st.rerun()

    with col3:
        if st.button(
            "≋Refresh RSS",
            width="stretch",
        ):
            qbt_client.rss_refresh_item(item_path="")
            st.toast("RSS Refreshing...")
            update_torrent_data(qbt_client)
            st.rerun()
else:
    st.info("No active torrents.")
    if st.button("Retry Connection"):
        update_torrent_data(qbt_client)
        st.rerun()
