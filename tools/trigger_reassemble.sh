#!/usr/bin/env bash
# Trigger reassembly of a failed/killed production run with ONE API call.
# Usage: GITHUB_TOKEN=<token> ./trigger_reassemble.sh <source_run_id> [vo_file] [bed_file]
# Rule: assembly death NEVER re-renders chunks. This dispatches ONLY the
# reassemble workflow against the failed run's already-rendered chunks.
set -euo pipefail

REPO="${REPO:-wastor453-ux/rendering-production}"
SOURCE_RUN_ID="${1:?Usage: $0 <source_run_id> [vo_file] [bed_file]}"
VO_FILE="${2:-public/audio/vo_p3.wav}"
BED_FILE="${3:-public/audio/bed.mp3}"
TOKEN="${GITHUB_TOKEN:?Set GITHUB_TOKEN env var}"

PAYLOAD=$(python3 -c "
import json,sys
print(json.dumps({
  'event_type': 'reassemble',
  'client_payload': {
    'source_run_id': '$SOURCE_RUN_ID',
    'vo_file': '$VO_FILE',
    'bed_file': '$BED_FILE',
  }
}))")

curl -sS -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "User-Agent: cosmo-reassemble-trigger" \
  "https://api.github.com/repos/$REPO/dispatches" \
  -d "$PAYLOAD" && echo && echo "Reassembly dispatched for run $SOURCE_RUN_ID"
