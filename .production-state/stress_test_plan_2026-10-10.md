# Deep stress tests — remaining 3 of Hamza's 4 (designed 2026-10-10)

Hamza's order (2026-10-09, ~21:12 UTC): "now again deeply test the github
production system with own given problems to see is thst work".
Test 0 (300-frame smoke, run 37992005965) already PASSED — master 0.6 MB,
caught by the monitor on its first check.

Base run for T1/T2: 37992005965 (300 frames, 3x100, SUCCESS, chunks+master exist).
Repo: wastor453-ux/rendering-production, branch p4-4-complete-preproduction-closure.
All API calls via: python3 ~/workspace/skills/github/bin/gh_api.py <METHOD> <PATH> [BODY]
(This is the credential path that works; the github CLI had transient
DynamicCredentialError on 2026-10-10.)

IMPORTANT: trigger_reassemble.sh defaults vo_file to public/audio/vo_p3.wav —
that is the WRONG VO (the file behind the first Q-004 dispatch failure).
Always pass public/audio/vo_housingbroke.wav explicitly, or use the
repository_dispatch API directly with the right vo_file. The reassemble
workflow verifies audio SHA against the source run and fails closed on
mismatch — a wrong VO will fail the run, not silently produce a bad master.

## T1 — Kill assembly mid-run (Hamza's test #1)
Goal: prove a killed assembly recovers with ZERO re-render.
1. Dispatch reassembly of 37992005965:
   gh_api.py POST /repos/wastor453-ux/rendering-production/dispatches
     '{"event_type":"reassemble","client_payload":{"source_run_id":"37992005965","vo_file":"public/audio/vo_housingbroke.wav","bed_file":"public/audio/bed.mp3"}}'
2. Watch the new run; when the assemble job starts (in_progress),
   cancel it: gh_api.py POST /repos/wastor453-ux/rendering-production/actions/runs/{NEW_ID}/cancel
   (if cancel is refused because the job already finished, force-cancel:
   .../actions/runs/{NEW_ID}/force-cancel)
3. Dispatch reassembly again with the same source_run_id.
4. PASS CRITERIA: second reassembly completes; plan marks all 3 chunks
   reusable; zero render-chunk jobs execute; master artifact produced;
   monitor classifies SUCCESS.
   EXPECTED monitor noise: the cancelled run classifies UNKNOWN/cancelled —
   that is a classifier gap to note, not a product failure.

## T2 — Corrupt one chunk manifest (Hamza's test #2)
Goal: prove selective recovery — only the bad chunk re-renders.
GitHub artifacts are immutable, so "corruption" = delete one chunk artifact:
1. List artifacts: gh_api.py GET /repos/wastor453-ux/rendering-production/actions/runs/37992005965/artifacts?per_page=100
2. Identify one chunk artifact (chunk_*.mp4 or chunk manifest artifact, NOT
   the master, NOT the job manifest) and delete it:
   gh_api.py DELETE /repos/wastor453-ux/rendering-production/actions/artifacts/{ARTIFACT_ID}
   (Deletion is permanent but these are smoke-test artifacts, not production.)
3. Dispatch reassembly with source_run_id=37992005965 (correct vo_file).
4. PASS CRITERIA: plan/ledger detects the missing chunk; exactly 1 chunk
   re-renders; the other 2 are reused; master produced; monitor SUCCESS.
   (Precedent: P4.1 Q-002 proved 19/20 selective recovery on run 37926640596.)

## T3 — Code change + commit (Hamza's test #3)
Status 2026-10-10: ALREADY PROVEN, no new run needed unless Hamza wants it.
Evidence: retry 9 (run 37990979375) reassembled chunks rendered under older
commits after the lifetime fingerprint fix at c190a040 — 39 chunks reusable,
0 re-rendered; plus a local end-to-end resume simulation covering all 4
validation layers and 200/200 tests green.
Optional explicit re-run: make a trivial commit (e.g. comment-only change in
a tool), push, dispatch reassembly of 37992005965, verify 3/3 chunks reused.

## T4 — Wrong VO file (Hamza's test #4)
Goal: prove the pre-dispatch validator catches bad input BEFORE dispatch.
Local test, zero GitHub cost:
1. python3 tools/dispatch_production.py --composition HousingBroke \
     --start-frame 0 --end-frame 299 --vo-file public/audio/vo_p3.wav --dry-run
   EXPECT: validation FAILS, exit 1, nothing dispatched.
   (vo_p3.wav is the known-wrong short file from the first Q-004 dispatch.)
2. Repeat with --vo-file /nonexistent.wav → same expectation.
3. Sanity: --dry-run with vo_housingbroke.wav → validation PASSES.
PASS CRITERIA: both bad inputs rejected locally; good input passes.
Validator: .github/scripts/validate_dispatch.py (GATE 1 of dispatch_production.py).

## After each test
- Monitor (production-watch cron, every 5 min) reports the outcome; surface
  ALERT lines to Hamza immediately with the run URL.
- Record run IDs + conclusions here. Do NOT re-render production chunks for
  tests — the smoke-test run is the only base (RENDER LAW).
