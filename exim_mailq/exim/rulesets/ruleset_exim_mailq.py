#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) 2022 Marcel Pennewiss <opensource@pennewiss.de>
# (c) 2025 Erik Stomp <mail@erik-stomp.de> - Updated Ruleset to API v1

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

from cmk.rulesets.v1 import Label, Title, Help
from cmk.rulesets.v1.form_specs import BooleanChoice, DefaultValue, DictElement, Dictionary, Integer, LevelDirection, SimpleLevels
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition, Topic

def _parameter_valuespec_exim_mailq():
    return Dictionary(
        elements={
          "length": DictElement(
            parameter_form = SimpleLevels(
              title = Title("Mails in outgoing mail queue"),
              help_text = Help("Set the levels for the maximum number of E-Mails currently in the mail queue."),
              form_spec_template = Integer(),
              level_direction = LevelDirection.UPPER,
              prefill_fixed_levels = DefaultValue(value=(5, 10)),
            ),
            required = True,
          ),
          "size": DictElement(
            parameter_form = SimpleLevels(
              title = Title("Mailsize in outgoing mail queue"),
              help_text = Help("Set the levels for the maximum size of all E-Mails in the mail queue."),
              form_spec_template = Integer(),
              level_direction = LevelDirection.UPPER,
              prefill_fixed_levels = DefaultValue(value=((1024**2), 2*(1024**2))),
            ),
            required = False,
          ),
          "age_oldest": DictElement(
            parameter_form = SimpleLevels(
              title = Title("Age of oldest mail"),
              help_text = Help("Set the levels for the maximum age of the oldest E-Mail in the mail queue."),
              form_spec_template = Integer(),
              level_direction = LevelDirection.UPPER,
              prefill_fixed_levels = DefaultValue(value=(3600, 7200)),
            ),
            required = False,
          )
        }
    )

rule_spec_exim_mailq = CheckParameters(
    name = "exim_mailq",
    title = Title("Exim mail queue parameters"),
    topic = Topic.GENERAL,
    parameter_form = _parameter_valuespec_exim_mailq,
    condition = HostCondition(),
)