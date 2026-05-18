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
    DictElement,
    Dictionary,
    DefaultValue,
    IECMagnitude,
    InputHint,
    Integer,
    LevelDirection,
    LevelsType,
    MatchingScope,
    migrate_to_upper_integer_levels,
    migrate_to_upper_float_levels,
    RegularExpression,
    SimpleLevels,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostAndItemCondition,
    Topic,
)


def _migrate_exit_code(value):

    if isinstance(value, tuple):
        return {
            "ok": "0",
            "warn": str(value[0]),
            "crit": str(value[1])
        }
    return value


def _migrate_lower_integer_levels_to_dict(value):

    if isinstance(value, tuple):
        return {
            "lower": ("fixed", (int(value[0]), int(value[1]))),
            "upper": ("no_levels", None)
        }
    return value


def _migrate_upper_float_levels_to_dict(value):

    if isinstance(value, tuple):
        return {
            "lower": ("no_levels", None),
            "upper": ("fixed", (float(value[0]), float(value[1])))
        }
    return value


def _parameter_form_lnx_backup():

    return Dictionary(
        title=Title("Limits"),
        help_text=Help("Limits for linux backup"),
        elements={
            "age": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Age"),
                    migrate=migrate_to_upper_float_levels,
                    help_text=Help("Set the levels for the maximum age of a backup."),
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[
                            TimeMagnitude.SECOND,
                            TimeMagnitude.MINUTE,
                            TimeMagnitude.HOUR,
                            TimeMagnitude.DAY,
                        ]
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(26*60*60, 50*60*60)),
                ),
            ),
            "duration": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("Duration"),
                    migrate=_migrate_upper_float_levels_to_dict,
                    help_text=Help("Set the levels for the duration of a backup."),
                    elements={
                        "lower": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Lower levels"),
                                form_spec_template=TimeSpan(
                                    displayed_magnitudes=[
                                        TimeMagnitude.SECOND,
                                        TimeMagnitude.MINUTE,
                                        TimeMagnitude.HOUR,
                                    ]
                                ),
                                level_direction=LevelDirection.LOWER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(20*60, 10*60)),
                            ),
                        ),
                        "upper": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Upper levels"),
                                form_spec_template=TimeSpan(
                                    displayed_magnitudes=[
                                        TimeMagnitude.SECOND,
                                        TimeMagnitude.MINUTE,
                                        TimeMagnitude.HOUR,
                                    ]
                                ),
                                level_direction=LevelDirection.UPPER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(60*60, 2*60*60)),
                            ),
                        ),
                    },
                ),
            ),
            "source_files": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("Files"),
                    migrate=_migrate_lower_integer_levels_to_dict,
                    help_text=Help("Set the levels of source files."),
                    elements={
                        "lower": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Lower levels"),
                                form_spec_template=Integer(
                                    unit_symbol="files",
                                ),
                                level_direction=LevelDirection.LOWER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                        "upper": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Upper levels"),
                                form_spec_template=Integer(
                                    unit_symbol="files",
                                ),
                                level_direction=LevelDirection.UPPER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                    },
                ),
            ),
            "source_filesize": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("Files - Size"),
                    migrate=_migrate_lower_integer_levels_to_dict,
                    help_text=Help("Set the levels for the size of source files."),
                    elements={
                        "lower": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Lower levels"),
                                form_spec_template=DataSize(
                                    displayed_magnitudes=[
                                        IECMagnitude.BYTE,
                                        IECMagnitude.KIBI,
                                        IECMagnitude.MEBI,
                                        IECMagnitude.GIBI,
                                        IECMagnitude.TEBI,
                                    ]
                                ),
                                level_direction=LevelDirection.LOWER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                        "upper": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Upper levels"),
                                form_spec_template=DataSize(
                                    displayed_magnitudes=[
                                        IECMagnitude.BYTE,
                                        IECMagnitude.KIBI,
                                        IECMagnitude.MEBI,
                                        IECMagnitude.GIBI,
                                        IECMagnitude.TEBI,
                                    ]
                                ),
                                level_direction=LevelDirection.UPPER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                    },
                ),
            ),
            "new_files": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("New files"),
                    migrate=_migrate_lower_integer_levels_to_dict,
                    help_text=Help("Set the levels of new files."),
                    elements={
                        "lower": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Lower levels"),
                                form_spec_template=Integer(
                                    unit_symbol="files",
                                ),
                                level_direction=LevelDirection.LOWER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                        "upper": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Upper levels"),
                                form_spec_template=Integer(
                                    unit_symbol="files",
                                ),
                                level_direction=LevelDirection.UPPER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                    },
                ),
            ),
            "new_filesize": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("New files - Size"),
                    migrate=_migrate_lower_integer_levels_to_dict,
                    help_text=Help("Set the levels for the size of new files."),
                    elements={
                        "lower": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Lower levels"),
                                form_spec_template=DataSize(
                                    displayed_magnitudes=[
                                        IECMagnitude.BYTE,
                                        IECMagnitude.KIBI,
                                        IECMagnitude.MEBI,
                                        IECMagnitude.GIBI,
                                        IECMagnitude.TEBI,
                                    ]
                                ),
                                level_direction=LevelDirection.LOWER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                        "upper": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Upper levels"),
                                form_spec_template=DataSize(
                                    displayed_magnitudes=[
                                        IECMagnitude.BYTE,
                                        IECMagnitude.KIBI,
                                        IECMagnitude.MEBI,
                                        IECMagnitude.GIBI,
                                        IECMagnitude.TEBI,
                                    ]
                                ),
                                level_direction=LevelDirection.UPPER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                    },
                ),
            ),
            "changed_files": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("Changed files"),
                    migrate=_migrate_lower_integer_levels_to_dict,
                    help_text=Help("Set the levels of changed files."),
                    elements={
                        "lower": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Lower levels"),
                                form_spec_template=Integer(
                                    unit_symbol="files",
                                ),
                                level_direction=LevelDirection.LOWER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                        "upper": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Upper levels"),
                                form_spec_template=Integer(
                                    unit_symbol="files",
                                ),
                                level_direction=LevelDirection.UPPER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                    },
                ),
            ),
            "changed_filesize": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("Changed files - Size"),
                    migrate=_migrate_lower_integer_levels_to_dict,
                    help_text=Help("Set the levels for the size of the changed files."),
                    elements={
                        "lower": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Lower levels"),
                                form_spec_template=DataSize(
                                    displayed_magnitudes=[
                                        IECMagnitude.BYTE,
                                        IECMagnitude.KIBI,
                                        IECMagnitude.MEBI,
                                        IECMagnitude.GIBI,
                                        IECMagnitude.TEBI,
                                    ]
                                ),
                                level_direction=LevelDirection.LOWER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                        "upper": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Upper levels"),
                                form_spec_template=DataSize(
                                    displayed_magnitudes=[
                                        IECMagnitude.BYTE,
                                        IECMagnitude.KIBI,
                                        IECMagnitude.MEBI,
                                        IECMagnitude.GIBI,
                                        IECMagnitude.TEBI,
                                    ]
                                ),
                                level_direction=LevelDirection.UPPER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                    },
                ),
            ),
            "deleted_files": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("Deleted files"),
                    migrate=_migrate_lower_integer_levels_to_dict,
                    help_text=Help("Set the levels of deleted files."),
                    elements={
                        "lower": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Lower levels"),
                                form_spec_template=Integer(
                                    unit_symbol="files",
                                ),
                                level_direction=LevelDirection.LOWER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                        "upper": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Upper levels"),
                                form_spec_template=Integer(
                                    unit_symbol="files",
                                ),
                                level_direction=LevelDirection.UPPER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                    },
                ),
            ),
            "backup_size": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("Backup - Size"),
                    migrate=_migrate_lower_integer_levels_to_dict,
                    help_text=Help("Set the levels for the backup size."),
                    elements={
                        "lower": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Lower levels"),
                                form_spec_template=DataSize(
                                    displayed_magnitudes=[
                                        IECMagnitude.BYTE,
                                        IECMagnitude.KIBI,
                                        IECMagnitude.MEBI,
                                        IECMagnitude.GIBI,
                                        IECMagnitude.TEBI,
                                    ]
                                ),
                                level_direction=LevelDirection.LOWER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(1024, 2*1024)),
                            ),
                        ),
                        "upper": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Upper levels"),
                                form_spec_template=DataSize(
                                    displayed_magnitudes=[
                                        IECMagnitude.BYTE,
                                        IECMagnitude.KIBI,
                                        IECMagnitude.MEBI,
                                        IECMagnitude.GIBI,
                                        IECMagnitude.TEBI,
                                    ]
                                ),
                                level_direction=LevelDirection.UPPER,
                                prefill_levels_type=DefaultValue(value=LevelsType.NONE),
                                prefill_fixed_levels=InputHint(value=(0, 0)),
                            ),
                        ),
                    },
                ),
            ),
            "errors": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Errors"),
                    migrate=migrate_to_upper_integer_levels,
                    help_text=Help("Set the levels for the maximum of errors."),
                    form_spec_template=Integer(
                        unit_symbol="errors",
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(1, 1)),
                ),
            ),
            "exit_code": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("Exit code"),
                    migrate=_migrate_exit_code,
                    help_text=Help("Define the exit codes for Ok, Warning and Critical. Any other code results in Unknown."),
                    elements={
                        "ok": DictElement(
                            required=False,
                            parameter_form=RegularExpression(
                                title=Title("Ok at"),
                                predefined_help_text=MatchingScope.FULL,
                                prefill=InputHint(value="0")
                            ),
                        ),
                        "warn": DictElement(
                            required=False,
                            parameter_form=RegularExpression(
                                title=Title("Warning at"),
                                predefined_help_text=MatchingScope.FULL,
                                prefill=InputHint(value="(1|2|3)")
                            ),
                        ),
                        "crit": DictElement(
                            required=False,
                            parameter_form=RegularExpression(
                                title=Title("Critical at"),
                                predefined_help_text=MatchingScope.FULL,
                                prefill=InputHint(value="(254|255)")
                            ),
                        ),
                    },
                ),
            ),
        }
    )


rule_spec_lnx_backup = CheckParameters(
    name="lnx_backup",
    title=Title("Linux Backup"),
    topic=Topic.LINUX,
    parameter_form=_parameter_form_lnx_backup,
    condition=HostAndItemCondition(item_title=Title("Backup")),
)
