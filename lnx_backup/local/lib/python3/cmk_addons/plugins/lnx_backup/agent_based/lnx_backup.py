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

# Example Agent Output
# <<<lnx_backup>>>
# ==> backupname rsync <==
# start_time 1657063210
# end_time 1657063231
# exit_code 0
# source_files 6839
# source_filesize 864839744
# new_files 111
# new_filesize 37084983
# deleted_files 0
# changed_files 0
# changed_filesize 0
# backup_size 19698101
# errors 0

import time
import re

from typing import Any, Callable, Dict, Mapping, TypedDict, Tuple

from cmk.agent_based.v2 import (
    AgentSection,
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    render,
    Result,
    Service,
    State,
    StringTable,
)

_METRIC_SPECS: Mapping[str, Tuple[str, Callable, bool, bool, bool, bool]] = {
    # 'metric': ('Metric Name', renderer, notice_only, Levels are lower levels, Levels are upper levels, Levels are regular expression)
    'age': ('Job age', render.timespan, False, False, True, False),
    'duration': ('Backup duration', render.timespan, False, True, True, False),
    'source_files': ('Files', str, True, True, True, False),
    'source_filesize': ('Filesize', render.bytes, True, True, True, False),
    'new_files': ('New Files', str, True, True, True, False),
    'new_filesize': ('New Filesize', render.bytes, True, True, True, False),
    'changed_files': ('Changed Files', str, True, True, True, False),
    'changed_filesize': ('Changed Filesize', render.bytes, True, True, True, False),
    'deleted_files': ('Deleted Files', str, True, True, True, False),
    'backup_size': ('Backup size', render.bytes, True, True, True, False),
    'errors': ('Errors', str, True, False, True, False),
    'exit_code': ('Last exit code', str, False, False, False, True)
}

Metrics = Dict[str, int]


class BackupJob(TypedDict, total=False):
    start_time: int
    end_time: int
    metrics: Metrics


Section = Dict[str, BackupJob]


def parse_lnx_backup(string_table: StringTable) -> Section:

    parsed: Section = {}
    backup_job: BackupJob = {}

    for idx, line in enumerate(string_table):

        if line[0] == "==>" and line[-1] == "<==":

            # Found section beginning
            jobname = f"{' '.join(string_table[idx][1:-1])}"
            metrics: Metrics = {}
            job_stats: BackupJob = {
                "metrics": metrics
            }
            backup_job = parsed.setdefault(jobname, job_stats)

        elif backup_job and len(line) == 2:

            # Found key value pair
            key, val = line

            # Convert values
            val = int(val)

            # Append data to job information or metrics
            if key in ['start_time', 'end_time']:
                backup_job[key] = val
            else:
                metrics[key] = val  # pyright: ignore[reportPossiblyUnboundVariable]

    return parsed


def discover_lnx_backup(section: Section) -> DiscoveryResult:

    for jobname, _ in section.items():
        yield Service(item=jobname)


