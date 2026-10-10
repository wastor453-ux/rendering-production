#!/usr/bin/env python3
"""NEGATIVE-CHECK FIXTURE — NOT A REAL TEST.

Purpose: prove that the `npm test` script in package.json propagates
failures (i.e. exits nonzero when a step fails).

This fixture ALWAYS fails on purpose. It is:
  - NEVER referenced by the `test` script in package.json
  - NEVER imported by any real test module
  - SAFE under `python3 -m unittest discover` (module-level import defines
    no tests and performs no assertions)

Run it directly, and ONLY directly:

    python3 tests/test_runner_negative_fixture.py   # expected: exit 1

If this file's failure ever shows up in a normal suite run, the test
harness is misconfigured — do not "fix" this file to pass.
"""
import sys


def main() -> int:
    print("NEGATIVE CHECK FIXTURE: intentional failure "
          "(this is the expected outcome of the failure-path check).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
