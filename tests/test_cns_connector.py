"""The answer key as a CNS gate.

These skip where ``cns`` is not installed and run in CI, which installs the extra.
Nothing here edits the real specimens: tampering is done on a throw-away copy
(``corpus``), and the real key is only read and verified.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

gate = pytest.importorskip("cns.gate")

from assay_production import manifest_registry as mr  # noqa: E402
from assay_production.cns_connector import (  # noqa: E402
    DEFAULT_SUBJECT, AssayKeyGate, CnsNotInstalled, VerifierRun, cns_chain, key_content, key_digest)
from assay_production.verification import SUMMARY_PREFIX, SUMMARY_SCHEMA  # noqa: E402
from conftest import ROOT, edit  # noqa: E402

TAMPER_SPECIMEN = "specimens/progressions/uztc/uztc-construct-v1.1-purged.py"


# ----------------------------------------------------------------- helpers

def proven_record(**over) -> dict:
    """The summary a proven key prints, in the documented shape. Always a fresh dict."""
    record = {
        "schema": SUMMARY_SCHEMA, "all_claims_hold": True, "status": "ANSWER_KEY_UNVALIDATED",
        "claims": {"total": 60, "passed": 60, "failed": 0, "skipped": 0},
        "entries": {"total": 27, "counts": {"VERIFIED_BY_EXECUTION": 11, "VERIFIED_BY_STATIC_CHECK": 3,
                                            "UNVALIDATED": 13}, "status": {}},
        "failures": []}
    record.update(over)
    return record


def failing_record(*reasons: str) -> dict:
    failures = [{"claim": f"claim.{i}", "reason": r, "detail": "x"} for i, r in enumerate(reasons)]
    return proven_record(all_claims_hold=False, status="MANIFEST_INCONSISTENT", failures=failures,
                         claims={"total": 60, "passed": 60 - len(failures), "failed": len(failures), "skipped": 0})


def skipped_record(n: int = 1) -> dict:
    return proven_record(all_claims_hold=False, claims={"total": 59, "passed": 59, "failed": 0, "skipped": n})


def said(record, rc: int = 0, *, stderr: str = "") -> VerifierRun:
    out = "60/60 manifest claims hold\n" + (SUMMARY_PREFIX + json.dumps(record) if record is not None else "")
    return VerifierRun(rc, out, stderr)


def runner_returning(run: VerifierRun):
    return lambda root, timeout: run


def never_run(root, timeout):
    raise AssertionError("the verifier must not be run for a key that cannot be bound")


@pytest.fixture(scope="module")
def real():
    """The real key, proven once. Frozen result; nothing in it is mutated by any test."""
    before = mr.corpus_files(ROOT)
    registry = (ROOT / "assay_production" / "registry.json").read_bytes()
    result = AssayKeyGate().check(ROOT)
    return result, before, registry


# ------------------------------------------------------------ the contract

def test_the_gate_satisfies_the_cns_protocol_at_the_precondition_end():
    g = AssayKeyGate()
    assert isinstance(g, gate.Gate)
    assert g.name == "assay.key_proven" and g.position is gate.GatePosition.ALPHA


def test_the_real_key_passes_and_is_bound_to_its_content(real):
    result, _, _ = real
    assert result.outcome is gate.GateOutcome.PASS, result.reason
    assert result.gate == "assay.key_proven" and result.position is gate.GatePosition.ALPHA
    assert result.subject == DEFAULT_SUBJECT and result.bound() and not result.blocking()
    assert result.subject_digest == gate.subject_digest(key_content(ROOT)) == key_digest(ROOT)
    assert "60/60" in result.reason or "claims hold" in result.reason
    # it says the unvalidated entries are not re-measured
    assert "do not" in result.reason or "does not" in result.reason


def test_proving_the_real_key_changed_nothing(real):
    _, before, registry = real
    assert mr.corpus_files(ROOT) == before
    assert (ROOT / "assay_production" / "registry.json").read_bytes() == registry


def test_a_verdict_cannot_be_moved_onto_another_key(real, corpus):
    result, _, _ = real
    edit(corpus / "MANIFEST.md", '"verdict": "REFUSE"', '"verdict": "ACCEPT"')
    other = key_digest(corpus)
    assert other != result.subject_digest
    assert result.binds(DEFAULT_SUBJECT, result.subject_digest)
    assert not result.binds(DEFAULT_SUBJECT, other)
    assert not result.binds("another-key", result.subject_digest)
    moved = gate.GateResult(gate=result.gate, position=result.position, outcome=result.outcome,
                            reason=result.reason, subject=result.subject, subject_digest=other)
    assert not moved.binds(DEFAULT_SUBJECT, result.subject_digest)


# --------------------------------------------- real tampering, real verifier

def _tamper_specimen(root: Path) -> None:
    target = root / TAMPER_SPECIMEN
    target.write_bytes(target.read_bytes() + b" ")


def _tamper_registry(root: Path) -> None:
    path = root / "assay_production" / "registry.json"
    data = json.loads(path.read_text())
    data["fm_3_1_silent_pass"]["expected_verdict"] = "ACCEPT"
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def _tamper_manifest(root: Path) -> None:
    edit(root / "MANIFEST.md", '"verdict": "REFUSE"', '"verdict": "ACCEPT"')


@pytest.mark.parametrize("tamper", [_tamper_specimen, _tamper_registry, _tamper_manifest])
def test_a_tampered_copy_makes_the_gate_refuse(tamper, corpus, real):
    tamper(corpus)
    result = AssayKeyGate().check(corpus)
    assert result.outcome is gate.GateOutcome.TERMINAL_BREACH, result.reason
    assert "not proven" in result.reason and result.blocking()
    assert result.bound() and result.subject_digest != real[0].subject_digest
    assert result.subject_digest == key_digest(corpus)
    assert not result.binds(DEFAULT_SUBJECT, real[0].subject_digest)


def test_an_untouched_copy_passes_and_digests_like_the_original(corpus, real):
    result = AssayKeyGate().check(corpus)
    assert result.outcome is gate.GateOutcome.PASS, result.reason
    assert result.subject_digest == real[0].subject_digest


def test_a_verifier_that_crashes_is_a_retry_not_a_pass(corpus):
    (corpus / "verify_manifest.py").write_text("raise SystemExit(1)\n")
    result = AssayKeyGate().check(corpus)
    assert result.outcome is gate.GateOutcome.RETRY and "without a summary" in result.reason
    assert result.bound()


def test_a_verifier_that_does_not_finish_is_a_retry(corpus):
    (corpus / "verify_manifest.py").write_text("import time\ntime.sleep(60)\n")
    result = AssayKeyGate(timeout=2).check(corpus)
    assert result.outcome is gate.GateOutcome.RETRY and "did not finish within 2s" in result.reason


# --------------------------------------------------- every mapping, by table

@pytest.mark.parametrize("run,outcome,words", [
    (said(proven_record()), gate.GateOutcome.PASS, "is proven"),
    (said(proven_record(status="ANSWER_KEY_VALIDATED")), gate.GateOutcome.PASS, "is proven"),
    (said(failing_record("hash_mismatch"), 1), gate.GateOutcome.TERMINAL_BREACH, "hash_mismatch"),
    (said(failing_record("answer_key_drift", "specimen_changed"), 1), gate.GateOutcome.TERMINAL_BREACH,
     "specimen_changed"),
    (said(failing_record("behaviour_changed"), 1), gate.GateOutcome.TERMINAL_BREACH, "behaviour_changed"),
    (said(failing_record("stray_write"), 1), gate.GateOutcome.TERMINAL_BREACH, "stray_write"),
    (said(failing_record("forged_result"), 1), gate.GateOutcome.TERMINAL_BREACH, "forged_result"),
    (said(failing_record("a_reason_nobody_has_heard_of"), 1), gate.GateOutcome.TERMINAL_BREACH, "nobody_has_heard"),
    (said(failing_record("timeout"), 1), gate.GateOutcome.RETRY, "timed out"),
    (said(failing_record("timeout", "timeout"), 1), gate.GateOutcome.RETRY, "timed out"),
    (said(failing_record("timeout", "hash_mismatch"), 1), gate.GateOutcome.TERMINAL_BREACH, "hash_mismatch"),
    (said(skipped_record(), 0), gate.GateOutcome.RETRY, "could not be run"),
    (said(skipped_record(), 1), gate.GateOutcome.RETRY, "could not be run"),
    (said(None, 1, stderr="ASSAY: answer key NOT PROVEN: the verifier itself failed (OSError: x)"),
     gate.GateOutcome.RETRY, "without a summary"),
    (VerifierRun(-9, "", ""), gate.GateOutcome.RETRY, "did not exit normally"),
    (VerifierRun(2, "", "usage"), gate.GateOutcome.RETRY, "did not exit normally"),
    (VerifierRun(None, "", "", timed_out=True), gate.GateOutcome.RETRY, "did not finish"),
])
def test_each_answer_maps_to_its_outcome(run, outcome, words, corpus):
    result = AssayKeyGate(runner=runner_returning(run)).check(corpus)
    assert result.outcome is outcome, result.reason
    assert words in result.reason
    assert result.position is gate.GatePosition.ALPHA and result.bound()
    assert result.subject_digest == key_digest(corpus)


@pytest.mark.parametrize("run", [
    said(None, 0),                                                          # exit 0 and no summary line at all
    VerifierRun(0, "all fine\nASSAY-SUMMARY: not json", ""),                # not JSON
    said(proven_record(schema="assay-summary/2")),                          # a schema nobody here knows
    said(proven_record(schema=None)),
    said(proven_record(status="SOMETHING_NEW")),                            # a status nobody here knows
    said(proven_record(status="MANIFEST_INCONSISTENT")),                    # inconsistent, yet nothing failed
    said(proven_record(all_claims_hold=False)),                             # not holding, yet nothing failed or skipped
    said(proven_record(all_claims_hold="yes")),
    said(proven_record(claims={"total": 0, "passed": 0, "failed": 0, "skipped": 0})),
    said(proven_record(claims={"total": 60, "passed": 59, "failed": 0, "skipped": 0})),   # counts do not add up
    said(proven_record(claims={"total": 60, "passed": 60, "failed": 0, "skipped": -1})),
    said(proven_record(claims={"total": 60, "passed": True, "failed": 0, "skipped": 0})),
    said(proven_record(claims=None)),
    said(proven_record(failures="none")),
    said(proven_record(failures=[{"claim": "x"}])),
    said(failing_record("hash_mismatch"), 0),                               # exit 0 with a failing claim
    said(proven_record(), 1),                                               # exit 1 with nothing wrong
    said([1, 2, 3]),
])
def test_an_answer_the_connector_does_not_recognise_is_a_breach_never_a_pass(run, corpus):
    result = AssayKeyGate(runner=runner_returning(run)).check(corpus)
    assert result.outcome is gate.GateOutcome.TERMINAL_BREACH, result.reason
    assert result.bound() and result.blocking()


def test_a_key_that_changes_while_it_is_proven_is_a_retry(corpus):
    def meddling(root, timeout):
        _tamper_specimen(root)
        return said(proven_record())

    before = key_digest(corpus)
    result = AssayKeyGate(runner=meddling).check(corpus)
    assert result.outcome is gate.GateOutcome.RETRY and "changed while" in result.reason
    assert result.subject_digest == before and result.subject_digest != key_digest(corpus)


def test_a_verifier_that_cannot_be_started_is_a_retry(corpus):
    def broken(root, timeout):
        raise OSError("no such interpreter")

    result = AssayKeyGate(runner=broken).check(corpus)
    assert result.outcome is gate.GateOutcome.RETRY and "could not be started" in result.reason


def test_an_exception_from_the_verifier_logic_is_not_turned_into_a_pass(corpus):
    def boom(root, timeout):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        AssayKeyGate(runner=boom).check(corpus)


# ----------------------------------------------- candidates that cannot be bound

@pytest.mark.parametrize("candidate", [
    None, 7, 1.5, b"/tmp", ["a"], {"path": "x"}, object(), "", "   ", "/nonexistent/assay/checkout"])
def test_a_candidate_that_is_not_a_checkout_is_a_breach_and_unbound(candidate):
    result = AssayKeyGate(runner=never_run).check(candidate)
    assert result.outcome is gate.GateOutcome.TERMINAL_BREACH and result.blocking()
    assert not result.bound() and "nothing is approved" in result.reason


def test_a_folder_that_is_not_a_checkout_is_a_breach_and_unbound(tmp_path):
    result = AssayKeyGate(runner=never_run).check(tmp_path)
    assert result.outcome is gate.GateOutcome.TERMINAL_BREACH and not result.bound()


@pytest.mark.parametrize("damage", ["registry_missing", "registry_garbage", "registry_repeats_an_id",
                                    "manifest_missing", "specimens_empty", "verifier_file_missing", "nan"])
def test_a_key_that_cannot_be_read_is_a_breach_and_unbound(damage, corpus):
    registry = corpus / "assay_production" / "registry.json"
    if damage == "registry_missing":
        registry.unlink()
    elif damage == "registry_garbage":
        registry.write_text("{not json")
    elif damage == "registry_repeats_an_id":
        registry.write_text('{"a": {}, "a": {}}')
    elif damage == "manifest_missing":
        (corpus / "MANIFEST.md").unlink()
    elif damage == "specimens_empty":
        import shutil
        shutil.rmtree(corpus / "specimens")
        (corpus / "specimens").mkdir()
    elif damage == "verifier_file_missing":
        (corpus / "assay_production" / "verification.py").unlink()
    elif damage == "nan":
        registry.write_text('{"a": {"x": NaN}}')
    result = AssayKeyGate(runner=never_run).check(corpus)
    assert result.outcome is gate.GateOutcome.TERMINAL_BREACH and result.blocking()
    assert not result.bound(), result.reason


def test_a_path_object_and_a_string_are_the_same_candidate(corpus):
    run = runner_returning(said(proven_record()))
    a = AssayKeyGate(runner=run).check(corpus)
    b = AssayKeyGate(runner=run).check(str(corpus))
    assert a == b and a.outcome is gate.GateOutcome.PASS


# ------------------------------------------------------------------ binding

def test_same_input_same_digest_changed_input_different_digest(corpus, tmp_path):
    run = runner_returning(said(proven_record()))
    first = AssayKeyGate(runner=run).check(corpus)
    again = AssayKeyGate(runner=run).check(corpus)
    assert first.subject_digest == again.subject_digest
    assert key_digest(corpus) == first.subject_digest
    _tamper_specimen(corpus)
    changed = AssayKeyGate(runner=run).check(corpus)
    assert changed.subject_digest != first.subject_digest
    assert not first.binds(DEFAULT_SUBJECT, changed.subject_digest)


@pytest.mark.parametrize("rel", ["verify_manifest.py", "assay_production/verification.py",
                                 "assay_production/sandbox.py", "assay_production/manifest_registry.py"])
def test_the_digest_covers_the_verifier_that_proved_the_key(rel, corpus):
    before = key_digest(corpus)
    with open(corpus / rel, "a", encoding="utf-8") as fh:
        fh.write("\n# changed\n")
    assert key_digest(corpus) != before


def test_the_digest_does_not_cover_the_connector_itself(corpus):
    before = key_digest(corpus)
    with open(corpus / "assay_production" / "cns_connector.py", "a", encoding="utf-8") as fh:
        fh.write("\n# changed\n")
    assert key_digest(corpus) == before


def test_the_digest_covers_the_manifest_and_every_specimen_file(corpus):
    before = key_digest(corpus)
    (corpus / "specimens" / "reference" / "wrapper" / "README.md").write_text("changed\n")
    assert key_digest(corpus) != before
    again = key_digest(corpus)
    (corpus / "MANIFEST.md").write_text((corpus / "MANIFEST.md").read_text() + "\n")
    assert key_digest(corpus) != again


def test_the_subject_label_is_kept(corpus):
    result = AssayKeyGate(subject="run-42", runner=runner_returning(said(proven_record()))).check(corpus)
    assert result.subject == "run-42" and result.binds("run-42", key_digest(corpus))


# --------------------------------------------------------- chain and resolve

def test_the_chain_holds_the_key_gate_at_the_precondition_end_only():
    chain = cns_chain()
    assert chain.omega == () and len(chain.alpha) == 1 and isinstance(chain.alpha[0], AssayKeyGate)
    assert chain.complete() is False and chain.misplaced() == ()


def test_resolve_treats_the_key_gate_like_any_other_gate(corpus):
    class Fixed:
        def __init__(self, name, outcome):
            self.name, self.position, self._outcome = name, gate.GatePosition.OMEGA, outcome

        def check(self, candidate):
            return gate.GateResult(gate=self.name, position=self.position, outcome=self._outcome, reason="x")

    ok = AssayKeyGate(runner=runner_returning(said(proven_record()))).check(corpus)
    retry = AssayKeyGate(runner=runner_returning(said(skipped_record()))).check(corpus)
    breach = AssayKeyGate(runner=runner_returning(said(failing_record("hash_mismatch"), 1))).check(corpus)
    other = Fixed("other", gate.GateOutcome.PASS).check(None)
    assert gate.resolve([ok, other]) is gate.GateOutcome.PASS
    assert gate.resolve([ok, retry, other]) is gate.GateOutcome.RETRY
    assert gate.resolve([retry, breach, other]) is gate.GateOutcome.TERMINAL_BREACH
    assert gate.unbound([ok, retry, breach]) == ()
    unreadable = AssayKeyGate(runner=never_run).check(None)
    assert gate.unbound([ok, unreadable]) == ("assay.key_proven",)
    assert gate.resolve([ok, unreadable]) is gate.GateOutcome.TERMINAL_BREACH


def test_building_a_gate_without_cns_names_the_extra(monkeypatch):
    import importlib

    def refuse(name, *a, **k):
        raise ImportError("blocked")

    monkeypatch.setattr(importlib, "import_module", refuse)
    with pytest.raises(CnsNotInstalled) as caught:
        AssayKeyGate()
    assert "pip install -e '.[cns]'" in str(caught.value) and isinstance(caught.value, ImportError)


# ----------------------------------------------------------------- diagnostics

def test_the_gate_logs_its_outcome_to_the_assay_logger_without_changing_it(caplog, monkeypatch):
    monkeypatch.setattr(logging.getLogger("assay"), "propagate", True)  # a CLI run in this process turns it off
    caplog.set_level("INFO", logger="assay")
    result = AssayKeyGate(runner=runner_returning(said(proven_record()))).check(ROOT)
    assert result.outcome is gate.GateOutcome.PASS
    messages = [r.getMessage() for r in caplog.records if r.name == "assay.gate"]
    assert any(m.startswith("gate assay.key_proven: PASS") for m in messages), messages


def test_the_gate_says_it_runs_the_candidate_unsandboxed(corpus, caplog, monkeypatch):
    from assay_production import cns_connector

    monkeypatch.setattr(logging.getLogger("assay"), "propagate", True)
    caplog.set_level("INFO", logger="assay")
    cns_connector.run_verifier(corpus, 120)
    assert any("unsandboxed" in r.getMessage() for r in caplog.records), [r.getMessage() for r in caplog.records]
