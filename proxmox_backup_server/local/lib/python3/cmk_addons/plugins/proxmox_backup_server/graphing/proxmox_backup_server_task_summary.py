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
    DecimalNotation,
    Metric,
    StrictPrecision,
    Unit,
)

UNIT_COUNTER = Unit(DecimalNotation(""), StrictPrecision(0))

metric_proxmox_backup_server_task_summary_backup_ok = Metric(
    name="proxmox_backup_server_task_summary_backup_ok",
    title=Title("Backups - Tasks OK"),
    unit=UNIT_COUNTER,
    color=Color.GREEN,
)

metric_proxmox_backup_server_task_summary_backup_warning = Metric(
    name="proxmox_backup_server_task_summary_backup_warning",
    title=Title("Backups - Warnings"),
    unit=UNIT_COUNTER,
    color=Color.YELLOW,
)

metric_proxmox_backup_server_task_summary_backup_error = Metric(
    name="proxmox_backup_server_task_summary_backup_error",
    title=Title("Backups - Errors"),
    unit=UNIT_COUNTER,
    color=Color.RED,
)

metric_proxmox_backup_server_task_summary_backup_unknown = Metric(
    name="proxmox_backup_server_task_summary_backup_unknown",
    title=Title("Backups - Tasks Unknown"),
    unit=UNIT_COUNTER,
    color=Color.LIGHT_GRAY,
)

metric_proxmox_backup_server_task_summary_garbage_collection_ok = Metric(
    name="proxmox_backup_server_task_summary_garbage_collection_ok",
    title=Title("Garbage collection - Tasks OK"),
    unit=UNIT_COUNTER,
    color=Color.GREEN,
)

metric_proxmox_backup_server_task_summary_garbage_collection_warning = Metric(
    name="proxmox_backup_server_task_summary_garbage_collection_warning",
    title=Title("Garbage collection - Warnings"),
    unit=UNIT_COUNTER,
    color=Color.YELLOW,
)

metric_proxmox_backup_server_task_summary_garbage_collection_error = Metric(
    name="proxmox_backup_server_task_summary_garbage_collection_error",
    title=Title("Garbage collection - Errors"),
    unit=UNIT_COUNTER,
    color=Color.RED,
)

metric_proxmox_backup_server_task_summary_garbage_collection_unknown = Metric(
    name="proxmox_backup_server_task_summary_garbage_collection_unknown",
    title=Title("Garbage collection - Tasks Unknown"),
    unit=UNIT_COUNTER,
    color=Color.LIGHT_GRAY,
)

metric_proxmox_backup_server_task_summary_other_ok = Metric(
    name="proxmox_backup_server_task_summary_other_ok",
    title=Title("Other - Tasks OK"),
    unit=UNIT_COUNTER,
    color=Color.GREEN,
)

metric_proxmox_backup_server_task_summary_other_warning = Metric(
    name="proxmox_backup_server_task_summary_other_warning",
    title=Title("Other - Warnings"),
    unit=UNIT_COUNTER,
    color=Color.YELLOW,
)

metric_proxmox_backup_server_task_summary_other_error = Metric(
    name="proxmox_backup_server_task_summary_other_error",
    title=Title("Other - Errors"),
    unit=UNIT_COUNTER,
    color=Color.RED,
)

metric_proxmox_backup_server_task_summary_other_unknown = Metric(
    name="proxmox_backup_server_task_summary_other_unknown",
    title=Title("Other - Tasks Unknown"),
    unit=UNIT_COUNTER,
    color=Color.LIGHT_GRAY,
)

metric_proxmox_backup_server_task_summary_prune_ok = Metric(
    name="proxmox_backup_server_task_summary_prune_ok",
    title=Title("Prunes - Tasks OK"),
    unit=UNIT_COUNTER,
    color=Color.GREEN,
)

metric_proxmox_backup_server_task_summary_prune_warning = Metric(
    name="proxmox_backup_server_task_summary_prune_warning",
    title=Title("Prunes - Warnings"),
    unit=UNIT_COUNTER,
    color=Color.YELLOW,
)

metric_proxmox_backup_server_task_summary_prune_error = Metric(
    name="proxmox_backup_server_task_summary_prune_error",
    title=Title("Prunes - Errors"),
    unit=UNIT_COUNTER,
    color=Color.RED,
)

metric_proxmox_backup_server_task_summary_prune_unknown = Metric(
    name="proxmox_backup_server_task_summary_prune_unknown",
    title=Title("Prunes - Tasks Unknown"),
    unit=UNIT_COUNTER,
    color=Color.LIGHT_GRAY,
)

