"""The answer key as a CNS gate (``cns.gate``), at the ALPHA end.

ASSAY is independent. It has no runtime dependency, imports nothing from CNS
when it loads, and its verifier and sandbox never import it. This module is
the one place that knows CNS exists, and it asks for CNS only when a gate is
built. Without CNS installed, building one raises :class:`CnsNotInstalled`
with the install command; nothing else in ASSAY is affected.

The question this gate answers
------------------------------
ASSAY's own question, in ASSAY's own words: *is the answer key proven, before
anyone grades against it?* It answers nothing else. What a failed proof means
for a run is the Judge's to decide, not this gate's.

The candidate is the path of an ASSAY checkout (a ``str`` or ``os.PathLike``).
It is not the verifier's result, because a result carries no key content: a
verdict on a result could be moved onto any key. A path can be read, hashed
and verified, so the verdict is bound to what was actually proven.

How the gate runs the verifier
------------------------------
Through the checkout's real entry point, ``verify_manifest.py``, as a
subprocess, the way SWIZZLE does. Not in this process: ``verification.main``
marks its process non-dumpable, installs signal handlers and, when it is not
the real script, clears ``os.environ``, none of which a loop that calls this
gate may have done to it. The structured result is the single line the
verifier prints last, ``ASSAY-SUMMARY: {json}`` (schema ``assay-summary/1``,
documented in the README), read together with the exit code. The two must
agree; when they do not, the answer is not read as permission.

The mapping, and why
--------------------
=============================  ================================================
ASSAY                          CNS
=============================  ================================================
gate position                  ``ALPHA``. The key is proven before anyone
                               grades against it; if it fails, the grading
                               never starts. This connector has no outcome end.
exit 0, no failing claim,      ``PASS``. The key is proven: every claim holds
no skipped claim, status       and none was left unrun. Proven here is ASSAY's
``ANSWER_KEY_VALIDATED`` or    word for an intact key whose runnable claims
``ANSWER_KEY_UNVALIDATED``     hold. The reason states how many entries rest
                               on a human judgement ("unvalidated"), because
                               PASS does not mean those were re-measured.
a claim failed (a changed      ``TERMINAL_BREACH``. Drift, a changed file hash,
specimen, a changed hash, the  the four copies of the key disagreeing, a
four copies disagreeing, a     tripped sandbox guard or a forged result. The
tripped guard, ...)            key is not what it was recorded to be, and no
                               retry repairs a changed key.
only claims that timed out     ``RETRY``. A timeout is a slow machine, not a
(reason ``timeout``)           changed specimen: the hash claims are separate
                               and held. Ask again, ideally when the machine
                               is quieter.
a claim could not be run here  ``RETRY``. A specimen needs numpy or
(skipped, missing library)     matplotlib that is not installed. The claim was
                               not measured, so nothing is proven; install the
                               library and ask again.
the verifier did not complete  ``RETRY``. It crashed, was killed, did not
(no summary line, odd exit     finish within ``timeout`` or could not be
code, could not be started,    started. Nothing was measured, so nothing is
timed out) or the key changed  permitted, and asking again is meaningful.
while it was being proven
a summary or exit code the     ``TERMINAL_BREACH``. An answer the connector
gate does not recognise (a     does not recognise is never read as permission.
wrong schema, exit 0 with a
failing claim, ...)
a candidate that is not a      ``TERMINAL_BREACH``, unbound. Nothing can be
path, is not an ASSAY          proven about it.
checkout, or whose key cannot
be read and hashed
=============================  ================================================

RETRY is still a refusal: ``cns.gate.resolve`` lets nothing through on it. It
differs from a breach only in saying that asking again can change the answer.

What the verdict is bound to
----------------------------
``subject_digest`` over the key's real content, read from the checkout with
the verifier's own functions (no hashing is done here):

* ``registry``: the parsed ``assay_production/registry.json``, which carries
  the recorded SHA-256 of every specimen and companion, the machine block's
  digest and every verdict;
* ``corpus_files``: the SHA-256 the verifier computes now for every entry
  under ``specimens/`` (``manifest_registry.corpus_files``);
* ``manifest``: the SHA-256 of ``MANIFEST.md``;
* ``verifier``: the SHA-256 of ``verify_manifest.py`` and of every module of
  ``assay_production`` that proves the key (this module is left out: it
  judges the verifier, it is not part of it).

A PASS therefore names one key proven by one verifier. It cannot be moved onto
a different key, and the same key at another path digests alike. The digest is
read before the verifier runs and again after; a key that changed in between
was not proven, and is a RETRY. This is tamper-evidence, not tamper-proofing:
a consumer compares the digest with the one it expects (``GateResult.binds``).

Install with the extra from a checkout: ``pip install -e '.[cns]'``. ASSAY is not published on PyPI, so it cannot
be installed by name; for just CNS, ``pip install "cns @ git+https://github.com/wking53214/CNS.git@v2.2.0"``.
"""

