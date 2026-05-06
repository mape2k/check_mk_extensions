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
    Label,
    Title,
)
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
)
from cmk.rulesets.v1.rule_specs import (
    AgentConfig,
    Topic,
)


def _parameter_form_bakery_exim_mailq():

    return Dictionary(
        elements={
            "deploy": DictElement(
                required=True,
                parameter_form=BooleanChoice(
                    label=Label("Deploy plugin for Exim Queue"),
                    prefill=DefaultValue(True),
                ),
            )
        },
    )


rule_spec_exim_mailq_bakery = AgentConfig(
    name="exim_mailq",
    title=Title("Exim Queue (Linux)"),
    help_text=Help("This will deploy the agent plugin <tt>exim_mailq</tt> to collect statistics of the exim mail queue."),
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_bakery_exim_mailq,
)
