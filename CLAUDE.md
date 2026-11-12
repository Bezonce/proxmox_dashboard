# Homelab context for the dashboard (proxmox_dashboard)

Copy this file into the dashboard repo as `CLAUDE.md`. The source of truth is
`docs/dashboard-context.md` in the IdaLab repo; update it there when the setup changes.

## The dashboard itself

- Streamlit app, repo `Bezonce/proxmox_dashboard`, branch `main`. Files: `app.py`,
  `pages/home.py`, `pages/torrent.py`, `torrent/status.py`, `styles/styles.py`.
- Runs in LXC container 108 (`192.168.0.108:8501`, Debian 13, Python 3.13) as the non-root
  user `dashboard`, systemd service `dashboard`, code in `/opt/dashboard`, virtualenv
  `/opt/dashboard/venv`. Users open it at `http://main.home.arpa` (Caddy reverse proxy).
- Deployed by Ansible (role `dashboard` in the IdaLab repo): clone, `pip install -r
  requirements.txt`, restart. After pushing to GitHub, on the Proxmox host:
  `ansible-playbook site.yml --tags dashboard --limit dashboard -e dashboard_update=true`
- `requirements.txt` must be UTF-8 (it was saved as UTF-16 by PowerShell `pip freeze`).
  Pin versions; every package must have wheels for Python 3.13.

## Configuration (.env)

Secrets and URLs live in `/opt/dashboard/.env` (root:dashboard, mode 640), read with
python-dotenv. Never commit `.env`; keep a `.env.example` with the names and empty values.

Existing names (keep them):

| Name | Meaning |
|---|---|
| `PROXMOX_HOST`, `PROXMOX_USER`, `PROXMOX_TOKEN` | Proxmox API token (read-only, see below) |
| `QBITTORRENT_NAME`, `QBITTORRENT_USER`, `QBITTORRENT_PASSWORD` | qBittorrent Web API login |
| `MEDIA_LINK`, `TORRENT_LINK`, `NAS_LINK`, `TORRENT_FOLDERS_LINK` | Links shown in the UI |
| `CAMERA_LINK` | The camera moved to an isolated network and can't be reached from the LAN. Point this at Surveillance Station on the NAS instead (`https://192.168.0.2:5001`). |

New ones, if the features are added: `<APP>_URL` + `<APP>_API_KEY` for `RADARR`, `SONARR`,
`PROWLARR`, `JELLYFIN`, `JELLYSEERR`, `IMMICH`; `PIHOLE_URL` + `PIHOLE_APP_PASSWORD`.

## Services

All on the LAN `192.168.0.0/24`; a container's IP is `192.168.0.<CT ID>`. Every web UI also
has a friendly name through Caddy: `http://<name>.home.arpa` (use these for links).

| CT | Service | Friendly link | Direct API base | Auth |
|---|---|---|---|---|
| – | Proxmox VE 9 (node `proxmox1`) | `proxmox.home.arpa` | `https://192.168.0.4:8006/api2/json` | API token `root@pam!dashboard`, role PVEAuditor (read-only). Self-signed cert. Library: `proxmoxer`. |
| 102 | Pi-hole v6 (DNS) | `pihole.home.arpa` | `http://192.168.0.102/api` | `POST /api/auth {"password": app password}` → `sid`, then header `X-FTL-SID`. Max 16 sessions: reuse one sid, never log in per page load. |
| 104 | qBittorrent 5.1 | `torrent.home.arpa` | `http://192.168.0.104:8080/api/v2` | Login cookie. Library: `qbittorrent-api`. |
| 107 | Caddy (reverse proxy) | – | – | – |
| 108 | This dashboard | `main.home.arpa` | – | – |
| 110 | Jellyfin | `watch.home.arpa` | `http://192.168.0.110:8096` | Header `Authorization: MediaBrowser Token="<key>"` |
| 111 | Radarr (movies) | `radarr.home.arpa` | `http://192.168.0.111:7878/api/v3` | Header `X-Api-Key` |
| 112 | Prowlarr (indexers) | `prowlarr.home.arpa` | `http://192.168.0.112:9696/api/v1` | Header `X-Api-Key` |
| 113 | Sonarr (series) | `sonarr.home.arpa` | `http://192.168.0.113:8989/api/v3` | Header `X-Api-Key` |
| 114 | Jellyseerr (requests) | `requests.home.arpa` | `http://192.168.0.114:5055/api/v1` | Header `X-Api-Key` |
| 115 | Immich (photos) | `photos.home.arpa` | `http://192.168.0.115:2283/api` | Header `x-api-key` |
| – | Synology NAS DS218+ | `rozi.home.arpa` | `https://192.168.0.2:5001/webapi` | DSM login (self-signed cert) |

