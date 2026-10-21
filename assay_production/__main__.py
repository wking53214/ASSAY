"""``python -m assay_production`` is ``assay-verify``."""
import sys

from .cli import verify

raise SystemExit(verify(sys.argv[1:]))
