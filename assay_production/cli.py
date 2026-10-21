"""The installed commands.

``assay-verify``    prove the answer key (the same as ``verify_manifest.py`` in a checkout)
``assay-manifest``  print the registry, or deliberately re-record it with ``--write``

Both need a checkout of the repository: the specimens and MANIFEST.md are the
data being proven and are not part of the installed package. Point them at one
with ``--root PATH`` (or ``ASSAY_ROOT``), or run them inside it. Arguments they
do not know exit 2 and do nothing.
"""
from __future__ import annotations

import sys
from typing import Optional, Sequence


def verify(argv: Optional[Sequence[str]] = None) -> int:
    from . import verification
    return verification.main(None, sys.argv[1:] if argv is None else argv, prog="assay-verify")


def manifest(argv: Optional[Sequence[str]] = None) -> int:
    from . import manifest_registry
    return manifest_registry.main(list(sys.argv[1:] if argv is None else argv), prog="assay-manifest")


if __name__ == "__main__":
    raise SystemExit(verify())
