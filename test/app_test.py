import os

import polars as pl
import qbittorrentapi
import streamlit as st
from dotenv import load_dotenv
from proxmoxer import ProxmoxAPI

# 1. Load the variables from the .env file
load_dotenv()

# 2. Initialize Proxmox connection
try:
    proxmox = ProxmoxAPI(
        os.getenv("PROXMOX_HOST"),
        user=os.getenv("PROXMOX_USER"),
        token_name="dashboard",
        token_value=os.getenv("PROXMOX_TOKEN"),
        verify_ssl=False,
    )
    st.success("Connected to Proxmox!")
except Exception as e:
    st.error(f"Failed to connect: {e}")


st.title("🚀 Proxmox Homelab Dashboard")

# 3. Fetch Data
nodes = proxmox.nodes.get()

# 4. Display Data
for node in nodes:
    st.subheader(f"Node: {node['node']}")
    col1, col2, col3 = st.columns(3)

    # Calculate CPU percentage
    cpu_pct = round(node["cpu"] * 100, 2)

    col1.metric("Status", node["status"])
    col2.metric("CPU Usage", f"{cpu_pct}%")
    col3.metric("Uptime", f"{node['uptime'] // 3600} hours")
st.divider()

st.title("💾 Proxmox Storage")
try:
    nodes = proxmox.nodes.get()
    raw_data = []

    for node in nodes:
        node_name = node["node"]
        node_storage = proxmox.nodes(node_name).storage.get()

        for s in node_storage:
            if s.get("active") and "total" in s:
                raw_data.append(
                    {
                        "Node": node_name,
                        "Storage": s["storage"],
                        "Type": s["type"],
                        "total_bytes": s["total"],
                        "used_bytes": s["used"],
                    }
                )
        disks = proxmox.nodes(node_name).disks.list.get()

        # for d in disks:
        #     if d.get("devpath") == "/dev/sdb":  # Or check if 'usb' in d.get('vendor', '').lower()
        #         # Note: Proxmox Disks API uses 'size' for total bytes
        #         # We can't always get 'used' bytes from the disks API easily
        #         # unless it's mounted as storage.
        #         raw_data.append(
        #             {
        #                 "Node": node_name,
        #                 "Storage": f"USB-{d['model']}",
        #                 "Type": "Unmanaged USB",
        #                 "total_bytes": d["size"],
        #                 "used_bytes": d.get("used", 0),  # API might return 0 if not mounted
        #             }
        #         )
    # 1. Create Polars DataFrame
    df = pl.DataFrame(raw_data)
    if not df.is_empty():
        # 2. Perform calculations using Polars expressions
        # This is more efficient than calculating during the loop
        df = df.with_columns(
            [
                (pl.col("total_bytes") / (1024**3)).round(2).alias("Total (GB)"),
                (pl.col("used_bytes") / (1024**3)).round(2).alias("Used (GB)"),
                ((pl.col("total_bytes") - pl.col("used_bytes")) / (1024**3)).round(2).alias("Free (GB)"),
            ]
        )

        # 3. Display table (Streamlit can display Polars DFs directly)
        st.subheader("Storage Overview")
        st.dataframe(
            df.select(["Node", "Storage", "Type", "Used (GB)", "Free (GB)", "Total (GB)"]), use_container_width=True
        )

        # 4. Plotting
        st.subheader("Usage Visualization")

        # Streamlit's bar_chart likes the index to be the labels.
        # We convert back to pandas just for the chart rendering (Streamlit requirement)
        chart_df = df.select(["Storage", "Used (GB)", "Free (GB)"]).to_pandas().set_index("Storage")
        st.bar_chart(chart_df)

    else:
        st.warning("No active storage found.")

except Exception as e:
    st.error(f"Error fetching storage: {e}")


try:
    # 1. Initialize Client
    qbt_client = qbittorrentapi.Client(
        host=os.getenv("QBITTORRENT_NAME"),
        # port=os.getenv("QBITTORRENT_PORT"),
        username=os.getenv("QBITTORRENT_USER"),
        password=os.getenv("QBITTORRENT_PASSWORD"),
    )
    qbt_client.auth_log_in()

    # 2. Get Torrents
    # 'filter="active"' gets torrents that are currently downloading, uploading, or queued
    torrents = qbt_client.torrents_info(filter="active")

    if torrents:
        # 3. Process with Polars
        df_qbt = pl.DataFrame(torrents)

        # 4. Clean up the data
        # Convert bytes to MB/s and round percentages
        df_active = df_qbt.select(
            [
                pl.col("name").alias("Name"),
                pl.col("state").alias("Status"),
                (pl.col("progress") * 100).round(1).alias("Progress %"),
                (pl.col("dlspeed") / (1024**2)).round(2).alias("DL (MB/s)"),
                (pl.col("upspeed") / (1024**2)).round(2).alias("UP (MB/s)"),
                pl.col("eta").alias("ETA (s)"),
            ]
        )

        # 5. Display Table
        st.subheader(f"Active Transfers ({len(df_active)} torrents)")
        st.dataframe(df_active, use_container_width=True, hide_index=True)

        # 6. Plotting Speed
        if len(df_active) > 0:
            st.subheader("Download Speed per Torrent")
            chart_data = df_active.to_pandas().set_index("Name")[["DL (MB/s)"]]
            st.bar_chart(chart_data)

    else:
        st.info("No active torrents at the moment.")

except Exception as e:
    st.error(f"Failed to connect to qBittorrent: {e}")
