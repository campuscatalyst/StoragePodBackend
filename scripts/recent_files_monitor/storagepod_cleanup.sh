#!/bin/bash

#Clean entries older than 7 days with cron

LOG_FILE="/var/log/storagepod/storagepod_recent_activity.json"
tmp=$(mktemp)

jq --arg now "$(date --iso-8601=seconds)" '
  . | map(select((.timestamp | fromdateiso8601) >= (env.now | fromdateiso8601 - (60*60*24*7))))
' "$LOG_FILE" > "$tmp" && mv "$tmp" "$LOG_FILE"

