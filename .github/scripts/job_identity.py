#!/usr/bin/env python3
"""
Canonical render-job identity generation and validation.

A render job's identity must uniquely identify the render *generation*:
the same workflow run, the same attempt, the same source revision.

Format: run-{run_id}-attempt-{attempt}-{sha8}
Example: run-37860000000-attempt-1-a1b2c3d4

Manual labels (e.g. "2026-001") are display metadata only and MUST NOT
determine artifact identity.
"""

import re
import sys

# run-<digits>-attempt-<digits>-<8 hex chars>
IDENTITY_RE = re.compile(r"^run-(\d+)-attempt-(\d+)-([0-9a-f]{8})$")


def generate(run_id: str, attempt: str, sha: str) -> str:
    """Generate a canonical job identity from GitHub context."""
    run_id = str(run_id).strip()
    attempt = str(attempt).strip()
    sha8 = str(sha).strip()[:8].lower()
    if not run_id.isdigit():
        raise ValueError(f"run_id must be numeric, got: {run_id!r}")
    if not attempt.isdigit():
        raise ValueError(f"attempt must be numeric, got: {attempt!r}")
    if not re.fullmatch(r"[0-9a-f]{8}", sha8):
        raise ValueError(f"sha must start with 8 hex chars, got: {sha!r}")
    return f"run-{run_id}-attempt-{attempt}-{sha8}"


def parse(identity: str) -> dict:
    """Parse a canonical identity into its components. Raises ValueError if invalid."""
    m = IDENTITY_RE.match(identity.strip())
    if not m:
        raise ValueError(
            f"Invalid job identity: {identity!r}. "
            f"Expected format: run-<run_id>-attempt-<attempt>-<sha8>"
        )
    return {"run_id": m.group(1), "attempt": m.group(2), "sha8": m.group(3)}


def validate(identity: str) -> bool:
    """Return True if the identity matches the canonical format."""
    return bool(IDENTITY_RE.match(identity.strip()))


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: job_identity.py generate <run_id> <attempt> <sha>")
        print("       job_identity.py validate <identity>")
        print("       job_identity.py parse <identity>")
        return 2
    cmd = sys.argv[1]
    try:
        if cmd == "generate":
            print(generate(sys.argv[2], sys.argv[3], sys.argv[4]))
        elif cmd == "validate":
            print("valid" if validate(sys.argv[2]) else "INVALID")
            return 0 if validate(sys.argv[2]) else 1
        elif cmd == "parse":
            print(parse(sys.argv[2]))
        else:
            print(f"Unknown command: {cmd}", file=sys.stderr)
            return 2
    except (ValueError, IndexError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