from __future__ import annotations

import importlib
import json
import os
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Optional

from . import manifest_registry as mr
from . import runtime
from . import sandbox as sandbox_module
from .verification import SUMMARY_PREFIX, SUMMARY_SCHEMA

log = runtime.get_logger("gate")

__all__ = [
    "AssayKeyGate",
    "CnsNotInstalled",
    "VerifierRun",
    "cns_available",
    "cns_chain",
    "key_content",
    "key_digest",
]

# ASSAY is not on PyPI (installing it by its bare name fails or fetches someone else's package), so the hint names
# the two commands that work. The CNS spec is the cns extra of pyproject.toml; tests/test_install_hints.py holds
# them equal.
INSTALL_HINT = (
    "pip install -e '.[cns]' (from an ASSAY checkout), or, for just CNS: "
    "pip install \"cns @ git+https://github.com/wking53214/CNS.git@v2.2.0\""
)

#: What ``subject`` is set to when the caller does not name the judged key.
DEFAULT_SUBJECT = "assay-answer-key"

#: Statuses the verifier gives a key whose claims all held.
_PROVEN_STATUSES = ("ANSWER_KEY_VALIDATED", "ANSWER_KEY_UNVALIDATED")

#: Failure reasons that mean "could not be measured here", not "the key changed".
#: Only a timeout, which the README says is reported so that a slow machine is
#: not mistaken for a changed specimen. Every other reason is read as drift.
_RETRYABLE_REASONS = frozenset({"timeout"})

#: Extra seconds on top of the verifier's own total budget before the gate gives up on it.
_GRACE_SECONDS = 60.0

#: This module judges the verifier; it is not part of what proves the key.
_NOT_THE_VERIFIER = frozenset({"cns_connector.py"})

#: The modules a checkout must have for ``verify_manifest.py`` to run at all. Any other module is hashed too.
_VERIFIER_MODULES = frozenset({"__init__.py", "verification.py", "sandbox.py", "manifest_registry.py",
                               "manifest_status.py", "specimen_registry.py"})


class CnsNotInstalled(ImportError):
    """Raised when a gate is built and ``cns`` cannot be imported."""


def _cns_gate() -> ModuleType:
    """Import ``cns.gate`` on demand, or say exactly what is missing."""
    try:
        return importlib.import_module("cns.gate")
    except ImportError as exc:
        raise CnsNotInstalled(
            "assay_production.cns_connector needs the CNS package (cns.gate), which is not "
            f"installed. Install it with: {INSTALL_HINT}. ASSAY itself works without it."
        ) from exc


def _assay_row() -> Optional[ModuleType]:
    """``cns.assay``, the shared row for the summary line, or None where the installed CNS has none.

    CNS v1.8.0 has none; v1.9.0 and later have it.

    Asked for at the moment a summary is read, like ``cns.gate``: nothing here imports CNS when the module loads.
    """
    try:
        return importlib.import_module("cns.assay")
    except ImportError:
        return None


def assay_row_available() -> bool:
    """Whether summaries are also checked against CNS's shared row in this environment."""
    return _assay_row() is not None


def cns_available() -> bool:
    """Whether the CNS gate contract can be imported in this environment."""
    try:
        _cns_gate()
    except CnsNotInstalled:
        return False
    return True


