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
    migrate_to_upper_integer_levels,
    migrate_to_upper_float_levels,
    SimpleLevels,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostCondition,
    Topic,
)


def _parameter_form_exim_mailq():

    return Dictionary(
        title=Title("Limits"),
        help_text=Help("Limits for exim mail queue"),
        elements={
            "length": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Mails in outgoing mail queue"),
                    migrate=migrate_to_upper_integer_levels,
                    help_text=Help("Set the levels for the maximum number of E-Mails currently in the mail queue."),
                    form_spec_template=Integer(
                        unit_symbol="mails",
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(10, 20)),
                ),
            ),
            "size": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Mailsize in outgoing mail queue"),
                    migrate=migrate_to_upper_integer_levels,
                    help_text=Help("Set the levels for the maximum size of all E-Mails in the mail queue."),
                    form_spec_template=DataSize(
                        displayed_magnitudes=[
                            IECMagnitude.BYTE,
                            IECMagnitude.KIBI,
                            IECMagnitude.MEBI,
                        ]
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(1024**2, 2*(1024**2))),
                ),
            ),
            "age_oldest": DictElement(
                required=False,
                parameter_form=SimpleLevels(
                    title=Title("Age of oldest mail"),
                    migrate=migrate_to_upper_float_levels,
                    help_text=Help("Set the levels for the maximum age of the oldest E-Mail in the mail queue."),
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[
                            TimeMagnitude.SECOND,
                            TimeMagnitude.MINUTE,
                            TimeMagnitude.HOUR
                        ]
                    ),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(60*60, 2*60*60)),
                ),
            ),
        }
    )


rule_spec_exim_mailq = CheckParameters(
    name="exim_mailq",
    title=Title("Exim Queue"),
    topic=Topic.GENERAL,
    parameter_form=_parameter_form_exim_mailq,
    condition=HostCondition(),
)
