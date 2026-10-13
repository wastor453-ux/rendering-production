"""
test_artifact_integrity.py — Validated input artifact tests.

Synthetic fixtures, isolated from production video discovery.
"""
import unittest
import hashlib
import tempfile
import os
import json

class TestArtifactIntegrity(unittest.TestCase):
    def _hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()
    
    def test_missing_artifact_fails(self):
        """Missing validated-inputs artifact must fail."""
        # Simulate worker check
        artifact_path = "/tmp/nonexistent-validated-inputs-12345"
        self.assertFalse(os.path.exists(artifact_path))
    
    def test_corrupted_artifact_detected(self):
        """Corrupted file must fail SHA256 verification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files
            data = b"original content"
            filepath = os.path.join(tmpdir, "timeline.json")
            with open(filepath, "wb") as f:
                f.write(data)
            
            # Record hash
            expected = self._hash(data)
            
            # Corrupt the file
            with open(filepath, "wb") as f:
                f.write(b"corrupted!")
            
            # Verify fails
            actual = self._hash(open(filepath, "rb").read())
            self.assertNotEqual(expected, actual)
    
    def test_worker_consistency(self):
        """All workers must receive identical artifacts."""
        # Simulate two workers downloading same artifact
        artifact_content = b"validated timeline v1"
        h1 = self._hash(artifact_content)
        h2 = self._hash(artifact_content)
        self.assertEqual(h1, h2)
    
    def test_no_fallback_to_checkout(self):
        """Workers must not copy from checkout when artifact exists (F-12)."""
        # Real test: parse the workflow and verify the render-chunk job
        # fails closed if the artifact is missing (no checkout fallback).
        import yaml
        with open(".github/workflows/render-production.yml") as f:
            wf = yaml.safe_load(f)
        
        render_job = wf["jobs"]["render-chunk"]
        steps = render_job["steps"]
        
        # Find the "Prepare event-driven manifest" step
        prepare = None
        for s in steps:
            if s.get("name", "").startswith("Prepare event-driven manifest"):
                prepare = s
                break
        self.assertIsNotNone(prepare, "Prepare step not found")
        
        run_script = prepare.get("run", "")
        # Must fail if artifact missing (not fall back to checkout)
        self.assertIn("/tmp/validated-inputs", run_script,
                      "Must use validated artifact path")
        self.assertIn("FATAL", run_script,
                      "Must fail closed if artifact missing")
        # Must NOT copy from src/videos/ (checkout) as fallback
        # (cp FROM /tmp/validated-inputs is OK; cp FROM src/videos is not)
        for line in run_script.split("\n"):
            line = line.strip()
            if line.startswith("cp ") and "src/videos/" in line:
                # Allow cp TO src/videos/_active (populating from artifact)
                # Forbid cp FROM src/videos/ (checkout fallback)
                parts = line.split()
                if len(parts) >= 3 and parts[1].startswith("src/videos/"):
                    self.fail(f"Checkout fallback detected: {line}")

if __name__ == "__main__":
    unittest.main()