# ------------------------------------------------------------- what is judged

def _verifier_files(root: Path) -> list:
    code = {p.name for p in (root / "assay_production").glob("*.py")} - _NOT_THE_VERIFIER
    return ["verify_manifest.py", *("assay_production/" + n for n in sorted(code | _VERIFIER_MODULES))]


def key_content(root: "str | os.PathLike[str]") -> dict:
    """The key's real content as plain data a digest can bind, read from a checkout.

    Raises ``ValueError`` when the checkout has no readable key (no registry,
    a registry with repeated ids, nothing under ``specimens/``, no manifest) and
    ``OSError`` when a file cannot be read.
    """
    root = Path(root)
    registry, problem = mr.load_registry_strict(mr.registry_path(root))
    if problem or not isinstance(registry, dict) or not registry:
        raise ValueError(problem or "registry.json is not a non-empty mapping of specimens")
    corpus = mr.corpus_files(root)
    if not corpus:
        raise ValueError("there is nothing under specimens/ to prove")
    manifest = mr.hash_path(root, "MANIFEST.md")
    if manifest is None:
        raise ValueError("MANIFEST.md is missing")
    verifier = {rel: mr.hash_path(root, rel) for rel in _verifier_files(root)}
    missing = sorted(rel for rel, digest in verifier.items() if digest is None)
    if missing:
        raise ValueError("the verifier is incomplete: " + ", ".join(missing))
    return {"registry": registry, "corpus_files": corpus, "manifest": manifest, "verifier": verifier}


def key_digest(root: "str | os.PathLike[str]") -> str:
    """The digest a verdict on the key at ``root`` carries.

    Pass it, with the subject label, to ``GateResult.binds`` to check that a
    verdict was issued against exactly this key.
    """
    return _cns_gate().subject_digest(key_content(root))


# ----------------------------------------------------------- running the proof

@dataclass(frozen=True)
class VerifierRun:
    """What running ``verify_manifest.py`` produced. ``returncode`` is None when it timed out."""

    returncode: Optional[int]
    stdout: str
    stderr: str
    timed_out: bool = False


def run_verifier(root: Path, timeout: float) -> VerifierRun:
    """Run the checkout's own ``verify_manifest.py`` as a subprocess, with ASSAY's minimal environment."""
    env = sandbox_module.minimal_parent_environment()
    env.pop("ASSAY_MINIMAL_ENV", None)  # let the verifier restart itself exactly as it does when run by hand
    log.info("running %s in a subprocess, unsandboxed (the candidate's own code; see README, Security and limits); "
             "timeout %gs", root / "verify_manifest.py", timeout)
    proc = subprocess.Popen(
        [sys.executable, str(root / "verify_manifest.py")], cwd=str(root), env=env,
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, errors="replace", start_new_session=True)
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            proc.kill()
        out, err = proc.communicate()
        log.info("the verifier did not finish within %gs and its process group was killed", timeout)
        return VerifierRun(None, out or "", err or "", timed_out=True)
    log.info("the verifier exited %s", proc.returncode)
    log.debug("verifier stderr (tail): %s", err[-400:] if err else "")
    return VerifierRun(proc.returncode, out, err)