Not managed by the IdaLab Ansible: CT 103 DuckDNS (dynamic DNS updater), CT 105 OpenVPN.
API keys: each app → Settings → General (Arr apps), Dashboard → API Keys (Jellyfin),
Account Settings → API Keys (Immich), Settings → Web interface/API → app password (Pi-hole).

### Health checks (no auth needed)

| Service | Check | Healthy |
|---|---|---|
| Radarr / Sonarr / Prowlarr | `GET /ping` | `{"status": "OK"}` |
| Jellyfin | `GET /health` | `Healthy` |
| Jellyseerr | `GET /api/v1/status` | JSON with `version` |
| Immich | `GET /api/server/ping` | `{"res": "pong"}` |
| qBittorrent | `GET /api/v2/app/version` | 403 without login also means "up" |
| Pi-hole | DNS query to 192.168.0.102:53, or `GET /api/auth` | answers |
| Proxmox | `GET /api2/json/version` with the token | JSON |

### Useful endpoints

- Proxmox: `/nodes/proxmox1/status` (CPU, RAM, uptime), `/nodes/proxmox1/lxc` (containers
  with CPU/RAM/status), `/nodes/proxmox1/storage` (pool usage),
  `/nodes/proxmox1/storage/backup-hdd/content?content=backup` (backup list),
  `/nodes/proxmox1/tasks?typefilter=vzdump` (backup results).
- qBittorrent: `/transfer/info` (speeds), `/torrents/info?filter=downloading|seeding`.
- Radarr / Sonarr: `/queue`, `/calendar?start=&end=` (upcoming), `/history`,
  `/diskspace`, `/health` (warnings).
- Jellyfin: `/Sessions` (now playing, transcoding info), `/Items/Counts`.
- Jellyseerr: `/request/count`, `/request?filter=pending`.
- Immich: `/server/statistics` (admin key), `/server/storage`.
- Pi-hole: `/stats/summary` (queries, blocked %), `/stats/top_clients`.

## Storage (good dashboard material)

- Proxmox SSD 256 GB: storage `local` (ISOs, templates) and `local-lvm` (container disks).
- Media pool (mergerfs) `/mnt/external_transfer` = 4 TB IronWolf + 500 GB WD, on USB.
  Downloads in `torrents/tmp`, library in `torrents/arr/Movies` and `torrents/arr/Shows`
  (Radarr/Sonarr hardlink finished downloads into the library).
- Proxmox backups: storage `backup-hdd` (`/mnt/disk2/pve-backup`), job nightly at 02:30.
- Photos: NAS share `//192.168.0.2/Photos`, used by Immich (`Photos/immich` for uploads).

## Rules

- Read-only: show and link, don't change server state unless explicitly decided. The
  Proxmox token is read-only on purpose; don't ask for a stronger one.
- Every request gets a timeout (2–5 s) and failures show as "down", never crash the page.
- Cache API results (`st.cache_data(ttl=30..300)`) and reuse logins (Pi-hole sid,
  qBittorrent cookie) via `st.cache_resource`, so a page refresh doesn't hit every service.
- Unreachable on purpose: the camera network (VLAN 30, 192.168.30.0/24) and the guest
  network (VLAN 40); the internet-facing side of the router.
- Everything is plain HTTP inside the LAN today; don't put passwords in URLs or logs.
