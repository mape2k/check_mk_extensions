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
    Integer,
    Password,
    String,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.rule_specs import (
    AgentConfig,
    Topic,
)


def _parameter_form_bakery_proxmox_ve():

    return Dictionary(
        elements={
            "_deploy": DictElement(
                required=True,
                parameter_form=BooleanChoice(
                    label=Label("Deploy plugin for Proxmox VE"),
                    prefill=DefaultValue(True),
                ),
            ),
            "host": DictElement(
                parameter_form=String(
                    title=Title("Hostname of Proxmox VE host"),
                )
            ),
            "api": DictElement(
                parameter_form=Dictionary(
                    title=Title("Authentication with API-Token"),
                    elements={
                        "api_token_id": DictElement(
                            required=True,
                            parameter_form=String(
                                title=Title("API - Token ID"),
                            )
                        ),
                        "api_token_secret": DictElement(
                            required=True,
                            parameter_form=Password(
                                title=Title("API - Token Secret"),
                            )
                        ),
                    },
                ),
            ),
            # "api_token_id2": DictElement(
            #     parameter_form=String(
            #         title=Title("API - Token ID"),
            #     )
            # ),
            # "api_token_secret2": DictElement(
            #     parameter_form=String(
            #         title=Title("API - Token Secret"),
            #     )
            # ),
            "userpass": DictElement(
                parameter_form=Dictionary(
                    title=Title("Authentication with Username and Password"),
                    help_text=Help("Authentication with API-Token is preferred and used if also configured."),
                    elements={
                        "username": DictElement(
                            required=True,
                            parameter_form=String(
                                title=Title("Username"),
                            )
                        ),
                        "password": DictElement(
                            required=True,
                            parameter_form=Password(
                                title=Title("Password"),
                            )
                        ),
                    },
                ),
            ),
            # "username": DictElement(
            #     parameter_form=String(
            #         title=Title("Username"),
            #     )
            # ),
            # "password": DictElement(
            #     parameter_form=String(
            #         title=Title("Password"),
            #     )
            # ),
            "port": DictElement(
                parameter_form=Integer(
                    title=Title("Port"),
                    prefill=DefaultValue(8006),
                )
            ),
            "no_cert_check": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Disable SSL certificate validation"),
                    label=Label("SSL certificate validation is disabled"),
                    prefill=DefaultValue(False),
                ),
            ),
            "timeout": DictElement(
                parameter_form=Integer(
                    title=Title("Query Timeout"),
                    help_text=Help("The network timeout in seconds"),
                    unit_symbol="seconds",
                    prefill=DefaultValue(50),
                )
            ),
            "log_cutoff_weeks": DictElement(
                parameter_form=Integer(
                    title=Title("Maximum log age"),
                    help_text=Help("Age in weeks of log data to fetch"),
                    unit_symbol="weeks",
                    prefill=DefaultValue(2),
                )
            ),
            "_interval": DictElement(
                parameter_form=TimeSpan(
                    title=Title("Run asynchronously"),
                    label=Label("Interval for collecting data"),
                    displayed_magnitudes=[TimeMagnitude.SECOND, TimeMagnitude.MINUTE],
                    prefill=DefaultValue(300.0),
                )
            ),
        },
    )


rule_spec_proxmox_ve_bakery = AgentConfig(
    name="proxmox_ve",
    title=Title("Proxmox VE"),
    help_text=Help("This will deploy the agent plugin <tt>proxmox_ve</tt> to collect statistics of the Proxmox VE."),
    topic=Topic.LINUX,
    parameter_form=_parameter_form_bakery_proxmox_ve,
)
