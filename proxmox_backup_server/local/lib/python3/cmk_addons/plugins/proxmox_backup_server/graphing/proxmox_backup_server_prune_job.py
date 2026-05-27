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


from cmk.graphing.v1 import Title
from cmk.graphing.v1.metrics import (
    Color,
    Metric,
    TimeNotation,
    Unit,
)

metric_proxmox_backup_server_prune_job_last_run = Metric(
    name="proxmox_backup_server_prune_job_last_run",
    title=Title("Last run"),
    unit=Unit(TimeNotation()),
    color=Color.GREEN,
)

metric_proxmox_backup_server_prune_job_next_run = Metric(
    name="proxmox_backup_server_prune_job_next_run",
    title=Title("Next run"),
    unit=Unit(TimeNotation()),
    color=Color.YELLOW,
)
