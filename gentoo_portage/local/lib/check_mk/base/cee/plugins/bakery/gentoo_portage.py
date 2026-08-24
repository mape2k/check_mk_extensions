#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) 2026 Marcel Pennewiss <opensource@pennewiss.de>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License. This program
# is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details. You should have received a copy of the GNU
# General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA.

from pathlib import Path
from typing import TypedDict

from cmk.base.plugins.bakery.bakery_api.v1 import (
    FileGenerator,
    OS,
    Plugin,
    register,
)


class GentooPortageConfig(TypedDict, total=False):
    # Private variables just for bakery configuration
    _deploy: bool
    _interval: float


def _get_gentoo_portage_files(conf: GentooPortageConfig) -> FileGenerator:

    _interval = conf.get("_interval", 0)

    if conf.get("_deploy"):
        yield Plugin(
            base_os=OS.LINUX,
            source=Path("gentoo_portage.py"),
            target=Path("gentoo_portage.py"),
            interval=int(_interval) if _interval > 0 else None
        )


register.bakery_plugin(
    name="gentoo_portage",
    files_function=_get_gentoo_portage_files,
)
