#!/usr/bin/env python3
"""
test_sfx_migration.py — A1 canonical library regression tests.

Fails if:
- Active production code references the retired 36-entry bench.
- An active asset reference points outside the A1 manifest.
- A staged-manifest mapping references a nonexistent A1 asset.
- The A1 manifest and actual WAV files disagree (hash/count).
- The retired bench is reachable via production routing paths.
- A picture/event mapping is dropped or silently substituted.
"""
import json
import os
import hashlib
import unittest

HOME = os.path.expanduser('~')
CRACKIT = os.path.join(HOME, 'workspace', 'crackit')
A1_BASE = os.path.join(CRACKIT, 'A1_sfx', 'A1 sound effects')
A1_MANIFEST = os.path.join(CRACKIT, 'A1_sfx', 'MANIFEST.json')
STAGED = os.path.join(CRACKIT, 'weekly', 'proof', 'P4_4', 'P4_4_SFX_STAGED_MANIFEST.json')
RETIRED = os.path.join(CRACKIT, '_retired')
SKILL = os.path.join(HOME, 'workspace', 'skills', 'sound-design', 'SKILL.md')
SOUND_DESIGN = os.path.join(HOME, 'workspace', 'skills', 'sound-design', 'SOUND_DESIGN.md')


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for c in iter(lambda: f.read(65536), b''):
            h.update(c)
    return h.hexdigest()


class TestA1Canonical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(A1_MANIFEST) as f:
            cls.manifest = json.load(f)
        with open(STAGED) as f:
            cls.staged = json.load(f)

    def test_manifest_has_180_assets(self):
        self.assertEqual(len(self.manifest['assets']), 180)

    def test_archive_sha_recorded(self):
        self.assertEqual(
            self.manifest['archive']['sha256'],
            '8cf48d70358dda8e3d2391beeb8edf0a5945f29feecd28bdc5796b60bff2e539')

    def test_all_manifest_files_exist_and_hash_match(self):
        bad = []
        for a in self.manifest['assets']:
            p = os.path.join(CRACKIT, 'A1_sfx', a['rel_path'])
            if not os.path.isfile(p):
                bad.append((a['asset_id'], 'missing'))
            elif sha256_file(p) != a['sha256']:
                bad.append((a['asset_id'], 'hash mismatch'))
        self.assertEqual(bad, [], f"Bad assets: {bad[:5]}")

    def test_no_duplicate_asset_ids(self):
        ids = [a['asset_id'] for a in self.manifest['assets']]
        self.assertEqual(len(ids), len(set(ids)))

    def test_staged_manifest_covers_33_events(self):
        self.assertEqual(len(self.staged['events']), 33)
        self.assertEqual(
            [e['seq'] for e in self.staged['events']], list(range(1, 34)))

    def test_no_event_dropped(self):
        dropped = self.staged['coverage']['dropped']
        self.assertEqual(dropped, 0)

    def test_all_a1_assignments_resolve(self):
        manifest_ids = {a['asset_id'] for a in self.manifest['assets']}
        for e in self.staged['events']:
            if e['source'] == 'A1':
                self.assertIn(e['asset_id'], manifest_ids,
                              f"Event {e['seq']} references unknown asset {e['asset_id']}")

    def test_triggers_deterministic(self):
        for e in self.staged['events']:
            if e['source'] == 'A1':
                expected = e['impact_frame'] - round(e['peak_time_s'] * 30)
                self.assertEqual(e['trigger_frame'], expected,
                                 f"Event {e['seq']} trigger mismatch")


class TestLegacyRetired(unittest.TestCase):
    def test_old_manifest_not_in_active_path(self):
        self.assertFalse(
            os.path.isfile(os.path.join(CRACKIT, 'bench_manifest.premium.json')),
            "Retired bench manifest still in active path")

    def test_old_bench_files_not_in_active_path(self):
        # The 36 retired files must not exist under sfx-aejuice/bench/
        retired_manifest = os.path.join(RETIRED, 'bench_manifest.premium.json.RETIRED')
        self.assertTrue(os.path.isfile(retired_manifest), "Retired backup missing")
        with open(retired_manifest) as f:
            old = json.load(f)
        bench_dir = os.path.join(CRACKIT, 'sfx-aejuice', 'bench')
        leaked = []
        for b in old:
            for root, _, files in os.walk(bench_dir):
                if b['file'] in files:
                    leaked.append(b['file'])
                    break
        self.assertEqual(leaked, [], f"Retired files still in active path: {leaked}")

    def test_retired_backup_exists_and_labeled(self):
        self.assertTrue(os.path.isfile(os.path.join(RETIRED, 'README.md')))
        self.assertTrue(os.path.isdir(os.path.join(RETIRED, 'sfx-bench-36')))
        n = sum(len(files) for _, _, files in os.walk(os.path.join(RETIRED, 'sfx-bench-36')))
        self.assertEqual(n, 36, f"Expected 36 retired files, found {n}")

    def test_skill_routes_to_a1_only(self):
        with open(SKILL) as f:
            skill = f.read()
        self.assertIn('A1_sfx/MANIFEST.json', skill)
        # Must not present the old bench as the active vocabulary
        self.assertNotIn('bench_manifest.premium.json` (36 human-approved sounds — the ONLY',
                         skill)

    def test_sound_design_routes_to_a1_only(self):
        with open(SOUND_DESIGN) as f:
            sd = f.read()
        self.assertIn('A1_sfx/MANIFEST.json', sd)
        # Old bench must only appear in retired context
        for line in sd.split('\n'):
            if 'bench_manifest.premium.json' in line and 'RETIRED' not in line and 'retired' not in line:
                self.fail(f"Active routing reference to old bench: {line[:100]}")

    def test_no_hardcoded_old_bench_in_tools(self):
        tool = os.path.join(CRACKIT, 'tools', 'compile_sfx_triggers.py')
        with open(tool) as f:
            src = f.read()
        # The tool takes --manifest as an argument; it must not default to the old bench
        self.assertNotIn('bench_manifest.premium.json', src,
                         "Tool hardcodes retired bench path")


if __name__ == '__main__':
    unittest.main(verbosity=2)
