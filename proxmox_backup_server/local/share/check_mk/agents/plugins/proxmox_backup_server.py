#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) 2026 Marcel Pennewiss <opensource@pennewiss.de>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  This file is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

import json
import shutil
import subprocess
import sys

from datetime import datetime, timedelta
from typing import Any

# Proxmox backup debug binery
PROXMOX_BACKUP_DEBUG = "/usr/sbin/proxmox-backup-debug"


def get_api_data(api_path: str, query_parameters: dict = {}) -> Any:
    """Execute proxmox-backup-debug API call and return parsed JSON data."""
    command = [
        PROXMOX_BACKUP_DEBUG,
        "api",
        "get",
        api_path,
        "--output-format",
        "json",
    ]

    for query_parameter, query_value in query_parameters.items():
        command.append(f"--{query_parameter}")
        command.append(str(query_value))

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Command execution failed with exit code "
            f"{e.returncode}: {e.stderr.strip()}"
        ) from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse JSON output: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error while executing API request: {e}") from e


def get_datastores() -> Any:
    """Retrieve datastore usage information from the API."""
    api_path = "/status/datastore-usage"
    return get_api_data(api_path)


def get_version() -> str:
    """Retrieve Proxmox Backup Server version."""
    api_path = "/version"
    data = get_api_data(api_path)
    return data.get("version", "UNKNOWN")


def get_gc_info(store: str) -> dict[str, Any]:
    """Retrieve Garbage Collection info for a specific datastore."""
    api_path = f"/admin/datastore/{store}/gc"
    data = get_api_data(api_path)

    return {
        "gc_last_run_state": data.get("last-run-state", "UNKNOWN"),
        "gc_last_run_endtime": data.get("last-run-endtime", "UNKNOWN"),
        "gc_duration": data.get("duration", "UNKNOWN"),
        "gc_removed_bytes": data.get("removed-bytes", "UNKNOWN"),
        "gc_pending_bytes": data.get("pending-bytes", "UNKNOWN"),
        "gc_disk_bytes": data.get("disk-bytes", "UNKNOWN"),
        "gc_index_data_bytes": data.get("index-data-bytes", "UNKNOWN"),
    }


def get_tasks(since: int = 0) -> list[dict[str, str]]:
    """Retrieve Proxmox Backup Server tasks (optional filtered with timestamp)."""
    api_path = "/nodes/localhost/tasks"
    query_parameters = {"limit": 0}
    if since > 0:
        query_parameters["since"] = since
    return get_api_data(api_path, query_parameters)


def print_version() -> None:
    """Print Proxmox Backup Server version."""
    version = get_version()
    print(f"version: {version}")


def print_datastores() -> None:
    """Print datastore information according to mount-status rules."""

    print("[datastores]")

    # Get sorted list of datastores
    datastores = sorted(get_datastores(), key=lambda x: x.get("store", ""))
    for entry in datastores:
        store_name = entry.get("store", "UNKNOWN")
        mount_status = entry.get("mount-status")
        backend_type = entry.get("backend-type")
        error = entry.get("error")

        if error is not None:
            if error.endswith("datastore is being unmounted"):
                # GC informations unavailable during unmount, so handle as not mounted
                mount_status = "notmounted"
            else:
                # Ignore datastaore on unhandled error
                continue

        if mount_status in ("mounted", "nonremovable"):
            avail = entry["avail"]
            used = entry["used"]
            total = entry["total"]
            filled = int(entry["used"] / entry["total"] * 100)

            if entry["estimated-full-date"] != "":
                # Calculate timespan
                # Set to zero if timespan is in the past
                estimated_full_timespan = max(0, int(entry["estimated-full-date"]) - int(datetime.now().timestamp()))
            else:
                # Not available
                estimated_full_timespan = -1

            # GC Infos abrufen
            gc_info = get_gc_info(store_name)
            gc_last_run_state = gc_info["gc_last_run_state"]
            gc_last_run_endtime = gc_info["gc_last_run_endtime"]
            gc_duration = gc_info["gc_duration"]
            gc_removed_bytes = gc_info["gc_removed_bytes"]
            gc_pending_bytes = gc_info["gc_pending_bytes"]
            gc_disk_bytes = gc_info["gc_disk_bytes"]
            gc_index_data_bytes = gc_info["gc_index_data_bytes"]

            print(
                f"{store_name}: "
                f"{mount_status} "
                f"{backend_type} "
                f"{avail} "
                f"{used} "
                f"{total} "
                f"{filled} "
                f"{estimated_full_timespan} "
                f"{gc_last_run_state} "
                f"{gc_last_run_endtime} "
                f"{gc_duration} "
                f"{gc_removed_bytes} "
                f"{gc_pending_bytes} "
                f"{gc_disk_bytes} "
                f"{gc_index_data_bytes}"
            )

        elif mount_status == "notmounted":
            print(f"{store_name}: {mount_status} {backend_type}")
        else:
            print(f"{store_name}: UNKNOWN UNKNOWN")


def print_task_summary() -> None:
    """Print task summary."""

    print("[task_summary]")

    # Get tasks of the last 30 days
    since = int((datetime.now() - timedelta(days=30)).timestamp())
    tasks = get_tasks(since)

    status_counter = {"ok": 0, "warning": 0, "error": 0, "unknown": 0}
    result = {
        "backup": dict(status_counter),
        "garbage_collection": dict(status_counter),
        "prune": dict(status_counter),
        "sync": dict(status_counter),
        "tape_backup": dict(status_counter),
        "tape_restore": dict(status_counter),
        "other": dict(status_counter),
        "verify": dict(status_counter),
    }
    worker_type_aliases = {
        "backup": ["backupjob"],
        "prune": ["prunejob"],
        "sync": ["syncjob"],
        "tape_backup": ["tape-backup", "tape-backup-job"],
        "tape_restore": ["tape-restore"],
        "verify": ["verificationjob", "verify_group", "verify_snapshot"]
    }

    # List of known ignored worker_types
    # acme-deactivate acme-new-cert acme-register acme-renew-cert acme-revoke-cert acme-update aptupdate barcode-label-media catalog-media 
    # create-datastore delete-datastore delete-namespace dircreate dirremove diskinit eject-media forget-group format-media inventory-update
    # label-media load-media logrotate mount-device mount-sync-jobs notification-threshold-reset reader realm-sync remove-encryption-key 
    # rewind-media s3-refresh spiceshell srvreload srvrestart srvstart srvstop termproxy unload-media unmount-device vncshell wipedisk zfscreate

    for task in tasks:

        worker_type = task.get("worker_type", "unknown")
        status = task.get("status", "not_found").lower()

        # Combine known different worker_type values
        for real_worker_type, worker_type_alias in worker_type_aliases.items():
            if worker_type in worker_type_alias:
                worker_type = real_worker_type

        # Handle warnings
        if status.startswith("warnings"):
            status = "warning"

        # Handle non-standard status as error
        if status not in ["ok", "warning", "unknown", "error"]:
            status = "error"

        try:
            result[worker_type][status] += 1
        except KeyError:
            result["other"][status] += 1

    # Output summarized counters
    for status in result:
        print(f"{status}: {result[status]["ok"]} {result[status]["warning"]} {result[status]["error"]} {result[status]["unknown"]}")


def main() -> int:

    # Exit silently if command is not available
    if shutil.which(PROXMOX_BACKUP_DEBUG) is None:
        return 0

    try:
        # Plugin header
        print("<<<proxmox_backup_server>>>")

        # Version
        print_version()

        # Datastores and garbage collection
        print_datastores()

        # Task summary
        print_task_summary()

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
