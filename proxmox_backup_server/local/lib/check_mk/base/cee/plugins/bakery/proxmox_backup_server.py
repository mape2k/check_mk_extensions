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
from typing import Any, Dict

from cmk.base.plugins.bakery.bakery_api.v1 import (
    FileGenerator,
    OS,
    Plugin,
    register,
)


def _get_proxmox_backup_server_files(conf: Dict[str, Any]) -> FileGenerator:

    interval = conf.get("interval", 0)

    if conf.get("deploy"):
        target_path = "proxmox_backup_server.py"
        if interval > 0:
            target_path = f"{interval}/{target_path}"

        yield Plugin(
            base_os=OS.LINUX,
            source=Path("proxmox_backup_server.py"),
            target=Path(target_path)
        )


register.bakery_plugin(
    name="proxmox_backup_server",
    files_function=_get_proxmox_backup_server_files,
)
