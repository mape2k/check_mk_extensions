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
    DefaultValue,
    DictElement,
    Dictionary,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.rule_specs import (
    AgentConfig,
    Topic,
)


def _parameter_form_bakery_gentoo_portage():

    return Dictionary(
        help_text=Help(
            "This will deploy the agent plug-in <tt>gentoo_portage</tt>. This will activate the "
            "check <tt>gentoo_portage</tt> on Gentoo based hosts and monitor "
            "pending updates and unpatched security advisories."
        ),
        elements={
            "_deploy": DictElement(
                required=True,
                parameter_form=BooleanChoice(
                    label=Label("Deploy plugin for Gentoo Portage"),
                    prefill=DefaultValue(True),
                ),
            ),
            "_interval": DictElement(
                parameter_form=TimeSpan(
                    title=Title("Run asynchronously"),
                    label=Label("Interval for collecting data"),
                    displayed_magnitudes=[TimeMagnitude.SECOND, TimeMagnitude.MINUTE],
                    prefill=DefaultValue(3600.0),
                )
            ),
        },
    )


rule_spec_gentoo_portage_bakery = AgentConfig(
    name="gentoo_portage",
    title=Title("Gentoo Portage - Updates and security adivsories (Linux)"),
    help_text=Help("This will deploy the agent plugin <tt>gentoo_portage</tt> to collect update and security informations on Gentoo"),
    topic=Topic.OPERATING_SYSTEM,
    parameter_form=_parameter_form_bakery_gentoo_portage,
)
