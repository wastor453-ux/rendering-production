# GitHub Reassembly Proof Plan — COMPLETE (prepared, NOT dispatched)

**Status:** PREPARED 2026-10-10, completed with actual input data. No dispatch,
no render, no reassembly performed. Awaiting Hamza's explicit authorization.
**Standing rule:** assembly death NEVER re-renders. This plan consumes verified
existing chunks only — zero new chunk jobs.

## 1. Objective

Prove the fixed reassembly path end-to-end on real production chunks: the
`-c copy` concat contract (Batch 1 fix for the proven 14-frame duplication),
the ledger COMPLETE gate, per-chunk SHA-256 verification, exact frame count,
and manifest-driven audio handling — on GitHub Actions, where the duplication
actually occurred. This is the first live exercise of the fixed recovery path.

It does NOT mark Q-004 green and does NOT prove the full 39-chunk production
path — it proves the recovery *mechanism* on a real 3-chunk set. Q-004
acceptance still needs Hamza's visual verdict and the final mix.

## 2. Critical finding: Q-004 chunks are gone

The Q-004 source runs have **zero artifacts** (verified via API 2026-10-10):
run `37990979375` → 0 artifacts; run `37985185686` → 0 artifacts. The chunks
were most likely deleted by the overbroad `cleanup-artifacts.yml` (deletes
artifacts beyond the 10 newest repo-wide — a known gap, see §9). **No Q-004
reassembly is possible.** This plan therefore uses the verified surviving set
below. This also confirms the cleanup policy gap is production-relevant: it
can destroy the very chunks the recovery law depends on.

## 3. Source run (actual, verified via API)

- **Run:** `38043130687` — "Render Production (Chunked Parallel)", conclusion
  **success**, branch `p4-4-complete-preproduction-closure`, created
  2026-10-10T09:55:56Z.
- **Job:** `run-38043130687-attempt-1-41b9c237`
- **Label:** `VERIFICATION: 300f visual brain test (M1/M2/M3)`
- **Composition:** `HousingBroke` · frames **0–299** · chunk_size 100 ·
  **3 chunks** · `with_audio: False` (VO/bed: none — audio steps skip by manifest)

## 4. Actual input chunks (verified by download 2026-10-10)

| Chunk | Frames | SHA-256 (`output_sha256`) | Artifact ID | Size |
|---|---|---|---|---|
| chunk_0 | 0–99 | `43ca19f4240e76049e105d89854ea54ca892aaa8ac3a0ca5bb457e21b053ef78` | 11666159455 | 214,693 B |
| chunk_1 | 100–199 | `0e53f6c06d766a7d19349ae3d53c093c71172b09e718853a21b5dd8882bab911` | 11666536178 | 256,896 B |
| chunk_2 | 200–299 | `27184cbf9e5065f863aebc9936de545f560c27b19898a5211d17414899582e60` | 11666289177 | 145,154 B |

- **Locally verified:** each downloaded `chunk_<id>.mp4`'s actual SHA-256 matches
  its manifest's `output_sha256` (3/3 match). Each artifact also carries a
  `chunk_<id>.sha256` sidecar.
- **Ledger** (`chunk-ledger-run-38043130687-attempt-1-41b9c237.json`, artifact
  11666384257): `complete: True`, 3/3 `rendered_ok`.
- **Job manifest** (artifact 11666149332): identity matches the job above.

## 5. Exact workflow and ref

- Workflow: `.github/workflows/render-production-reassemble.yml`
  ("Render Production — Reassemble Only")
- Ref: branch `p4-4-complete-preproduction-closure`
- **Precondition (authorization needed):** the branch must contain the Batch 1
  fix — recovery concat at `-c copy` (currently UNCOMMITTED locally). Do not
  dispatch until the pushed branch carries the fixed workflow; otherwise the
  run would exercise the old re-encode path and prove nothing.

## 6. Trigger (authorized dispatch only)

```
GITHUB_TOKEN=<token> tools/trigger_reassemble.sh 38043130687
```

POSTs `repository_dispatch` event `reassemble` with
`client_payload: {source_run_id: "38043130687"}`. `vo_file`/`bed_file` are
irrelevant here (`with_audio: False` — the workflow skips audio SHA checks and
both mux steps by manifest). `workflow_dispatch` with `source_run_id` is
equivalent. **Do not run without Hamza's explicit authorization.**

## 7. Manifest and ledger validation (must all pass)

1. `validate-source` downloads the 5 artifacts, extracts `job_manifest.json`,
   aborts on `job_identity` mismatch.
2. `build_ledger.py` rebuilds `chunk-ledger-reassembled.json` from the 3 chunk
   manifests → must report **COMPLETE** (3/3); fails naming missing chunk IDs.
3. `manifest.verify_assembly()` checks: job identity match, chunk count == 3,
   per-manifest file hashes, generation fingerprint parity (codec + CRF +
   Remotion version — the `-c copy` precondition).
4. Stage step: SHA-256 of each staged `chunk_<id>.mp4` must equal the manifest
   `output_sha256` values in §4 (any mismatch → FATAL, names the chunk).

## 8. Assembly — the fixed contract

```
ffmpeg -y -f concat -safe 0 -i /tmp/assemble/concat.txt -c copy /tmp/master_video.mp4
```

Byte-identical on main and recovery paths. No re-encode → no `-vsync cfr`
frame duplication (the proven cause of `dup=14` on run 37942159718).

## 9. Audio handling (manifest-driven)

`with_audio: False` for this source run, so:
- The VO/bed build and mux steps are skipped (`if: with_audio == 'true'`).
- The master is video-only — **expected and correct** for this proof input.
- Audio continuity checks reduce to: verify the master has no audio stream
  (consistent with the source manifest), i.e. the workflow must not invent
  audio. The A/V sync check is skipped by the same gate.

## 10. Output verification (all must pass)

From the workflow's `Verify master` step:
- Resolution exactly `1920x1080`, frame rate exactly `30/1`.
- **Frame count exactly `300`** (`ffprobe -count_frames`; `FRAMES == EXPECTED`
  or exit 1). This is the decisive check for the duplication fix: any
  re-encoded duplication would show as `300 + N`.
- Full decode pass: `ffmpeg -v error -i $MASTER -f null -`.
- Master + manifest uploaded as run artifacts.

## 11. Success / failure criteria

- **SUCCESS:** §7 gates pass → `-c copy` concat → §10 verification passes with
  `FRAMES == 300` → master uploaded → run concludes success. Proves the
  fixed recovery mechanism on real chunks. Advances the program to "recovery
  path proven" — Q-004 itself remains open (chunks gone; needs a fresh
  authorized chunk render + Hamza's verdict + final mix).
- **FAILURE classes:**
  - Missing/incomplete chunks (ledger names IDs) → do NOT re-render without
    authorization; investigate retention first.
  - Checksum mismatch (names chunk) → that chunk is corrupt; others stand.
  - `FRAMES != 300` → concat contract violated; investigate, never accept.
  - Decode fail → master rejected; nothing promoted.

## 12. What this plan does not do

No chunk rendering, no new compositions, no SFX changes, no token changes, no
branch switches, no cleanup. The live reassembly path is **not proven** until
an authorized run passes every check in §7–§10. The Q-004 chunk loss (§2)
should also prompt a decision on the cleanup-artifacts overbreadth: the
recovery law is only as durable as the artifacts it depends on.
