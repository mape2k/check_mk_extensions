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


from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph
from cmk.graphing.v1.metrics import (
    Color,
    DecimalNotation,
    Metric,
    StrictPrecision,
    Unit,
)

from cmk.graphing.v1.perfometers import (
    Closed,
    FocusRange,
    Open,
    Perfometer,
    Stacked,
)

UNIT_COUNTER = Unit(DecimalNotation(""), StrictPrecision(0))

metric_gentoo_portage_updates_newslot = Metric(
    name="gentoo_portage_updates_newslot",
    title=Title("Pending updates in new slots"),
    unit=UNIT_COUNTER,
    color=Color.ORANGE,
)

metric_gentoo_portage_updates_update = Metric(
    name="gentoo_portage_updates_update",
    title=Title("Pending normal updates"),
    unit=UNIT_COUNTER,
    color=Color.YELLOW,
)

metric_gentoo_portage_glsa_impact_low = Metric(
    name="gentoo_portage_glsa_impact_low",
    title=Title("Gentoo Linux Security Advisory - Impact: Low"),
    unit=UNIT_COUNTER,
    color=Color.LIGHT_ORANGE,
)

metric_gentoo_portage_glsa_impact_normal = Metric(
    name="gentoo_portage_glsa_impact_normal",
    title=Title("Gentoo Linux Security Advisory - Impact: Normal"),
    unit=UNIT_COUNTER,
    color=Color.LIGHT_RED,
)

metric_gentoo_portage_glsa_impact_high = Metric(
    name="gentoo_portage_glsa_impact_high",
    title=Title("Gentoo Linux Security Advisory - Impact: High"),
    unit=UNIT_COUNTER,
    color=Color.RED,
)

metric_gentoo_portage_glsa_packages = Metric(
    name="gentoo_portage_glsa_packages",
    title=Title("Affected packages in Gentoo Linux Security Advisory"),
    unit=UNIT_COUNTER,
    color=Color.DARK_RED,
)

perfometer_gentoo_portage_updates = Stacked(
    name="perfometer_gentoo_portage_updates",
    lower=Perfometer(
        name="lower",
        focus_range=FocusRange(Closed(0), Open(20)),
        segments=["gentoo_portage_glsa_packages"],
    ),
    upper=Perfometer(
        name="upper",
        focus_range=FocusRange(Closed(0), Open(20)),
        segments=["gentoo_portage_updates_update"],
    ),
)

graph_gentoo_portage_updates = Graph(
    name="graph_gentoo_portage_updates",
    title=Title("Pending updates"),
    compound_lines=[
        "gentoo_portage_updates_update",
        "gentoo_portage_updates_newslot",
    ],
)

graph_gentoo_portage_glsa = Graph(
    name="graph_gentoo_portage_GLSA",
    title=Title("Gentoo Linux Security Advisory"),
    compound_lines=[
        "gentoo_portage_glsa_impact_low",
        "gentoo_portage_glsa_impact_normal",
        "gentoo_portage_glsa_impact_high",
    ],
)
