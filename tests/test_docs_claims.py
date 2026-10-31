"""Numbers and facts the documents state are checked here or by the verifier, not trusted."""
import importlib.metadata
import importlib.util
import re
import tomllib

import pytest

from conftest import ROOT, edit, run_verify

README = (ROOT / "README.md").read_text(encoding="utf-8")


def test_readme_does_not_quote_a_test_count():
    # A pass count is true for one commit only. Say what is skipped and why, not how many tests ran.
    assert not re.search(r"\b\d+\s+(passed|tests?\s+pass)", README), re.findall(r"\b\d+\s+passed", README)


def test_readme_names_the_same_cns_pin_as_pyproject():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    found = re.search(r"@(v\d+\.\d+\.\d+)$", project["optional-dependencies"]["cns"][0])
    assert found is not None
    assert found.group(1) in README


def test_readme_claim_about_the_cns_assay_row_matches_the_installed_cns():
    """The README says the pinned CNS (v2.3.0) has a cns.assay row. Where that CNS is installed, check it."""
    try:
        version = importlib.metadata.version("cns")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("CNS is not installed")
    if version != "2.2.0":
        pytest.skip(f"CNS {version} is installed, not the pinned 2.2.0")
    assert importlib.util.find_spec("cns.assay") is not None
    assert "find_spec(\"cns.assay\")` is not `None`" in README


def test_stack_doc_does_not_call_the_public_cns_repository_private():
    stack = (ROOT / "STACK.md").read_text(encoding="utf-8")
    assert "CNS (private)" not in stack and "CNS (public" in stack


def test_the_readme_counts_are_generated_and_the_verifier_checks_them(corpus):
    assert "ASSAY-STATUS:BEGIN" in README and "ASSAY-SUMMARY-EXAMPLE:BEGIN" in README
    claims = re.search(r"Claims the verifier checks on every run: \*\*(\d+)\*\*", README)
    example = re.search(r'"claims":\{"total":(\d+),"passed":(\d+)', README)
    assert claims and example and claims.group(1) == example.group(1) == example.group(2)


@pytest.mark.parametrize("old, new", [
    ("Claims the verifier checks on every run: **", "Claims the verifier checks on every run: **9"),
    ('"entries":{"total":27,', '"entries":{"total":26,'),
    ('"VERIFIED_BY_STATIC_CHECK":3,', '"VERIFIED_BY_STATIC_CHECK":4,'),
    ("Specimens in the answer key: **27**", "Specimens in the answer key: **26**"),
])
def test_a_drifted_number_in_the_readme_fails_verification(corpus, old, new):
    edit(corpus / "README.md", old, new)
    proc = run_verify(corpus)
    assert proc.returncode == 1, proc.stdout[-500:]
    assert "readme.status_block" in proc.stdout
    assert "overclaim or underclaim" in proc.stdout


def test_readme_log_levels_equal_the_accepted_set():
    import logging

    from assay_production import runtime

    line = next(ln for ln in README.splitlines() if "at the level named by `ASSAY_LOG_LEVEL`" in ln)
    listed = re.search(r"`ASSAY_LOG_LEVEL` \(([^;]*);", line)
    assert listed is not None, line
    names = set(re.findall(r"`([A-Z]+)`", listed.group(1)))
    assert names == set(runtime._LEVELS) == {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    # and every listed name really is accepted, case-insensitively
    for name in names:
        assert runtime.configure_logging({runtime.LOG_LEVEL_ENV: name.lower()}) == getattr(logging, name)
    runtime.configure_logging({})


def test_log_levels_in_help_and_module_docs_match_the_accepted_set():
    import subprocess
    import sys

    from assay_production import runtime
    from conftest import _env

    helped = subprocess.run([sys.executable, str(ROOT / "verify_manifest.py"), "--help"], capture_output=True,
                            text=True, env=_env(), timeout=120).stdout
    flat = " ".join(helped.split())
    help_levels = re.search(r"ASSAY_LOG_LEVEL \(([A-Z, ]+)\)", flat)
    assert help_levels is not None
    assert {n.strip() for n in help_levels.group(1).split(",")} == set(runtime._LEVELS)
    doc_levels = re.search(r"``ASSAY_LOG_LEVEL`` \(([^;]*);", (runtime.__doc__ or "").replace("\n", " "))
    assert doc_levels is not None
    assert set(re.findall(r"``([A-Z]+)``", doc_levels.group(1))) == set(runtime._LEVELS)


def test_gitignore_covers_what_the_documented_install_leaves_behind():
    lines = {ln.strip() for ln in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()}
    assert {"*.egg-info/", "build/", "dist/"} <= lines


def test_stack_doc_names_the_five_circuit_repositories_and_not_the_old_seven():
    """The circuit is five repositories since the owner ruling of 2026-10-29; STACK.md must not say seven."""
    stack = (ROOT / "STACK.md").read_text(encoding="utf-8")
    assert "Seven repositories" not in stack and "all seven" not in stack
    assert "Five repositories" in stack
    for name in ("ghost_tools", "SWIZZLE", "ASSAY", "Judge", "Warden"):
        assert "/" + name + ")" in stack, name
