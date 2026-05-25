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


def parse_proxmox_backup_server(string_table: StringTable) -> Section:

    parsed: Section = {"version": None, "datastores": {}}
    current_section = None

    for line in string_table:
        if not line:
            continue

        # Line "version: x.y"
        if line[0] == "version:":
            parsed["version"] = line[1]
            continue

        # Detect start of section "datastores"
        if line[0] == "[datastores]":
            current_section = "datastores"
            continue

        # Section "datastores"
        # Format: "<store>: <mount_status> <backend_type> <avail> <used> <total> <filled>
        #          <estimated-full-date> <gc_state> <gc_endtime> <gc_duration>
        #          <gc_removed_bytes> <gc_pending_bytes> <gc_disk_bytes>
        #          <gc_index_data_bytes>"
        if current_section == "datastores":

            # Ignore line does not start with "<store>:"
            if not str(line[0]).endswith(":"):
                continue

            # Get store name
            store = str(line[0])[:-1]

            # Get values
            metrics: Metrics = {}
            datastore: Datastore = {
                "mount_status": line[1],
                "backend_type": line[2],
            }

            # Parse metrics from specs for mounted and nonremoval
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
                            # [metric_spec] = int(line[idx+3])

                # Calculate deduplication factor
                metrics["deduplication_factor"] = round(metrics["gc_index_data_bytes"] / int(metrics["gc_disk_bytes"]), 2)

                # Calculate timespan from Garbage Collection Endtime
                # (done on server to prevent overdue caused by cached agent results)
                metrics["gc_endtime_timespan"] = int(time.time())-metrics["gc_endtime_timespan"]

                # Add metrics
                datastore["metrics"] = metrics

            parsed["datastores"][store] = datastore

    return parsed


def discover_proxmox_backup_server(section: Section) -> DiscoveryResult:
    yield Service()


def check_proxmox_backup_server(section: Section) -> CheckResult:

    version = section.get('version')
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
