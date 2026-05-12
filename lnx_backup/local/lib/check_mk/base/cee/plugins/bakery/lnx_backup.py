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
    SystemBinary
)


def _get_lnx_backup_files(conf: Dict[str, Any]) -> FileGenerator:

    if conf.get("deploy"):
        yield Plugin(
            base_os=OS.LINUX,
            source=Path("lnx_backup"),
            target=Path("lnx_backup")
        )
        yield SystemBinary(
            base_os=OS.LINUX,
            source=Path('lnx_backup'),
            target=Path('../local/bin/lnx_backup')
        )


register.bakery_plugin(
    name="lnx_backup",
    files_function=_get_lnx_backup_files,
)
