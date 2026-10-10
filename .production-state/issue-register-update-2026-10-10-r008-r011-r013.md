# Issue Register Update — 2026-10-10 R-008/R-011/R-013 Evidence (final)

## R-008: FIXED (hosted proof complete)
- Shared installer `.github/scripts/install_snapshot.sh`: fail-closed, requires
  UBUNTU_SNAPSHOT, configures snapshot.ubuntu.com only, rejects rolling sources,
  logs timestamp/sources/resolved versions.
- All 5 production install sites routed through it; zero bare apt-get remains.
- Runner proof, run 38066659959 (sfx-chain-test): snapshot 20260820T000000Z,
  ffmpeg 7:6.1.1-3ubuntu5 installed and logged, no rolling sources.
- Runner proof, run 38067195302 (install-verify): render-chunk BROWSER_PACKAGES
  (13 packages, versions logged), assemble ffmpeg, sfx-mix ffmpeg — all from
  snapshot, zero archive.ubuntu.com references.
- First attempt caught missing `universe` component and failed closed (by design);
  fixed and retested green.
- 16/16 regression tests pass (per-job install-site map, no-bypass, fail-closed,
  browser-repair path, install-verify gating, with_sfx_mix default-false guardrail).
- Remaining gap: the render-chunk *browser-repair* path is proven by focused
  regression tests (snapshot installer, no rolling fallback, unified package set)
  but has not triggered on a runner (preflight always passes on GitHub images).
  Static + identical-code proof only.

## R-011: FIXED (evidence preserved)
- Artifacts 11673718243 and 11673134490 downloaded via manual 302-redirect +
  auth-stripping flow; both valid ZIPs, contents verified.
- Evidence: `.production-state/r011-artifact-evidence.md`.

## R-013: PARTIAL (logic proven, hosted proof deferred)
- Guard logic extracted to `.github/scripts/rerun_guard.sh`, 6/6 tests pass
  (attempt 1 ok, attempts 2/5 fail closed, invalid input fails closed).
- Workflow binds `github.run_attempt` → script; guard is first plan step.
- Hosted proof of the `github.run_attempt` binding requires rerunning a
  production workflow — forbidden by standing order. Deferred.
- Safest procedure documented in `.production-state/r013-limitation.md`.

## Test-suite status
- `npm test`: exit 0.
- Python: 304 tests, 301 pass. 3 pre-existing failures in
  `tests/test_render_infra.py`, recorded with base-reproduction evidence in
  `.production-state/pre-existing-test-failures.md` (not caused by this work).
