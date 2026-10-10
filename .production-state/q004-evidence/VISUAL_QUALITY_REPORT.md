# Q-004 Visual-Quality Report — Objective Measurements (2026-10-10)

**Master:** `~/workspace/your_files/Q004_HousingBroke_master.mp4`
**Source run:** 38057551643 (completed/success)
**Method:** ffprobe stream analysis + full-file black/frozen detection. No re-render.

## Stream properties
| Property | Value |
|---|---|
| Video codec | H.264 |
| Resolution | 1920×1080 |
| Pixel format | yuvj420p |
| Frame rate | 30 fps |
| Frame count | 23,151 (exact, matches plan) |
| Duration | 772.118 s (12.87 min) |
| Video bitrate | ~168 kbps |
| Audio codec | AAC, 48 kHz, stereo |
| File size | 36.2 MB |

## Defect scans (full file)
| Check | Parameters | Result |
|---|---|---|
| Black frames | blackdetect d=0.5s, pix_th=0.10 | **0 segments** |
| Frozen frames | freezedetect n=0.001, d=2s | **0 segments** |

## Verdict
Technically valid: exact frame count, no black/frozen defects, correct
resolution and frame rate. **Creative quality is a separate judgment** —
Hamza ruled the master below required quality and forbade rerender.
Technical validity ≠ creative approval.
