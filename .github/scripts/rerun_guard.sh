#!/bin/bash
# R-013: Stale-rerun guard. GitHub may permit reruns against an older workflow
# revision. A rerun (attempt > 1) must fail before any rendering or publication.
#
# Usage: rerun_guard.sh <attempt>
#   attempt 1  -> prints pass message, exit 0
#   attempt >1 -> prints fatal message, exit 1
#
# The workflow binds github.run_attempt to the argument; this script owns the
# fail-closed logic and is regression-tested. The binding itself can only be
# proven by a hosted rerun (see R-013 limitation note).
set -euo pipefail

ATTEMPT="${1:-}"

if ! [ "$ATTEMPT" -ge 1 ] 2>/dev/null; then
  echo "FATAL: R-013 - invalid attempt value: '$ATTEMPT'" >&2
  exit 1
fi

if [ "$ATTEMPT" -gt 1 ]; then
  echo "FATAL: R-013 - This is run attempt $ATTEMPT (a rerun)." >&2
  echo "Stale reruns may execute incompatible workflow logic." >&2
  echo "Use fresh workflow_dispatch for a new source revision." >&2
  echo "The canonical job identity includes the attempt number," >&2
  echo "so this run cannot silently reuse prior artifacts." >&2
  exit 1
fi

echo "R-013 guard passed: fresh dispatch (attempt 1)"
