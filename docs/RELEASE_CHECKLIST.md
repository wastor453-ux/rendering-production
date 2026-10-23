# Release Checklist — Finance Video Factory

Copy this checklist into the release record. Do not publish on the strength of CI alone.

## A. Source readiness
- [ ] Approved branch and commit SHA recorded.
- [ ] Composition exists and is registered.
- [ ] Timeline/events JSON parse and conform to expected schema.
- [ ] Payload references resolve.
- [ ] All required assets exist, are non-empty, and decode.
- [ ] Frame range, FPS, dimensions, and audio settings confirmed.
- [ ] Rights, licensing, attribution, and usage approved.

## B. Automation
- [ ] CI ran on the exact commit SHA.
- [ ] All required checks passed; no required checks skipped.
- [ ] Chunk sequence/ranges are contiguous and complete.
- [ ] Chunk checksums and metadata passed.
- [ ] Master file is non-empty.
- [ ] ffprobe dimensions and FPS match expectations.
- [ ] Decoded frame count matches expected count.
- [ ] Full decode completed without errors.
- [ ] Required audio stream exists and duration delta is within configured tolerance.
- [ ] Artifact upload succeeded and artifact URL is recorded.

## C. Human playback
- [ ] Watched the entire master at normal speed.
- [ ] Checked beginning, transitions, middle, and ending.
- [ ] No missing, frozen, black, corrupt, or unintended frames.
- [ ] Narration is complete, clear, and synchronized.
- [ ] Music/SFX levels are balanced; no clipping.
- [ ] Captions match narration, spelling, timing, and readability.
- [ ] No visual overlap, cut-off text, tiny labels, or unreadable charts.
- [ ] No accidental silence or blank tail.

## D. Financial/editorial integrity
- [ ] Numbers, rates, dates, currencies, formulas, and units verified.
- [ ] Assumptions and time periods are clear.
- [ ] Comparisons use consistent definitions and periods.
- [ ] Claims are supported; caveats included where needed.
- [ ] No unsupported guarantee or misleading certainty.
- [ ] Title, thumbnail, description, and CTA accurately represent video.
- [ ] Source references and fact-check reviewer recorded.

## E. Delivery approval
- [ ] Master filename, file size, SHA-256, dimensions, FPS, frame count, durations recorded.
- [ ] Technical reviewer approved.
- [ ] Finance/editorial reviewer approved.
- [ ] Release owner approved.
- [ ] Publication approved separately and explicitly.
- [ ] Rollback artifact and owner identified.

Decision: HOLD / APPROVED FOR DELIVERY / APPROVED FOR PUBLICATION
Approver and date:
Exceptions and rationale:
