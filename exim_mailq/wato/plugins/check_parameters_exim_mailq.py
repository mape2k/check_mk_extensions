# From https://github.com/cncook001/check_mk/blob/master/redis/wato/plugins/check_parameters_redis_queue.py

#group = "exim_mailq"
#subgroup_applications = _("Applications, Processes &amp; Services")
register_check_parameters(
    subgroup_applications,
    "exim_mailq",
    _("Exim_Mailq"),
    Dictionary(
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
    TextAscii( title=_("Exim mailq"), allow_empty = True),
    match_type='dict',
)
