#!/usr/bin/env python3
"""P3.12.2 regression tests: archive safety, pagination, provenance.

Tests the artifact_verify module and the pagination logic directly.
"""

import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                               "../.github/scripts"))
from artifact_verify import (
    inspect_chunk_archive, open_archive, find_chunk_files,
    ArchiveError, ArchiveContradiction,
)


def make_test_archive(members):
    """Create a ZIP in a temp file. members: {name: bytes}."""
    fd, path = tempfile.mkstemp(suffix=".zip")
    os.close(fd)
    with zipfile.ZipFile(path, "w") as z:
        for name, data in members.items():
            z.writestr(name, data)
    return path


def make_valid_chunk(cid=0):
    """Create a valid chunk archive for testing."""
    manifest = {
        "kind": "chunk", "chunk_id": cid,
        "frame_range": {"start": 0, "end": 99},
    }
    video_bytes = b"fake-video-data-" * 100  # 1600 bytes
    return make_test_archive({
        f"chunk_{cid}.mp4": video_bytes,
        f"chunk_{cid}_manifest.json": json.dumps(manifest).encode(),
    }), video_bytes, manifest


class TestArchiveSafety(unittest.TestCase):
    def test_valid_archive_inspected(self):
        path, video_bytes, manifest = make_valid_chunk(0)
        try:
            result = inspect_chunk_archive(path, 0)
            self.assertEqual(result["manifest"]["chunk_id"], 0)
            self.assertEqual(result["video_sha256"],
                             hashlib.sha256(video_bytes).hexdigest())
            self.assertEqual(result["video_bytes"], len(video_bytes))
            # Manifest SHA is of the file bytes, not the video.
            self.assertEqual(result["manifest_sha256"],
                             hashlib.sha256(
                                 json.dumps(manifest).encode()).hexdigest())
        finally:
            os.unlink(path)

    def test_traversal_rejected(self):
        path = make_test_archive({
            "chunk_0.mp4": b"video",
            "chunk_0_manifest.json": b'{"kind": "chunk", "chunk_id": 0}',
            "../evil.txt": b"evil",
        })
        try:
            with self.assertRaises(ArchiveContradiction):
                inspect_chunk_archive(path, 0)
        finally:
            os.unlink(path)

    def test_absolute_path_rejected(self):
        path = make_test_archive({
            "chunk_0.mp4": b"video",
            "chunk_0_manifest.json": b'{"kind": "chunk", "chunk_id": 0}',
        })
        # Manually add an absolute path (writestr normalizes, so we hack)
        with zipfile.ZipFile(path, "a") as z:
            info = zipfile.ZipInfo("/absolute/evil.txt")
            z.writestr(info, b"evil")
        try:
            with self.assertRaises(ArchiveContradiction):
                inspect_chunk_archive(path, 0)
        finally:
            os.unlink(path)

    def test_duplicate_manifest_rejected(self):
        # Two manifests with same basename in different dirs.
        path = make_test_archive({
            "chunk_0.mp4": b"video",
            "a/chunk_0_manifest.json": b'{"kind": "chunk", "chunk_id": 0}',
            "b/chunk_0_manifest.json": b'{"kind": "chunk", "chunk_id": 0}',
        })
        try:
            with self.assertRaises(ArchiveContradiction):
                inspect_chunk_archive(path, 0)
        finally:
            os.unlink(path)

    def test_duplicate_video_rejected(self):
        path = make_test_archive({
            "a/chunk_0.mp4": b"video1",
            "b/chunk_0.mp4": b"video2",
            "chunk_0_manifest.json": b'{"kind": "chunk", "chunk_id": 0}',
        })
        try:
            with self.assertRaises(ArchiveContradiction):
                inspect_chunk_archive(path, 0)
        finally:
            os.unlink(path)

    def test_corrupt_zip_rerenders(self):
        fd, path = tempfile.mkstemp(suffix=".zip")
        os.write(fd, b"this is not a zip file")
        os.close(fd)
        try:
            with self.assertRaises(ArchiveError):
                inspect_chunk_archive(path, 0)
        finally:
            os.unlink(path)

    def test_missing_video_rerenders(self):
        path = make_test_archive({
            "chunk_0_manifest.json": b'{"kind": "chunk", "chunk_id": 0}',
        })
        try:
            with self.assertRaises(ArchiveError):
                inspect_chunk_archive(path, 0)
        finally:
            os.unlink(path)

    def test_missing_manifest_rerenders(self):
        path = make_test_archive({
            "chunk_0.mp4": b"video",
        })
        try:
            with self.assertRaises(ArchiveError):
                inspect_chunk_archive(path, 0)
        finally:
            os.unlink(path)

    def test_empty_video_rerenders(self):
        path = make_test_archive({
            "chunk_0.mp4": b"",
            "chunk_0_manifest.json": b'{"kind": "chunk", "chunk_id": 0}',
        })
        try:
            with self.assertRaises(ArchiveError):
                inspect_chunk_archive(path, 0)
        finally:
            os.unlink(path)

    def test_lfs_pointer_rerenders(self):
        lfs = (b"version https://git-lfs.github.com/spec/v1\n"
               b"oid sha256:abc123\nsize 12345\n")
        path = make_test_archive({
            "chunk_0.mp4": lfs,
            "chunk_0_manifest.json": b'{"kind": "chunk", "chunk_id": 0}',
        })
        try:
            with self.assertRaises(ArchiveError):
                inspect_chunk_archive(path, 0)
        finally:
            os.unlink(path)

    def test_wrong_chunk_manifest_rejected(self):
        # Manifest for chunk 1 in chunk 0's archive.
        path = make_test_archive({
            "chunk_0.mp4": b"video",
            "chunk_0_manifest.json": b'{"kind": "chunk", "chunk_id": 1}',
        })
        try:
            with self.assertRaises(ArchiveContradiction):
                inspect_chunk_archive(path, 0)
        finally:
            os.unlink(path)

    def test_malformed_json_rerenders(self):
        path = make_test_archive({
            "chunk_0.mp4": b"video",
            "chunk_0_manifest.json": b"{not valid json",
        })
        try:
            with self.assertRaises(ArchiveError):
                inspect_chunk_archive(path, 0)
        finally:
            os.unlink(path)


