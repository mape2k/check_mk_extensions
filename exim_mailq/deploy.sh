#!/bin/bash

[[ -z $1 ]] && {
    echo "Usage $0 dev|prod"
    exit 1;
}

agentnametest="agents/plugins/exim_mailq-test"
agentname="agents/plugins/exim_mailq"
checkname="checks/exim_mailq"
watoplugin="wato/plugins/check_parameters_exim_mailq.py"
checkman="checkman/exim_mailq"

[[ "xdev" == "x$1" ]] && {
    # for testing and development. Not ment to be used by others
    scp $checkname test@omd.lxd:local/share/check_mk/checks/
    scp $agentnametest web.lxd:/usr/lib/check_mk_agent/plugins/$agentname
    scp $watoplugin test@omd.lxd:local/share/check_mk/web/plugins/wato/
    scp $checkman test@omd.lxd:local/share/check_mk/checkman/
    exit 0;
}

[[ "xprod" == "x$1" ]] && {
    # push to check_mk servers
    scp $checkname front@chk01.copyleft.no:local/share/check_mk/checks/
    # Checks from front should be synced here over time, but this makes it faster:
    scp $checkname cl@omdproxy01.copyleft.no:/omd/sites/cl/local/share/check_mk/checks/

#     scp $checkname root@icinga01.copyleft.no:/usr/share/check_mk/checks/
#     # push to check_mk proxies
#     scp $checkname root@chkp01.telefactory:/usr/share/check_mk/checks/
#     ssh root@chkp01.telefactory $depsinstall

#     # old puppet nodes
#     rsync -a $agentname root@icinga01.copyleft.no:/usr/lib/check_mk_agent/plugins/webchecks-agent.py
#     rsync -a $agentname root@gitlab01.copyleft.no:/usr/lib/check_mk_agent/plugins/webchecks-agent.py
#     rsync -a $agentname root@zimbra01.copyleft.no:/usr/lib/check_mk_agent/plugins/webchecks-agent.py
#     rsync -a $agentname root@hosting12.kloner.no:/usr/share/check-mk-agent/plugins/webchecks-agent.py
#     rsync -a $agentname root@hosting11.kloner.no:/usr/share/check-mk-agent/plugins/webchecks-agent.py

#     # Deploy agent to PML
#     cp agents/plugins/webchecks ../copyleft-checkmk/files/plugins/webchecks-agent.py
#     #rsync -a $agentname larsfp@terminalserver1013.copyleft:git/copyleft-checkmk/files/plugins/webchecks-agent.py ; echo "copyleft-base need commit & push"

#     # Deploy agent to legacy copyleft puppet
#     rsync -a $agentname larsfp@terminalserver1013.copyleft:git/puppet-checkmk/files/plugins/webchecks-agent.py && echo "puppet-checkmk need commit & push"

    exit 0;
}

echo "What did you do?"
exit 1;
