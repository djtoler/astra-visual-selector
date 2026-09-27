#!/bin/bash
set -euo pipefail

PIPELINE_ROOT="/Users/dwaynetoler/Documents/ChatGPT/Polish/image-sourcing-system"
PIPELINE_RUNNER="$PIPELINE_ROOT/process_media_folder.sh"
LATEST_IMGS_ROOT="${LATEST_IMGS_ROOT:-/Users/dwaynetoler/Downloads/latest_imgs}"

usage() {
  cat <<'EOF'
Usage:
  run_media_processing_pipeline.sh run <media-folder> [project-name]
  run_media_processing_pipeline.sh watch [latest_imgs-root]
  run_media_processing_pipeline.sh status [folder-run-receipt.json]
  run_media_processing_pipeline.sh finalize [folder-run-receipt.json]

Short form:
  run_media_processing_pipeline.sh <media-folder> [project-name]

Google and Instagram searches use their shared browser review first. Approved
results are staged beneath latest_imgs with provenance and then enter this same
runner automatically. Do not send a search batch directly to the legacy People
screen.
EOF
}

[ -x "$PIPELINE_RUNNER" ] || {
  printf 'Media pipeline runner is missing or not executable: %s\n' "$PIPELINE_RUNNER" >&2
  exit 1
}

command_name="${1:-help}"
case "$command_name" in
  -h|--help|help)
    usage
    ;;
  run)
    [ -n "${2:-}" ] || { usage >&2; exit 2; }
    exec "$PIPELINE_RUNNER" run "$2" "${3:-Latest media $(date +%Y-%m-%d)}"
    ;;
  watch)
    exec "$PIPELINE_RUNNER" watch "${2:-$LATEST_IMGS_ROOT}"
    ;;
  status|finalize)
    if [ -n "${2:-}" ]; then
      exec "$PIPELINE_RUNNER" "$command_name" "$2"
    fi
    exec "$PIPELINE_RUNNER" "$command_name"
    ;;
  *)
    exec "$PIPELINE_RUNNER" run "$1" "${2:-Latest media $(date +%Y-%m-%d)}"
    ;;
esac
