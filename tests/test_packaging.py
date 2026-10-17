"""One version, real console entry points, a pinned CNS, and gates in CI."""
import importlib
import importlib.metadata
import re
import tomllib

import pytest

import assay_production
from assay_production import _version

from conftest import ROOT

PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
FULL_SHA = re.compile(r"@([0-9a-f]{40})(?:\s|$)")


def test_version_has_a_single_source():
    assert "version" in PYPROJECT["project"]["dynamic"] and "version" not in PYPROJECT["project"]
    assert PYPROJECT["tool"]["setuptools"]["dynamic"]["version"] == {"attr": "assay_production._version.__version__"}
    assert assay_production.__version__ == _version.__version__
    assert re.fullmatch(r"\d+\.\d+\.\d+", _version.__version__)


def test_installed_metadata_agrees_with_the_source():
    try:
        installed = importlib.metadata.version("assay")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("assay is not installed here (pip install -e .)")
    assert installed == _version.__version__, (
        "the installed metadata is stale: run `pip install -e .` again after bumping the version")


def test_changelog_leads_with_the_current_version():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    headings = re.findall(r"^## \[([^\]]+)\]", text, re.M)
    assert headings[0] == _version.__version__, headings
    assert "Keep a Changelog" in text
    # newest first, and every version is listed once
    assert len(headings) == len(set(headings))


def test_console_scripts_exist_and_resolve():
    scripts = PYPROJECT["project"]["scripts"]
    assert set(scripts) == {"assay-verify", "assay-manifest"}
    for name, target in scripts.items():
        module, _, attr = target.partition(":")
        assert callable(getattr(importlib.import_module(module), attr)), name


def test_the_registry_ships_with_the_package():
    assert PYPROJECT["tool"]["setuptools"]["packages"] == ["assay_production"]
    assert "registry.json" in PYPROJECT["tool"]["setuptools"]["package-data"]["assay_production"]


def test_the_cns_extra_is_pinned_to_a_full_commit_sha():
    (spec,) = PYPROJECT["project"]["optional-dependencies"]["cns"]
    assert spec.startswith("cns @ git+https://github.com/wking53214/CNS.git@")
    assert FULL_SHA.search(spec + "\n"), spec
    # The pin is explained next to it, with the tag it corresponds to.
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "v1.8.0" in text.split("[project.scripts]")[0]


def test_ci_runs_the_static_gates_on_three_pythons():
    workflow = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    for version in ("3.11", "3.12", "3.13"):
        assert f'"{version}"' in workflow
    assert "ruff check" in workflow and "mypy" in workflow
    assert "verify_manifest.py --strict" in workflow and "pytest" in workflow
    # A sibling checkout, if the workflow makes one, is pinned to a full SHA.
    for block in re.findall(r"repository:.*\n(?:\s+.*\n){0,3}", workflow):
        assert re.search(r"ref:\s*[0-9a-f]{40}\b", block), block


def test_static_gate_configuration_is_present():
    assert PYPROJECT["tool"]["ruff"]["line-length"] == 120
    assert "E" in PYPROJECT["tool"]["ruff"]["lint"]["select"]
    assert PYPROJECT["tool"]["mypy"]["check_untyped_defs"] is True


def test_no_dash_punctuation_that_the_house_style_forbids():
    for name in ("README.md", "STACK.md", "CHANGELOG.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert chr(0x2014) not in text, f"{name} contains an em dash"


def test_every_action_in_the_workflow_is_pinned_by_full_sha_with_its_tag():
    workflow = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    uses = re.findall(r"^\s*-?\s*uses:\s*(\S+)(.*)$", workflow, re.M)
    assert uses
    for target, rest in uses:
        assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", target), f"{target} is not pinned by full commit SHA"
        assert re.search(r"#\s*v\d+\.\d+\.\d+", rest), f"{target} has no tag comment"


def test_the_tagging_statement_is_true_and_the_same_in_both_documents():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for text in (changelog, readme):
        assert "older `v0.10.0` tag exists" in text.replace("\n", " ")
        assert "tagging is" in text.replace("\n", " ") and "owner's decision" in text.replace("\n", " ")
        assert "No release has been tagged" not in text
