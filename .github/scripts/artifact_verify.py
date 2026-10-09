#!/usr/bin/env python3
"""Safe inspection of prior-run artifact archives (P3.12.2).

Every function here classifies failures deliberately: a bad individual
archive yields an ineligibility reason (rerender), never an unhandled
exception that kills the whole selection process. Generation-wide
contradictions are reported as errors (fail closed).

Safety rules:
- Never extract archives blindly. Member paths are validated before use:
  reject absolute paths, `..` traversal, symlinks, and duplicates.
- Require exactly one video and one manifest per chunk archive, matched by
  chunk ID — not by first-basename-match.
- The original archives are never modified.
"""

import hashlib
import io
import json
import os
import zipfile


class ArchiveError(Exception):
    """A single archive is unusable. The chunk is rerendered, not reused."""
    pass


class ArchiveContradiction(Exception):
    """Archive content contradicts expectations. Fail closed."""
    pass


def _safe_members(zf):
    """Yield (info) for members with safe paths. Raise on unsafe members."""
    seen = set()
    for info in zf.infolist():
        name = info.filename
        # Reject absolute paths and traversal.
        if os.path.isabs(name):
            raise ArchiveContradiction(f"absolute path in archive: {name!r}")
        parts = name.replace("\\", "/").split("/")
        if ".." in parts:
            raise ArchiveContradiction(f"traversal in archive: {name!r}")
        # Reject symlinks (external_attr symlink bits).
        if (info.external_attr >> 16) & 0o170000 == 0o120000:
            raise ArchiveContradiction(f"symlink in archive: {name!r}")
        # Skip directory entries.
        if name.endswith("/"):
            continue
        norm = "/".join(p for p in parts if p not in (".", ""))
        if norm in seen:
            raise ArchiveContradiction(
                f"duplicate member in archive: {name!r}")
        seen.add(norm)
        yield info


def open_archive(path):
    """Open a ZIP archive, classifying corruption deliberately."""
    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile as e:
        raise ArchiveError(f"corrupt ZIP: {e}")
    except FileNotFoundError:
        raise ArchiveError("archive file not found")
    except OSError as e:
        raise ArchiveError(f"cannot read archive: {e}")
    # Validate the central directory by listing members.
    try:
        list(_safe_members(zf))
    except ArchiveContradiction:
        zf.close()
        raise
    except Exception as e:
        zf.close()
        raise ArchiveError(f"cannot list archive members: {e}")
    return zf


def find_chunk_files(zf, chunk_id):
    """Locate exactly one video and one manifest for chunk_id.

    Returns (video_info, manifest_info). Raises ArchiveError if either is
    missing; ArchiveContradiction on duplicates or ambiguity.
    """
    video_name = f"chunk_{chunk_id}.mp4"
    manifest_name = f"chunk_{chunk_id}_manifest.json"
    videos = []
    manifests = []
    for info in _safe_members(zf):
        base = os.path.basename(info.filename)
        if base == video_name:
            videos.append(info)
        elif base == manifest_name:
            manifests.append(info)
    if len(videos) == 0:
        raise ArchiveError(f"missing video {video_name}")
    if len(videos) > 1:
        raise ArchiveContradiction(
            f"duplicate video entries for chunk {chunk_id}")
    if len(manifests) == 0:
        raise ArchiveError(f"missing manifest {manifest_name}")
    if len(manifests) > 1:
        raise ArchiveContradiction(
            f"duplicate manifest entries for chunk {chunk_id}")
    return videos[0], manifests[0]


def read_manifest(zf, manifest_info):
    """Parse the chunk manifest JSON, classifying malformation."""
    try:
        with zf.open(manifest_info.filename) as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ArchiveError(f"malformed manifest JSON: {e}")
    except Exception as e:
        raise ArchiveError(f"cannot read manifest: {e}")
    if not isinstance(data, dict):
        raise ArchiveError("manifest JSON is not an object")
    return data


def hash_member(zf, info):
    """SHA-256 hash and size of a member's bytes. Rejects LFS pointers."""
    try:
        with zf.open(info.filename) as f:
            head = f.read(200)
            if b"git-lfs.github.com" in head:
                raise ArchiveError("member is a Git LFS pointer, not content")
            h = hashlib.sha256()
            h.update(head)
            size = len(head)
            for block in iter(lambda: f.read(65536), b""):
                h.update(block)
                size += len(block)
    except ArchiveError:
        raise
    except Exception as e:
        raise ArchiveError(f"cannot hash member: {e}")
    if size == 0:
        raise ArchiveError("member is empty")
    return h.hexdigest(), size


def manifest_bytes_sha256(zf, manifest_info):
    """SHA-256 of the raw manifest FILE bytes (P3.12.2 provenance)."""
    try:
        with zf.open(manifest_info.filename) as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        raise ArchiveError(f"cannot hash manifest bytes: {e}")


def inspect_chunk_archive(path, chunk_id):
    """Fully inspect one chunk artifact archive.

    Returns {"manifest": dict, "video_sha256": str, "video_bytes": int,
             "manifest_sha256": str} on success.
    Raises ArchiveError (rerender this chunk) or ArchiveContradiction
    (fail closed).
    """
    zf = open_archive(path)
    try:
        video_info, manifest_info = find_chunk_files(zf, chunk_id)
        manifest = read_manifest(zf, manifest_info)
        video_sha, video_bytes = hash_member(zf, video_info)
        manifest_sha = manifest_bytes_sha256(zf, manifest_info)
    finally:
        zf.close()
    # The manifest must belong to this exact chunk.
    if manifest.get("chunk_id") != chunk_id:
        raise ArchiveContradiction(
            f"manifest chunk_id {manifest.get('chunk_id')} != "
            f"expected {chunk_id}")
    return {"manifest": manifest, "video_sha256": video_sha,
            "video_bytes": video_bytes, "manifest_sha256": manifest_sha}
