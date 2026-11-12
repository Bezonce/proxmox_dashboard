"""Read-only view of the Proxmox node: load, containers, storage and backups."""

import time

from proxmoxer import ProxmoxAPI
from proxmoxer.core import ResourceException

from services.client import ServiceError, cached
from services.registry import env, proxmox_host

WEEK = 7 * 24 * 3600


def _api() -> ProxmoxAPI:
    host, user, token = proxmox_host(), env("PROXMOX_USER"), env("PROXMOX_TOKEN")
    if not (host and user and token):
        raise ServiceError("not configured – set PROXMOX_HOST, PROXMOX_USER and PROXMOX_TOKEN in .env")
    # PROXMOX_USER is "root@pam", or the full token id "root@pam!dashboard"
    user, _, token_name = user.partition("!")
    return ProxmoxAPI(
        host,
        user=user,
        token_name=token_name or env("PROXMOX_TOKEN_NAME", "dashboard"),
        token_value=token,
        verify_ssl=False,
        timeout=5,
    )


def _node(api: ProxmoxAPI) -> str:
    return env("PROXMOX_NODE") or api.nodes.get()[0]["node"]


def _api_error(error: ResourceException) -> ServiceError:
    hint = " – check the API token" if error.status_code in (401, 403) else ""
    return ServiceError(f"HTTP {error.status_code}{hint}")


def _version(pveversion: str) -> str:
    """'pve-manager/9.2.26/41a0e2e0' -> '9.2.26'"""
    parts = pveversion.split("/")
    return parts[1] if len(parts) > 1 else pveversion


def _fraction(value) -> float:
    """Proxmox reports idle containers with a CPU share slightly below zero."""
    return min(max(float(value or 0), 0.0), 1.0)


@cached(ttl=30)
def overview() -> dict:
    """The node's load, its containers and its storage pools."""
    try:
        api = _api()
        node = _node(api)
        status = api.nodes(node).status.get()
        guests = api.nodes(node).lxc.get()
        pools = api.nodes(node).storage.get()
    except ResourceException as error:
        raise _api_error(error) from None

    return {
        "node": node,
        "version": _version(status.get("pveversion", "")),
        "cpu": _fraction(status.get("cpu")),
        "cpus": status.get("cpuinfo", {}).get("cpus", 0),
        "load": [float(value) for value in status.get("loadavg", [])],
        "mem_used": status.get("memory", {}).get("used", 0),
        "mem_total": status.get("memory", {}).get("total", 0),
        "uptime": status.get("uptime", 0),
        "guests": sorted(
            (
                {
                    "id": int(guest["vmid"]),
                    "name": guest.get("name", ""),
                    "running": guest.get("status") == "running",
                    "cpu": _fraction(guest.get("cpu")),
                    "mem": guest.get("mem", 0),
                    "maxmem": guest.get("maxmem", 0),
                    "disk": guest.get("disk", 0),
                    "maxdisk": guest.get("maxdisk", 0),
                    "uptime": guest.get("uptime", 0),
                }
                for guest in guests
            ),
            key=lambda guest: guest["id"],
        ),
        "storage": [
            {
                "name": pool["storage"],
                "type": pool.get("type", ""),
                "content": pool.get("content", ""),
                "used": pool.get("used", 0),
                "total": pool.get("total", 0),
            }
            for pool in pools
            if pool.get("active")
        ],
    }


@cached(ttl=300)
def backups() -> dict:
    """The newest backup of every guest, plus the backup jobs of the last week that did not end OK."""
    try:
        api = _api()
        node = _node(api)
        archives = []
        for pool in api.nodes(node).storage.get(content="backup"):
            if pool.get("active"):
                archives += api.nodes(node).storage(pool["storage"]).content.get(content="backup")
        tasks = api.nodes(node).tasks.get(typefilter="vzdump", since=int(time.time()) - WEEK, limit=500)
    except ResourceException as error:
        raise _api_error(error) from None

    latest: dict[int, dict] = {}
    for archive in archives:
        guest = latest.setdefault(int(archive["vmid"]), {"when": 0, "size": 0, "count": 0})
        guest["count"] += 1
        if archive.get("ctime", 0) > guest["when"]:
            guest["when"], guest["size"] = archive["ctime"], archive.get("size", 0)

    return {
        "latest": latest,
        "total_size": sum(archive.get("size", 0) for archive in archives),
        "runs": len(tasks),
        # A running job has no endtime and no status yet; "WARNINGS: n" counts as not OK
        "failed": [
            {"guest": task.get("id") or "all", "status": task.get("status", ""), "when": task["endtime"]}
            for task in tasks
            if task.get("endtime") and task.get("status") != "OK"
        ],
    }
