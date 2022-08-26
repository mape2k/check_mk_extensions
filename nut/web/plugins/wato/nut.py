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
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)

def _item_valuespec_lnx_backup():
    return TextAscii(
            title=_("UPS"),
            help = _("The name of the UPS.")
    )

def _parameter_valuespec_lnx_backup():
    return Dictionary(elements=[
        ("battery_charge",
         Tuple(
             title=_("Battery charge"),
             help = _("Set the levels for the minimum charge amount of the battery."),
             elements=[
                 Percentage(title=_("Warning below"), default_value=90),
                 Percentage(title=_("Critical below"), default_value=85),
             ],
         )),
        ("battery_runtime",
         Tuple(
             title=_("Battery runtime"),
             help = _("Set the levels for time left on battery."),
             elements=[
                 Age(title=_("Warning below"), display=[ "minutes" ], minvalue=0, default_value=1200),
                 Age(title=_("Critical below"), display=[ "minutes" ], minvalue=0, default_value=900),
             ],
         )),
        ("battery_voltage",
         Tuple(
             title = _("Battery voltage"),
             help = _("Set the levels for the battery voltage."),
             elements = [
                 Float(title = _("Warning below"), minvalue = 0.0,default_value = 10.0, unit = u"V"),
                 Float(title = _("Critical below"), minvalue = 0.0, default_value = 5.0, unit = u"V"),
             ],
         )),
        ("input_frequency",
         Tuple(
             title = _("Input freqquency"),
             help = _("Set the levels for the input frequency."),
             elements = [
                 Float(title = _("Critical below"), minvalue = 0.0, default_value = 45.0, unit = u"Hz"),
                 Float(title = _("Warning below"), minvalue = 0.0, default_value = 49.0, unit = u"Hz"),
                 Float(title = _("Warning at or above"), minvalue = 0.0, default_value = 51.0, unit = u"Hz"),
                 Float(title = _("Critical at or above"), minvalue = 0.0, default_value = 55.0, unit = u"Hz"),
             ],
         )),
        ("input_voltage",
         Tuple(
             title = _("Input voltage"),
             help = _("Set the levels for the input voltage."),
             elements = [
                 Float(title = _("Critical below"), minvalue = 0.0, default_value = 0.0, unit = u"V"),
                 Float(title = _("Warning below"), minvalue = 0.0, default_value = 0.0, unit = u"V"),
                 Float(title = _("Warning at or above"), minvalue = 0.0, default_value = 245.0, unit = u"V"),
                 Float(title = _("Critical at or above"), minvalue = 0.0, default_value = 250.0, unit = u"V"),
             ],
         )),
        ("input_voltage_fault",
         Tuple(
             title = _("Input voltage fault"),
             help = _("Set the levels for the input voltage fault."),
             elements = [
                 Float(title = _("Warning at or above"), minvalue = 0.0, default_value = 155.0, unit = u"V"),
                 Float(title = _("Critical at or above"), minvalue = 0.0, default_value = 160.0, unit = u"V"),
             ],
         )),
        ("output_voltage",
         Tuple(
             title = _("Output voltage"),
             help = _("Set the levels for the output voltage."),
             elements = [
                 Float(title = _("Critical below"), minvalue = 0.0, default_value = 0.0, unit = u"V"),
                 Float(title = _("Warning below"), minvalue = 0.0, default_value = 0.0, unit = u"V"),
                 Float(title = _("Warning at or above"), minvalue = 0.0, default_value = 245.0, unit = u"V"),
                 Float(title = _("Critical at or above"), minvalue = 0.0, default_value = 250.0, unit = u"V"),
             ],
         )),
        ("ups_beeper_status",
         DropdownChoice(
             title = _("Beeper status"),
             help = _("Set the expected beeper status."),
             choices = [
                 ('enabled', _('Enabled')),
                 ('disabled', _('Disabled'))
             ],
         )),
        ("ups_load",
         Tuple(
             title = _("Load"),
             help = _("Set the levels for the load of the UPS."),
             elements = [
                 Percentage(title = _("Critical below"), default_value = 0.0),
                 Percentage(title = _("Warning below"),  default_value = 0.0),
                 Percentage(title = _("Warning at or above"), default_value = 50.0),
                 Percentage(title = _("Critical at or above"), default_value = 70.0),
             ],
         )),
        ("ups_temperature",
         Tuple(
             title = _("Temperature"),
             help = _("Set the levels for the temperature of the UPS."),
             elements = [
                 Float(title = _("Warning at or above"), minvalue = 0.0, default_value = 35.0, unit = u"°C"),
                 Float(title = _("Critical at or above"), minvalue = 0.0, default_value = 40.0, unit = u"°C"),
             ],
         )),
    ],)


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="nut",
        group=RulespecGroupCheckParametersApplications,
        match_type="dict",
        item_spec=_item_valuespec_lnx_backup,
        parameter_valuespec=_parameter_valuespec_lnx_backup,
        title=lambda: _("Network UPS Tools"),
    ))
