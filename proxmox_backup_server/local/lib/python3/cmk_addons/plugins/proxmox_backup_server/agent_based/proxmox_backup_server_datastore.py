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

# For example Agent Output see proxmox_backup_server.py

# Import _METRIC_SPECS_*
from . import proxmox_backup_server_metric_specs

from typing import Any, Dict

from cmk.agent_based.v2 import (
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    render,
    Result,
    Service,
    State,
)

Section = Dict[str, Any]


def discover_proxmox_backup_server_datastore(section: Section) -> DiscoveryResult:
    for store in section.get("datastores", {}):
        yield Service(item=store)


def check_proxmox_backup_server_datastore(item: str, params: Dict[str, Any], section: Section) -> CheckResult:

    datastore = (section.get("datastores", {})).get(item, {})

    # No data in agent output
    if not datastore:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Datastore '{item}' not found in agent output",
        )
        return

    # Section "datastores"
    # Format: "<store>: <mount_status> <backend_type> <avail> <used> <total> <filled>
    #          <estimated-full-date> <gc_state> <gc_endtime> <gc_duration>
    #          <gc_removed_bytes> <gc_pending_bytes> <gc_disk_bytes>
    #          <gc_index_data_bytes>"
    yield Result(
        state=State.OK,
        notice="Backend: %s" % datastore.get("backend_type"),
    )
    yield Result(
        state=State.OK,
        notice="Mount status: %s" % datastore.get("mount_status"),
    )

    # No metrics found
    if "metrics" not in datastore:
        if datastore["mount_status"] == "notmounted":
            yield Result(
                state=State.OK,
                summary="Datastore not mounted",
            )
        else:
            yield Result(
                state=State.UNKNOWN,
                summary="Got incomplete information for this datastore",
            )
        return

    for metric in proxmox_backup_server_metric_specs._METRIC_SPECS_DATASTORES:

        # Get metric specs
        _, label, render_func, notice_only, levels_lower, levels_upper = proxmox_backup_server_metric_specs._METRIC_SPECS_DATASTORES[metric]

        # Convert dictionaries
        if isinstance(params.get(metric), dict):
            params_any: Any = params.get(metric)
            params_dict: dict = params_any
        elif isinstance(params.get(metric), tuple):
            params_any: Any = params.get(metric)
            params_tuple: tuple = params_any

        # Ignore metric "estimated_full_timespan" with value -1 (missing)
        if metric == "estimated_full_timespan" and datastore["metrics"][metric] == -1:
            render_func = None
            levels_lower = False
            levels_upper = False

        if metric == "gc_state":
            # Check Garbage Collection state
            yield Result(
                state=State.OK if (datastore["metrics"][metric] == "OK") else State.CRIT,
                notice="GC State: %s" % datastore["metrics"][metric],
            )

        elif metric == "filled":
            # Handle filled stated of datastore like df
            yield Metric(
                name=f"proxmox_backup_server_datastore_{metric}",
                value=datastore["metrics"][metric],
                levels=params_tuple[1],  # pyright: ignore[reportPossiblyUnboundVariable]
                boundaries=(0.0, 100.0)
            )

            status = (
                State.CRIT if datastore["metrics"]["filled"] >= params_tuple[1][1] else State.WARN if datastore["metrics"]["filled"] >= params_tuple[1][0] else State.OK  # pyright: ignore[reportPossiblyUnboundVariable]
            )

            summary = (
                f"Used: {render.percent(datastore["metrics"]["filled"])} "
                f"- {render.bytes(datastore["metrics"]["used"])} of {render.bytes(datastore["metrics"]["total"])}"
            )

            if status in [State.WARN, State.CRIT]:
                summary = f"{summary} (warn/crit at {render.percent(params_tuple[1][0])}/{render.percent(params_tuple[1][1])})"  # pyright: ignore[reportPossiblyUnboundVariable]

            yield Result(state=status, summary=summary)

        else:

            if levels_lower and levels_upper:
                # Metric with both levels
                yield from check_levels(
                    datastore["metrics"][metric],
                    metric_name=f"proxmox_backup_server_datastore_{metric}",
                    label=label,
                    levels_lower=params_dict["lower"] if params_dict["lower"] != ("no_levels", None) else None,  # pyright: ignore[reportPossiblyUnboundVariable]
                    levels_upper=params_dict["upper"] if params_dict["upper"] != ("no_levels", None) else None,  # pyright: ignore[reportPossiblyUnboundVariable]
                    render_func=render_func,
                    notice_only=notice_only,
                    boundaries=(0, None),
                )
            elif levels_lower or levels_upper:
                # Metric with single or no levels
                yield from check_levels(
                    datastore["metrics"][metric],
                    metric_name=f"proxmox_backup_server_datastore_{metric}",
                    label=label,
                    levels_lower=params.get(metric) if (levels_lower and params.get(metric) != ("no_levels", None)) else None,
                    levels_upper=params.get(metric) if (levels_upper and params.get(metric) != ("no_levels", None)) else None,
                    render_func=render_func,
                    notice_only=notice_only,
                    boundaries=(0, None),
                )
            else:
                # Metric without levels
                yield Metric(
                    name=f"proxmox_backup_server_datastore_{metric}",
                    value=datastore["metrics"][metric],
                )


check_plugin_proxmox_backup_server_datastore = CheckPlugin(
    name="proxmox_backup_server_datastore",
    sections=["proxmox_backup_server"],
    service_name="Proxmox Backup Server Datastore %s",
    discovery_function=discover_proxmox_backup_server_datastore,
    check_function=check_proxmox_backup_server_datastore,
    check_ruleset_name="proxmox_backup_server_datastore",
    check_default_parameters={
        "filled":                   ("fixed", (80.0, 90.0)),
        "estimated_full_timespan":  ("fixed", (48*60*60, 24*60*60)),
        "gc_endtime_timespan":      ("fixed", (26*60*60, 50*60*60)),
        "gc_duration":              ("no_levels", None),
        "gc_removed_bytes":         ("no_levels", None),
        "gc_pending_bytes":         ("no_levels", None),
        "gc_disk_bytes":            ("no_levels", None),
        "gc_index_data_bytes":      ("no_levels", None),
        "deduplication_factor":     {"lower": ("no_levels", None), "upper": ("no_levels", None)},
    },
)
