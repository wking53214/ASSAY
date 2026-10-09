#!/usr/bin/env python3
"""Check that every specimen still behaves the way MANIFEST.md says it does.

A corpus whose answer key has drifted from its contents is worse than no
corpus: it scores verifiers against claims that are no longer true, and does
it confidently. This script is the guard against that, and it should be run
before anyone trusts a score produced from this repository.

It deliberately asserts the *damage*. A specimen that quietly got fixed --
someone reformatting a flattened file, someone defining the missing method in
UZTC -- destroys the thing that made it a specimen, and this reports it as a
failure rather than an improvement.

What it checks, in plain terms:

* every specimen still behaves as MANIFEST.md says (specimens are RUN in a
  sandbox: a separate process, scratch directory, stripped environment,
  timeout, no network where the machine allows it, and a write guard);
* the four copies of the answer key agree: the MANIFEST.md prose, the
  machine block in MANIFEST.md, the table in assay_production/
  manifest_registry.py and assay_production/registry.json;
* every file under specimens/ still has the SHA-256 recorded for it;
* each registry entry's validation status is what this run really asserted;
* the numbers in the README status block are the true ones.

    python3 verify_manifest.py            # exits non-zero on drift
    python3 verify_manifest.py --strict   # also fail if a claim could not be run here
    python3 -m assay_production.manifest_registry --write   # deliberate re-record

Works from any directory and needs no network.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from assay_production import verification  # noqa: E402

if __name__ == "__main__":
    sys.exit(verification.main(ROOT, sys.argv[1:]))
