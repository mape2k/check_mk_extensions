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
    DataSize,
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
    IECMagnitude,
    InputHint,
    # Integer,
    LevelDirection,
    LevelsType,
    # migrate_to_lower_float_levels,
    # migrate_to_upper_integer_levels,
    # migrate_to_upper_float_levels,
    Percentage,
    SimpleLevels,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostAndItemCondition,
    Topic,
)


def _parameter_form_proxmox_backup_server_datastore():

    return Dictionary(
        title=Title("Limits"),
        help_text=Help("Limits for Proxmox Backup Server - Datastore"),
        elements={
            "filled": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Levels for used space"),
                    # migrate=migrate_to_upper_float_levels,
                    help_text=Help("Set the levels for the maximum percentage of used space."),
                    form_spec_template=Percentage(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(80.0, 90.0)),
                ),
            ),
            "estimated_full_timespan": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Estimated Full time"),
                    # migrate=migrate_to_lower_float_levels,
                    help_text=Help("Set the level for the maximum estimated until datastore is full."),
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[
                            TimeMagnitude.SECOND,
                            TimeMagnitude.MINUTE,
                            TimeMagnitude.HOUR,
                            TimeMagnitude.DAY,
                        ]
                    ),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=InputHint(value=(48*60*60, 24*60*60)),
                ),
            ),
            "gc_endtime_timespan": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Garbage Collector - Last Run before"),
                    # migrate=migrate_to_lower_float_levels,
                    help_text=Help("Set the level for the maximum age of the last run of the garbage collector."),
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[
                            TimeMagnitude.SECOND,
                            TimeMagnitude.MINUTE,
                            TimeMagnitude.HOUR,
                            TimeMagnitude.DAY,
                        ]
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(26*60*60, 60*60*60)),
                ),
            ),
            "gc_duration": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Garbage Collector - Duration"),
                    # migrate=migrate_to_lower_float_levels,
                    help_text=Help("Set the level for the maximum duration for a run of the garbage collector."),
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[
                            TimeMagnitude.SECOND,
                            TimeMagnitude.MINUTE,
                            TimeMagnitude.HOUR,
                            TimeMagnitude.DAY,
                        ]
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(15*60, 30*60)),
                ),
            ),
            "gc_removed_bytes": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Garbage Collector - Removed Data"),
                    # migrate=migrate_to_upper_integer_levels,
                    help_text=Help("Set the level for the maximum size of removed data by the garbage collector."),
                    form_spec_template=DataSize(
                        displayed_magnitudes=[
                            IECMagnitude.BYTE,
                            IECMagnitude.KIBI,
                            IECMagnitude.MEBI,
                            IECMagnitude.GIBI,
                        ]
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
            ),
            "gc_pending_bytes": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Garbage Collector - Pending Data"),
                    # migrate=migrate_to_upper_integer_levels,
                    help_text=Help("Set the level for the maximum size of pending data by the garbage collector."),
                    form_spec_template=DataSize(
                        displayed_magnitudes=[
                            IECMagnitude.BYTE,
                            IECMagnitude.KIBI,
                            IECMagnitude.MEBI,
                            IECMagnitude.GIBI,
                        ]
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
            ),
            "gc_disk_bytes": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("On-Disk usage"),
                    # migrate=migrate_to_upper_integer_levels,
                    help_text=Help("Set the level for the maximum size of On-Disk usage."),
                    form_spec_template=DataSize(
                        displayed_magnitudes=[
                            IECMagnitude.BYTE,
                            IECMagnitude.KIBI,
                            IECMagnitude.MEBI,
                            IECMagnitude.GIBI,
                            IECMagnitude.TIBI,
                        ]
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
            ),
            "gc_index_data_bytes": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Original data usage"),
                    # migrate=migrate_to_upper_integer_levels,
                    help_text=Help("Set the level for the maximum size of Original data usage."),
                    form_spec_template=DataSize(
                        displayed_magnitudes=[
                            IECMagnitude.BYTE,
                            IECMagnitude.KIBI,
                            IECMagnitude.MEBI,
                            IECMagnitude.GIBI,
                            IECMagnitude.TIBI,
                        ]
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
            ),
            "deduplication_factor": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("Deduplication Factor"),
                    # migrate=_migrate_lower_integer_levels_to_dict,
                    help_text=Help("Set the levels for the deduplication factor."),
                    elements={
                        "lower": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Lower levels"),
                                form_spec_template=Float(),
                                level_direction=LevelDirection.LOWER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0.0, 0.0)),
                            ),
                        ),
                        "upper": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Upper levels"),
                                form_spec_template=Float(),
                                level_direction=LevelDirection.UPPER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                    },
                ),
            ),
        }
    )


rule_spec_proxmox_backup_server_datastore = CheckParameters(
    name="proxmox_backup_server_datastore",
    title=Title("Proxmox Backup Server - Datastore"),
    topic=Topic.LINUX,
    parameter_form=_parameter_form_proxmox_backup_server_datastore,
    condition=HostAndItemCondition(item_title=Title("Datastore")),
)
