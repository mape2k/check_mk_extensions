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

from cmk.rulesets.v1 import (
    Help,
    Title,
)
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    InputHint,
    Integer,
    LevelDirection,
    LevelsType,
    SimpleLevels,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostCondition,
    Topic,
)


def _parameter_form_proxmox_backup_server_task_summary_subform(title: str) -> DictElement:

    return DictElement(
        required=False,
        parameter_form=Dictionary(
            title=Title(title),
            help_text=Help("Set the levels for the task summary."),
            elements={
                "ok": DictElement(
                    required=True,
                    parameter_form=SimpleLevels(
                        title=Title("Tasks OK"),
                        form_spec_template=Integer(
                            unit_symbol=""
                        ),
                        level_direction=LevelDirection.UPPER,
                        prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                        prefill_fixed_levels=InputHint(value=(0, 0)),
                    ),
                ),
                "warning": DictElement(
                    required=True,
                    parameter_form=SimpleLevels(
                        title=Title("Tasks with Warnings"),
                        form_spec_template=Integer(
                            unit_symbol=""
                        ),
                        level_direction=LevelDirection.UPPER,
                        prefill_levels_type=DefaultValue(value=LevelsType.FIXED),
                        prefill_fixed_levels=InputHint(value=(1, 10)),
                    ),
                ),
                "error": DictElement(
                    required=True,
                    parameter_form=SimpleLevels(
                        title=Title("Tasks with Errors"),
                        form_spec_template=Integer(
                            unit_symbol=""
                        ),
                        level_direction=LevelDirection.UPPER,
                        prefill_levels_type=DefaultValue(value=LevelsType.FIXED),
                        prefill_fixed_levels=InputHint(value=(1, 1)),
                    ),
                ),
                "unknown": DictElement(
                    required=True,
                    parameter_form=SimpleLevels(
                        title=Title("Tasks Unknown"),
                        form_spec_template=Integer(
                            unit_symbol=""
                        ),
                        level_direction=LevelDirection.UPPER,
                        prefill_levels_type=DefaultValue(value=LevelsType.FIXED),
                        prefill_fixed_levels=InputHint(value=(1, 1)),
                    ),
                ),
            },
        )
    )


def _parameter_form_proxmox_backup_server_task_summary():

    return Dictionary(
        title=Title("Limits"),
        help_text=Help("Limits for Proxmox Backup Server Task Summary"),
        elements={
            "backup": _parameter_form_proxmox_backup_server_task_summary_subform("Backup"),
            "garbage_collection": _parameter_form_proxmox_backup_server_task_summary_subform("Garbage collection"),
            "other": _parameter_form_proxmox_backup_server_task_summary_subform("Other"),
            "prune": _parameter_form_proxmox_backup_server_task_summary_subform("Prunes"),
            "sync": _parameter_form_proxmox_backup_server_task_summary_subform("Syncs"),
            "tape_backup": _parameter_form_proxmox_backup_server_task_summary_subform("Tape Backup"),
            "tape_restore": _parameter_form_proxmox_backup_server_task_summary_subform("Tape Restore"),
            "verify": _parameter_form_proxmox_backup_server_task_summary_subform("Verify"),
        }
    )


rule_spec_proxmox_backup_server_task_summary = CheckParameters(
    name="proxmox_backup_server_task_summary",
    title=Title("Proxmox Backup Server Task Summary"),
    topic=Topic.LINUX,
    parameter_form=_parameter_form_proxmox_backup_server_task_summary,
    condition=HostCondition(),
)
