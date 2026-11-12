# proxmox_dashboard
My Take on a proxmox dashboard

# Create a proxmox API Token:

## Step 1: Create the Token in Proxmox
1. Log into your Proxmox Web UI.
2. Go to Datacenter > Permissions > API Tokens.
3. Click Add.
    - User: root@pam
    - Token ID: dashboard (or whatever name you like)
    - Privilege Separation: Checked (recommended).
4. IMPORTANT: Copy the Secret immediately. It will never be shown again.

## Step 2: Give the Token Permissions
1. Go to Datacenter > Permissions.
2. Click Add > API Token Permission.
3. Path: / (This gives access to the whole cluster)
4. Token: Select the root@pam!dashboard token you just made.
5. Role: PVEAuditor (This is "Read Only" — perfect for a dashboard).

## Configuration
Copy `.env.example` to `.env` and fill it in. Every service is optional: one that is not
configured or not reachable shows up as a single "offline" line, never as an error page.

| Page | Shows | Needs |
|---|---|---|
| Home | Service buttons with a status light, server and media vitals | the links (defaults: `http://<name>.home.arpa`) |
| Server | Node load, containers, storage, backups | `PROXMOX_*` (read-only token) |
| Media | Now playing, downloads, upcoming releases, requests, indexers, photos | `<APP>_API_KEY` for Jellyfin, Radarr, Sonarr, Prowlarr, Jellyseerr, Immich |
| Network | Pi-hole statistics, every service's status | `PIHOLE_APP_PASSWORD` |
| Torrent | qBittorrent list, delete, RSS refresh | `QBITTORRENT_*` |

Service addresses live in `services/registry.py`; API clients in `services/`.
Pages refresh themselves every 30–300 s, and API answers are cached, so a reload doesn't hit every service.

## Development
```sh
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt -r requirements-dev.txt
streamlit run app.py
pytest -q          # renders every page against sample data, no network needed
ruff check --line-length 140 services styles tests
```
CI (`.github/workflows/ci.yml`) runs the same checks on Python 3.13 on every push.