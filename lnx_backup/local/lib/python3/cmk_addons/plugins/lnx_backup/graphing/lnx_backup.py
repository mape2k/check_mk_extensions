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
    Metric,
    SINotation,
    StrictPrecision,
    TimeNotation,
    Unit,
)
from cmk.graphing.v1.perfometers import (
    Closed,
    FocusRange,
    Open,
    Perfometer,
)

UNIT_BYTES = Unit(SINotation('bytes'), AutoPrecision(2))
UNIT_COUNTER = Unit(DecimalNotation(''), StrictPrecision(0))

metric_lnx_backup_age = Metric(
    name="lnx_backup_age",
    title=Title("Age"),
    unit=Unit(TimeNotation()),
    color=Color.ORANGE,
)

metric_lnx_backup_duration = Metric(
    name="lnx_backup_duration",
    title=Title("Duration"),
    unit=Unit(TimeNotation()),
    color=Color.LIGHT_ORANGE,
)

metric_lnx_backup_errors = Metric(
    name="lnx_backup_errors",
    title=Title("Errors"),
    unit=UNIT_COUNTER,
    color=Color.DARK_RED,
)

metric_lnx_backup_backup_size = Metric(
    name="lnx_backup_backup_size",
    title=Title("Backup Size"),
    unit=UNIT_BYTES,
    color=Color.YELLOW,
)

metric_lnx_backup_new_files = Metric(
    name="lnx_backup_new_files",
    title=Title("New files"),
    unit=UNIT_COUNTER,
    color=Color.BLUE,
)

metric_lnx_backup_new_filesize = Metric(
    name="lnx_backup_new_filesize",
    title=Title("New files - Size"),
    unit=UNIT_BYTES,
    color=Color.LIGHT_BLUE,
)

metric_lnx_backup_changed_files = Metric(
    name="lnx_backup_changed_files",
    title=Title("Changed files"),
    unit=UNIT_COUNTER,
    color=Color.GREEN,
)

metric_lnx_backup_changed_filesize = Metric(
    name="lnx_backup_changed_filesize",
    title=Title("Changed files - Size"),
    unit=UNIT_BYTES,
    color=Color.LIGHT_GREEN,
)

metric_lnx_backup_deleted_files = Metric(
    name="lnx_backup_deleted_files",
    title=Title("Deleted files"),
    unit=UNIT_COUNTER,
    color=Color.LIGHT_RED,
)

metric_lnx_backup_source_files = Metric(
    name="lnx_backup_source_files",
    title=Title("Files"),
    unit=UNIT_COUNTER,
    color=Color.CYAN,
)

metric_lnx_backup_source_filesize = Metric(
    name="lnx_backup_source_filesize",
    title=Title("Files - Size"),
    unit=UNIT_BYTES,
    color=Color.LIGHT_CYAN,
)

perfometer_lnx_backup = Perfometer(
    name="lnx_backup",
    focus_range=FocusRange(Closed(0), Open(240)),
    segments=["lnx_backup_duration"],
)
