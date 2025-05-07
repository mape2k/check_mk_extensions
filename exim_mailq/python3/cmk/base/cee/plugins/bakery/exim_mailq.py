#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) 2025 Erik Stomp <mail@erik-stomp.de>

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

from .bakery_api.v1 import (
    OS,
    Plugin,
    register,
    FileGenerator,
)

def get_exim_mailq_plugin_files() -> FileGenerator:

    yield Plugin(
        base_os = OS.LINUX,
        source = Path('exim_mailq'),
    )

register.bakery_plugin(
    name = "exim_mailq",
    files_function = get_exim_mailq_plugin_files
)