def _check_lnx_backup_levels(backup_job: BackupJob, params: Mapping[str, Any], metric: str):

    # Get metric specs
    label, render_func, notice_only, levels_lower, levels_upper, levels_regex = _METRIC_SPECS[metric]

    if 'metrics' not in backup_job:
        yield Result(
            state=State.UNKNOWN,
            summary='Got incomplete information for this backup',
        )
        return

    # Convert dictionaries
    if isinstance(params.get(metric), dict):
        params_any: Any = params.get(metric)
        params_dict: dict = params_any

    if levels_lower and levels_upper:
        # Metric with both levels
        yield from check_levels(
            backup_job['metrics'][metric],
            metric_name=f"lnx_backup_{metric}",
            label=label,
            levels_lower=params_dict['lower'] if params_dict['lower'] != ('no_levels', None) else None,  # pyright: ignore[reportPossiblyUnboundVariable]
            levels_upper=params_dict['upper'] if params_dict['upper'] != ('no_levels', None) else None,  # pyright: ignore[reportPossiblyUnboundVariable]
            render_func=render_func,
            notice_only=notice_only,
            boundaries=(0, None),
        )
    elif levels_regex:
        # Metrics with regular expressions
        # Check in reverse state order with "not_found" as fake state for non-matching regex
        for level in ['crit', 'warn', 'ok', 'not_found']:

            if level not in params_dict:  # pyright: ignore[reportPossiblyUnboundVariable]
                continue

            if level != 'not_found':
                regex = re.compile(f"^{params_dict[level]}$")  # pyright: ignore[reportPossiblyUnboundVariable]
                if regex.match(str(backup_job['metrics'][metric])) is not None:
                    yield Result(
                        state=State[level.upper()],
                        summary=f"{label}: {backup_job['metrics'][metric]}",
                    )
                    # Stop if regex matches
                    break
            else:
                yield Result(
                    state=State.CRIT,
                    summary=f"Got unhandled '{label}' for configured levels",
                )
    else:
        # Metric with single levels
        yield from check_levels(
            backup_job['metrics'][metric],
            metric_name=f"lnx_backup_{metric}",
            label=label,
            levels_lower=params.get(metric) if (levels_lower and params.get(metric) != ('no_levels', None)) else None,
            levels_upper=params.get(metric) if (levels_upper and params.get(metric) != ('no_levels', None)) else None,
            render_func=render_func,
            notice_only=notice_only,
            boundaries=(0, None),
        )


def _process_lnx_backup_data(backup_job: BackupJob, params: Mapping[str, Any]) -> CheckResult:

    # Calculate duration and age of last job
    if ('metrics' not in backup_job):
        metrics: Metrics = {}
        backup_job['metrics'] = metrics
    backup_job['metrics']['duration'] = backup_job.get('end_time', 0)-backup_job.get('start_time', 0)
    backup_job['metrics']['age'] = int(time.time())-backup_job.get('end_time', 0)

    # Add start notice
    yield Result(
        state=State.OK,
        notice="Latest job started at %s" % render.datetime(backup_job.get('start_time', 0)),
    )

    # Check all metrics
    for metric in sorted(backup_job['metrics']):
        yield from _check_lnx_backup_levels(backup_job, params, metric)


def check_lnx_backup(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:

    backup_job = section.get(item)
    if backup_job is None:
        return

    yield from _process_lnx_backup_data(backup_job, params)


agent_section_lnx_backup = AgentSection(
    name="lnx_backup",
    parse_function=parse_lnx_backup,
)

check_plugin_lnx_backuo = CheckPlugin(
    name="lnx_backup",
    sections=["lnx_backup"],
    service_name="Linux Backup %s",
    discovery_function=discover_lnx_backup,
    check_function=check_lnx_backup,
    check_default_parameters={
        'age':              ("fixed", (26*60*60, 50*60*60)),
        'duration':         {'lower': ('no_levels', None), 'upper': ('no_levels', None)},
        'source_files':     {'lower': ('no_levels', None), 'upper': ('no_levels', None)},
        'source_filesize':  {'lower': ('no_levels', None), 'upper': ('no_levels', None)},
        'new_files':        {'lower': ('no_levels', None), 'upper': ('no_levels', None)},
        'new_filesize':     {'lower': ('no_levels', None), 'upper': ('no_levels', None)},
        'deleted_files':    {'lower': ('no_levels', None), 'upper': ('no_levels', None)},
        'changed_files':    {'lower': ('no_levels', None), 'upper': ('no_levels', None)},
        'changed_filesize': {'lower': ('no_levels', None), 'upper': ('no_levels', None)},
        'backup_size':      {'lower': ("fixed", (1024, 2*1024)), 'upper': ('no_levels', None)},
        'errors':           ("fixed", (1,  1)),
        # Values for ok/warn/crit are regular expression(!)
        'exit_code':        {'ok': '(0)', 'warn': '(1)', 'crit': '(255)'},
    },
    check_ruleset_name="lnx_backup",
)
