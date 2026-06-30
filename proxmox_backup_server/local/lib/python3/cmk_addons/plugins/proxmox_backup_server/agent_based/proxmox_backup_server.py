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

# Example Agent Output
# <<<proxmox_backup_server>>>
# version: 4.2
# [datastores]
# local: nonremovable filesystem 6641242112 600023642112 633523994624 94.71 1771397371 OK 1779271206 6 0 1624563356 597285282328 8340617313837
# mobile-disk-01: mounted filesystem 257566208000 675756896256 983350071296 68.72 1780559822 OK 1779274270 1270 3576196397 0 674466529488 10527045155076
# mobile-disk-02: notmounted filesystem
# [task_summary]
# backup: 0 0 0 0 0
# garbage_collection: 166 0 10 0 0
# prune: 86 0 0 0 0
# sync: 1851 0 293 2 5
# tape_backup: 0 0 0 0 0
# tape_restore: 0 0 0 0 0
# other: 168 1 3 0 0
# verify: 50 0 1 0 0
# [sync_jobs]
# s-54c9245e-a0b8: ERROR 1779825601 1779829200 pull local/pve1.example.org proxmox-backup.example.org:local/pve1.example.org 0
# s-b3565376-c06a: OK 1779825600 1779829200 push local/pve2.example.org proxmox-backup.example.org:local/pve2.example.org 1
# s-ec9ae6b0-20c4: NOTMOUNTED 1779769800 1779856200 pull mobile-disk-01 proxmox-backup.example.org:local Full
# [prune_jobs]
# s-902c8dea-03e7: OK 1779827400 1779913800 local/pve1.example.org 0
# s-5148965e-d0cd: OK 0 1779826800 mobile-disk-01 Full
# s-9b04d22c-389b: PENDING 0 1779826800 mobile-disk-02 Full
# [verify_jobs]
# v-81d035b0-e0b2: OK 1779766987 1779852600 local Full
# v-90e4fc0b-7506: OK 1779692412 1779778800 mobile-disk-01 Full
# v-b00a0f32-a07f: PENDING 1779778805 1779865200 mobile-disk-02 Full

import time

# Import _METRIC_SPECS_*
from . import proxmox_backup_server_metric_specs

from typing import Any, Dict, TypedDict

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    render,
    Result,
    Service,
    State,
    StringTable,
)

Section = Dict[str, Any]
Metrics = Dict[str, Any]


class Datastore(TypedDict, total=False):
    mount_status: str
    backend_type: str
    metrics: Dict[str, Any]


class Job(TypedDict, total=False):
    state: str
    local: str
    max_depth: Any
    metrics: Dict[str, Any]
    # Only required for sync jobs
    sync_direction: str
    remote: str


