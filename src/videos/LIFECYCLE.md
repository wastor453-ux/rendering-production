# Video Production Lifecycle

## Principle
Each video is an island. It generates its own data, uses shared infrastructure,
and never touches another video's files.

## Lifecycle Stages

### 1. INIT
Create `src/videos/{video-name}/` from template.
The folder starts EMPTY - no data, no inherited styles.

### 2. GENERATE (Apply All Rules)
Run the rule pipeline. Each rule writes its output INTO the video folder:
- Visual Brain → `data/visual.json` (colors, modes, layout per this video)
- Editorial Brain → `data/beat_timeline.json` (beats specific to this video)
- Sound Design → `data/sfx_events.json` (SFX specific to this video)

**CRITICAL:** If a rule doesn't generate data for this video, the video FAILS.
It NEVER falls back to another video's data. This prevents the "same cheap style" problem.

### 3. VALIDATE (CI Enforces)
- `test_no_broken_imports.py` - all imports resolve
- `test_video_data_isolated.py` - video uses only its own data files
- Contract matches RemotionRoot

### 4. RENDER
Production render uses:
- `src/videos/{video-name}/` (video-specific code + data)
- `src/light/`, `src/lib/` (shared infrastructure - components, NOT data)
- Pipeline inputs (SFX events file, VO, etc.)

### 5. ARCHIVE
On successful render:
- Move `src/videos/{video-name}/` → `src/videos/_archive/{video-name}-{YYYYMMDD}/`
- Remove from RemotionRoot and contract
- CI validates removal is clean (no dangling refs)

### 6. CLEANUP (7-day retention)
Weekly job deletes `_archive/` folders older than 7 days.
If an update is needed within 7 days, restore from archive.

## Why This Fixes "Same Cheap Style"
Old problem: Video B didn't generate its own `beat_timeline.json`, so the
pipeline used Video A's file. Result: same beats, same visuals, same cheap style.

New rule: If `src/videos/{video}/data/beat_timeline.json` doesn't exist,
validation FAILS. The video cannot render. This forces every video to go
through the full rule pipeline and generate its own data.
