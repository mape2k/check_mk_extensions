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

metric_info["exim_mailq_length"] = {
    "title": _("Length"),
    "unit": "count",
    "color": "13/a",
}

metric_info["exim_mailq_size"] = {
    "title": _("Size"),
    "unit": "bytes",
    "color": "22/a",
}

metric_info["exim_mailq_age_oldest"] = {
    "title": _("Oldest mail"),
    "unit": "s",
    "color": "44/a",
}

metric_info["exim_mailq_age_newest"] = {
    "title": _("Newest mail"),
    "unit": "s",
    "color": "44/b",
}
