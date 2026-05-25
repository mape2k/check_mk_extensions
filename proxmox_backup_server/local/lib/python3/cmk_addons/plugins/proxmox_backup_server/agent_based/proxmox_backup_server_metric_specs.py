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

from typing import Callable, Mapping, Tuple

from cmk.agent_based.v2 import (
    render,
)


# Metric specs for datastores
_METRIC_SPECS_DATASTORES: Mapping[str, Tuple[bool, str, Callable, bool, bool, bool]] = {
    # 'metric': (parse, 'Metric Name', renderer, notice_only, Levels are lower levels, Levels are upper levels)
    'avail': (True, 'Available', render.bytes, True, False, False),
    'used': (True, 'Used', render.bytes, True, False, False),
    'total': (True, 'Total', render.bytes, True, False, False),
    'filled': (True, 'Used', render.percent, False, False, True),
    'estimated_full_timespan': (True, 'Estimated full in', render.timespan, True, True, False),
    'gc_state': (True, 'GC State', str, True, False, False),
    'gc_endtime_timespan': (True, 'GC Last Run before', render.timespan, True, False, True),
    'gc_duration': (True, 'GC Duration', render.timespan, True, False, True),
    'gc_removed_bytes': (True, 'GC Removed Data', render.bytes, True, False, True),
    'gc_pending_bytes': (True, 'GC Pending Data', render.bytes, True, False, True),
    'gc_disk_bytes': (True, 'On-Disk usage', render.bytes, True, False, True),
    'gc_index_data_bytes': (True, 'Original data usage', render.bytes, True, False, True),
    # Non-parsed values must be at the end
    'deduplication_factor': (False, 'Deduplication Factor', float, False, True, True),
}