def parse_proxmox_backup_server(string_table: StringTable) -> Section:

    parsed: Section = {
        "version": None,
        "datastores": {},
        "task_summary": {},
        "sync_jobs": {},
        "prune_jobs": {},
        "verify_jobs": {},
    }
    current_section = None

    for line in string_table:
        if not line:
            continue

        # Line "version: x.y"
        if line[0] == "version:":
            parsed["version"] = line[1]
            continue

        # Detect sections
        if line[0].startswith("[") and line[0].endswith("]"):
            current_section = line[0][1:-1]
            continue

        # Section "datastores"
        # Format: "<store>: <mount_status> <backend_type> <avail> <used> <total> <filled>
        #          <estimated-full-date> <gc_state> <gc_endtime> <gc_duration>
        #          <gc_removed_bytes> <gc_pending_bytes> <gc_disk_bytes>
        #          <gc_index_data_bytes>"
        if current_section == "datastores":

            # Ignore line does not start with "<store>:"
            if not line[0].endswith(":"):
                continue

            # Get store name
            store = line[0][:-1]

            # Get values
            metrics: Metrics = {}
            datastore: Datastore = {
                "mount_status": line[1],
                "backend_type": line[2],
            }

            # Parse metrics from specs for mounted and nonremoval
            try:
                if datastore["mount_status"] in ["mounted", "nonremovable"]:
                    for idx, metric_spec in enumerate(proxmox_backup_server_metric_specs._METRIC_SPECS_DATASTORES):
                        parse_metric = proxmox_backup_server_metric_specs._METRIC_SPECS_DATASTORES[metric_spec][0]
                        if len(line) >= idx+3 and parse_metric:
                            if proxmox_backup_server_metric_specs._METRIC_SPECS_DATASTORES[metric_spec][2] == str:
                                metrics[metric_spec] = line[idx+3]
                            elif proxmox_backup_server_metric_specs._METRIC_SPECS_DATASTORES[metric_spec][2] is render.percent:
                                metrics[metric_spec] = float(line[idx+3])
                            else:
                                # Convert non-string metrics to integer
                                metrics[metric_spec] = int(line[idx+3])

                    # Calculate deduplication factor
                    metrics["deduplication_factor"] = round(metrics["gc_index_data_bytes"] / int(metrics["gc_disk_bytes"]), 2)

                    # Calculate timespan from Garbage Collection Endtime
                    # (done on server to prevent overdue caused by cached agent results)
                    metrics["gc_endtime_timespan"] = int(time.time())-metrics["gc_endtime_timespan"]

                    # Add metrics
                    datastore["metrics"] = metrics

            except (KeyError, TypeError, ValueError):
                # Ignore entry for datastore due to errors in conversion
                pass

            parsed["datastores"][store] = datastore

        # Section "task_summary"
        # Format: "<worker_type>: <ok> <warning> <error> <unknown> <notmounted>"
        elif current_section == "task_summary":

            # Ignore line does not start with "<worker_type>:"
            if not line[0].endswith(":"):
                continue

            # Get worker type
            worker_type = line[0][:-1]

            # Get values
            metrics: Metrics = {}

            try:
                for idx, metric_spec in enumerate(proxmox_backup_server_metric_specs._METRIC_SPECS_TASK_SUMMARY):
                    metrics[metric_spec] = int(line[idx+1])

                # Add metrics
                parsed["task_summary"][worker_type] = metrics
            except (KeyError, TypeError, ValueError):
                # Ignore entry for task summary due to errors in conversion
                pass

        # Section "sync_jobs", "prune_jobs" / "verify_jobs"
        # Format sync: "<id>: <state> <last_run> <next_run> <sync_direction> <local> <remote> <max_depth>"
        # Format prune/verify: "<id>: <state> <last_run> <next_run> <local> <max_depth>"
        elif current_section in ["sync_jobs", "prune_jobs", "verify_jobs"]:

            # Ignore line does not start with "<id>:"
            if not line[0].endswith(":"):
                continue

            # Get id
            id = line[0][:-1]

            # Get values
            metrics: Metrics = {}
            job: Job = {}
            if current_section == "sync_jobs":
                # Sync job
                job["state"] = line[1]
                job["sync_direction"] = line[4]
                job["local"] = line[5]
                job["remote"] = line[6]
                job["max_depth"] = line[7] if line[7] == "Full" else int(line[7])
            else:
                # Prune job / Verify job
                job["state"] = line[1]
                job["local"] = line[4]
                job["max_depth"] = line[5] if line[5] == "Full" else int(line[5])

            for idx, metric_spec in enumerate(proxmox_backup_server_metric_specs._METRIC_SPECS_JOB):
                if proxmox_backup_server_metric_specs._METRIC_SPECS_JOB[metric_spec][1] == render.timespan:
                    # Create absolute difference of time
                    metrics[metric_spec] = abs(int(time.time())-int(line[idx+2]))
                else:
                    # Convert non-string metrics to integer
                    metrics[metric_spec] = int(line[idx+2])

            # Add metrics
            job["metrics"] = metrics

            # Add metrics
            parsed[current_section][id] = job

    return parsed


def discover_proxmox_backup_server(section: Section) -> DiscoveryResult:
    yield Service()


def check_proxmox_backup_server(section: Section) -> CheckResult:

    version = section.get("version")
    if version is not None:
        yield Result(state=State.OK, summary=f"Version: {version}")
    else:
        yield Result(state=State.UNKNOWN, summary="Version not found in agent output")


agent_section_proxmox_backup_server = AgentSection(
    name="proxmox_backup_server",
    parse_function=parse_proxmox_backup_server,
)


check_plugin_proxmox_backup_server = CheckPlugin(
    name="proxmox_backup_server",
    sections=["proxmox_backup_server"],
    service_name="Proxmox Backup Server",
    discovery_function=discover_proxmox_backup_server,
    check_function=check_proxmox_backup_server,
)
