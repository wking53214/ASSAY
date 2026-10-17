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
    found = re.search(r"@([0-9a-f]{40})$", project["optional-dependencies"]["cns"][0])
    assert found is not None
    assert found.group(1) in README and "v1.8.0" in README


def test_readme_claim_about_the_cns_assay_row_matches_the_installed_cns():
    """The README says the pinned CNS (v1.8.0) has no cns.assay row. Where that CNS is installed, check it."""
    try:
        version = importlib.metadata.version("cns")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("CNS is not installed")
    if version != "1.8.0":
        pytest.skip(f"CNS {version} is installed, not the pinned 1.8.0")
    assert importlib.util.find_spec("cns.assay") is None
    assert "find_spec(\"cns.assay\")` is `None`" in README


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
