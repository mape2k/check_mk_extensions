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
    IECMagnitude,
    InputHint,
    Integer,
    LevelDirection,
    MatchingScope,
    migrate_to_lower_integer_levels,
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


def _migrateHostAndItemCondition(value):
    print(value)
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
                parameter_form=SimpleLevels(
                    title=Title("Duration"),
                    migrate=migrate_to_upper_float_levels,
                    help_text=Help("Set the levels for the maximum duration of a backup."),
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[
                            TimeMagnitude.SECOND,
                            TimeMagnitude.MINUTE,
                            TimeMagnitude.HOUR,
                        ]
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
            ),
            "source_files": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Files"),
                    migrate=migrate_to_lower_integer_levels,
                    help_text=Help("Set the levels for the minimum of source files."),
                    form_spec_template=Integer(
                        unit_symbol="files",
                    ),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
            ),
            "source_filesize": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Files - Size"),
                    migrate=migrate_to_lower_integer_levels,
                    help_text=Help("Set the levels for the minimum source file size."),
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
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
            ),
            "new_files": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("New files"),
                    migrate=migrate_to_lower_integer_levels,
                    help_text=Help("Set the levels for the minimum of new files."),
                    form_spec_template=Integer(
                        unit_symbol="files",
                    ),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
            ),
            "new_filesize": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("New files - Size"),
                    migrate=migrate_to_lower_integer_levels,
                    help_text=Help("Set the levels for the minimum new file size."),
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
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
            ),
            "changed_files": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Changed files"),
                    migrate=migrate_to_lower_integer_levels,
                    help_text=Help("Set the levels for the minimum of changed files."),
                    form_spec_template=Integer(
                        unit_symbol="files",
                    ),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
            ),
            "changed_filesize": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Changed files - Size"),
                    migrate=migrate_to_lower_integer_levels,
                    help_text=Help("Set the levels for the minimum changed filesize."),
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
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
            ),
            "deleted_files": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Deleted files"),
                    migrate=migrate_to_lower_integer_levels,
                    help_text=Help("Set the levels for the minimum of deleted files."),
                    form_spec_template=Integer(
                        unit_symbol="files",
                    ),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=InputHint(value=(0, 0)),
                ),
            ),
            "backup_size": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Backup size"),
                    migrate=migrate_to_lower_integer_levels,
                    help_text=Help("Set the levels for the minimum backup size."),
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
                    prefill_fixed_levels=InputHint(value=(1024, 2048)),
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
