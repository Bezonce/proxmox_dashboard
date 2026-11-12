"""Sample answers of every service client, shaped like the real ones."""

import datetime as dt
import time

NOW = time.time()
TODAY = dt.datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)

PROXMOX = {
    "node": "proxmox1",
    "version": "9.2.26",
    "cpu": 0.12,
    "cpus": 6,
    "load": [0.8, 0.6, 0.5],
    "mem_used": 7.2e9,
    "mem_total": 16.6e9,
    "uptime": 3 * 86400 + 4 * 3600,
    "guests": [
        {
            "id": 102,
            "name": "pihole",
            "running": True,
            "cpu": 0.01,
            "mem": 6e7,
            "maxmem": 5.4e8,
            "disk": 9.6e8,
            "maxdisk": 8.3e9,
            "uptime": 600,
        },
        {
            "id": 110,
            "name": "jellyfin",
            "running": True,
            "cpu": 0.35,
            "mem": 2e9,
            "maxmem": 4.3e9,
            "disk": 2.3e9,
            "maxdisk": 2.9e10,
            "uptime": 6628,
        },
        {"id": 105, "name": "openvpn", "running": False, "cpu": 0, "mem": 0, "maxmem": 5.4e8, "disk": 0, "maxdisk": 4.1e9, "uptime": 0},
    ],
    "storage": [
        {"name": "local", "type": "dir", "content": "iso", "used": 1.1e10, "total": 8.9e10},
        {"name": "backup-hdd", "type": "dir", "content": "backup", "used": 3.6e12, "total": 3.9e12},
    ],
}

BACKUPS = {
    "latest": {102: {"when": NOW - 3600, "size": 3e8, "count": 3}, 110: {"when": NOW - 5 * 86400, "size": 1e9, "count": 2}},
    "total_size": 1.3e12,
    "runs": 7,
    "failed": [{"guest": "110", "status": "job errors", "when": NOW - 86400}],
}

RADARR = {
    "queue": [{"app": "Radarr", "title": "Dune: Part Two", "status": "downloading", "progress": 42.0, "time_left": "00:12:00"}],
    "upcoming": [{"when": TODAY, "timed": False, "kind": "Movie · Digital", "title": "Some Movie (2026)", "have": False}],
    "warnings": [{"app": "Radarr", "level": "warning", "message": "Indexers unavailable due to failures"}],
}

SONARR = {
    "queue": [{"app": "Sonarr", "title": "Show S01E02 Pilot <b>", "status": "importPending", "progress": 100.0, "time_left": ""}],
    "upcoming": [
        {"when": TODAY + dt.timedelta(days=1), "timed": True, "kind": "Episode", "title": "Show S01E03 Next", "have": False},
        {"when": TODAY + dt.timedelta(days=1, hours=1), "timed": True, "kind": "Episode", "title": "Other S02E01", "have": True},
    ],
    "warnings": [],
}

DISKS = [{"path": "/mnt/external_transfer", "free": 1.2e12, "total": 4.5e12}]

PROWLARR = {"indexers": 6, "failing": 1, "warnings": []}

JELLYFIN = {
    "movies": 412,
    "series": 37,
    "episodes": 1650,
    "streams": [{"user": "anna", "title": "Show S01E01 Pilot", "device": "Web · Firefox", "playback": "Transcode", "progress": 33.3}],
}

JELLYSEERR = {
    "pending": 2,
    "approved": 10,
    "processing": 1,
    "available": 55,
    "waiting": [{"title": "Some Series", "kind": "Series", "user": "anna", "when": TODAY}],
}

IMMICH = {"photos": 25000, "videos": 900, "library_size": 2.1e11, "disk_used": 1.4e12, "disk_total": 3.8e12}

PIHOLE = {
    "queries": 48000,
    "blocked": 6200,
    "percent_blocked": 12.9,
    "clients": 14,
    "blocklist": 180000,
    "top_clients": [
        {"name": "laptop.home.arpa", "ip": "192.168.0.50", "queries": 9000},
        {"name": "192.168.0.60", "ip": "192.168.0.60", "queries": 4000},
    ],
}
