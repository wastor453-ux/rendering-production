# Troubleshooting Guide

## First principles
Do not bypass failed verification gates. Preserve the failed run URL, commit SHA, job ID, logs, and artifacts before retrying. Fix the source of the failure, add a regression test where possible, then rerun CI.

| Symptom | Likely causes | Safe response |
|---|---|---|
| JSON parse/preflight failure | Invalid JSON, wrong path, incomplete commit | Validate with python -m json.tool; fix source manifest and verify payload references. |
| Missing/empty audio | Wrong workflow input, case mismatch, untracked asset | Check exact path on selected ref, Git tracking, file size, and ffprobe output. |
| Missing chunk | Failed matrix job, naming mismatch, upload/download issue | Inspect failed chunk job and artifact names; never assemble incomplete chunks. |
| Checksum mismatch | Corruption, wrong artifact, stale job ID collision | Preserve metadata and artifact; confirm unique job ID and provenance. |
| Unexpected frame count | Incorrect frame bounds, off-by-one, wrong composition/FPS | Recheck frame convention and composition metadata; inspect decoded frames. |
| Wrong resolution/FPS | Composition config or render arguments | Confirm registered composition and workflow flags; do not relax assertions to get green CI. |
| FFmpeg decode fails | Corrupt chunk/master, invalid concat, incomplete upload | Retain logs/artifact; isolate corrupt file and rerender only after authorization. |
| Missing audio stream | Audio disabled, mux step skipped, bad input | Verify workflow input and source streams. If audio is required, block release. |
| A/V duration delta fails | Wrong trim, input too short, timestamps/sample rate | Compare source, segment, and master durations; listen and inspect sync. |
| Duration passes but narration is late | Duration-only check cannot detect local offset | Review timeline and audio onset manually; inspect representative frames and waveform. |
| CI passes but video looks wrong | CI cannot judge all editorial quality | Watch the entire master and complete release checklist. |
| Local works but CI fails | Linux path case, dependency mismatch, missing tracked asset | Match Node/lockfile, use exact path case, verify assets are committed. |

## Minimal diagnostics

    node --version
    npm ci
    python -m json.tool src/compiled_p3/beat_timeline.json >/dev/null
    python -m json.tool src/compiled_p3/events.json >/dev/null
    ffprobe -v error -show_streams -show_format path/to/file.mp4
    ffmpeg -v error -i path/to/file.mp4 -f null -
    sha256sum path/to/file.mp4

Replace example paths with actual inputs/outputs. The FFmpeg decode command reads the file but does not modify it.

## Escalate when
- A required check is missing or skipped unexpectedly.
- The artifact differs from the expected commit/run.
- A checksum or frame-count check fails repeatedly.
- Financial claims cannot be sourced.
- Media licensing or privacy is unclear.
- A proposed fix weakens validation instead of correcting the defect.
