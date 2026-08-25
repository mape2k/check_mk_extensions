#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) 2026 Marcel Pennewiss <opensource@pennewiss.de>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License. This program
# is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details. You should have received a copy of the GNU
# General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA.

# Example Agent Output
# <<<gentoo_portage>>>
# [sync]
# 1777071667 1
# [updates]
# NEWSLOT dev-db/mariadb:11.8 10.6.17 11.8.3-r2 gentoo
# UPDATE dev-db/mariadb-connector-c 3.2.7 3.4.7 gentoo
# UPDATE dev-lang/perl 5.40.0 5.42.0-r1 gentoo
# NEWSLOT dev-lang/php:8.3 8.2.24 8.3.29 gentoo
# UPDATE sys-libs/db:5.3 5.3.28-r10 5.3.28-r11 gentoo
# [glsa]
# 202505-01 high sys-libs/pam 1.6.1 1.7.2
# 202506-07 high dev-lang/python:3.12 3.12.8 3.12.12
# 202506-07 high dev-lang/python:3.13 3.13.1 3.13.11
# 202508-01 high sys-libs/pam 1.6.1 1.7.2
# 202601-02 high app-editors/vim 9.1.0366 9.1.1652-r2
# 202601-02 high app-editors/vim-core 9.1.0366-r1 9.1.1652-r3

import time

from typing import Any, Dict, TypedDict
from enum import StrEnum

from cmk.agent_based.v2 import (
    render,
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
    StringTable,
)

# Section = Dict[str, Any]
Metrics = Dict[str, Any]


class UpdateType(StrEnum):
    UPDATE = "UPDATE"
    NEWSLOT = "NEWSLOT"


