#!/bin/bash

if which upsc > /dev/null 2>&1; then
  echo '<<<nut>>>'
  for ups in $(upsc -l 2>/dev/null); do
    echo "==> $ups <=="
    upsc $ups 2>/dev/null
  done
fi
