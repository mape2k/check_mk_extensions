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
from cmk.gui.plugins.metrics import metric_info

metric_info["nut_battery_charge"] = {
    "title": _("Battery charge"),
    "unit": "%",
    "color": "33/a",
}

metric_info["nut_battery_runtime"] = {
    "title": _("Battery runtime"),
    "unit": "s",
    "color": "33/b",
}

metric_info["nut_battery_voltage"] = {
    "title": _("Battery voltage"),
    "unit": "",
    "color": "32/a",
}

metric_info["nut_input_frequency"] = {
    "title": _("Input frequency"),
    "unit": "1/s",
    "color": "23/a",
}

metric_info["nut_input_voltage"] = {
    "title": _("Input voltage"),
    "unit": "",
    "color": "21/a",
}

metric_info["nut_input_voltage_fault"] = {
    "title": _("Input voltage (fault)"),
    "unit": "",
    "color": "21/b",
}

metric_info["nut_output_voltage"] = {
    "title": _("Output voltage"),
    "unit": "",
    "color": "46/a",
}

metric_info["nut_ups_load"] = {
    "title": _("Load"),
    "unit": "%",
    "color": "14/a",
}

metric_info["nut_ups_temperature"] = {
    "title": _("Temperature"),
    "unit": "",
    "color": "14/b",
}
