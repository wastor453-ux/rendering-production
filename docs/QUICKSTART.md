# Production Quickstart

This guide does not start a render, merge a pull request, or publish a video. Read [the full Production Operations Manual](PRODUCTION_OPERATIONS_MANUAL.md) first.

## 1. Get the code

    git clone https://github.com/wastor453-ux/rendering-production.git
    cd rendering-production
    git checkout repair/verified-pipeline-gates-2026-10-14
    npm ci

Use the branch/commit approved for your job; do not assume the repair branch is the release branch.

## 2. Run safe local checks

    node --version
    npm run
    npm test --if-present
    python -m json.tool src/compiled_p3/beat_timeline.json >/dev/null
    python -m json.tool src/compiled_p3/events.json >/dev/null

Some repositories do not define a generic test script; inspect package.json and use actual available commands. Do not infer a command ran if skipped or absent.

## 3. Inspect workflow

Open [render-production.yml](../.github/workflows/render-production.yml). Its current dispatch inputs and validation rules are authoritative. Verify composition, unique job ID, frame range, chunk size, CRF, audio toggle, VO path, and bed path.

## 4. Before dispatch

- Confirm manifests, payloads, and media exist on the target ref.
- Confirm audio files are non-empty and decodable if audio is enabled.
- Confirm composition and frame range.
- Get explicit authorization for a render.
- Do not merge or publish without separate explicit authorization.

## 5. After an authorized render

Download the master artifact. Verify dimensions, FPS, decoded frame count, full decode, audio stream, duration difference, and SHA-256. Watch the entire video and listen to the full mix. Complete the release checklist.

## Status language

Say “CI passed” only for CI. Say “master verified” only after checking the actual rendered master. Say “A/V sync verified” only after technical checks and human playback review.
