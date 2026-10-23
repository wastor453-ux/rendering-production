# Finance Video Factory — Rendering Production

A Remotion-based finance-video production repository with chunked rendering, audio mixing, artifact verification, and GitHub Actions checks.

## Start here
1. [Production Quickstart](docs/QUICKSTART.md)
2. [Production Operations Manual](docs/PRODUCTION_OPERATIONS_MANUAL.md)
3. [Release Checklist](docs/RELEASE_CHECKLIST.md)
4. [Troubleshooting](docs/TROUBLESHOOTING.md)
5. [Production Run Record Template](docs/PRODUCTION_RUN_RECORD_TEMPLATE.md)

## Main areas
- `.github/workflows/render-production.yml` — production rendering workflow and artifact gates.
- `.github/workflows/render-benchmark.yml` — benchmark workflow.
- `src/RemotionRoot.tsx` — registered Remotion compositions.
- `src/compiled_p3/` — P3 timeline, events, and payloads used by the production preflight.
- `scripts/` — verification and workflow contract tests.
- `public/audio/` and `audio/` — committed audio assets.

## Important release rule
Green CI means configured automated checks passed. It does not prove that a real master was rendered, visually correct, factually accurate, or synchronized by ear. Verify the actual artifact and complete the release checklist before delivery. Rendering, merging, and publishing require explicit authorization.

## Reproducible setup
Use the Node version configured in the workflow and install dependencies with `npm ci`. Check `package.json` for the available scripts rather than assuming a generic command exists.

## Current documentation note
The manual records the last known status when written. Always check the latest GitHub Actions run and the actual artifact before making release claims.
