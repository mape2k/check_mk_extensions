#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) 2022 Marcel Pennewiss <opensource@pennewiss.de>
# (c) 2025 Erik Stomp <mail@erik-stomp.de> - Updated Plugin to graphing API v1

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

from cmk.graphing.v1 import Title
from cmk.graphing.v1.metrics import Color, DecimalNotation, Metric, Unit, StrictPrecision, IECNotation
from cmk.graphing.v1.perfometers import Closed, FocusRange, Open, Perfometer

metric_exim_mailq_length = Metric(
    name = "exim_mailq_length",
    title = Title("Length"),
    unit = Unit(DecimalNotation(""), StrictPrecision(0)),
    color = Color.ORANGE,
)

metric_exim_mailq_size = Metric(
    name = "exim_mailq_size",
    title = Title("Size"),
    unit = Unit(IECNotation("")),
    color = Color.BLUE,
)

metric_exim_mailq_age_oldest = Metric(
    name = "exim_mailq_age_oldest",
    title = Title("Oldest mail"),
    unit = Unit(DecimalNotation("s"), StrictPrecision(0)),
    color = Color.RED,
)

metric_exim_mailq_age_newest = Metric(
    name = "exim_mailq_age_newest",
    title = Title("Newest mail"),
    unit = Unit(DecimalNotation("s"), StrictPrecision(0)),
    color = Color.GREEN,
)

perfometer_exim_mailq = Perfometer(
    name = "exim_mailq",
    focus_range = FocusRange(Closed(0),Open(25)),
    segments = ["exim_mailq_length"]
)