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

from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import metric_info

metric_info["lnx_backup_age"] = {
    "title": _("Age"),
    "unit": "s",
    "color": "16/a",
}

metric_info["lnx_backup_duration"] = {
    "title": _("Duration"),
    "unit": "s",
    "color": "16/b",
}

metric_info["lnx_backup_errors"] = {
    "title": _("Errors"),
    "unit": "count",
    "color": "13/a",
}

metric_info["lnx_backup_backup_size"] = {
    "title": _("Backup Size"),
    "unit": "bytes",
    "color": "22/a",
}

metric_info["lnx_backup_new_files"] = {
    "title": _("New files"),
    "unit": "count",
    "color": "44/a",
}

metric_info["lnx_backup_new_filesize"] = {
    "title": _("New files - Size"),
    "unit": "bytes",
    "color": "44/b",
}

metric_info["lnx_backup_changed_files"] = {
    "title": _("Changed files"),
    "unit": "count",
    "color": "41/a",
}

metric_info["lnx_backup_changed_filesize"] = {
    "title": _("Changed files - Size"),
    "unit": "bytes",
    "color": "41/b",
}

metric_info["lnx_backup_deleted_files"] = {
    "title": _("Deleted files"),
    "unit": "bytes",
    "color": "13/a",
}

metric_info["lnx_backup_source_files"] = {
    "title": _("Source files"),
    "unit": "count",
    "color": "34/a",
}

metric_info["lnx_backup_source_filesize"] = {
    "title": _("Source files - Size"),
    "unit": "bytes",
    "color": "34/b",
}
