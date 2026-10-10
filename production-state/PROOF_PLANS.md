# PROOF PLANS — Q-002 / Q-003 / Q-004
Date: 2026-10-10 · Branch: p4-4-complete-preproduction-closure · HEAD: 0f0b9e6
STATUS: PLANS ONLY — NOT EXECUTED. No runs launched. Execution needs Hamza's authorization.

Truthful run-status rule (all three): a master file existing ≠ green. Green requires the full
criterion list, each with a checkable handle (run URL, ledger artifact, master SHA).

## Q-002 — Selective recovery (fail chunk → resume → reuse good chunks)
Prerequisite (not done): render-production-q002-test.yml is currently a stub (registration
check + deliberate exit 1, no render). Before the proof, wire it to render a small composition
(e.g. P3Rehearsal, 600 frames, 30-frame chunks = 20 chunks) with fail_chunk killing one chunk.
1. Dispatch test workflow with fail_chunk: 7. Expected: run classifies CHUNK_FAILURE
   (classify_failure.py exit 11), exactly chunk 7 failed, 19 chunks have valid artifacts.
2. `python3 tools/dispatch_production.py --dry-run --composition P3Rehearsal … --resume-from-run-id <failed_run>`
   then real dispatch. Expected: resume_plan.json render list == [7] only; reused_count == 19;
   each reused chunk's staged SHA-256 == source run's recorded output_sha256.
3. Pass criteria: resume run classify == SUCCESS; ledger artifact COMPLETE (20/20);
   verify_assembly ok; master "Verify master" step exit 0 with frame count == plan;
   no chunk id rendered twice; zero full re-renders.
4. Blocker to resolve first: tests/test_recovery_split.py:139 and tests/test_recovery_decisive.py:212
   currently fail — they assert the old "source SHA mismatch must fail" invariant, but Hamza's
   2026-10-10 assembly_only rule intentionally normalizes source_sha. Decide: update tests to the
   new trust model (recovery_plan validates) or re-litigate the rule. Q-002 cannot be claimed
   green with red tests.

## Q-003 — Distributed scheduling & realistic throughput (OPEN — 3-way proven, 20-way never tested)
1. `python3 tools/dispatch_production.py --composition HousingBroke --start-frame 0 --end-frame 5999 --chunk-size 600 --max-parallel 20 --crf 18 --label "Q-003 throughput" --dry-run` (validate), then dispatch on authorization.
2. Measure from chunk manifests (render_duration_s, render_started_at/finished_at) + run wall-clock:
   aggregate frames/min, per-chunk p50/p95, matrix start-spread (scheduler overhead), runner-minutes.
   render-benchmark.yml (concurrency 1/2/4, single runner) is supporting evidence only.
3. Pass criteria: all 20 parallel slots demonstrably utilized (~20 concurrent in matrix), no chunk
   starvation/timeout, master assembles and verifies; one measured throughput number recorded as
   the production baseline (measured, not extrapolated).

## Q-004 — Final acceptance (full 13.4-min HousingBroke)
1. `python3 tools/dispatch_production.py --composition HousingBroke --start-frame 0 --end-frame 23150 --chunk-size 600 --max-parallel 20 --crf 18 --label "Q-004" --dry-run` (must exit 0; catches vo_p3.wav-class input errors), then dispatch on Hamza's go-ahead. Requires public/audio/vo_housingbroke.wav or all 7 hb_p1..hb_p7 present.
2. Pass criteria (ALL): validate_dispatch exit 0; run conclusion `success`; classify == SUCCESS;
   ledger COMPLETE (39/39); master artifact 1920×1080, 30/1 fps, exactly 23,151 frames
   (count_frames), clean full decode, ≥1 audio stream, |video−audio duration| < 0.5s, stage label
   `av_intermediate` (honest — the curated SFX mix E-04 is a separate step), master SHA-256 recorded;
   monitor marks done and auto-disables.
3. Human gate: Hamza's visual verdict on the master — metrics without his approval, or approval
   without metrics, is insufficient. E-04 final mix follows green only.
4. Any attempt > 1 rerun is invalid per R-013 — fresh dispatch only. Assembly-only recovery must
   show zero render jobs.
