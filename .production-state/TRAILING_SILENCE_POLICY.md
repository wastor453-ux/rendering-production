# Trailing Silence Policy

**Universal policy for all videos. No per-video exceptions.**

## Definitions

- **Last spoken word**: The last word with duration > 0 AND probability ≥ 0.5
- **Speech endpoint**: End timestamp of the last spoken word
- **File duration**: Total duration of the WAV file
- **Trailing silence**: File duration − Speech endpoint

## Policy

1. **Alignment must filter hallucinations**: Zero-duration words and words with probability < 0.3 are whisper hallucinations, not speech. They must be excluded from the alignment output.

2. **Trailing silence ≤ 0.5s**: Acceptable. The video ends at the speech endpoint.

3. **Trailing silence > 0.5s**: FLAGGED by `test_vo_fill.py` (fail-closed, exit 1).
   - This is not automatically trimmed
   - Requires editorial decision: trim the audio OR approve as intentional outro
   - Do not silently accept dead air

4. **Never trim speech**: Only trailing silence may be trimmed, never words.

5. **Never invent timestamps**: The speech endpoint comes from alignment, not estimation.

## Example (credit-score)

- Last genuine word "you." ends at 111.780s (prob 1.000)
- File duration: 112.625s
- Trailing silence: 0.845s → FLAGGED (exceeds 0.5s)
- Action required: trim 0.845s OR approve as outro
