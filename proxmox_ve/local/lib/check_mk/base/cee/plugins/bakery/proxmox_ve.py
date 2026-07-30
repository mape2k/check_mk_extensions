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

from pathlib import Path
from typing import List, TypedDict, get_type_hints

from cmk.base.plugins.bakery.bakery_api.v1 import (
    FileGenerator,
    OS,
    Plugin,
    PluginConfig,
    password_store,
    register,
)


class ProxmoxVEConfigAPI(TypedDict, total=False):
    api_token_id: str
    # Use Secret in bakery_api.v2 later, once it is stable.
    api_token_secret: tuple


class ProxmoxVEConfigUser(TypedDict, total=False):
    username: str
    # Use Secret in bakery_api.v2 later, once it is stable.
    password: tuple


class ProxmoxVEConfig(TypedDict, total=False):
    # Private variables just for bakery configuration
    _deploy: bool
    _interval: float
    # Variables for configuration file
    host: str
    api: ProxmoxVEConfigAPI
    userpass: ProxmoxVEConfigUser
    port: int
    no_cert_check: bool
    timeout: int
    log_cutoff_weeks: int


def _lookup_for_bakery(pw_id: str) -> str:
    """Source: https://github.com/HeinleinSupport/check_mk_extensions/blob/cmk2.4/ox_filestore/lib/python3/cmk/base/cee/plugins/bakery/ox_filestore.py"""
    return password_store.lookup(password_store.password_store_path(), pw_id)


def _get_password(v):
    """Source: https://github.com/HeinleinSupport/check_mk_extensions/blob/cmk2.4/ox_filestore/lib/python3/cmk/base/cee/plugins/bakery/ox_filestore.py"""
    if isinstance(v, tuple):
        if v[0] == "cmk_postprocessed":
            if v[1] == "explicit_password":
                return v[2][1]
            if v[1] == "stored_password":
                return _lookup_for_bakery(v[2][0])
    return None


def _get_proxmox_ve_files(conf: ProxmoxVEConfig) -> FileGenerator:

    _interval = conf.get("_interval", 0)

    if conf.get("_deploy"):
        yield Plugin(
            base_os=OS.LINUX,
            source=Path("proxmox_ve.py"),
            target=Path("proxmox_ve.py"),
            interval=int(_interval) if _interval > 0 else None
        )
        yield PluginConfig(
            base_os=OS.LINUX,
            lines=_get_proxmox_ve_config_lines(conf),
            target=Path('proxmox_ve.cfg'),
            include_header=True
        )


def _get_proxmox_ve_config_lines(conf: ProxmoxVEConfig) -> List[str]:

    config_lines = []
    for varname, vartype in get_type_hints(ProxmoxVEConfig).items():

        if varname not in conf or varname.startswith("_"):
            # Ignore "private" an non-configured vars
            continue

        if vartype is ProxmoxVEConfigAPI:
            # API Token
            config_lines.append(f'api_token_id = "{conf[varname].get('api_token_id', '')}"')
            config_lines.append(f'api_token_secret = "{_get_password(conf[varname].get('api_token_secret'))}"')
        elif vartype is ProxmoxVEConfigUser:
            # User credentials
            config_lines.append(f'username = "{conf[varname].get('username', '')}"')
            config_lines.append(f'password = "{_get_password(conf[varname].get('password'))}"')
        else:
            # Create type based config lines
            if vartype is str:
                config_lines.append(f'{varname} = "{conf[varname]}"')
            elif vartype is bool:
                config_lines.append(f'{varname} = {str(conf[varname]).lower()}')
            else:
                config_lines.append(f'{varname} = {conf[varname]}')

    return config_lines


register.bakery_plugin(
    name="proxmox_ve",
    files_function=_get_proxmox_ve_files,
)
