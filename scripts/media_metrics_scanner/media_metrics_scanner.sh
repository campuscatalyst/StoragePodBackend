#!/bin/bash

# This will dynamically fetch the path for the folder1 mounted. The folder dev-disk-* will vary from device to device
BASE_DIR=$(find /srv -maxdepth 2 -type d -name "Folder1" -path "/srv/dev-disk-*/Folder1" | head -n 1)
METRICS_FILE="${2:-/var/log/storagepod/metrics.json}"

if [[ "$1" == "--help" || "$1" == "-h" ]]; then
	echo "Usage: $0 [directory_to_scan] [output_json_file]"
	echo "  Example: $0 /home/user/media /tmp/results.json"
	exit 0
fi

if [[ ! -d "$BASE_DIR" ]]; then
	echo "Error: Directory '$BASE_DIR' does not exist!" >&2
  	exit 1
fi

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT  # Clean up temp directory on exit

IMAGE_EXTENSIONS=("jpg" "jpeg" "png" "gif" "bmp" "tiff" "webp")
VIDEO_EXTENSIONS=("mp4" "mkv" "mov" "avi" "wmv" "flv" "webm" "m4v")
AUDIO_EXTENSIONS=("mp3" "wav" "flac" "ogg" "aac" "m4a" "wma")
DOCUMENT_EXTENSIONS=("pdf" "doc" "docx" "xls" "xlsx" "ppt" "pptx" "txt")

find_files_by_extensions() {
 	local dir="$1"
	local output_file="$2"
	shift 2
	local extensions=("$@")
	local find_args=()

  	for ext in "${extensions[@]}"; do
    		find_args+=(-o -iname "*.$ext")
  	done

  	# Remove the first "-o" since we don't need it
 	find_args=("${find_args[@]:1}")

  	# Run find and save results to temp file
  	find "$dir" -type f \( "${find_args[@]}" \) > "$output_file" 2>/dev/null
}

find_files_by_extensions "$BASE_DIR" "$TEMP_DIR/images.txt" "${IMAGE_EXTENSIONS[@]}"
find_files_by_extensions "$BASE_DIR" "$TEMP_DIR/videos.txt" "${VIDEO_EXTENSIONS[@]}"
find_files_by_extensions "$BASE_DIR" "$TEMP_DIR/audio.txt" "${AUDIO_EXTENSIONS[@]}"
find_files_by_extensions "$BASE_DIR" "$TEMP_DIR/documents.txt" "${DOCUMENT_EXTENSIONS[@]}"

images=$(wc -l < "$TEMP_DIR/images.txt")
videos=$(wc -l < "$TEMP_DIR/videos.txt")
music=$(wc -l < "$TEMP_DIR/audio.txt")
documents=$(wc -l < "$TEMP_DIR/documents.txt")
total_files=$(find "$BASE_DIR" -type f | wc -l)

current_date=$(date "+%Y-%m-%d %H:%M:%S")

cat <<EOF > "$METRICS_FILE"
{
  "scan_info": {
    "date": "$current_date",
    "directory": "$BASE_DIR"
  },
  "media_counts": {
    "images": $images,
    "videos": $videos,
    "audio": $music,
    "documents": $documents,
    "total_files": $total_files
  }
}
EOF

echo "Scan completed successfully!"