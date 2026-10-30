"""Install hints tell a user to run commands that work.

None of the stack's packages (ASSAY, SWIZZLE, Warden, CNS, Judge, Drafter, Burnish, ghost_tools, Watcher) is
published on PyPI, and a package of the same name there is not this project, so ``pip install 'assay[cns]'`` fails
or installs someone else's code. A hint must name a checkout (``pip install -e '.[cns]'``) or a git URL.
"""
import re
import tomllib

import pytest

from assay_production import cns_connector
from conftest import ROOT

PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

# Distribution names of this stack, normalised (lower case, runs of - _ . become one -).
STACK_DISTRIBUTIONS = {
    "assay", "swizzle", "warden", "cns", "judge", "drafter", "burnish", "ghost-tools", "watcher-mcu", "watcher",
}
CNS_SPEC = "cns @ git+https://github.com/wking53214/CNS.git@v2.2.0"
# The user-facing text: the package, its docs, the CI file. Not tests (they quote bad hints on purpose) and not the
# specimens (deliberately damaged files, the product).
SCANNED = ("README.md", "STACK.md", "CHANGELOG.md", "MANIFEST.md", "pyproject.toml", "verify_manifest.py",
           ".github/workflows/tests.yml")

_INSTALL = re.compile(r"pip3?\s+install\b(?P<rest>[^\n]*)")
_EXTRAS = re.compile(r"\[[^\]]*\]")
_PROSE_STARTS = re.compile(r"[`;#()|&,]")  # where the command ends and the sentence around it resumes
_TOKEN = re.compile(r"(?<![\w./@-])['\"\\]*(?P<name>[A-Za-z][\w.-]*)(?![\w./-])")


def _normalise(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def bare_stack_installs(text: str) -> list[str]:
    """Every ``pip install`` in *text* that names a stack package by its bare name, as PyPI would resolve it."""
    found = []
    for hint in _INSTALL.finditer(text):
        rest = _PROSE_STARTS.split(_EXTRAS.sub("", hint.group("rest")), 1)[0]
        for token in _TOKEN.finditer(rest):
            if _normalise(token.group("name")) not in STACK_DISTRIBUTIONS:
                continue
            if rest[token.end():].lstrip().startswith("@"):
                continue  # "name @ git+https://..." is a direct URL, not a PyPI lookup
            found.append(hint.group(0).strip())
    return found


def _scanned_files():
    paths = [ROOT / name for name in SCANNED if (ROOT / name).is_file()]
    paths += sorted((ROOT / "assay_production").glob("*.py"))
    return paths


@pytest.mark.parametrize("bad", [
    "pip install 'assay[cns]'",
    'pip install "assay[cns]"',
    "pip install assay",
    "python -m pip install swizzle warden",
    "pip install cns",
    "pip install Ghost_Tools",
    "pip install -U assay[dev]",
])
def test_the_scanner_catches_a_bare_name_from_this_stack(bad):
    assert bare_stack_installs(f"Run `{bad}` first.") or bare_stack_installs(bad), bad


@pytest.mark.parametrize("good", [
    "pip install -e '.[cns]'",
    "pip install -e .",
    'pip install -e ".[dev,cns]"',
    "pip install numpy matplotlib",
    f'pip install "{CNS_SPEC}"',
    f"pip install '{CNS_SPEC}'",
    "pip install \\\"cns @ git+https://github.com/wking53214/CNS.git@v2.2.0\\\"",
    "pip install build numpy matplotlib",
    "pip install \"$RUNNER_TEMP\"/dist/assay-*.whl numpy matplotlib",
    "pip install /path/to/assay",
])
def test_the_scanner_passes_a_hint_that_works(good):
    assert bare_stack_installs(good) == [], good


def test_no_user_facing_install_hint_names_a_bare_pypi_distribution_of_this_stack():
    offenders = {}
    for path in _scanned_files():
        bad = bare_stack_installs(path.read_text(encoding="utf-8"))
        if bad:
            offenders[str(path.relative_to(ROOT))] = bad
    assert not offenders, offenders


def test_the_connector_hint_names_a_checkout_install_and_the_pinned_cns():
    hint = cns_connector.INSTALL_HINT
    assert "pip install -e '.[cns]'" in hint
    assert f'pip install "{CNS_SPEC}"' in hint
    assert bare_stack_installs(hint) == []


def test_the_hinted_cns_spec_is_the_one_the_cns_extra_installs():
    assert PYPROJECT["project"]["optional-dependencies"]["cns"] == [CNS_SPEC]
    assert CNS_SPEC in cns_connector.INSTALL_HINT


def test_the_readme_gives_the_same_working_commands_and_says_there_is_no_pypi_package():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "pip install -e '.[cns]'" in readme and f'pip install "{CNS_SPEC}"' in readme
    assert "not published on PyPI" in readme
