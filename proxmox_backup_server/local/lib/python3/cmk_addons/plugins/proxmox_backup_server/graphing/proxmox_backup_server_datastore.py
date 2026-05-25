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
    AutoPrecision,
    Color,
    DecimalNotation,
    MaximumOf,
    Metric,
    SINotation,
    StrictPrecision,
    TimeNotation,
    Unit,
)
from cmk.graphing.v1.graphs import (
    Graph,
    MinimalRange
)
from cmk.graphing.v1.perfometers import (
    Closed,
    FocusRange,
    Perfometer,
)

metric_proxmox_backup_server_datastore_avail = Metric(
    name="proxmox_backup_server_datastore_avail",
    title=Title("Available space"),
    unit=Unit(SINotation('bytes'), AutoPrecision(2)),
    color=Color.PURPLE,
)

metric_proxmox_backup_server_datastore_used = Metric(
    name="proxmox_backup_server_datastore_used",
    title=Title("Used space"),
    unit=Unit(SINotation('bytes'), AutoPrecision(2)),
    color=Color.BLUE,
)

metric_proxmox_backup_server_datastore_total = Metric(
    name="proxmox_backup_server_datastore_total",
    title=Title("Total space"),
    unit=Unit(SINotation('bytes'), AutoPrecision(2)),
    color=Color.GREEN,
)

graph_proxmox_backup_server_datastore_combined = Graph(
    name="proxmox_backup_server_datastore_combined",
    title=Title("Size and used space"),
    minimal_range=MinimalRange(
        0,
        MaximumOf(
            "proxmox_backup_server_datastore_used",
            Color.GRAY,
        ),
    ),
    compound_lines=[
        "proxmox_backup_server_datastore_used",
        "proxmox_backup_server_datastore_avail",
    ],
)

metric_proxmox_backup_server_datastore_fill_level = Metric(
    name="proxmox_backup_server_datastore_filled",
    title=Title("Used Space %"),
    unit=Unit(DecimalNotation("%")),
    color=Color.LIGHT_CYAN,
)

metric_proxmox_backup_server_datastore_estimated_full_timespan = Metric(
    name="proxmox_backup_server_datastore_estimated_full_timespan",
    title=Title("Estimated full in"),
    unit=Unit(TimeNotation()),
    color=Color.LIGHT_BLUE,
)

metric_proxmox_backup_server_datastore_deduplication_factor = Metric(
    name="proxmox_backup_server_datastore_deduplication_factor",
    title=Title("Deduplication Factor"),
    unit=Unit(DecimalNotation("")),
    color=Color.GREEN,
)

metric_proxmox_backup_server_datastore_gc_endtime_timespan = Metric(
    name="proxmox_backup_server_datastore_gc_endtime_timespan",
    title=Title("Garbage Collection - Last Run before"),
    unit=Unit(TimeNotation()),
    color=Color.LIGHT_YELLOW,
)

metric_proxmox_backup_server_datastore_gc_duration = Metric(
    name="proxmox_backup_server_datastore_gc_duration",
    title=Title("Garbage Collection - Duration"),
    unit=Unit(TimeNotation()),
    color=Color.YELLOW,
)

metric_proxmox_backup_server_datastore_gc_removed_bytes = Metric(
    name="proxmox_backup_server_datastore_gc_removed_bytes",
    title=Title("Garbage Collection - Removed Data"),
    unit=Unit(SINotation('bytes'), AutoPrecision(2)),
    color=Color.RED,
)

metric_proxmox_backup_server_datastore_gc_pending_bytes = Metric(
    name="proxmox_backup_server_datastore_gc_pending_bytes",
    title=Title("Garbage Collection - Pending Data"),
    unit=Unit(SINotation('bytes'), AutoPrecision(2)),
    color=Color.LIGHT_RED,
)

metric_proxmox_backup_server_datastore_gc_disk_bytes = Metric(
    name="proxmox_backup_server_datastore_gc_disk_bytes",
    title=Title("On-Disk usage"),
    unit=Unit(SINotation('bytes'), AutoPrecision(2)),
    color=Color.CYAN,
)

metric_proxmox_backup_server_datastore_gc_index_data_bytes = Metric(
    name="proxmox_backup_server_datastore_gc_index_data_bytes",
    title=Title("Original data usage"),
    unit=Unit(SINotation('bytes'), AutoPrecision(2)),
    color=Color.LIGHT_CYAN,
)

perfometer_proxmox_backup_server_datastore = Perfometer(
    name="perfometer_proxmox_backup_server_datastore",
    focus_range=FocusRange(Closed(0), Closed(100)),
    segments=["proxmox_backup_server_datastore_filled"],
)
