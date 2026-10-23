# Finance Video Factory — Production Operations Manual

Status: operator manual for the current repository and GitHub Actions pipeline.
Scope: preparation, safe rendering, artifact verification, delivery, recovery, and sign-off.
Safety rule: CI success proves automated checks passed; it does not prove a real render's visual quality, narration alignment, licensing, or factual accuracy. Never publish or merge without explicit authorization.

## 1. Repository map

This repository contains Remotion compositions, finance-video assets, timeline/event manifests, audio manifests, verification scripts, and GitHub Actions workflows.

- src/RemotionRoot.tsx — registered compositions and entry points.
- src/compiled_p3/ — P3 timeline, event manifest, and payloads used by production preflight.
- src/ — compositions, scenes, visual components, themes, and finance helpers.
- public/audio/ and audio/ — narration/music/SFX assets; workflow inputs determine which paths are used.
- scripts/verify-render.js and scripts/verify_pipeline_physics.js — verification utilities.
- .github/workflows/ — CI and rendering automation.
- out/ and verify-report*.json — generated previews/reports; treat as outputs, not authoritative source.

Do not assume every sample manifest or composition is production-approved. Confirm the selected composition, manifest, and audio paths for each job.

## 2. Prerequisites

- GitHub access to wastor453-ux/rendering-production.
- Node.js version matching the workflow (currently Node 24.x).
- Install dependencies with npm ci using the committed lockfile.
- FFmpeg and ffprobe for local media inspection.
- GitHub Actions enabled and artifact storage available.
- All required media, manifests, and payloads committed at the selected branch/ref.
- Never place API keys, tokens, passwords, or private credentials in source files or logs.

Safe local checks:

    node --version
    npm ci
    npm test --if-present
    npm run

The last commands only run/list scripts that actually exist. Inspect package.json; do not assume a script exists because it is mentioned in a guide.

## 3. Safe operating model

1. Work on a dedicated feature/repair branch.
2. Review the exact diff before committing.
3. Let static CI/contract checks run first.
4. Validate input manifests and audio files.
5. Only an explicitly authorized operator starts a production render.
6. Inspect the resulting artifact before release.
7. Keep merge and publication as separate approval steps.

Never commit secrets, force-push over teammates' work, use a test artifact as a master, or publish a file just because a workflow says success. This manual does not authorize starting a render.

## 4. GitHub Actions workflow

Open the repository Actions tab and choose the intended workflow. Read the current workflow_dispatch inputs before launching; the YAML is the source of truth if this manual and UI disagree.

Current production workflow inputs include:
- composition (default P3Rehearsal)
- job_id (unique identifier for this run)
- start_frame / end_frame
- chunk_size (frames per render chunk)
- crf (encoding quality setting where used)
- with_audio
- vo_file (default public/audio/vo_p3.wav)
- bed_file (default public/audio/bed.mp3)

Before submitting:
- Confirm composition name exactly matches a registered Remotion composition.
- Confirm frame range is intentional and in bounds.
- Confirm the workflow's inclusive/exclusive frame convention.
- Use a unique job ID so artifacts do not collide.
- Confirm audio paths exist in the selected ref and are non-empty if audio is enabled.
- Confirm manifests parse as JSON and reference existing payloads.
- Do not run a full production render merely to test CI.

A workflow dispatch consumes runner time and may create artifacts. Obtain explicit approval before doing it.

## 5. Input and manifest readiness

Check that:
- Timeline and events files parse as JSON.
- Required keys and event references match the selected composition's expected schema.
- Payload references resolve to actual files.
- Frame values are integers, ordered, non-negative, and within the composition's valid range.
- Audio is present, decodable, and long enough for the requested segment.
- Images, video, fonts, and other assets are committed and paths are case-correct (Linux runners are case-sensitive).
- No placeholder, truncated, empty, or stale media is referenced.
- The composition can be rendered by the configured Remotion version.

Useful local inspection:

    python -m json.tool src/compiled_p3/beat_timeline.json >/dev/null
    python -m json.tool src/compiled_p3/events.json >/dev/null
    ffprobe -v error -show_streams -show_format public/audio/vo_p3.wav
    ffprobe -v error -show_streams -show_format public/audio/bed.mp3

Change paths to the selected job's actual inputs. These commands check parseability/metadata, not semantic correctness or sync.

## 6. What CI gates mean

The pipeline's automated checks are designed to catch missing inputs, malformed JSON, unsafe frame/path parameters, absent/empty chunk artifacts, chunk metadata/hash mismatches, wrong output dimensions/FPS, incorrect decoded frame count, decode errors, missing audio stream, and implausible A/V duration differences.

- Green CI: the jobs that ran passed their configured assertions.
- Red CI: stop; inspect the first failing step and fix the root cause before retrying.
- Skipped/unrun check: not evidence of success.
- No production render: no real master has been verified.
- A/V duration match: duration proximity only; it does not establish frame-accurate or semantic synchronization.
- Successful upload: artifact storage succeeded, not editorial approval.

## 7. Master-file QA checklist

### Technical
- [ ] File exists and size is non-zero.
- [ ] Container and codecs are supported by delivery destination.
- [ ] Expected resolution (workflow currently expects 1920×1080 unless configured otherwise).
- [ ] Expected frame rate (workflow currently expects 30 fps unless configured otherwise).
- [ ] Decoded frame count equals expected frames.
- [ ] Full decode finishes without FFmpeg errors.
- [ ] Audio stream exists when required.
- [ ] Audio/video durations are within configured tolerance.
- [ ] Beginning, middle, and end play correctly.
- [ ] No black frames, freezes, missing scenes, corrupt frames, clipped audio, or unexpected silence.

