"""A claim that could not be run is a failure by default; --allow-skips is the loud, explicit opt-out.

numpy being absent is simulated for real: the verifier runs under the interpreter of a fresh virtual environment
that has no numpy and no matplotlib (and no access to the base interpreter's packages), so the sandboxed specimens
that import them fail with ModuleNotFoundError exactly as they would on a machine without the libraries.
"""
import json
import re
import subprocess
import sys
import venv
from pathlib import Path

import pytest

from assay_production import verification as vf
from conftest import _env, edit, make_corpus

SUMMARY = re.compile(r"^ASSAY-SUMMARY: (\{.*\})$", re.M)
SKIPPED_CLAIM = "ref.solvar_cleanup.runs"


@pytest.fixture(scope="module")
def bare_python(tmp_path_factory) -> str:
    """The interpreter of a venv without numpy or matplotlib."""
    home = tmp_path_factory.mktemp("bare-venv")
    venv.EnvBuilder(with_pip=False, system_site_packages=False).create(home)
    python = str(home / "bin" / "python")
    for lib in ("numpy", "matplotlib"):
        probe = subprocess.run([python, "-I", "-c", f"import {lib}"], capture_output=True, text=True)
        assert probe.returncode != 0, f"{lib} is importable in the bare environment, so numpy-absent is not simulated"
    return python


@pytest.fixture(scope="module")
def bare_corpus(tmp_path_factory) -> Path:
    return make_corpus(tmp_path_factory.mktemp("bare-corpus") / "corpus")


def run_bare(python: str, corpus: Path, *args: str, extra_env: "dict | None" = None):
    env = _env()
    env.update(extra_env or {})
    return subprocess.run([python, str(corpus / "verify_manifest.py"), *args], cwd=corpus.parent, env=env,
                          capture_output=True, text=True, timeout=600)


def summary_of(proc) -> dict:
    found = SUMMARY.search(proc.stdout)
    assert found is not None, proc.stdout[-500:]
    assert proc.stdout.rstrip("\n").splitlines()[-1] == found.group(0), "the summary must be the last stdout line"
    return json.loads(found.group(1))


@pytest.fixture(scope="module")
def default_run(bare_python, bare_corpus):
    return run_bare(bare_python, bare_corpus)


@pytest.fixture(scope="module")
def allowed_run(bare_python, bare_corpus):
    return run_bare(bare_python, bare_corpus, "--allow-skips")


def test_default_run_without_numpy_fails_closed(default_run):
    assert default_run.returncode == 1, default_run.stdout[-600:] + default_run.stderr[-600:]
    last = default_run.stderr.strip().splitlines()[-1]
    assert "NOT PROVEN" in last and SKIPPED_CLAIM in last and "--allow-skips" in last
    assert "SKIP  " in default_run.stdout and SKIPPED_CLAIM in default_run.stdout
    assert "The corpus matches its answer key." not in default_run.stdout
    assert "The answer key is NOT PROVEN" in default_run.stdout
    record = summary_of(default_run)
    assert record["all_claims_hold"] is False
    assert record["claims"]["skipped"] >= 1 and record["claims"]["failed"] == 0


def test_strict_keeps_its_meaning_and_agrees_with_the_default(bare_python, bare_corpus, default_run):
    strict = run_bare(bare_python, bare_corpus, "--strict")
    assert strict.returncode == default_run.returncode == 1
    assert summary_of(strict) == summary_of(default_run)
    assert strict.stderr.strip().splitlines()[-1] == default_run.stderr.strip().splitlines()[-1]


def test_strict_through_the_environment_is_the_same(bare_python, bare_corpus):
    proc = run_bare(bare_python, bare_corpus, extra_env={"ASSAY_STRICT": "1"})
    assert proc.returncode == 1 and summary_of(proc)["claims"]["skipped"] >= 1


