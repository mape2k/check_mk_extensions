<?php
# PNP4Nagios template for check_mk eximq check
#
# (c) 2015 EXA EDV GmbH
#          Marcel Pennewiß <marcel.pennewiss@exa-edv.de>
#
# Inspired by check_mk-postfix_mailq.php

# recalculate units
$warn_size = $WARN[2] / 1024.0;
$crit_size = $CRIT[2] / 1024.0;
$warn_age = $WARN[3] / 3600.0;
$crit_age = $CRIT[3] / 3600.0;

# (length=22;10;20;; size=2048;;;;)
$opt[1] = "--vertical-label Mails -l0  --title \"Mail Queue Length\" ";
$def[1] =  "DEF:length=$RRDFILE[1]:$DS[1]:MAX " ;
$def[1] .= "HRULE:$WARN[1]#FFFF00 ";
$def[1] .= "HRULE:$CRIT[1]#FF0000 ";
$def[1] .= "AREA:length#6890a0:\"Mails\" " ;
$def[1] .= "LINE:length#2060a0 " ;
$def[1] .= "GPRINT:length:LAST:\"%6.2lf last\" " ;
$def[1] .= "GPRINT:length:AVERAGE:\"%6.2lf avg\" " ;
$def[1] .= "GPRINT:length:MAX:\"%6.2lf max\\n\" ";
$def[1] .= "HRULE:$WARN[1]#FFFF00:\"Warning\: $WARN[1]\\n\" ";
$def[1] .= "HRULE:$CRIT[1]#FF0000:\"Critical\: $CRIT[1]\" ";

$opt[2] = "--vertical-label KBytes -X0 -l0 --title \"Mail Queue Size".$DS[2]."\" ";
$def[2] = "DEF:size=$RRDFILE[2]:$DS[2]:MAX " ;
$def[2] .= "CDEF:queue_kb=size,1024,/ ";
$def[2] .= "AREA:queue_kb#65ab0e:\"Kilobytes\" ";
$def[2] .= "LINE:queue_kb#206a0e ";
$def[2] .= "GPRINT:queue_kb:LAST:\"%6.2lf KB last\" ";
$def[2] .= "GPRINT:queue_kb:AVERAGE:\"%6.2lf KB avg\" " ;
$def[2] .= "GPRINT:queue_kb:MAX:\"%6.2lf KB max\\n\" ";
$def[2] .= "HRULE:$warn_size#FFFF00:\"Warning\: ".sprintf("%6.2f", $warn_size)." KB\\n\" ";
$def[2] .= "HRULE:$crit_size#FF0000:\"Critical\: ".sprintf("%6.2f", $crit_size)." KB\" ";

$opt[3] = "--vertical-label 'Hours' -l0 --title \"Age of oldest mail in Mail Queue\" ";
$def[3] = "DEF:age=$RRDFILE[3]:$DS[3]:MAX " ;
$def[3] .= "CDEF:age_d=age,3600,/ ";
$def[3] .= "AREA:age_d#80f000:\"days\" ";
$def[3] .= "LINE:age_d#408000 ";
$def[3] .= "GPRINT:age_d:LAST:\"%6.2lf hours last\" ";
$def[3] .= "GPRINT:age_d:AVERAGE:\"%6.2lf hours avg\" " ;
$def[3] .= "GPRINT:age_d:MAX:\"%6.2lf hours max\\n\" ";
$def[3] .= "HRULE:$warn_age#FFFF00:\"Warning\: ".sprintf("%6.2f", $warn_age)." hours\\n\" ";
$def[3] .= "HRULE:$crit_age#FF0000:\"Critical\: ".sprintf("%6.2f", $crit_age)." hours\" ";

?>