class TestPagination(unittest.TestCase):
    def test_paginated_list_combines_pages(self):
        # Simulate gh_api_paginated_list with a mock.
        import recovery_plan
        calls = []

        def mock_gh_api(path):
            calls.append(path)
            # Parse page from path (avoid matching per_page).
            import re
            m = re.search(r"[?&]page=(\d+)", path)
            page = int(m.group(1)) if m else 1
            # Simulate 250 artifacts across 3 pages
            total = 250
            start = (page - 1) * 100
            end = min(start + 100, total)
            return {
                "total_count": total,
                "artifacts": [{"id": i, "name": f"chunk-x-{i}"}
                              for i in range(start, end)],
            }

        orig = recovery_plan.gh_api
        recovery_plan.gh_api = mock_gh_api
        try:
            items = recovery_plan.gh_api_paginated_list(
                "/repos/o/r/actions/runs/123/artifacts", "artifacts")
            self.assertEqual(len(items), 250)
            # Verify chunks beyond the first page are found.
            self.assertEqual(items[150]["id"], 150)
            self.assertEqual(items[249]["id"], 249)
            # Verify 3 pages were fetched.
            self.assertEqual(len(calls), 3)
        finally:
            recovery_plan.gh_api = orig

    def test_pagination_stops_at_total(self):
        import recovery_plan

        def mock_gh_api(path):
            return {"total_count": 5,
                    "artifacts": [{"id": i} for i in range(5)]}

        orig = recovery_plan.gh_api
        recovery_plan.gh_api = mock_gh_api
        try:
            items = recovery_plan.gh_api_paginated_list("/x", "artifacts")
            self.assertEqual(len(items), 5)
        finally:
            recovery_plan.gh_api = orig


