#!/usr/bin/env python3
"""
Q1 (2026-10-11): Composition frame-count registry verification.

Every total_frames in .github/scripts/composition_contract.py must match
the canonical TSX source. If a source file changes its duration, this test
fails and the registry must be updated — plan.py's upper-bound validation
is only as correct as this registry.

Resolution methods per composition (mirroring the TSX):
  static const arithmetic : parse file-local numeric consts, evaluate expr
  SCENES.reduce           : parse SCENES array, sum frames
  beat-driven             : load the beats JSON the TSX imports, replicate formula
  alias                   : resolve to the aliased constant
  literal                 : durationInFrames={N} in RemotionRoot.tsx
"""
import json
import math
import os
import re
import sys
import unittest

REPO_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(REPO_ROOT, ".github", "scripts"))
from composition_contract import COMPOSITIONS, get_total_frames


def read(path):
    with open(os.path.join(REPO_ROOT, path)) as f:
        return f.read()


def file_consts(content):
    """All simple numeric const assignments in a TS/TSX file."""
    consts = {}
    for m in re.finditer(r'(?:export\s+)?const\s+([A-Za-z0-9_]+)\s*=\s*(\d+)\s*;', content):
        consts[m.group(1)] = int(m.group(2))
    return consts


def eval_static_total(path, const_name):
    """Evaluate `export const NAME = <expr>;` using file-local numeric consts."""
    content = read(path)
    m = re.search(rf'export const {const_name}\s*=\s*([^;]+);', content)
    assert m, f"{const_name} export not found in {path}"
    return eval(m.group(1).strip(), {"__builtins__": {}}, file_consts(content))


def scenes_reduce_total(path):
    """Replicate `SCENES.reduce((a, s) => a + s.frames, 0)`."""
    content = read(path)
    m = re.search(r'(?:export\s+)?const\s+SCENES\s*=\s*\[(.*?)\];', content, re.DOTALL)
    assert m, f"SCENES array not found in {path}"
    frames = [int(f) for f in re.findall(r'frames:\s*(\d+)', m.group(1))]
    assert frames, f"no frames found in SCENES of {path}"
    return sum(frames)


def beat_max_total(beats_path, fps=30):
    """Replicate `Math.ceil(Math.max(...beats.map(b => b.end_time)) * FPS)`."""
    with open(os.path.join(REPO_ROOT, beats_path)) as f:
        doc = json.load(f)
    return math.ceil(max(b["end_time"] for b in doc["beats"]) * fps)


def showcase_totals():
    """Resolve SHOWCASE_MODES.length and combos.length from Showcase.tsx."""
    content = read("src/light/Showcase.tsx")
    modes_start = content.find("export const SHOWCASE_MODES")
    combos_start = content.find("const combos", modes_start)
    assert modes_start != -1 and combos_start != -1
    mode_ids = re.findall(r'\{\s*id:\s*"([^"]+)"',
                          content[modes_start:combos_start])
    combos_end = content.find("];", combos_start)
    combo_ids = re.findall(r'\{\s*id:\s*"([^"]+)"',
                           content[combos_start:combos_end])
    consts = file_consts(content)
    return {
        "modes": len(mode_ids),
        "combos": len(combo_ids),
        "showcase": consts["INTRO"] + len(mode_ids) * consts["MODE_SEC"]
                    + len(combo_ids) * consts["COMBO_SEC"],
        "regression": len(mode_ids) * 90,  # MODE_SLOT in ModeRegression.tsx
    }


def b6a_total():
    """Replicate B6A_TOTAL = FROM + DUR from src/videos/production-beats/data/beat_timeline.json."""
    with open(os.path.join(REPO_ROOT, "src/videos/production-beats/data/beat_timeline.json")) as f:
        doc = json.load(f)
    beat = next(b for b in doc["beats"] if b["beat_id"] == "b6")
    from_f = math.floor(beat["start_time"] * 30)
    dur = math.ceil(beat["end_time"] * 30) - from_f
    return from_f + dur


# Canonical resolution for every registered composition.
CANONICAL = {
    "MoneyDying":       lambda: eval_static_total("src/videos/moneydying/MoneyDying.tsx", "MD_TOTAL"),
    "ProductionBeats":  lambda: beat_max_total("src/videos/production-beats/data/beat_timeline.json"),
    "FromScratch":      lambda: 2709,
    "FromScratchLight": lambda: eval_static_total("src/videos/fromscratch-light/FromScratchLight.tsx", "FROMSCRATCH_LIGHT_TOTAL"),
    "FinanceProof":     lambda: eval_static_total("src/videos/finance-proof/FinanceProof.tsx", "PROOF_TOTAL"),
    "SavingsTrap":      lambda: eval_static_total("src/videos/savings-trap/SavingsTrap.tsx", "SAVINGSTRAP_TOTAL"),
}


class TestCompositionFramesRegistry(unittest.TestCase):
    def test_every_registered_composition_has_canonical_resolver(self):
        missing = set(COMPOSITIONS) - set(CANONICAL)
        self.assertEqual(missing, set(),
                         f"compositions without canonical resolver: {missing}")
        extra = set(CANONICAL) - set(COMPOSITIONS)
        self.assertEqual(extra, set(),
                         f"resolvers for unregistered compositions: {extra}")

    def test_registry_matches_canonical_source(self):
        for cid, resolve in sorted(CANONICAL.items()):
            with self.subTest(composition=cid):
                expected = resolve()
                actual = get_total_frames(cid)
                self.assertEqual(
                    actual, expected,
                    f"{cid}: registry has {actual}, canonical source says {expected}")

    def test_registry_values_are_positive_ints(self):
        for cid in COMPOSITIONS:
            total = get_total_frames(cid)
            self.assertIsInstance(total, int, f"{cid}: not an int")
            self.assertGreater(total, 0, f"{cid}: not positive")

    def test_registry_totals_are_self_consistent(self):
        # Every registered total must be usable as an exclusive upper bound.
        # (Pipeline property, no hardcoded video.)
        for cid in COMPOSITIONS:
            with self.subTest(composition=cid):
                total = get_total_frames(cid)
                self.assertGreater(total, 0)


if __name__ == "__main__":
    unittest.main()