metric_proxmox_backup_server_task_summary_sync_ok = Metric(
    name="proxmox_backup_server_task_summary_sync_ok",
    title=Title("Syncs - Tasks OK"),
    unit=UNIT_COUNTER,
    color=Color.GREEN,
)

metric_proxmox_backup_server_task_summary_sync_warning = Metric(
    name="proxmox_backup_server_task_summary_sync_warning",
    title=Title("Syncs - Warnings"),
    unit=UNIT_COUNTER,
    color=Color.YELLOW,
)

metric_proxmox_backup_server_task_summary_sync_error = Metric(
    name="proxmox_backup_server_task_summary_sync_error",
    title=Title("Syncs - Errors"),
    unit=UNIT_COUNTER,
    color=Color.RED,
)

metric_proxmox_backup_server_task_summary_sync_unknown = Metric(
    name="proxmox_backup_server_task_summary_sync_unknown",
    title=Title("Syncs - Tasks Unknown"),
    unit=UNIT_COUNTER,
    color=Color.LIGHT_GRAY,
)

metric_proxmox_backup_server_task_summary_tape_backup_ok = Metric(
    name="proxmox_backup_server_task_summary_tape_backup_ok",
    title=Title("Tape-Backup - Tasks OK"),
    unit=UNIT_COUNTER,
    color=Color.GREEN,
)

metric_proxmox_backup_server_task_summary_tape_backup_warning = Metric(
    name="proxmox_backup_server_task_summary_tape_backup_warning",
    title=Title("Tape-Backup - Warnings"),
    unit=UNIT_COUNTER,
    color=Color.YELLOW,
)

metric_proxmox_backup_server_task_summary_tape_backup_error = Metric(
    name="proxmox_backup_server_task_summary_tape_backup_error",
    title=Title("Tape-Backup - Errors"),
    unit=UNIT_COUNTER,
    color=Color.RED,
)

metric_proxmox_backup_server_task_summary_tape_backup_unknown = Metric(
    name="proxmox_backup_server_task_summary_tape_backup_unknown",
    title=Title("Tape-Backup - Tasks Unknown"),
    unit=UNIT_COUNTER,
    color=Color.LIGHT_GRAY,
)

metric_proxmox_backup_server_task_summary_tape_restore_ok = Metric(
    name="proxmox_backup_server_task_summary_tape_restore_ok",
    title=Title("Tape Restore - Tasks OK"),
    unit=UNIT_COUNTER,
    color=Color.GREEN,
)

metric_proxmox_backup_server_task_summary_tape_restore_warning = Metric(
    name="proxmox_backup_server_task_summary_tape_restore_warning",
    title=Title("Tape Restore - Warnings"),
    unit=UNIT_COUNTER,
    color=Color.YELLOW,
)

metric_proxmox_backup_server_task_summary_tape_restore_error = Metric(
    name="proxmox_backup_server_task_summary_tape_restore_error",
    title=Title("Tape Restore - Errors"),
    unit=UNIT_COUNTER,
    color=Color.RED,
)

metric_proxmox_backup_server_task_summary_tape_restore_unknown = Metric(
    name="proxmox_backup_server_task_summary_tape_restore_unknown",
    title=Title("Tape Restore - Tasks Unknown"),
    unit=UNIT_COUNTER,
    color=Color.LIGHT_GRAY,
)

metric_proxmox_backup_server_task_summary_verify_ok = Metric(
    name="proxmox_backup_server_task_summary_verify_ok",
    title=Title("Verify - Tasks OK"),
    unit=UNIT_COUNTER,
    color=Color.GREEN,
)

metric_proxmox_backup_server_task_summary_verify_warning = Metric(
    name="proxmox_backup_server_task_summary_verify_warning",
    title=Title("Verify - Warnings"),
    unit=UNIT_COUNTER,
    color=Color.YELLOW,
)

metric_proxmox_backup_server_task_summary_verify_error = Metric(
    name="proxmox_backup_server_task_summary_verify_error",
    title=Title("Verify - Errors"),
    unit=UNIT_COUNTER,
    color=Color.RED,
)

metric_proxmox_backup_server_task_summary_verify_unknown = Metric(
    name="proxmox_backup_server_task_summary_verify_unknown",
    title=Title("Verify - Tasks Unknown"),
    unit=UNIT_COUNTER,
    color=Color.LIGHT_GRAY,
)
