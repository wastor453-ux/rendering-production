#!/usr/bin/env python3
"""Bind verify-report.json to the current run's master identity; fail closed.

The Q-004 run uploaded a STALE verify-report (dated 2026-10-06, describing a
180s master, grading FAIL) because the workflow uploaded whatever
verify-report.json existed. This script gates the upload:

- stamp:  embed run_id / master sha / frames / duration into the report
- validate: fail (exit 1) if the report's identity does not match the actual
  master; exit 2 if the report is absent (caller skips upload, not a failure).

Usage:
  validate_verify_report.py stamp --report R --run-id ID --master M
  validate_verify_report.py validate --report R --run-id ID --master M --expected-frames N
"""
import argparse
import hashlib
import json
import subprocess
import sys


class Fail(Exception):
    pass


def ffprobe(path, args):
    r = subprocess.run(
        ["ffprobe", "-v", "error"] + args + [path],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise Fail(f"ffprobe failed on {path}: {r.stderr.strip()}")
    return r.stdout.strip()


def master_identity(master_path):
    frames = ffprobe(master_path, ["-count_frames", "-select_streams", "v:0",
                                   "-show_entries", "stream=nb_read_frames",
                                   "-of", "default=noprint_wrappers=1:nokey=1"])
    duration = ffprobe(master_path, ["-show_entries", "format=duration",
                                     "-of", "default=noprint_wrappers=1:nokey=1"])
    h = hashlib.sha256()
    with open(master_path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return {"frames": int(frames), "duration_s": round(float(duration), 3),
            "sha256": h.hexdigest()}


def cmd_stamp(a):
    try:
        with open(a.report) as f:
            report = json.load(f)
    except FileNotFoundError:
        raise Fail(f"report not found: {a.report}")
    except json.JSONDecodeError as e:
        raise Fail(f"report is not valid JSON: {e}")
    ident = master_identity(a.master)
    ident["run_id"] = str(a.run_id)
    report["master_identity"] = ident
    with open(a.report, "w") as f:
        json.dump(report, f, indent=2)
    print(f"stamped {a.report}: run {a.run_id}, {ident['frames']}f, "
          f"{ident['duration_s']}s, sha {ident['sha256'][:12]}")


def cmd_validate(a):
    try:
        with open(a.report) as f:
            report = json.load(f)
    except FileNotFoundError:
        print(f"no report at {a.report}; skipping upload (not a failure)")
        return 2
    except json.JSONDecodeError as e:
        raise Fail(f"report is not valid JSON: {e}")
    ident = report.get("master_identity")
    if not isinstance(ident, dict):
        raise Fail("report has no master_identity stamp — refusing to upload "
                   "a potentially stale report")
    if str(ident.get("run_id")) != str(a.run_id):
        raise Fail(f"report run_id {ident.get('run_id')} != current run "
                   f"{a.run_id} — stale report, refusing upload")
    actual = master_identity(a.master)
    if ident.get("sha256") != actual["sha256"]:
        raise Fail("report master sha256 does not match the assembled master "
                   "— stale report, refusing upload")
    if int(ident.get("frames", -1)) != actual["frames"]:
        raise Fail(f"report frames {ident.get('frames')} != actual "
                   f"{actual['frames']} — mismatched report, refusing upload")
    if a.expected_frames is not None and actual["frames"] != a.expected_frames:
        raise Fail(f"actual frames {actual['frames']} != expected "
                   f"{a.expected_frames}")
    print(f"report bound OK: run {a.run_id}, {actual['frames']}f, "
          f"sha {actual['sha256'][:12]}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stamp")
    s.add_argument("--report", required=True)
    s.add_argument("--run-id", required=True)
    s.add_argument("--master", required=True)
    v = sub.add_parser("validate")
    v.add_argument("--report", required=True)
    v.add_argument("--run-id", required=True)
    v.add_argument("--master", required=True)
    v.add_argument("--expected-frames", type=int, default=None)
    a = p.parse_args()
    try:
        if a.cmd == "stamp":
            cmd_stamp(a)
            return 0
        return cmd_validate(a)
    except Fail as e:
        print(f"VERIFY-REPORT FAIL-CLOSED: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
