#!/bin/zsh
# Run ANY command that hits DuckDuckGo (beat_source.py sourcing / --beats, whatif_photos.py) under a global lock,
# so parallel agents never query DDG at the same time (it throttles and returns junk).
# Usage: ./ddg_lock.sh <command...>     (waits for the lock; a lock older than 20 min is treated as stale)
LOCK=/tmp/ddg.lock
while ! mkdir $LOCK 2>/dev/null; do
  if [[ -d $LOCK ]]; then
    age=$(( $(date +%s) - $(stat -f %m $LOCK) ))
    (( age > 1200 )) && rmdir $LOCK 2>/dev/null
  fi
  sleep $(( 3 + RANDOM % 5 ))
done
trap 'rmdir $LOCK 2>/dev/null' EXIT INT TERM
# 10-minute watchdog so a hung DDG call cannot hold the lock forever
"$@" &
pid=$!
( sleep 600; kill $pid 2>/dev/null ) </dev/null >/dev/null 2>&1 & wd=$!
wait $pid; rc=$?
kill $wd 2>/dev/null
exit $rc
