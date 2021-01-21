# From https://github.com/cncook001/check_mk/blob/master/redis/wato/plugins/check_parameters_redis_queue.py

group = "checkparams"
subgroup_applications = _("Applications, Processes &amp; Services")
register_check_parameters(
    subgroup_applications,
    "exim_mailq",
    _("Exim Mailq lenght, size, age"),
    Dictionary(
        title = _("Limits"),
        elements = [
            ("warn_length",
                  Integer(
                      title = _("Warning at length"),
                      default_value = None,
                  ),
            ),
            ("crit_length",
                  Integer(
                      title = _("Critical at lenght"),
                      default_value = None,
                  ),
            ),
            ("warn_size",
                  Integer(
                      title = _("Warning at size"),
                      default_value = None,
                  ),
            ),
            ("crit_size",
                  Integer(
                      title = _("Critical at size"),
                      default_value = None,
                  ),
            ),
            ("warn_age",
                  Integer(
                      title = _("Warning at age"),
                      default_value = None,
                  ),
            ),
            ("crit_age",
                  Integer(
                      title = _("Critical at age"),
                      default_value = None,
                  ),
            ),
        ],
        optional_keys = [ "warn_length", "crit_length", "warn_size", "crit_size", "warn_age", "crit_age" ],
    ),
    # TextAscii( title=_("Ascii title?"),
    # help=_("The name of the REDIS queue")),
    # 'first'
    match_type='dict',
)
