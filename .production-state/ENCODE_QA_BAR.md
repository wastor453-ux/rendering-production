# B-21: Encode QA Bar (DRAFT — needs Hamza's approval)

**Status:** APPROVED by Hamza 2026-10-11.

## Proposed acceptance thresholds

| Metric | Proposed bar | Rationale |
|--------|--------------|-----------|
| Resolution | 1920×1080 exact | Channel standard |
| Frame rate | 30fps constant | No VFR |
| Total frames | Matches composition ±0 | No dropped/duplicated frames |
| Black frames | 0 | Zero tolerance (existing law) |
| Frozen frames | 0 | Zero tolerance (existing law) |
| Audio sync drift | < 100ms end-to-end | Lip-sync threshold |
| True peak | ≤ -1 dBTP | Broadcast safe |
| Loudness | -14 LUFS ±1 | YouTube normalization target |
| CRF | 18 | Current production setting |

## Verification method (proposed)
- `tools/verify_visual.py` for frame-level checks (already built, PASS on Q-004)
- `ffmpeg -v error -i <master> -f null -` for decode integrity
- `loudnorm` filter for LUFS/true-peak measurement

## Open question for Hamza
- Are these thresholds correct, or should any be tightened/loosened?
- Should VMAF or SSIM be added for perceptual quality?
