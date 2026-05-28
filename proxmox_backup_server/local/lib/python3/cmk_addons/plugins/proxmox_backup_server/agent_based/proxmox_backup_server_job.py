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
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
)

Section = Dict[str, Any]


def _discover_proxmox_backup_server_job(jobtype: str, section: Section) -> DiscoveryResult:

    for job in section.get(f"{jobtype}_jobs", {}):
        yield Service(item=job)


def _check_proxmox_backup_server_job(jobtype: str, item: str, params: Dict[str, Any], section: Section) -> CheckResult:

    job = (section.get(f"{jobtype}_jobs", {})).get(item, {})

    # No data in agent output
    if not job:
        yield Result(
            state=State.UNKNOWN,
            summary=f"{jobtype.capitalize()} Job '{item}' not found in agent output",
        )
        return

    # Section "sync_job"
    # Format: "<id>: <state> <last_run> <next_run> <local> <max_depth>"
    if jobtype == "sync":
        yield Result(
            state=State.OK,
            summary=f"{job.get("sync_direction").upper()} {job.get("local", "Unknown")} {"<-" if job.get("sync_direction") == "pull" else "->"} {job.get("remote", "Unknown")} (Max depth: {job.get("max_depth", "Unknown")})",
        )
    else:
        yield Result(
            state=State.OK,
            summary=f"Datastore/Namespace {job.get("local", "Unknown")} (Max depth: {job.get("max_depth", "Unknown")})",
        )

    # Check states ERROR, NOTMOUNTED, OK, RUNNING, PENDING, UNKNOWN
    job_state = job.get("state", "UNKOWN")
    state = State.UNKNOWN
    summary = "Job state unknown"
    if job_state == "ERROR":
        state = State.CRIT
        summary = "Job failed"
    elif job_state == "NOTMOUNTED":
        state = State.OK
        summary = "Datastore not mounted"
    elif job_state == "OK":
        state = State.OK
        summary = "Job successfull"
    elif job_state == "RUNNING":
        state = State.OK
        summary = "Job running"
    elif job_state == "PENDING":
        state = State.OK
        summary = "Job pending"

    yield Result(
        state=state,
        summary=summary
    )

    # No metrics found
    if "metrics" not in job:
        yield Result(
            state=State.UNKNOWN,
            summary="Got incomplete information for this job",
        )
        return

    for metric in proxmox_backup_server_metric_specs._METRIC_SPECS_JOB:

        # Get metric specs
        label, render_func, notice_only, levels_lower, levels_upper = proxmox_backup_server_metric_specs._METRIC_SPECS_JOB[metric]

        # Metrics maybe zero in states NOTMOUNTED, RUNNING and PENDING
        # Do not check these metrics to prevent false positive
        if job_state not in ["NOTMOUNTED", "RUNNING", "PENDING"]:
            # Metric with single or no levels
            yield from check_levels(
                job["metrics"][metric],
                metric_name=f"proxmox_backup_server_{jobtype}_job_{metric}",
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
                name=f"proxmox_backup_server_{jobtype}_job_{metric}",
                value=job["metrics"][metric],
            )