class TestManifestProvenance(unittest.TestCase):
    def test_origin_manifest_sha_is_file_hash_not_video_hash(self):
        # The resume plan's origin_manifest_sha256 must differ from the
        # video hash (it's the manifest file's hash).
        sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                       "../.github/scripts"))
        from recovery import build_resume_plan
        sys.path.insert(0, os.path.dirname(__file__))
        from test_recovery import (make_job_manifest, make_chunk_manifest,
                                   base_inputs, manifest_file_sha)

        src = "a" * 40
        prior = make_job_manifest(run_id="111", sha=src,
                                  inputs=base_inputs(source_sha=src))
        gen = prior["generation_fingerprint"]
        # Build 3 chunks to match the prior's 3-chunk plan.
        pcm = {}
        for cid in range(3):
            s, e = cid * 100, cid * 100 + 99
            cm = make_chunk_manifest(prior["job_identity"], cid, s, e, gen,
                                     source_sha=src)
            pcm[cid] = cm
        real_shas = {cid: cm["output_sha256"] for cid, cm in pcm.items()}
        mshas = {cid: manifest_file_sha(cm) for cid, cm in pcm.items()}
        current = base_inputs(source_sha=src)
        plan = [{"chunk_id": i, "start": i * 100, "end": i * 100 + 99}
                for i in range(3)]
        result = build_resume_plan(
            prior, pcm, current, plan,
            prior["inputs"]["asset_manifest_sha256"],
            artifact_shas=real_shas, manifest_shas=mshas)
        self.assertTrue(result["ok"], f"errors: {result.get('errors')}")
        rp = result["resume_plan"]
        self.assertEqual(len(rp["reuse"]), 3)
        for entry in rp["reuse"]:
            # Manifest file hash != video hash (proves it's not a copy).
            self.assertNotEqual(entry["origin_manifest_sha256"],
                                entry["verified_output_sha256"])
            self.assertEqual(entry["origin_manifest_sha256"],
                             mshas[entry["chunk_id"]])