### Editorial and finance
- [ ] Voiceover begins/ends at intended points; no clipped words.
- [ ] Music/SFX are balanced below speech and do not clip.
- [ ] Scene transitions, captions, labels, chart values, and currency units are legible.
- [ ] Numbers, rates, dates, and examples are verified against sources.
- [ ] Assumptions, time periods, nominal/real values, fees, and caveats are explicit.
- [ ] No misleading guarantees or unsupported performance promises.
- [ ] Captions match narration and stay on screen long enough.
- [ ] Brand, licensing, attribution, privacy, and rights checks pass.
- [ ] Final seconds include intended closing/CTA; no accidental blank tail.
- [ ] Thumbnail/title/description match the actual final cut.

Watch the entire video and listen with headphones. Machine-readable checks do not replace human review. Have a second reviewer verify high-stakes financial claims and on-screen arithmetic.

## 8. Audio and synchronization

The workflow mixes voiceover and bed audio for the selected segment. Validate actual media, not just durations:
1. Inspect each source with ffprobe.
2. Listen to the first 10 seconds and every scene transition.
3. Check narration onset and ending against picture.
4. Check music ducking and voice intelligibility.
5. Inspect the final 10 seconds for abrupt cuts or extended silence.
6. If A/V duration differs beyond the configured tolerance, fail release and investigate source duration, frame range, mux arguments, sample rate, and timestamps.

Do not fix sync by blindly stretching audio or changing -shortest. Determine which stream is wrong first. A duration delta under 0.5 seconds can still contain an audible/visual sync problem.

## 9. Failure response

JSON parse/preflight error:
- Validate the named file with python -m json.tool.
- Repair the source file, not generated output.
- Confirm encoding, commas, quotes, and trailing content.

Audio missing/empty:
- Verify path relative to repository root and exact letter case.
- Confirm file is tracked and available on the workflow ref.
- Run ffprobe to confirm decodability.
- Check whether audio is enabled.

Chunk missing, empty, or checksum mismatch:
- Treat artifact as invalid; do not assemble around it.
- Check failed matrix job, artifact names, job ID uniqueness, and upload/download paths.
- Re-run only after the cause is understood.

Frame count/resolution/FPS failure:
- Confirm selected composition, frame bounds, range convention, and expected FPS.
- Verify chunk metadata and concat order.
- Inspect ffprobe output; do not rely solely on container duration.

FFmpeg decode failure:
- Keep failed artifact/log for diagnosis.
- Check corrupt chunk, invalid concat list, incompatible stream parameters, or incomplete upload.
- Do not bypass full-decode gate.

Audio duration or stream missing:
- Confirm audio was enabled and correct files selected.
- Compare stream duration, video duration, and expected frame duration.
- Inspect trimming, mix filter, sample rate, and timestamps.
- Watch/listen to exported file after any fix.

CI red:
- Read the first failing job/step and downstream failures.
- Reproduce the smallest safe check locally.
- Make one focused fix and add/update a regression test.
- Never mark a failure as known-good without a documented reason and owner.

## 10. Release and rollback

Release checklist:
- [ ] Approved commit SHA recorded.
- [ ] CI green on that exact SHA.
- [ ] Master artifact name, size, SHA-256, and workflow run URL recorded.
- [ ] Human technical and editorial QA complete.
- [ ] Finance facts and sources reviewed.
- [ ] Release owner approved.
- [ ] Publication approval explicitly granted separately.
- [ ] Rollback artifact/location and owner recorded.

If a bad master is discovered:
1. Stop distribution if possible.
2. Preserve artifact and logs.
3. Notify release owner.
4. Revert to last approved artifact; do not assume last CI-green commit equals last approved master.
5. Correct on a branch, rerun checks, render only with authorization, and repeat QA.

## 11. Security and data hygiene

- Store credentials in approved GitHub secrets/secure connectors, never source files or logs.
- Use least-privilege access.
- Never print secret values for debugging.
- Treat third-party scripts, media, fonts, and downloaded assets as untrusted until reviewed.
- Keep copyrighted/licensed material within permitted usage.
- Avoid embedding private personal/financial data in examples, manifests, logs, or videos.

## 12. Run record template

Record one copy per release:
- Release/job ID:
- Repository branch and commit SHA:
- Workflow run URL:
- Composition and frame range:
- Manifest paths/revisions:
- Audio paths:
- CI status and checks run:
- Master artifact name:
- File size:
- SHA-256:
- Resolution / FPS / decoded frame count:
- Video duration / audio duration / delta:
- Human playback reviewer and date:
- Finance fact-check reviewer and date:
- Known limitations:
- Release approval:
- Publication approval:

## 13. Verified status at authoring

The latest reported workflow runs on the repair branch passed CI for static/contract checks. No real production render was started. Actual master output, real audio/video synchronization, visual quality, finance fact accuracy, and publication readiness remain unverified until a render is explicitly authorized and QA is completed.

## 14. Change control

The workflow YAML, package manifest/lockfile, registered composition code, and current branch content are authoritative over examples in this document. If code changes, update this manual and tests in the same change. Rendering, merging, and publishing require explicit authorization.