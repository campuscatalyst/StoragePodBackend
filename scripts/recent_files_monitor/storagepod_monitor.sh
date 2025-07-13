#!/bin/bash

LOG_FILE="/var/log/storagepod/storagepod_recent_activity.json"
BASE="/srv"
# Find the first dev-disk-* path
WATCH_DIR=$(find "$BASE" -maxdepth 1 -type d -name "dev-disk-*" | head -n1)/Folder1

if [ ! -d "$WATCH_DIR" ]; then
    echo "Watch folder not found: $WATCH_DIR"
    exit 1
fi

# this command will extract the directory name from the given log file, which we will create it not exists
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

echo "Watching: $WATCH_DIR"

# Append JSON entries on file create/modify
inotifywait -m -r -e create -e modify --format '%e %w%f' "$WATCH_DIR" | while read event fullpath; do
    timestamp=$(date --iso-8601=seconds)

    tmp=$(mktemp)
    jq --arg path "$fullpath" --arg event "$event" --arg timestamp "$timestamp" \
        '. += [{"path": $path, "event": $event, "timestamp": $timestamp}]' "$LOG_FILE" > "$tmp" && mv "$tmp" "$LOG_FILE"
done