class TestArtifactDownloadRedirect(unittest.TestCase):
    """P4.1: artifact download must handle cross-origin redirects safely.

    The GitHub API returns 302 to artifact storage (different host).
    The GitHub bearer token must NOT be forwarded to the storage host.
    """

    def _make_module(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "recovery_plan_test",
            os.path.join(os.path.dirname(__file__),
                         "../.github/scripts/recovery_plan.py"))
        mod = importlib.util.module_from_spec(spec)
        # Stub out the fatal() to raise instead of exiting.
        return mod, spec

    def test_redirect_strips_auth_header(self):
        """Auth header is sent to api.github.com but NOT to storage host."""
        import urllib.request
        import urllib.error
        import io

        sent_headers = {}

        class FakeResp:
            def __init__(self, headers, body=b""):
                self.headers = headers
                self._body = io.BytesIO(body)
            def read(self, n=-1):
                return self._body.read(n)
            def close(self):
                pass

        original_build_opener = urllib.request.build_opener

        def fake_build_opener(*handlers):
            class FakeOpener:
                def open(self, req, timeout=None):
                    url = req.full_url
                    # Record Authorization header presence per host.
                    auth = req.get_header("Authorization")
                    sent_headers[url] = auth is not None
                    if "api.github.com" in url:
                        # Simulate 302 redirect to storage.
                        err = urllib.error.HTTPError(
                            url, 302, "Found", {}, None)
                        err.headers = {"Location":
                                       "https://objects.example.com/signed?sig=abc"}
                        raise err
                    elif "objects.example.com" in url:
                        return FakeResp({}, b"fake-zip-content")
                    raise AssertionError(f"unexpected URL {url}")
            return FakeOpener()

        urllib.request.build_opener = fake_build_opener
        try:
            mod, spec = self._make_module()
            # We need REPO and fatal; exec only the function in isolation.
            # Instead, test the logic directly by importing and calling
            # with mocked environment.
            import types
            # Build a minimal namespace to exec the function.
            src = open(os.path.join(
                os.path.dirname(__file__),
                "../.github/scripts/recovery_plan.py")).read()
            # Extract just the download function via exec in a namespace.
            ns = {"os": os, "sys": sys}
            # Provide fatal that raises.
            class FatalErr(Exception):
                pass
            ns["fatal"] = lambda msg: (_ for _ in ()).throw(FatalErr(msg))
            ns["REPO"] = "o/r"
            os.environ["GITHUB_TOKEN"] = "test-token-123"
            # Find and exec only the download_artifact_zip def.
            start = src.index("def download_artifact_zip(")
            end = src.index("\ndef extract_json(")
            exec(src[start:end], ns)
            import tempfile
            tmpd = tempfile.mkdtemp()
            try:
                path = ns["download_artifact_zip"](999, tmpd)
                with open(path, "rb") as f:
                    self.assertEqual(f.read(), b"fake-zip-content")
            finally:
                import shutil
                shutil.rmtree(tmpd, ignore_errors=True)
            # Verify: auth sent to API, NOT to storage host.
            api_url = [u for u in sent_headers if "api.github.com" in u][0]
            storage_url = [u for u in sent_headers
                           if "objects.example.com" in u][0]
            self.assertTrue(sent_headers[api_url],
                            "auth must be sent to api.github.com")
            self.assertFalse(sent_headers[storage_url],
                             "auth must NOT be forwarded to storage host")
        finally:
            urllib.request.build_opener = original_build_opener

    def test_non_https_redirect_rejected(self):
        """Redirect to non-HTTPS URL fails closed."""
        import urllib.request
        import urllib.error

        def fake_build_opener(*handlers):
            class FakeOpener:
                def open(self, req, timeout=None):
                    if "api.github.com" in req.full_url:
                        err = urllib.error.HTTPError(
                            req.full_url, 302, "Found", {}, None)
                        err.headers = {"Location":
                                       "http://evil.example.com/file"}
                        raise err
                    raise AssertionError("should not reach here")
            return FakeOpener()

        original = urllib.request.build_opener
        urllib.request.build_opener = fake_build_opener
        try:
            src = open(os.path.join(
                os.path.dirname(__file__),
                "../.github/scripts/recovery_plan.py")).read()
            ns = {"os": os, "sys": sys}
            class FatalErr(Exception):
                pass
            ns["fatal"] = lambda msg: (_ for _ in ()).throw(FatalErr(msg))
            ns["REPO"] = "o/r"
            os.environ["GITHUB_TOKEN"] = "test-token-123"
            start = src.index("def download_artifact_zip(")
            end = src.index("\ndef extract_json(")
            exec(src[start:end], ns)
            import tempfile
            tmpd = tempfile.mkdtemp()
            try:
                with self.assertRaises(FatalErr) as ctx:
                    ns["download_artifact_zip"](999, tmpd)
                self.assertIn("non-HTTPS", str(ctx.exception))
            finally:
                import shutil
                shutil.rmtree(tmpd, ignore_errors=True)
        finally:
            urllib.request.build_opener = original

    def test_failed_download_is_explicit(self):
        """HTTP 401 from API fails with clear diagnostic, no false success."""
        import urllib.request
        import urllib.error

        def fake_build_opener(*handlers):
            class FakeOpener:
                def open(self, req, timeout=None):
                    err = urllib.error.HTTPError(
                        req.full_url, 401, "Unauthorized", {}, None)
                    # Simulate empty body read.
                    err.read = lambda: b""
                    raise err
            return FakeOpener()

        original = urllib.request.build_opener
        urllib.request.build_opener = fake_build_opener
        try:
            src = open(os.path.join(
                os.path.dirname(__file__),
                "../.github/scripts/recovery_plan.py")).read()
            ns = {"os": os, "sys": sys}
            class FatalErr(Exception):
                pass
            ns["fatal"] = lambda msg: (_ for _ in ()).throw(FatalErr(msg))
            ns["REPO"] = "o/r"
            os.environ["GITHUB_TOKEN"] = "test-token-123"
            start = src.index("def download_artifact_zip(")
            end = src.index("\ndef extract_json(")
            exec(src[start:end], ns)
            import tempfile
            tmpd = tempfile.mkdtemp()
            try:
                with self.assertRaises(FatalErr) as ctx:
                    ns["download_artifact_zip"](999, tmpd)
                msg = str(ctx.exception)
                self.assertIn("401", msg)
                # Token must not appear in the diagnostic.
                self.assertNotIn("test-token-123", msg)
            finally:
                import shutil
                shutil.rmtree(tmpd, ignore_errors=True)
        finally:
            urllib.request.build_opener = original


if __name__ == "__main__":
    unittest.main(verbosity=2)
