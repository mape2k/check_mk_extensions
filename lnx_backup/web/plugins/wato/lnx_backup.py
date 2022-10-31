checkgroups = []
subgroup_applications = _("Applications, Processes & Services")

register_check_parameters(
    subgroup_applications,
    "lnx_backup",
    _("Backup Linux (rsync, tar, duply)"),
    Dictionary(
        elements = [
            ( "age",
                Tuple(
                    title = _("Age of backup"),
                    help = _("Set the warn and crit levels for the maximum age of a backup."),
                    elements = [
                        Age(
                            title = _("Warning if backup ended before"),
                            display = [ "days", "hours", "minutes" ],
                            minvalue = 60,
                            default_value = 26 * 60 * 60,
                        ),
                        Age(
                            title = _("Critical if backup ended before"),
                            display = [ "days", "hours", "minutes" ],
                            minvalue = 60,
                            default_value = 50 * 60 * 60,
                        ),
                    ],
                ),
            ),
            ( "source_files",
                Tuple(
                    title = _("Number of source files"),
                    help = _("Set the warn and crit levels for the minimum of source files"),
                    elements = [
                        Integer(title = _("Warning at"), minvalue = 0, default_value = 0),
                        Integer(title = _("Critical at"), minvalue = 0, default_value = 0),
                    ]
                )
            ),
            ( "source_filesize",
                Tuple(
                    title = _("Source filesize"),
                    help = _("Set the warn and crit levels for the minimum source filesize."),
                    elements = [
                         Filesize(title = _("Warning at"), minvalue = 0, default_value = 0),
                         Filesize(title = _("Critical at"), minvalue = 0, default_value = 0),
                    ],
                ),

            ),
            ( "new_files",
                Tuple(
                    title = _("Number of new files"),
                    help = _("Set the warn and crit levels for the minimum of new files"),
                    elements = [
                        Integer(title = _("Warning at"), minvalue = 0, default_value = 0),
                        Integer(title = _("Critical at"), minvalue = 0, default_value = 0),
                    ]
                )
            ),
            ( "new_filesize",
                Tuple(
                    title = _("New filesize"),
                    help = _("Set the warn and crit levels for the minimum new filesize."),
                    elements = [
                         Filesize(title = _("Warning at"), minvalue = 0, default_value = 0),
                         Filesize(title = _("Critical at"), minvalue = 0, default_value = 0),
                    ],
                ),

            ),
            ( "deleted_files",
                Tuple(
                    title = _("Number of deleted files"),
                    help = _("Set the warn and crit levels for the minimum of deleted files"),
                    elements = [
                        Integer(title = _("Warning at"), minvalue = 0, default_value = 0),
                        Integer(title = _("Critical at"), minvalue = 0, default_value = 0),
                    ]
                )
            ),
            ( "changed_files",
                Tuple(
                    title = _("Number of changed files"),
                    help = _("Set the warn and crit levels for the minimum of changed files"),
                    elements = [
                        Integer(title = _("Warning at"), minvalue = 0, default_value = 0),
                        Integer(title = _("Critical at"), minvalue = 0, default_value = 0),
                    ]
                )
            ),
            ( "changed_filesize",
                Tuple(
                    title = _("Changed filesize"),
                    help = _("Set the warn and crit levels for the minimum changed filesize."),
                    elements = [
                         Filesize(title = _("Warning at"), minvalue = 0, default_value = 0),
                         Filesize(title = _("Critical at"), minvalue = 0, default_value = 0),
                    ],
                ),

            ),
            ( "backup_size",
                Tuple(
                    title = _("Backup size"),
                    help = _("Set the warn and crit levels for the minimum backup size."),
                    elements = [
                         Filesize(title = _("Warning at"), minvalue = 0, default_value = 1024),
                         Filesize(title = _("Critical at"), minvalue = 0, default_value = 1024),
                    ],
                ),

            ),
            ( "errors",
                Tuple(
                    title = _("Number of errors"),
                    help = _("Set the warn and crit levels for the maximum of errors"),
                    elements = [
                        Integer(title = _("Warning at"), minvalue = 0, default_value = 1),
                        Integer(title = _("Critical at"), minvalue = 0, default_value = 1),
                    ]
                )
            ),
            ( "exit_code",
                Tuple(
                    title = _("Exit code"),
                    help = _("Set the warn and crit levels for the minimal exit code"),
                    elements = [
                        Integer(title = _("Warning at"), minvalue = 0, default_value = 1),
                        Integer(title = _("Critical at"), minvalue = 0, default_value = 1),
                    ]
                )
            ),
        ],
        optional_keys = ["age", "source_files", "source_filesize", "new_files", "new_filesize", "deleted_files", "changed_files","changed_filesize", "backup_size", "errors", "exit_code"]
    ),
    TextAscii(
        title = _("Backup"),
        help = _("The identifier of the backup.")
    ),
    "dict",
)
