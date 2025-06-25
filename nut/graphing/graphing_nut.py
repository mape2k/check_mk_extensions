#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) 2025 Christian Kreidl <christian.kreidl@ziti.uni-heidelberg.de>

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

from cmk.graphing.v1 import metrics, perfometers, graphs, Title

metric_nut_battery_charge = metrics.Metric(
    name="nut_battery_charge",
    title=Title("Battery charge"),
    unit=metrics.Unit(metrics.DecimalNotation("%")),
    color=metrics.Color.RED,
)

metric_nut_battery_runtime = metrics.Metric(
    name="nut_battery_runtime",
    title=Title("Battery runtime"),
    unit=metrics.Unit(metrics.DecimalNotation("s")),
    color=metrics.Color.ORANGE,
)

metric_nut_battery_voltage = metrics.Metric(
    name="nut_battery_voltage",
    title=Title("Battery voltage"),
    unit=metrics.Unit(metrics.DecimalNotation("V")),
    color=metrics.Color.YELLOW,
)

metric_nut_input_frequency = metrics.Metric(
    name="nut_input_frequency",
    title=Title("Input frequency"),
    unit=metrics.Unit(metrics.DecimalNotation("Hz")),
    color=metrics.Color.GREEN,
)

metric_nut_input_voltage = metrics.Metric(
    name="nut_input_voltage",
    title=Title("Input voltage"),
    unit=metrics.Unit(metrics.DecimalNotation("V")),
    color=metrics.Color.BLUE,
)

metric_nut_input_voltage_fault = metrics.Metric(
    name="nut_input_voltage_fault",
    title=Title("Input voltage (fault)"),
    unit=metrics.Unit(metrics.DecimalNotation("V")),
    color=metrics.Color.CYAN,
)

metric_nut_output_voltage = metrics.Metric(
    name="nut_output_voltage",
    title=Title("Output voltage"),
    unit=metrics.Unit(metrics.DecimalNotation("V")),
    color=metrics.Color.PURPLE,
)

metric_nut_ups_load = metrics.Metric(
    name="nut_ups_load",
    title=Title("Load"),
    unit=metrics.Unit(metrics.DecimalNotation("%")),
    color=metrics.Color.PINK,
)

metric_nut_ups_temperature = metrics.Metric(
    name="nut_ups_temperature",
    title=Title("Temperature"),
    unit=metrics.Unit(metrics.DecimalNotation("°C")),
    color=metrics.Color.BROWN,
)



perfometer_nut_battery_charge = perfometers.Perfometer(
    name="nut_battery_charge",
    focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Closed(100)),
    segments=["nut_battery_charge"],
)
