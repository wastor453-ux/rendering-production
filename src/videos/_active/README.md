# src/videos/_active/ — runtime-generated inputs (STUBS in Git)

`EventDriven.tsx` statically imports these three files. They are
**placeholders** so the Remotion bundle resolves in every checkout.

- `manifest.json` — `{"videoId": "__STUB__"}` (placeholder marker)
- `timeline.json` — `{"events": []}` (zero events)
- `vo.wav` — 0.1s of silence (valid WAV, never real audio)

## Contract

1. The render workflow **must overwrite all three** before any bundling
   (plan-job "Prepare event-driven manifest" + per-worker prepare).
2. A render that runs on stubs **fails closed**: the empty timeline fails
   `tools/validate_timeline.py` and `verify_provenance.py`, and
   `EventDrivenVideo` reports "Timeline has zero events". Stubs can
   never silently ship as a real video.
3. **Never commit real video data here.** This path is generic; real
   data lives in `src/videos/{video_id}/data/` + `audio/` and is
   copied here at render time only.

Enforced by `tests/test_no_broken_imports.py::test_runtime_generated_stubs_are_placeholders`.