def test_allow_skips_is_loud_still_reports_and_does_not_claim_a_full_proof(allowed_run):
    assert allowed_run.returncode == 0, allowed_run.stdout[-600:] + allowed_run.stderr[-600:]
    assert "WARNING: --allow-skips" in allowed_run.stdout and "SKIPPED and NOT PROVEN" in allowed_run.stdout
    assert SKIPPED_CLAIM in allowed_run.stdout
    last = allowed_run.stderr.strip().splitlines()[-1]
    assert "--allow-skips" in last and "SKIPPED, NOT PROVEN" in last and SKIPPED_CLAIM in last
    assert "The corpus matches its answer key." not in allowed_run.stdout
    assert "for every claim that could be run" in allowed_run.stdout
    record = summary_of(allowed_run)
    # The summary is the same contract: the skip is counted and the key is not reported as fully holding.
    assert record["schema"] == "assay-summary/1"
    assert record["all_claims_hold"] is False and record["claims"]["skipped"] >= 1 and record["claims"]["failed"] == 0


def test_allow_skips_never_hides_a_real_failure(bare_python, tmp_path):
    corpus = make_corpus(tmp_path / "corpus")
    edit(corpus / "specimens" / "reference" / "resilience_stability_kernel.py", "def ", "def  ")
    proc = run_bare(bare_python, corpus, "--allow-skips")
    assert proc.returncode == 1, proc.stdout[-600:]
    record = summary_of(proc)
    assert record["claims"]["failed"] >= 1 and record["claims"]["skipped"] >= 1
    assert "NOT PROVEN" in proc.stderr


@pytest.mark.parametrize("args, env", [
    (["--allow-skips", "--strict"], {}),
    (["--strict", "--allow-skips"], {}),
    (["--allow-skips"], {"ASSAY_STRICT": "1"}),
    (["--allow-skips", "--write"], {}),
])
def test_contradictory_options_exit_2_and_check_nothing(bare_python, bare_corpus, args, env):
    proc = run_bare(bare_python, bare_corpus, *args, extra_env=env)
    assert proc.returncode == 2, (args, proc.stdout[-300:], proc.stderr[-300:])
    assert proc.stdout == "" and "--allow-skips" in proc.stderr


@pytest.mark.parametrize("flag", ["--allow-skip", "--allow_skips", "--allowskips", "--allow-skips=yes"])
def test_a_mistyped_opt_out_is_an_error_not_a_weaker_run(bare_python, bare_corpus, flag):
    proc = run_bare(bare_python, bare_corpus, flag)
    assert proc.returncode == 2 and proc.stdout == ""


def test_with_the_libraries_present_the_default_still_exits_0(corpus):
    from conftest import run_verify

    proc = run_verify(corpus)
    assert proc.returncode == 0, proc.stdout[-600:] + proc.stderr[-600:]
    assert summary_of(proc)["claims"]["skipped"] == 0
    assert "The corpus matches its answer key." in proc.stdout


def test_render_report_wording_depends_on_the_opt_out(tmp_path):
    report = vf.Report()
    report.claims.append(vf.Claim("x.runs", "x runs (not run: numpy is not installed)", False, "execution", ("e",),
                                  True, False, "", "", ("e",), "", ""))
    default_text, default_ok = vf.render_report(report, tmp_path)
    allowed_text, allowed_ok = vf.render_report(report, tmp_path, allow_skips=True)
    assert default_ok and allowed_ok  # nothing failed; _verify turns an unrun claim into exit 1 by default
    assert "NOT PROVEN" in default_text and "WARNING" not in default_text
    assert "WARNING: --allow-skips" in allowed_text and "x.runs" in allowed_text


def test_help_documents_the_default_and_the_opt_out():
    out = subprocess.run([sys.executable, str(Path(vf.__file__).resolve().parent.parent / "verify_manifest.py"),
                          "--help"], capture_output=True, text=True, env=_env(), timeout=120).stdout
    flat = " ".join(out.split())
    assert "--allow-skips" in flat and "--strict" in flat and "failure by default" in flat
