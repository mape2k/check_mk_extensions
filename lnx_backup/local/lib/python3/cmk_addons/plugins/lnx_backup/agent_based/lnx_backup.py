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

_METRIC_SPECS: Mapping[str, Tuple[str, Callable, bool, bool, bool]] = {
    # 'metric': ('Metric Name', renderer, notice_only, Levels are lower levels, Levels are upper levels)
    'age': ('Job age', render.timespan, False, False, True),
    'duration': ('Backup duration', render.timespan, False, False, True),
    'source_files': ('Files', str, True, True, False),
    'source_filesize': ('Filesize', render.bytes, True, True, False),
    'new_files': ('New Files', str, True, True, False),
    'new_filesize': ('New Filesize', render.bytes, True, True, False),
    'deleted_files': ('Deleted Files', str, True, True, False),
    'changed_files': ('Changed Files', str, True, True, False),
    'changed_filesize': ('Changed Filesize', render.bytes, True, True, False),
    'backup_size': ('Backup size', render.bytes, True, True, False),
    'errors': ('Errors', str, True, False, True),
}

Metrics = Dict[str, int]


class BackupJob(TypedDict, total=False):
    start_time: int
    end_time: int
    exit_code: int
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
                "exit_code": -1,
                "metrics": metrics
            }
            backup_job = parsed.setdefault(jobname, job_stats)

        elif backup_job and len(line) == 2:

            # Found key value pair
            key, val = line

            # Convert values
            val = int(val)

            # Append data to job information or metrics
            if key in ['start_time', 'end_time', 'exit_code']:
                backup_job[key] = val
            else:
                metrics[key] = val  # pyright: ignore[reportPossiblyUnboundVariable]

    return parsed


def discover_lnx_backup(section: Section) -> DiscoveryResult:

    for jobname, _ in section.items():
        yield Service(item=jobname)


def _check_lnx_backup_levels(backup_job: BackupJob, params: Mapping[str, Any], metric: str):

    # Get metric specs
    label, render_func, notice_only, levels_lower, levels_upper = _METRIC_SPECS[metric]

    if 'metrics' not in backup_job:
        yield Result(
            state=State.UNKNOWN,
            summary='Got incomplete information for this backup',
        )
        return

    yield from check_levels(
        backup_job['metrics'][metric],
        metric_name=f"lnx_backup_{metric}",
        label=label,
        levels_lower=params.get(metric) if (levels_lower and params.get(metric) != (0, 0)) else None,
        levels_upper=params.get(metric) if (levels_upper and params.get(metric) != (0, 0)) else None,
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

    # Check exit codes with regular expressions
    if isinstance(params.get('exit_code'), dict):
        params_exit_code: Any = params.get('exit_code')
        params_exit_code_dict: dict = params_exit_code

        # Check exit codes with regular expressions
        # in reverse state order with "not_found" as
        # fake state for non-matching exit_code
        for level in ['crit', 'warn', 'ok', 'not_found']:

            if level != 'not_found':
                regex = re.compile(f"^{params_exit_code_dict[level]}$")
                if regex.match(str(backup_job.get('exit_code', -1))) is not None:
                    yield Result(
                        state=State[level.upper()],
                        summary=f"Last exit code: {backup_job.get('exit_code')}",
                    )
                    # Stop if regex matches
                    break
            else:
                yield Result(
                    state=State.CRIT,
                    summary='Got unhandled exit_code for levels',
                )

    else:
        yield Result(
            state=State.UNKNOWN,
            summary='Got invalid parameters for exit_code levels',
        )


def check_lnx_backup(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:

    # print(params)
    backup_job = section.get(item)
    if backup_job is None:
        return

    if backup_job.get("exit_code") == -1:
        yield Result(
            state=State.UNKNOWN,
            summary='Got incomplete information for this backup',
        )
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
        'age':              ("fixed", (93600, 180000)),
        'source_files':     ("fixed", (0,  0)),
        'source_filesize':  ("fixed", (0,  0)),
        'new_files':        ("fixed", (0,  0)),
        'new_filesize':     ("fixed", (0,  0)),
        'deleted_files':    ("fixed", (0,  0)),
        'changed_files':    ("fixed", (0,  0)),
        'changed_filesize': ("fixed", (0,  0)),
        'backup_size':      ("fixed", (1024, 2048)),
        'errors':           ("fixed", (1,  1)),
        # Values for ok/warn/crit are regular expression(!)
        'exit_code':        {'ok': '(0)', 'warn': '(1)', 'crit': '(255)'},
    },
    check_ruleset_name="lnx_backup",
)
