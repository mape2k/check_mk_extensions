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
    #Dict,
    Mapping,
    #Optional,
    #TypedDict,
    Tuple,
)
from .agent_based_api.v1 import (
    check_levels,
    register,
    render,
    type_defs,
    #Metric,
    Result,
    Service,
    #ServiceLabel,
    State,
)
#import datetime

# <<<exim_mailq>>>
#     2     668     44m     43m  TOTAL
# <<<exim_mailq>>>
#     4   252KB     61m      0m  TOTAL


_METRIC_SPECS: Mapping[str, Tuple[str, Callable, bool, bool, bool]] = {
    # 'metric': ('Metric Name', renderer, notice_only, Levels are lower levels, Levels are upper levels)
    'length': ('Length', str, False, False, True),
    'size': ('Size', render.bytes, False, False, True),
    'age_oldest': ('Oldest mail', render.timespan, False, False, True),
    'age_newest': ('Newest mail', render.timespan, True, False, False),
}


def _exim_mailq_to_bytes(value):
    if value[-1].isdigit():
        return int(value)

    size, uom = int(value[:-2]), value[-2:].lower()

    if uom == 'kb':
        return size * 1024
    elif uom == 'mb':
        return size * (1024 ** 2)
    elif uom == 'gb':
        return size * (1024 ** 3)


def _exim_mailq_to_seconds(value):
    if value[-1].isdigit():
        return int(value)

    time, uom = int(value[:-1]), value[-1:].lower()

    if uom == 'm':
        return time * 60
    elif uom == 'h':
        return time * 60 * 60
    elif uom == 'd':
        return time * 60 * 60 * 24


def exim_mailq_parse(string_table: type_defs.StringTable):

    if len(string_table[0]) != 5:
        return {}

    # Get exim mailq values
    exim_mailq = {
        'length': int(string_table[0][0]),
        'size': _exim_mailq_to_bytes(string_table[0][1]),
        'age_oldest': _exim_mailq_to_seconds(string_table[0][2]),
        'age_newest': _exim_mailq_to_seconds(string_table[0][3]),
    }

    return exim_mailq


def discover_exim_mailq(section) -> type_defs.DiscoveryResult:
    if section:
        yield Service()


def check_exim_mailq(params: Mapping[str, Any], section) -> type_defs.CheckResult:

    if 'length' not in section:
        yield Result(
            state=State.UNKNOWN,
            summary="Could not find summarizing line in output"
        )
        return

    # Check all metrics
    for metric in section:
        yield from check_levels(
            section[metric],
            metric_name="exim_mailq_%s" % metric,
            label=_METRIC_SPECS[metric][0],
            levels_lower=params.get(metric) if (_METRIC_SPECS[metric][3] and params.get(metric) != (0,0)) else None,
            levels_upper=params.get(metric) if (_METRIC_SPECS[metric][4] and params.get(metric) != (0,0)) else None,
            render_func=_METRIC_SPECS[metric][1],
            notice_only=_METRIC_SPECS[metric][2],
            boundaries=(0, None),
        )


register.agent_section(
    name = "exim_mailq",
    parse_function = exim_mailq_parse
)


register.check_plugin(
    name = "exim_mailq",
    service_name = "Exim Queue",
    sections=["exim_mailq"],
    discovery_function = discover_exim_mailq,
    check_function = check_exim_mailq,
    check_default_parameters = {
        'length':           (10, 20),
        'size':             (1048576, 2097152),
        'age_oldest':       (3600, 7200),
    },
    check_ruleset_name="exim_mailq",
)