def _int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _read_summary(stdout: str) -> Optional[dict]:
    """The verifier's last line as a checked ``assay-summary/1`` record, None if there is no such line.

    Raises ``ValueError`` for a summary that is there but not the record the
    README documents. Where the installed CNS has ``cns.assay`` the record is
    also read through that row, and a record it refuses is refused here too.
    """
    lines = [ln for ln in stdout.splitlines() if ln.strip()]
    if not lines or not lines[-1].startswith(SUMMARY_PREFIX):
        return None
    try:
        record = json.loads(lines[-1][len(SUMMARY_PREFIX):])
    except ValueError as exc:
        raise ValueError(f"the summary line is not JSON ({exc})") from exc
    if not isinstance(record, dict):
        raise ValueError("the summary is not a mapping")
    if record.get("schema") != SUMMARY_SCHEMA:
        raise ValueError(f"the summary is not schema {SUMMARY_SCHEMA!r} (it says {record.get('schema')!r})")
    claims, failures = record.get("claims"), record.get("failures")
    if (not isinstance(claims, dict) or not all(_int(claims.get(k)) for k in ("total", "passed", "failed", "skipped"))
            or not isinstance(record.get("all_claims_hold"), bool) or not isinstance(record.get("status"), str)
            or not isinstance(failures, list)
            or not all(isinstance(f, dict) and isinstance(f.get("claim"), str) and isinstance(f.get("reason"), str)
                       for f in failures)):
        raise ValueError("the summary does not have the documented fields")
    if claims["failed"] != len(failures) or claims["passed"] + claims["failed"] != claims["total"]:
        raise ValueError("the summary's claim counts do not add up")
    row = _assay_row()
    if row is not None:
        # The record passed this connector's own reading. The shared row is CNS's statement of the same shape, so a
        # summary that satisfies one and not the other means ASSAY and CNS have drifted apart; say so rather than guess.
        try:
            row.AssaySummary.from_dict(record)
        except ValueError as exc:
            raise ValueError(f"the summary is not the shared cns.assay row ({exc})") from exc
    return record


def _tail(text: str, n: int = 240) -> str:
    one = " ".join(text.split())
    return one[-n:]


