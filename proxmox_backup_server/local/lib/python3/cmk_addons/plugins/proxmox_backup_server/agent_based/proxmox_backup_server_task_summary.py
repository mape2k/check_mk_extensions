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

from typing import Any, Dict, Mapping

from cmk.agent_based.v2 import (
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)

Section = Dict[str, Any]

_WORKER_TYPES_TASK_SUMMARY: Mapping[str, str] = {
    "backup": "Backups",
    "garbage_collection": "Garbage collection",
    "other": "Other",
    "prune": "Prunes",
    "sync": "Syncs",
    "tape_backup": "Tape Backup",
    "tape_restore": "Tape Restore",
    "verify": "Verify",
}

_CHECK_DEFAULT_PARAMETERS = {
    "ok":       ('no_levels', None),
    "warning":  ("fixed", (1, 10)),
    "error":    ("fixed", (1, 1)),
    "unknown":  ("fixed", (1, 1)),
}


def discover_proxmox_backup_server_task_summary(section: Section) -> DiscoveryResult:
    yield Service()


def check_proxmox_backup_server_task_summary(params: Dict[str, Any], section: Section) -> CheckResult:

    task_summary = (section.get("task_summary", {}))

    if not task_summary:
        yield Result(
            state=State.UNKNOWN,
            summary="Task Summary not found in agent output",
        )
        return

    yield Result(
        state=State.OK,
        summary=f"Tasks: {sum(int(item['ok'] + int(item["warning"]) + int(item["error"]) + int(item["unknown"])) for item in task_summary.values())}",
    )

    # Check metrics for every worker_type
    for worker_type in task_summary:

        # Convert dictionaries
        if isinstance(params.get(worker_type), dict):
            params_any: Any = params.get(worker_type)
            params_dict: dict = params_any

        for metric in proxmox_backup_server_metric_specs._METRIC_SPECS_TASK_SUMMARY:

            # Get metric specs
            label, render_func, notice_only, levels_lower, levels_upper = proxmox_backup_server_metric_specs._METRIC_SPECS_TASK_SUMMARY[metric]

            # Metric missed in agent output
            if metric not in task_summary[worker_type]:
                yield Result(
                    state=State.UNKNOWN,
                    notice=f"Counter '{metric}' missed for {_WORKER_TYPES_TASK_SUMMARY[worker_type]}",
                )
                continue

            # Metric with single or no levels
            yield from check_levels(
                task_summary[worker_type][metric],
                metric_name=f"proxmox_backup_server_task_summary_{worker_type}_{metric}",
                label=f"{_WORKER_TYPES_TASK_SUMMARY[worker_type]} - {label}",
                levels_lower=params_dict[metric] if (levels_lower and params_dict[metric] != ('no_levels', None)) else None,  # pyright: ignore[reportPossiblyUnboundVariable]
                levels_upper=params_dict[metric] if (levels_upper and params_dict[metric] != ('no_levels', None)) else None,  # pyright: ignore[reportPossiblyUnboundVariable]
                render_func=render_func,
                notice_only=notice_only,
                boundaries=(0, None),
            )


check_plugin_proxmox_backup_server_task_summary = CheckPlugin(
    name="proxmox_backup_server_task_summary",
    sections=["proxmox_backup_server"],
    service_name="Proxmox Backup Server Task Summary",
    discovery_function=discover_proxmox_backup_server_task_summary,
    check_function=check_proxmox_backup_server_task_summary,
    check_ruleset_name="proxmox_backup_server_task_summary",
    check_default_parameters={
        "backup": _CHECK_DEFAULT_PARAMETERS,
        "garbage_collection": _CHECK_DEFAULT_PARAMETERS,
        "other": _CHECK_DEFAULT_PARAMETERS,
        "prune": _CHECK_DEFAULT_PARAMETERS,
        "sync": _CHECK_DEFAULT_PARAMETERS,
        "tape_backup": _CHECK_DEFAULT_PARAMETERS,
        "tape_restore": _CHECK_DEFAULT_PARAMETERS,
        "verify": _CHECK_DEFAULT_PARAMETERS,
    }
)
