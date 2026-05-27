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

# Import job functions for discovery and check
from . import proxmox_backup_server_job

from typing import Any, Dict

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
)

Section = Dict[str, Any]


def discover_proxmox_backup_server_prune_job(section: Section) -> DiscoveryResult:
    yield from proxmox_backup_server_job._discover_proxmox_backup_server_job("prune", section)


def check_proxmox_backup_server_prune_job(item: str, params: Dict[str, Any], section: Section) -> CheckResult:
    yield from proxmox_backup_server_job._check_proxmox_backup_server_job("prune", item, params, section)


check_plugin_proxmox_backup_server_job = CheckPlugin(
    name="proxmox_backup_server_prune_job",
    sections=["proxmox_backup_server"],
    service_name="Proxmox Backup Server Prune Job %s",
    discovery_function=discover_proxmox_backup_server_prune_job,
    check_function=check_proxmox_backup_server_prune_job,
    check_ruleset_name="proxmox_backup_server_prune_job",
    check_default_parameters={
        "last_run": ("fixed", (26*60*60, 50*60*60)),
        "next_run": ("fixed", (26*60*60, 50*60*60)),
    },
)
