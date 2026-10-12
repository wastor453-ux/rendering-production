#!/usr/bin/env python3
"""Provision the faster-whisper model required by tools/align_vo.py.

The aligner requires a pinned model at:
  ~/.cache/huggingface/hub/models--Systran--faster-whisper-base/snapshots/ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66

This script downloads it if not present. Called by the workflow before alignment.
"""
import os
import sys

MODEL_REPO = "Systran/faster-whisper-base"
MODEL_REVISION = "ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66"

def main():
    model_path = os.path.expanduser(
        "~/.cache/huggingface/hub/models--Systran--faster-whisper-base"
        f"/snapshots/{MODEL_REVISION}"
    )
    if os.path.exists(model_path):
        print(f"Model already cached: {model_path}")
        return 0
    
    print(f"Downloading {MODEL_REPO}@{MODEL_REVISION}...", file=sys.stderr)
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("FATAL: huggingface_hub not installed. Run: pip install huggingface-hub", file=sys.stderr)
        return 1
    
    snapshot_download(repo_id=MODEL_REPO, revision=MODEL_REVISION)
    print("Model download complete.", file=sys.stderr)
    
    if not os.path.exists(model_path):
        print(f"FATAL: Model not found after download: {model_path}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
