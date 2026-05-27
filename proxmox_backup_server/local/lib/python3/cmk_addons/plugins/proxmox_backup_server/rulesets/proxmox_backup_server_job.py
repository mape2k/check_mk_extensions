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
    DictElement,
    Dictionary,
    InputHint,
    LevelDirection,
    SimpleLevels,
    TimeMagnitude,
    TimeSpan,
)


def _parameter_form_proxmox_backup_server_job(jobtype: str) -> Dictionary:

    return Dictionary(
        title=Title("Limits"),
        help_text=Help(f"Limits for Proxmox Backup Server {jobtype.capitalize()} Job"),
        elements={
            "last_run": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Last run"),
                    help_text=Help("Set the level for the maximum timespan for last run."),
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
            "next_run": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Next run"),
                    help_text=Help("Set the level for the maximum timespan for next run."),
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
        }
    )