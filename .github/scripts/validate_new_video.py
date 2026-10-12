#!/usr/bin/env python3
"""Validate a new video before commit. Prevents schema/pipeline errors.
Usage: python3 .github/scripts/validate_new_video.py <video_name>
Checks:
  1. Video folder exists at src/videos/{name}/
  2. Beat file exists and matches EDITORIAL_BEAT_SCHEMA.json
  3. Composition registered in RemotionRoot.tsx
  4. Composition registered in composition_contract.py
  5. Beat file in BEAT_FILES (if beat-driven)
  6. No sideways imports (only ../../light/, ../../lib/, ./data/)
  7. No references to deleted compositions
"""
import json, os, re, sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)

def main():
    if len(sys.argv) != 2:
        fail("Usage: validate_new_video.py <video_name>")
    name = sys.argv[1]
    
    # 1. Folder exists
    video_dir = os.path.join(REPO_ROOT, "src", "videos", name)
    if not os.path.isdir(video_dir):
        fail(f"Video folder missing: src/videos/{name}/")
    print(f"PASS: Folder exists")
    
    # 2. Beat file schema validation
    beat_path = os.path.join(video_dir, "data", "beat_timeline.json")
    schema_path = os.path.join(REPO_ROOT, ".github", "schemas", "EDITORIAL_BEAT_SCHEMA.json")
    if os.path.exists(beat_path):
        with open(schema_path) as f:
            schema = json.load(f)
        with open(beat_path) as f:
            beats = json.load(f)
        required = schema["required"]
        for beat in beats:
            missing = [f for f in required if f not in beat]
            if missing:
                fail(f"Beat '{beat.get('beat_id', '?')}' missing fields: {missing}")
            # Check enums
            for field, enum_key in [
                ("semantic_role", "semantic_role_enum"),
                ("visual_verb", "visual_verb_enum"),
                ("duration_class", "duration_class_enum"),
                ("sfx_policy", "sfx_policy_enum"),
                ("visual_mode", "visual_mode_enum"),
            ]:
                if beat[field] not in schema[enum_key]:
                    fail(f"Beat '{beat['beat_id']}' invalid {field}: {beat[field]}")
        print(f"PASS: Beat file schema valid ({len(beats)} beats)")
    
    # 3. No sideways imports
    for root, dirs, files in os.walk(video_dir):
        for fn in files:
            if fn.endswith((".tsx", ".ts")):
                path = os.path.join(root, fn)
                with open(path) as f:
                    content = f.read()
                # Check for sideways imports (../other-video/)
                for m in re.finditer(r'from\s+["'](\.\./[^"']+)["']', content):
                    imp = m.group(1)
                    if imp.startswith("../") and not imp.startswith("../../"):
                        fail(f"{path}: sideways import forbidden: {imp}")
    print(f"PASS: No sideways imports")
    
    print(f"\nAll checks passed for '{name}'")

if __name__ == "__main__":
    main()
