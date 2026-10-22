"""The README's description of ``claims.total`` is held to what the verifier actually prints.

``total`` counts the claims that were run to a verdict (held or failed). A skipped claim is in ``skipped`` only, so
``passed + skipped`` is not ``total`` and the claims made in a run are ``total + skipped``. The shape
``assay-summary/1`` is unchanged; only its meaning is written down, and these tests fail if the text and the
behaviour part company.
"""
import json
import re
import subprocess
import sys
import venv

import pytest

from conftest import ROOT, _env, edit, make_corpus

README = " ".join((ROOT / "README.md").read_text(encoding="utf-8").split())
SUMMARY = re.compile(r"^ASSAY-SUMMARY: (\{.*\})$", re.M)
_GENERATED = re.search(r"Claims the verifier checks on every run: \*\*(\d+)\*\*", README)
assert _GENERATED is not None, "the generated claims line is missing from the README"
CLAIMS_MADE = int(_GENERATED.group(1))


def _summary(proc: subprocess.CompletedProcess) -> dict:
    found = SUMMARY.search(proc.stdout)
    assert found is not None, proc.stdout[-500:]
    return json.loads(found.group(1))["claims"]


def _run(python: str, corpus, *args: str) -> dict:
    proc = subprocess.run([python, str(corpus / "verify_manifest.py"), *args], cwd=corpus.parent, env=_env(),
                          capture_output=True, text=True, timeout=600)
    return _summary(proc)


@pytest.fixture(scope="module")
def bare_python(tmp_path_factory) -> str:
    """The interpreter of a venv without numpy or matplotlib (a real absence, as in tests/test_skips.py)."""
    home = tmp_path_factory.mktemp("bare-venv")
    venv.EnvBuilder(with_pip=False, system_site_packages=False).create(home)
    python = str(home / "bin" / "python")
    for lib in ("numpy", "matplotlib"):
        assert subprocess.run([python, "-I", "-c", f"import {lib}"], capture_output=True).returncode != 0
    return python


def test_the_readme_states_the_meaning_of_total_in_words():
    assert "`claims.total` is the number of claims that were run to a verdict, held or failed" in README
    assert "`claims.passed` + `claims.failed` = `claims.total`" in README
    assert "counted in `claims.skipped` only and is not in `claims.total`" in README
    assert "`claims.total` + `claims.skipped`" in README
    assert "`passed` + `skipped` is not `total`" in README


def test_a_run_that_skips_nothing_has_passed_plus_failed_equal_to_total_and_total_equal_to_the_claims_made(corpus):
    claims = _run(sys.executable, corpus)
    assert claims["passed"] + claims["failed"] == claims["total"]
    assert claims["total"] + claims["skipped"] == CLAIMS_MADE
    # where this interpreter has numpy and matplotlib nothing is skipped, and total is the generated figure itself
    if claims["skipped"] == 0:
        assert claims["total"] == CLAIMS_MADE


def test_a_run_without_numpy_excludes_the_skipped_claim_from_total_exactly_as_the_readme_says(bare_python, tmp_path):
    corpus = make_corpus(tmp_path / "corpus")
    claims = _run(bare_python, corpus)
    stated = re.search(r"With numpy missing the line says total (\d+) and skipped (\d+), passed (\d+) and failed (\d+)",
                       README)
    assert stated, "README must give the numpy-missing example"
    total, skipped, passed, failed = (int(n) for n in stated.groups())
    assert claims == {"total": total, "skipped": skipped, "passed": passed, "failed": failed}, claims
    assert claims["skipped"] >= 1
    assert claims["passed"] + claims["skipped"] != claims["total"]
    assert claims["passed"] + claims["failed"] == claims["total"]
    assert claims["total"] + claims["skipped"] == CLAIMS_MADE
    assert f"that is {CLAIMS_MADE} claims made, {total} run and held, {skipped} not run" in README


def test_a_failed_claim_is_in_total_and_a_skipped_one_is_not(bare_python, tmp_path):
    corpus = make_corpus(tmp_path / "corpus")
    edit(corpus / "specimens" / "reference" / "resilience_stability_kernel.py", "def ", "def  ")
    claims = _run(bare_python, corpus, "--allow-skips")
    assert claims["failed"] >= 1 and claims["skipped"] >= 1
    assert claims["passed"] + claims["failed"] == claims["total"]
    assert claims["total"] + claims["skipped"] == CLAIMS_MADE
