#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) 2026 Marcel Pennewiss <opensource@pennewiss.de>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License. This program
# is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details. You should have received a copy of the GNU
# General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA.

from cmk.rulesets.v1 import (
    Help,
    Label,
    Title,
)
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DictElement,
    Dictionary,
    DefaultValue,
    InputHint,
    LevelDirection,
    ServiceState,
    SimpleLevels,
    String,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostCondition,
    Topic,
)


def parameter_form_gentoo_portage():

    return Dictionary(
        title=Title("Limits"),
        help_text=Help("Limits for linux backup"),
        elements={
            "portage": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("Portage synchronization"),
                    help_text=Help("Set the levels for portage synchronization"),
                    elements={
                        "timestamp_timespan": DictElement(
                            required=True,
                            parameter_form=SimpleLevels(
                                title=Title("Age of portage timestamp"),
                                form_spec_template=TimeSpan(
                                    displayed_magnitudes=[
                                        TimeMagnitude.SECOND,
                                        TimeMagnitude.MINUTE,
                                        TimeMagnitude.HOUR,
                                        TimeMagnitude.DAY,
                                    ]
                                ),
                                level_direction=LevelDirection.UPPER,
                                prefill_fixed_levels=InputHint(value=(24*60*60, 48*60*60)),
                            ),
                        ),
                        "ignore_exit_code": DictElement(
                            required=True,
                            parameter_form=BooleanChoice(
                                label=Label("Ignore exit code from synchronization not equal zero"),
                                prefill=DefaultValue(False),
                            ),
                        ),
                    },
                ),
            ),
            "updates": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("Updates"),
                    help_text=Help("Set the levels for updates"),
                    elements={
                        "state_normal_updates": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("State when normal updates are pending"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "state_newslot_updates": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("State when updates in new slots are pending"),
                                prefill=DefaultValue(ServiceState.OK),
                            ),
                        ),
                        "add_package_names": DictElement(
                            required=True,
                            parameter_form=BooleanChoice(
                                label=Label("Add package names to service summary"),
                                prefill=DefaultValue(False),
                            ),
                        ),
                        "default_repository": DictElement(
                            required=True,
                            parameter_form=String(
                                title=Title("Name of default repository"),
                                prefill=DefaultValue("gentoo"),
                            ),
                        )
                    },
                ),
            ),
            "glsa": DictElement(
                required=False,
                parameter_form=Dictionary(
                    title=Title("Gentoo Linux Security Advisory"),
                    help_text=Help("Set the levels for GLSA"),
                    elements={
                        "state_impact_low": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("State when packages affected by GLSA with LOW impact"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "state_impact_normal": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("State when packages affected by GLSA with NORMAL impact"),
                                prefill=DefaultValue(ServiceState.WARN),
                            ),
                        ),
                        "state_impact_high": DictElement(
                            required=True,
                            parameter_form=ServiceState(
                                title=Title("State when packages affected by GLSA with HIGH impact"),
                                prefill=DefaultValue(ServiceState.CRIT),
                            ),
                        ),
                        "add_package_names": DictElement(
                            required=True,
                            parameter_form=BooleanChoice(
                                label=Label("Add affected package names to service summary"),
                                prefill=DefaultValue(True),
                            ),
                        ),
                    },
                ),
            ),
        }
    )


rule_spec_gentoo_portage = CheckParameters(
    name="gentoo_portage",
    title=Title("Gentoo Portage Updates"),
    topic=Topic.OPERATING_SYSTEM,
    parameter_form=parameter_form_gentoo_portage,
    condition=HostCondition(),
)
