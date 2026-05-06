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
from cmk.gui.valuespec import (
    Age,
    Dictionary,
    DropdownChoice,
    TextAscii,
    Tuple,
    ListOf,
    Integer,
    MonitoringState,
)

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)

def _item_valuespec_lnx_backup():
    return TextAscii(
            title=_("Backup"),
            help = _("The name of the backup.")
    )

def _parameter_valuespec_lnx_backup():
    return Dictionary(elements=[
        ("age",
         Tuple(
             title=_("Age"),
             help = _("Set the levels for the maximum age of a backup."),
             elements=[
                 Age(title=_("Warning at"), default_value=25*60*60),
                 Age(title=_("Critical at"), default_value=49*60*60),
             ],
         )),
        ("duration",
         Tuple(
             title=_("Duration"),
             help = _("Set the levels for the maximum duration of a backup."),
             elements=[
                 Age(title=_("Warning at"), default_value=0),
                 Age(title=_("Critical at"), default_value=0),
             ],
         )),
        ("source_files",
         Tuple(
             title = _("Source files"),
             help = _("Set the levels for the minimum of source files."),
             elements = [
                 Integer(title = _("Warning at"), minvalue = 0, default_value = 0),
                 Integer(title = _("Critical at"), minvalue = 0, default_value = 0),
             ],
         )),
        ("source_filesize",
         Tuple(
             title = _("Source files - Size"),
             help = _("Set the levels for the minimum source file size."),
             elements = [
                 Filesize(title = _("Warning at"), minvalue = 0, default_value = 0),
                 Filesize(title = _("Critical at"), minvalue = 0, default_value = 0),
             ],
         )),
        ("new_files",
         Tuple(
             title = _("New files"),
             help = _("Set the levels for the minimum of new files."),
             elements = [
                 Integer(title = _("Warning at"), minvalue = 0, default_value = 0),
                 Integer(title = _("Critical at"), minvalue = 0, default_value = 0),
             ],
         )),
        ("new_filesize",
         Tuple(
             title = _("New files - Size"),
             help = _("Set the levels for the minimum new file size."),
             elements = [
                 Filesize(title = _("Warning at"), minvalue = 0, default_value = 0),
                 Filesize(title = _("Critical at"), minvalue = 0, default_value = 0),
             ],
         )),
        ("deleted_files",
         Tuple(
             title = _("Deleted files"),
             help = _("Set the levels for the minimum of deleted files."),
             elements = [
                 Integer(title = _("Warning at"), minvalue = 0, default_value = 0),
                 Integer(title = _("Critical at"), minvalue = 0, default_value = 0),
             ],
         )),
        ("changed_files",
         Tuple(
             title = _("Changed files"),
             help = _("Set the levels for the minimum of changed files."),
             elements = [
                 Integer(title = _("Warning at"), minvalue = 0, default_value = 0),
                 Integer(title = _("Critical at"), minvalue = 0, default_value = 0),
             ]
         )),
        ("changed_filesize",
         Tuple(
             title = _("Changed files - Size"),
             help = _("Set the levels for the minimum changed filesize."),
             elements = [
                 Filesize(title = _("Warning at"), minvalue = 0, default_value = 0),
                 Filesize(title = _("Critical at"), minvalue = 0, default_value = 0),
             ],
         )),
        ("backup_size",
         Tuple(
             title = _("Backup size"),
             help = _("Set the levels for the minimum backup size."),
             elements = [
                 Filesize(title = _("Warning at"), minvalue = 0, default_value = 1024),
                 Filesize(title = _("Critical at"), minvalue = 0, default_value = 1024),
             ],
         )),
       ("errors",
        Tuple(
            title = _("Errors"),
            help = _("Set the levels for the maximum of errors."),
            elements = [
                Integer(title = _("Warning at"), minvalue = 0, default_value = 1),
                Integer(title = _("Critical at"), minvalue = 0, default_value = 1),
            ],
        )),
       ("exit_code",
        Tuple(
            title = _("Exit code"),
            help = _("Set the levels for the minimal exit code."),
            elements = [
                Integer(title = _("Warning at"), minvalue = 0, default_value = 1),
                Integer(title = _("Critical at"), minvalue = 0, default_value = 1),
            ]
        )),
    ],)


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="lnx_backup",
        group=RulespecGroupCheckParametersApplications,
        match_type="dict",
        item_spec=_item_valuespec_lnx_backup,
        parameter_valuespec=_parameter_valuespec_lnx_backup,
        title=lambda: _("Linux Backup"),
    ))
