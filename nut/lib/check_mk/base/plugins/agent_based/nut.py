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

import time
from typing import (
    Any,
    Callable,
    Dict,
    Mapping,
    Optional,
    TypedDict,
    Tuple,
)
from .agent_based_api.v1 import (
    check_levels,
    register,
    render,
    type_defs,
    Metric,
    Result,
    Service,
    ServiceLabel,
    State,
)
import datetime

# <<<nut>>>
# ==> demo_ups <==
# demo_ups battery.charge: 100
# demo_ups battery.packs: 6
# demo_ups battery.runtime: 788
# demo_ups battery.voltage: 2.16
# demo_ups battery.voltage.high: 62.4
# demo_ups battery.voltage.low: 78
# demo_ups battery.voltage.nominal: 12
# demo_ups device.type: ups
# demo_ups driver.flag.novendor: enabled
# demo_ups driver.name: blazer_usb
# demo_ups driver.parameter.pollinterval: 2
# demo_ups driver.parameter.port: auto
# demo_ups driver.parameter.productid: 0005
# demo_ups driver.parameter.protocol: megatec
# demo_ups driver.parameter.runtimecal: 270,100,594,50
# demo_ups driver.parameter.subdriver: phoenix
# demo_ups driver.parameter.vendorid: 06da
# demo_ups driver.version: 2.7.2
# demo_ups driver.version.internal: 0.11
# demo_ups input.frequency: 50.0
# demo_ups input.voltage: 238.0
# demo_ups input.voltage.fault: 0.0
# demo_ups output.voltage: 229.9
# demo_ups ups.beeper.status: disabled
# demo_ups ups.delay.shutdown: 30
# demo_ups ups.delay.start: 180
# demo_ups ups.load: 39
# demo_ups ups.productid: 0005
# demo_ups ups.status: OL
# demo_ups ups.temperature: 27.8
# demo_ups ups.type: online
# demo_ups ups.vendorid: 06da

Metrics = Dict[str, int]


class UpsData(TypedDict, total=False):
    battery_charge: float
    battery_packs: int
    battery_runtime: float
    battery_voltage: float
    input_frequency: float
    input_voltage: float
    input_voltage_fault: float
    output_voltage: float
    ups_beeper_status: str
    ups_load: float
    ups_temperature: float


Section = Dict[str, UpsData]

def nut_parse(string_table: type_defs.StringTable) -> Section:
    parsed: Section = {}

    for idx, line in enumerate(string_table):

        if line[0] == "==>" and line[-1] == "<==":
            # Found section beginning
            upsName = " ".join(string_table[idx][1:-1])
            parsed[upsName] = {}

        elif len(line) >= 2:
            # Found key value pair
            key = line[0]
            val = " ".join(line[1:])
            
            # Fix key
            key = key.replace('.', '_').replace(':', '')

            # Convert several keys/values
            if key in [ 'battery_charge', 'battery_runtime', 'battery_voltage', 'input_frequency', 'input_voltage', 'input_voltage_fault', 'output_voltage', 'ups_load', 'ups_temperature' ]:
                parsed[upsName][key] = float(val)
            elif key in [ 'battery_packs' ]:
                parsed[upsName][key] = int(val)
            elif key in [ 'ups_status', 'ups_beeper_status' ]:
                parsed[upsName][key] = val

    return parsed


def discover_nut(section: Section) -> type_defs.DiscoveryResult:
    for upsname, upsdata in section.items():
        if len(upsdata) > 0:
            yield Service(item=upsname)


_METRIC_SPECS: Mapping[str, Tuple[str, Callable, bool, bool, bool]] = {
    # 'metric': ('Metric Name', renderer, notice_only, lower_levels, upper_levels)
    'battery_charge': ('Battery charge', render.percent, False, True, False),
    'battery_runtime': ('Battery runtime', render.timespan, False, True, False),
    'battery_voltage': ('Battery voltage', lambda v: "%0.2f V" % v, True, True, False),
    'input_frequency': ('Input frequency', render.frequency, True, True, True),
    'input_voltage': ('Input voltage', lambda v: "%0.2f V" % v, True, True, True),
    'input_voltage_fault': ('Input voltage (fault)', lambda v: "%0.2f V" % v, True, False, True),
    'output_voltage': ('Output voltage', lambda v: "%.2f V" % v, True, True, True),
    'ups_load': ('Load', render.percent, False, True, True),
    'ups_temperature': ('Temperature', lambda v: "%0.1f °C" % v, True, False, True),
}


def check_nut(item: str, params: Mapping[str, Any], section: Section) -> type_defs.CheckResult:

    upsData = section.get(item)
    if upsData is None:
        yield Result(
            state=State.UNKNOWN,
            summary="Could not find data in output"
        )
        return

    yield Result(
        state=State.OK,
        summary="Status: %s" % upsData['ups_status']
    )

    # Check Beeper status
    if upsData.get('ups_beeper_status', 'disabled') != params.get('ups_beeper_status'):
        yield Result(
            state=State.CRIT,
            summary="Beeper: %s" % upsData.get('ups_beeper_status', 'disabled')
        )

    # Check all metrics
    for metric in upsData:

        # Ignore unspecified metrics
        if metric not in _METRIC_SPECS:
            continue

        # Get lower levels
        if _METRIC_SPECS[metric][3]:
            if len(params.get(metric)) == 4:
                levels_lower = params.get(metric)[:2]
            else:
                levels_lower = params.get(metric)
        
        if _METRIC_SPECS[metric][4]:
            if len(params.get(metric)) == 4:
                levels_upper = params.get(metric)[2:]
            else:
                levels_upper = params.get(metric)

        # Calculate real voltage
        if metric == 'battery_voltage':
            upsData[metric] = upsData[metric] * upsData.get('battery_packs', 1)

        yield from check_levels(
            upsData[metric],
            metric_name="nut_%s" % metric,
            label=_METRIC_SPECS[metric][0],
            levels_lower=levels_lower if (_METRIC_SPECS[metric][3] and params.get(metric) != (0,0)) else None,
            levels_upper=levels_upper if (_METRIC_SPECS[metric][4] and params.get(metric) != (0,0)) else None,
            render_func=_METRIC_SPECS[metric][1],
            notice_only=_METRIC_SPECS[metric][2],
            boundaries=(0, None),
        )


register.agent_section(
    name = "nut",
    parse_function = nut_parse
)


register.check_plugin(
    name = "nut",
    service_name = "UPS %s",
    discovery_function = discover_nut,
    check_function = check_nut,
    check_default_parameters = {
        'battery_charge': (90, 85),
        'battery_runtime': (1200, 900),
        'battery_voltage': (10, 5),
        'input_frequency': (45, 49, 51, 55),
        'input_voltage': (0, 0, 245, 250),
        'input_voltage_fault': (155, 160),
        'output_voltage': (0, 0, 245, 250),
        'ups_beeper_status': 'disabled',
        'ups_load': (0, 0, 50, 70),
        'ups_temperature': (35, 40),
    },
    check_ruleset_name="nut",
)
