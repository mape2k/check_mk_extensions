#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) 2022 Marcel Pennewiss <opensource@pennewiss.de>

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

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Age,
    Dictionary,
    DropdownChoice,
    TextAscii,
    Tuple,
    ListOf,
    Integer,
    MonitoringState,
)

from cmk.gui.plugins.wato import (
    rulespec_registry,
    CheckParameterRulespecWithoutItem,
    RulespecGroupCheckParametersApplications,
)


def _parameter_valuespec_exim_mailq():
    return Dictionary(elements=[
        ("length",
         Tuple(
             title = _("Mails in outgoing mail queue"),
             help = _("Set the levels for the maximum number of E-Mails currently in the mail queue."),
             elements = [
                 Integer(title = _("Warning at"), unit = "mails", minvalue = 0, default_value = 10),
                 Integer(title = _("Critical at"), unit = "mails", minvalue = 0, default_value = 20),
             ],
         )),
        ("size",
         Tuple(
             title=_("Mailsize in outgoing mail queue"),
             help = _("Set the levels for the maximum size of all E-Mails in the mail queue."),
             elements=[
                 Filesize(title=_("Warning at"), minvalue=0, default_value=(1024**2)),
                 Filesize(title=_("Critical at"), minvalue=0, default_value=2*(1024**2)),
             ],
         )),
         ("age_oldest",
         Tuple(
             title=_("Age of oldest mail"),
             help = _("Set the levels for the maximum age of the oldest E-Mail in the mail queue."),
             elements=[
                 Age(title=_("Warning at"), minvalue=0, default_value=60*60),
                 Age(title=_("Critical at"), minvalue=0, default_value=2*60*60),
             ],
         )),

    ],)


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="exim_mailq",
        group=RulespecGroupCheckParametersApplications,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_exim_mailq,
        title=lambda: _("Exim Queue"),
    ))