class AssayKeyGate:
    """ASSAY's answer key as a ``cns.gate.Gate`` at the ALPHA end.

    ``check`` takes the path of an ASSAY checkout, proves its key by running
    its verifier, and returns the answer as a ``cns.gate.GateResult`` bound to
    the key's content. An exception from ASSAY's own logic propagates; it is
    never turned into a PASS. Constructing a gate without CNS installed raises
    :class:`CnsNotInstalled`.
    """

    def __init__(self, *, subject: str = DEFAULT_SUBJECT, timeout: Optional[float] = None,
                 runner: Optional[Callable[[Path, float], VerifierRun]] = None) -> None:
        self._cns = _cns_gate()
        self._subject = subject
        self._timeout = timeout
        self._runner = runner if runner is not None else run_verifier

    @property
    def name(self) -> str:
        return "assay.key_proven"

    @property
    def position(self) -> Any:
        return self._cns.GatePosition.ALPHA

    def _result(self, outcome_name: str, reason: str, digest: str = "") -> Any:
        c = self._cns
        return c.GateResult(
            gate=self.name, position=c.GatePosition.ALPHA, outcome=getattr(c.GateOutcome, outcome_name),
            reason=reason, subject=self._subject, subject_digest=digest)

    @staticmethod
    def _checkout(candidate: object) -> Path:
        """The candidate as a checkout directory, or ValueError saying why it is not one."""
        if not isinstance(candidate, (str, os.PathLike)):
            raise ValueError(f"{type(candidate).__name__} is not the path of an ASSAY checkout")
        text = os.fspath(candidate)
        if not isinstance(text, str) or not text.strip():
            raise ValueError("an empty or non-text path is not the path of an ASSAY checkout")
        root = Path(text).resolve()
        for rel, ok in (("verify_manifest.py", root.joinpath("verify_manifest.py").is_file()),
                        ("specimens/", root.joinpath("specimens").is_dir()),
                        ("assay_production/registry.json", root.joinpath("assay_production/registry.json").is_file())):
            if not ok:
                raise ValueError(f"{root} is not an ASSAY checkout ({rel} is missing)")
        return root

    def check(self, candidate: object) -> Any:
        if os.environ.get(runtime.LOG_LEVEL_ENV):
            runtime.configure_logging()  # opt in by environment; a library does not touch logging otherwise
        result = self._check(candidate)
        log.info("gate %s: %s: %s", self.name, getattr(result.outcome, "name", result.outcome), result.reason)
        return result

    def _check(self, candidate: object) -> Any:
        try:
            root = self._checkout(candidate)
            digest = self._cns.subject_digest(key_content(root))
        except (OSError, TypeError, ValueError, RecursionError) as exc:
            return self._result(
                "TERMINAL_BREACH",
                f"the answer key cannot be read and bound to a verdict, so nothing is approved ({exc})")
        timeout = self._timeout if self._timeout is not None else sandbox_module.total_budget() + _GRACE_SECONDS
        try:
            run = self._runner(root, timeout)
        except OSError as exc:
            return self._result("RETRY", f"the verifier could not be started, so the key was not proven ({exc})",
                                digest)
        if run.timed_out:
            return self._result("RETRY", f"the verifier did not finish within {timeout:g}s, so the key was not "
                                "proven; ask again when the machine is quieter", digest)
        try:
            after = self._cns.subject_digest(key_content(root))
        except (OSError, TypeError, ValueError, RecursionError) as exc:
            return self._result("TERMINAL_BREACH", f"the answer key could not be read after the proof ({exc})",
                                digest)
        if after != digest:
            return self._result("RETRY", "the answer key changed while the verifier was running, so neither state "
                                "was proven; ask again once the checkout is still", digest)
        outcome, reason = self._decide(run)
        return self._result(outcome, reason, digest)

    @staticmethod
    def _decide(run: VerifierRun) -> tuple:
        """The outcome name and reason for one finished run of the verifier."""
        if run.returncode not in (0, 1):
            return "RETRY", (f"the verifier did not exit normally (status {run.returncode}), so the key was not "
                             f"proven: {_tail(run.stderr)}")
        try:
            record = _read_summary(run.stdout)
        except ValueError as exc:
            return "TERMINAL_BREACH", (f"the verifier's summary is not one this connector recognises ({exc}); "
                                       "an unknown answer is never read as permission")
        if record is None:
            if run.returncode == 1:
                return "RETRY", ("the verifier ended without a summary, so the key was not proven: "
                                 f"{_tail(run.stderr)}")
            return "TERMINAL_BREACH", ("the verifier exited 0 without its summary line; an answer this connector "
                                       "does not recognise is never read as permission")
        claims, failures = record["claims"], record["failures"]
        if failures:
            if run.returncode != 1:
                return "TERMINAL_BREACH", ("the verifier exited 0 but reports failing claims; the exit code and the "
                                           "summary disagree, which is never read as permission")
            shown = "; ".join(f"{f['claim']} ({f['reason']})" for f in failures[:5])
            more = f" and {len(failures) - 5} more" if len(failures) > 5 else ""
            if all(f["reason"] in _RETRYABLE_REASONS for f in failures):
                return "RETRY", (f"{len(failures)} claim(s) timed out, not changed: {shown}{more}; the hash claims "
                                 "held, so ask again when the machine is quieter")
            return "TERMINAL_BREACH", (f"the answer key is not proven: {claims['failed']} of {claims['total']} "
                                       f"claims failed: {shown}{more}")
        if claims["skipped"]:
            return "RETRY", (f"{claims['skipped']} claim(s) could not be run here (a specimen needs numpy or "
                             "matplotlib), so the key was not fully proven; install them and ask again")
        if run.returncode != 0 or not record["all_claims_hold"] or not claims["total"] \
                or record["status"] not in _PROVEN_STATUSES:
            return "TERMINAL_BREACH", (f"the verifier exited {run.returncode} with status {record['status']!r} and "
                                       "no failing or skipped claim; an answer this connector does not recognise "
                                       "is never read as permission")
        counts = record.get("entries", {}).get("counts", {}) if isinstance(record.get("entries"), dict) else {}
        unvalidated = counts.get("UNVALIDATED")
        note = (f"; {unvalidated} entries rest on a judgement the verifier does not repeat"
                if _int(unvalidated) and unvalidated else "")
        return "PASS", f"the answer key is proven: {claims['passed']}/{claims['total']} claims hold, none skipped{note}"


def cns_chain(*, subject: str = DEFAULT_SUBJECT, timeout: Optional[float] = None) -> Any:
    """A ``cns.gate.GateChain`` holding the key gate in the ``alpha`` slot.

    ``omega`` stays empty: ASSAY judges no produced result.
    """
    return _cns_gate().GateChain(alpha=(AssayKeyGate(subject=subject, timeout=timeout),))