class GLSAImpactType(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class Sync(TypedDict, total=False):
    timestamp: int
    exit_code: int
    metrics: Dict[str, Any]


class UpdateEntry(TypedDict, total=True):
    type: UpdateType
    cp: str
    version_old: str
    version_new: str
    repository: str


class Updates(TypedDict, total=False):
    update: list[UpdateEntry]
    newslot: list[UpdateEntry]
    metrics: Metrics


class GLSAEntry(TypedDict, total=True):
    id: str
    impact_type: GLSAImpactType
    cp: str
    version_installed: str
    version_fixed: str


class GLSA(TypedDict, total=False):
    glsa: list[GLSAEntry]
    metrics: Metrics


class Section(TypedDict, total=False):
    sync: Sync | None
    updates: Updates
    glsa: GLSA


def parse_gentoo_portage(string_table: StringTable) -> Section:

    updates: Updates = {"update": [], "newslot": []}
    glsa: GLSA = {"glsa": []}

    parsed: Section = {
        "sync": None,
        "updates": updates,
        "glsa": glsa,
    }
    current_section = None

    for line in string_table:
        if not line:
            continue

        # Detect sections
        if line[0].startswith("[") and line[0].endswith("]"):
            current_section = line[0][1:-1]
            continue

        # Section "sync"
        # Format: "<tree-epoch> <exit_code>
        if current_section == "sync":

            metrics: Metrics = {}
            sync: Sync = {}

            try:
                # Get values
                sync["timestamp"] = int(line[0])
                sync["exit_code"] = int(line[1])
                if sync["timestamp"] > 0:
                    # Create absolute difference of time
                    metrics["timestamp_timespan"] = int(time.time())-sync["timestamp"]

                # Add metrics
                sync["metrics"] = metrics
                parsed["sync"] = sync

            except (KeyError, TypeError, ValueError, IndexError):
                # Ignore entry for sync due to errors in conversion
                pass

        # Section "updates"
        # Format: <UpdateType> <cp> <version_old> <version_new> <repository>
        elif current_section == "updates":

            try:
                # Get values
                update_entry: UpdateEntry = {
                    "type": UpdateType(line[0]),
                    "cp": line[1],
                    "version_old": line[2],
                    "version_new": line[3],
                    "repository": line[4],
                }

                # Add update to list
                match update_entry["type"]:
                    case UpdateType.UPDATE:
                        updates["update"].append(update_entry)
                    case UpdateType.NEWSLOT:
                        updates["newslot"].append(update_entry)

            except (ValueError, IndexError):
                # Ignore updates due to errors in conversion
                pass

        # Section "glsa"
        # Format <id> <GLSAImpacttype> <cp> <version_installed> <version_fixed>
        elif current_section == "glsa":

            try:
                # Get values
                glsa_entry: GLSAEntry = {
                    "id": line[0],
                    "impact_type": GLSAImpactType(line[1]),
                    "cp": line[2],
                    "version_installed": line[3],
                    "version_fixed": line[4],
                }

                # Add glsa entry to list
                glsa["glsa"].append(glsa_entry)

            except (ValueError, IndexError):
                # Ignore glsa entries due to errors in conversion
                pass

    # Count entries as metrics
    metrics_updates: Metrics = {}
    for enum in UpdateType:
        metrics_updates[enum.lower()] = len(updates[enum.lower()])
    parsed["updates"]["metrics"] = metrics_updates

    metrics_glsa: Metrics = {
        "entries": len(glsa["glsa"]),
        "packages": len({glsa_entry["cp"] for glsa_entry in glsa["glsa"]}),
        **{f"impact_{glsa_impact_type}": sum(1 for glsa_entry in glsa["glsa"] if glsa_entry["impact_type"] is glsa_impact_type)
           for glsa_impact_type in GLSAImpactType}
    }
    parsed["glsa"]["metrics"] = metrics_glsa

    return parsed


def discover_gentoo_portage(section: Section) -> DiscoveryResult:
    yield Service()


def _format_cp(entry: UpdateEntry | GLSAEntry, default_repository: str | None) -> str:
    """Format cp with repository"""
    if default_repository is None or entry.get("repository", "") == default_repository:
        return entry["cp"]
    return f"{entry['cp']}::{entry.get("repository", "")}"


def _check_gentoo_portage_sync(params: Dict[str, Any], section: Section) -> CheckResult:

    sync = section.get("sync", {})

    # No data in agent output
    if not sync:
        yield Result(
            state=State.UNKNOWN,
            summary="Sync information of portage not found in agent output",
        )
        return

    # No metrics found
    if "metrics" not in sync:
        yield Result(
            state=State.UNKNOWN,
            summary="Sync metrics missing",
        )
        return

    # Check timestamp of portage
    sync_status = State.OK
    if sync["metrics"]["timestamp_timespan"] >= params["portage"]["timestamp_timespan"][1][1]:
        sync_status = State.CRIT
    elif sync["metrics"]["timestamp_timespan"] >= params["portage"]["timestamp_timespan"][1][0]:
        sync_status = State.WARN

    sync_notice = (
        f"Portage timestamp: {render.datetime(sync.get("timestamp", 0))}"
    )

    if sync_status in [State.WARN, State.CRIT]:
        sync_notice = f"{sync_notice} (warn/crit at {render.timespan(params["portage"]["timestamp_timespan"][1][0])}/{render.timespan(params["portage"]["timestamp_timespan"][1][1])})"
        sync_notice += "(!)" if sync_status == State.WARN else "(!!)"

    yield Result(state=sync_status, notice=sync_notice)

    # Check sync exit code
    if not params["portage"]["ignore_exit_code"]:
        exit_code = sync.get("exit_code", -1)
        # Ignore exit code 0 (ok) and -1 (disabled sync)
        if exit_code not in [0, -1]:
            yield Result(state=State.UNKNOWN if exit_code < -1 else State.WARN, notice=f"Last exit code for sync: {exit_code}")


def _check_gentoo_portage_updates(params: Dict[str, Any], section: Section) -> CheckResult:

    updates = section.get("updates", {})

    # No data in agent output
    if not updates:
        yield Result(
            state=State.UNKNOWN,
            summary="Update information not found in agent output",
        )
        return

    # No metrics found
    if "metrics" not in updates:
        yield Result(
            state=State.UNKNOWN,
            summary="Update metrics missing",
        )
        return

    # Create package lists if configured
    cps_update = ""
    cps_newslot = ""
    if params["updates"]["add_package_names"]:
        cps_update = f" ({", ".join(sorted((_format_cp(e, params["updates"]["default_repository"]) for e in updates.get("update", [])), key=str.lower))})"
        cps_newslot = f" ({", ".join(sorted((_format_cp(e, params["updates"]["default_repository"]) for e in updates.get("newslot", [])), key=str.lower))})"

    # Check for updates of installed packages
    if updates["metrics"]["update"] > 0:
        yield Result(
            state=State(params["updates"]["state_normal_updates"]),
            summary=f"{updates["metrics"]["update"]} normal updates{cps_update}"
        )

    # Check for updates in new slotss of installed packages
    if updates["metrics"]["newslot"] > 0:
        yield Result(
            state=State(params["updates"]["state_newslot_updates"]),
            summary=f"{updates["metrics"]["newslot"]} updates in new slots{cps_newslot}"
        )

    # Add metrics for graphs
    for enum in UpdateType:
        yield Metric(
            name=f"gentoo_portage_updates_{enum.lower()}",
            value=updates["metrics"][enum.lower()],
        )

    # Default state without any updates
    if updates["metrics"]["update"] == 0 and updates["metrics"]["newslot"] == 0:
        yield Result(state=State.OK, summary="No updates pending for installation")


def _check_gentoo_portage_glsa(params: Dict[str, Any], section: Section) -> CheckResult:

    glsa = section.get("glsa", {})

    # No data in agent output
    if not glsa:
        yield Result(
            state=State.UNKNOWN,
            summary="GLSA information not found in agent output",
        )
        return

    # No metrics found
    if "metrics" not in glsa:
        yield Result(
            state=State.UNKNOWN,
            summary="GLSA metrics missing",
        )
        return

    # Create package lists if configured
    cps = ""
    if params["glsa"]["add_package_names"]:
        cps = f" ({", ".join(sorted((_format_cp(e, None) for e in glsa.get("glsa", [])), key=str.lower))})"

    # Check for glsa entries of installed packages
    if glsa["metrics"]["entries"] > 0:
        # Get worst state for all impact types
        state_impact_type = State.OK
        for impact_type in GLSAImpactType:
            if glsa["metrics"][f"impact_{impact_type}"] > 0:
                state_impact_type = State.worst(state_impact_type, State(params["glsa"][f"state_impact_{impact_type}"]))

        yield Result(
            state=state_impact_type,
            summary=f"{glsa["metrics"]["entries"]} GLSA for {glsa["metrics"]["packages"]} package(s){cps}"
        )
    else:
        yield Result(state=State.OK, summary="No GLSA pending")

    # Add metrics for graphs
    for enum in GLSAImpactType:
        yield Metric(
            name=f"gentoo_portage_glsa_impact_{enum.lower()}",
            value=glsa["metrics"][f"impact_{enum.lower()}"],
        )

    yield Metric(
        name="gentoo_portage_glsa_packages",
        value=glsa["metrics"]["packages"],
    )


def check_gentoo_portage(params: Dict[str, Any], section: Section) -> CheckResult:

    # Check portage sync state
    yield from _check_gentoo_portage_sync(params=params, section=section)

    # Check updates
    yield from _check_gentoo_portage_updates(params=params, section=section)

    # Check glsa
    yield from _check_gentoo_portage_glsa(params=params, section=section)


agent_section_gentoo_portage = AgentSection(
    name="gentoo_portage",
    parse_function=parse_gentoo_portage,
)


check_plugin_gentoo_portage = CheckPlugin(
    name="gentoo_portage",
    sections=["gentoo_portage"],
    service_name="Gentoo Portage Updates",
    discovery_function=discover_gentoo_portage,
    check_function=check_gentoo_portage,
    check_default_parameters={
        "portage": {
            "timestamp_timespan": ("fixed", (24*60*60, 48*60*60)),
            "ignore_exit_code": (False)
        },
        "updates": {
            "state_normal_updates": (int(State.WARN)),
            "state_newslot_updates": (int(State.OK)),
            "add_package_names": (False),
            "default_repository": ("gentoo")
        },
        "glsa": {
            "state_impact_low": (int(State.WARN)),
            "state_impact_normal": (int(State.WARN)),
            "state_impact_high": (int(State.CRIT)),
            "add_package_names": (True),
        }
    },
    check_ruleset_name="gentoo_portage",
)
