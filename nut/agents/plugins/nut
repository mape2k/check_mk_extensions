#!/bin/bash

which upsc >/dev/null 2>&1 || exit 0

echo '<<<nut>>>'

hosts=`(
  if which awk >/dev/null 2>&1; then
    for file in /etc/nut/upsmon.conf; do
      [ -f $file ] || continue
      grep "^MONITOR\s" $file
    done | awk '{if(split($2, parts, "@") >= 2) { print parts[2] } }'
  fi
  echo localhost # make sure localhost is on the list
) | sort -u`
for host in $hosts; do
  for ups in $(upsc -l $host 2>/dev/null); do
    if [ "$host" = "localhost" ]; then
      echo "==> $ups <=="
    else
      echo "==> $ups@$host <=="
    fi
    upsc $ups@$host 2>/dev/null
  done
done
