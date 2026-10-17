"""Small shared runtime helpers: where the checkout is, and diagnostic logging.

Nothing here touches stdout. The verifier's stdout is a contract (the report
and, as its last line, ``ASSAY-SUMMARY: ...``), so diagnostics go to stderr
through the standard ``logging`` module, at a level chosen by the environment
variable ``ASSAY_LOG_LEVEL`` (``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``;
default ``WARNING``, which prints nothing on a normal run).
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Optional

LOG_LEVEL_ENV = "ASSAY_LOG_LEVEL"
LOGGER_NAME = "assay"
_FORMAT = "assay[%(levelname)s] %(name)s: %(message)s"

_LEVELS = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING,
           "ERROR": logging.ERROR, "CRITICAL": logging.CRITICAL}


class _StderrHandler(logging.StreamHandler):
    """Marker type, so configuring twice replaces the handler instead of stacking a second one."""


def get_logger(name: str = "") -> logging.Logger:
    """The ``assay`` logger, or a child of it (``assay.verify``)."""
    return logging.getLogger(f"{LOGGER_NAME}.{name}" if name else LOGGER_NAME)


def configure_logging(env: Optional[dict] = None) -> int:
    """Send ``assay.*`` log records to stderr at the level ``ASSAY_LOG_LEVEL`` names. Safe to call twice.

    An unknown level is reported once and ignored (WARNING is used): a
    diagnostics knob must never decide whether the key is proven.
    """
    environ = os.environ if env is None else env
    raw = (environ.get(LOG_LEVEL_ENV) or "").strip()
    level = _LEVELS.get(raw.upper(), logging.WARNING) if raw else logging.WARNING
    logger = logging.getLogger(LOGGER_NAME)
    for handler in list(logger.handlers):
        if isinstance(handler, _StderrHandler):
            logger.removeHandler(handler)
    handler = _StderrHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(_FORMAT))
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    if raw and raw.upper() not in _LEVELS:
        logger.warning("%s=%r is not one of %s; using WARNING", LOG_LEVEL_ENV, raw, ", ".join(_LEVELS))
    return level


class CheckoutNotFound(Exception):
    """No ASSAY checkout (a folder with MANIFEST.md and specimens/) could be found."""


def is_checkout(path: Path) -> bool:
    return (path / "MANIFEST.md").is_file() and (path / "specimens").is_dir()


def resolve_root(explicit: Optional[str] = None, *, prefer_package: bool = False) -> Path:
    """The ASSAY checkout to work on.

    The answer key (``specimens/`` and ``MANIFEST.md``) is data that lives in
    the repository and is not part of the installed package, so an installed
    ``assay-verify`` needs a checkout. In order: ``--root``, the
    ``ASSAY_ROOT`` environment variable, the current directory, then the
    folder the package itself sits in (an editable install or a plain
    checkout); ``prefer_package`` swaps those last two. Anything else is an
    error, never a guess.
    """
    candidates = []
    if explicit:
        candidates.append(("--root", Path(explicit)))
    elif os.environ.get("ASSAY_ROOT"):
        candidates.append(("ASSAY_ROOT", Path(os.environ["ASSAY_ROOT"])))
    if explicit or os.environ.get("ASSAY_ROOT"):
        label, path = candidates[0]
        if not is_checkout(path):
            raise CheckoutNotFound(f"{label} {str(path)!r} is not an ASSAY checkout "
                                   "(it needs MANIFEST.md and specimens/)")
        return path.resolve()
    here = [Path.cwd(), Path(__file__).resolve().parent.parent]
    for path in (reversed(here) if prefer_package else here):
        if is_checkout(path):
            return path.resolve()
    raise CheckoutNotFound("no ASSAY checkout found: the answer key (MANIFEST.md and specimens/) is not part of "
                           "the installed package. Run this inside a checkout, or pass --root PATH "
                           "(or set ASSAY_ROOT).")
