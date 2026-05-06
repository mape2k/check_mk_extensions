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

# <<<lnx_backup>>>
# ==> backup_name backup_type <==
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

Metrics = Dict[str, int]


class BackupJob(TypedDict, total=False):
    start_time: int
    end_time: int
    exit_code: int
    metrics: Metrics


Section = Dict[str, BackupJob]


def lnx_backup_parse(string_table: type_defs.StringTable) -> Section:
    parsed: Section = {}
    backup_job: BackupJob = {}
    for idx, line in enumerate(string_table):

        if line[0] == "==>" and line[-1] == "<==":
            # Found section beginning
            jobname = " ".join(string_table[idx][1:-1])
            metrics: Metrics = {}
            job_stats: BackupJob = {
                "exit_code": -1,
                "metrics": metrics
            }
            backup_job = parsed.setdefault(jobname, job_stats)

        elif backup_job and len(line) == 2:
            # Found key value pair
            key, val = line
            # Convert several keys/values
            if key in [ 'start_time', 'end_time' ]:
            #    val = datetime.datetime.fromtimestamp(int(val))
                val = int(val)
            elif key in [ 'exit_code', 'source_files', 'new_files', 'deleted_files', 'changed_files', 'errors' ]:
                val = int(val)
            elif key in [ 'source_filesize', 'new_filesize', 'deleted_filesize', 'changed_filesize', 'backup_size' ]:
                #key = key.replace('kbytes', 'bytes')
                val = int(val)

            # Append data to job information or metrics
            if key in ['start_time', 'end_time', 'exit_code']:
                backup_job[key] = val
            else:
                metrics[key] = val

    return parsed


def discover_lnx_backup(section: Section) -> type_defs.DiscoveryResult:
    for jobname, backup_job in section.items():
        yield Service(item=jobname)


#_METRIC_SPECS: Mapping[str, Tuple[str, Callable, bool, Tuple[int, int], Tuple[int, int]]] = {
_METRIC_SPECS: Mapping[str, Tuple[str, Callable, bool, bool, bool]] = {
    # 'metric': ('Metric Name', renderer, notice_only, (lower_warn, lower_crit), (upper_warn, upper_crit))
    #'age': ('Job age', render.timespan, False, (0,0), (90000, 176400)),
    #'duration': ('Backup duration', render.timespan, False, (0,0), (0,0)),
    #'source_files': ('Files', str, True, (0,0), (0,0)),
    #'source_filesize': ('Filesize', render.bytes, True, (0,0), (0,0)),
    #'new_files': ('New Files', str, True, (0,0), (0,0)),
    #'new_filesize': ('New Filesize', render.bytes, True, (0,0), (0,0)),
    #'deleted_files': ('Deleted Files', str, True, (0,0), (0,0)),
    #'changed_files': ('Changed Files', str, True, (0,0), (0,0)),
    #'changed_filesize': ('Changed Filesize', render.bytes, True, (0,0), (0,0)),
    #'backup_size': ('Backup size', render.bytes, True, (1024, 2048), (0,0)),
    #'errors': ('Errors', str, True, (0,0), (1,1)),
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


def _check_lnx_backup_levels(backup_job: BackupJob, params: Mapping[str, Any], metric: str):
    label, render_func, notice_only, levels_lower, levels_upper = _METRIC_SPECS[metric]
    yield from check_levels(
        backup_job['metrics'][metric],
        metric_name="lnx_backup_%s" % metric,
        label=label,
        levels_lower=params.get(metric) if (levels_lower and params.get(metric) != (0,0)) else None,
        levels_upper=params.get(metric) if (levels_upper and params.get(metric) != (0,0)) else None,
        render_func=render_func,
        notice_only=notice_only,
        boundaries=(0, None),
    )


def _process_lnx_backup_data(
    backup_job: BackupJob,
    params: Mapping[str, Any],
    exit_code_to_state_map: Dict[int, State],
) -> type_defs.CheckResult:

    yield Result(
        state=exit_code_to_state_map.get(backup_job['exit_code'], State.CRIT),
        summary=f"Latest exit code: {backup_job['exit_code']}",
    )

    # Calculate duration and age of last job
    backup_job['metrics']['duration'] = backup_job['end_time']-backup_job['start_time']
    backup_job['metrics']['age'] = time.time()-backup_job['end_time']

    yield Result(
        state=State.OK,
        notice="Latest job started at %s" % render.datetime(backup_job['start_time']),
    )

    for metric in sorted(backup_job['metrics']):
        #yield from _check_lnx_backup_levels(backup_job, param, metric)
        yield from _check_lnx_backup_levels(backup_job, params, metric)


def check_lnx_backup(item: str, params: Mapping[str, Any], section: Section) -> type_defs.CheckResult:

    backup_job = section.get(item)
    if backup_job is None:
        return

    if backup_job.get("exit_code") == -1:
        yield Result(
            state=State.UNKNOWN,
            summary='Got incomplete information for this backup',
        )
        return

    yield from _process_lnx_backup_data(
       backup_job,
       params,
       {
           0: State.OK,
           **{k: State(v) for k, v in params.get('exit_code_to_state_map', [])}
       },
   )


register.agent_section(
    name = "lnx_backup",
    parse_function = lnx_backup_parse
)


register.check_plugin(
    name = "lnx_backup",
    service_name = "Linux Backup %s",
    discovery_function = discover_lnx_backup,
    check_function = check_lnx_backup,
    check_default_parameters = {
        'age':              (93600, 180000),
        'source_files':     (0,  0),
        'source_filesize':  (0,  0),
        'new_files':        (0,  0),
        'new_filesize':     (0,  0),
        'deleted_files':    (0,  0),
        'changed_files':    (0,  0),
        'changed_filesize': (0,  0),
        'backup_size':      (1024, 2048),
        'errors':           (1,  1),
        'exit_code':        (1,  1),
    },
    check_ruleset_name="lnx_backup",
)
