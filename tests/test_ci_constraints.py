"""CI installs numpy and matplotlib at the versions the README states, so the claim count cannot drift.

Four specimens import numpy or matplotlib, and the claims that run them are only proven where the libraries are
installed. An unpinned install would let an upstream release change what CI proves without any change here, so
``ci-constraints.txt`` pins them (numpy per interpreter), every CI job that installs them passes it with ``-c``, and the
README says which versions those are.
"""
import importlib.metadata as metadata
import os
import re
import sys

from conftest import ROOT

CONSTRAINTS = ROOT / "ci-constraints.txt"
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
README = ROOT / "README.md"
PYTHONS = ("3.11", "3.12", "3.13")


def _constraints() -> list[tuple[str, str, str]]:
    """(name, version, marker) for each active line; ``name==version`` only, so nothing is a range."""
    rows = []
    for raw in CONSTRAINTS.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        match = re.fullmatch(r'([A-Za-z][\w.-]*)==(\d+\.\d+\.\d+)\s*(?:;\s*(.+))?', line)
        assert match, f"{CONSTRAINTS.name}: {raw!r} is not an exact name==version pin"
        rows.append((match.group(1).lower(), match.group(2), (match.group(3) or "").strip()))
    return rows


def _pinned(name: str, python: str) -> str:
    """The version the constraints file selects for *name* on Python *python* (a "3.x" string)."""
    major, minor = (int(part) for part in python.split("."))
    chosen = []
    for pinned_name, version, marker in _constraints():
        if pinned_name != name:
            continue
        if not marker:
            chosen.append(version)
            continue
        match = re.fullmatch(r'python_version\s*(<|>=)\s*"(\d+)\.(\d+)"', marker)
        assert match, f"unsupported marker {marker!r}"
        bound = (int(match.group(2)), int(match.group(3)))
        if ((major, minor) < bound) if match.group(1) == "<" else ((major, minor) >= bound):
            chosen.append(version)
    assert len(chosen) == 1, f"{name} on Python {python}: {len(chosen)} pins ({chosen}), expected exactly one"
    return chosen[0]


def _readme_versions() -> dict[str, str]:
    text = " ".join(README.read_text(encoding="utf-8").split())
    sentence = re.search(
        r"CI installs them with `pip install -c ci-constraints\.txt numpy matplotlib`, which pins (.*?) so that", text)
    assert sentence, "README must state the CI pins in the sentence that names ci-constraints.txt"
    stated = {}
    pin = r"(numpy|matplotlib) (\d+\.\d+\.\d+)(?: on Python (\d+\.\d+(?: and later)?))?"
    for name, version, scope in re.findall(pin, sentence.group(1)):
        stated[f"{name}|{scope}"] = version
    return stated


def test_the_constraints_file_pins_exact_versions_of_exactly_numpy_and_matplotlib():
    assert {name for name, _, _ in _constraints()} == {"numpy", "matplotlib"}


def test_every_supported_python_gets_exactly_one_pin_of_each():
    for python in PYTHONS:
        for name in ("numpy", "matplotlib"):
            assert _pinned(name, python)


def test_the_constraints_file_matches_the_versions_the_readme_states():
    stated = _readme_versions()
    assert set(stated) == {"numpy|3.11", "numpy|3.12 and later", "matplotlib|"}, stated
    assert _pinned("numpy", "3.11") == stated["numpy|3.11"]
    for python in ("3.12", "3.13"):
        assert _pinned("numpy", python) == stated["numpy|3.12 and later"]
    for python in PYTHONS:
        assert _pinned("matplotlib", python) == stated["matplotlib|"]


def test_every_ci_install_of_numpy_or_matplotlib_uses_the_constraints_file():
    installs = [line.strip() for line in WORKFLOW.read_text(encoding="utf-8").splitlines()
                if re.search(r"\bpip3?\"?\s+install\b", line) and re.search(r"\b(numpy|matplotlib)\b", line)]
    assert len(installs) >= 4, installs  # pytest job, consumers job, and two in the wheel job
    for line in installs:
        assert re.search(r"\s-c\s+\S*ci-constraints\.txt\b", line), f"installs numpy or matplotlib unpinned: {line}"


def test_ci_has_the_pinned_versions_installed():
    """In CI (and only there) what the runner installed is what the constraints file says."""
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return
    python = f"{sys.version_info.major}.{sys.version_info.minor}"
    for name in ("numpy", "matplotlib"):
        assert metadata.version(name) == _pinned(name, python), f"{name} on Python {python}"
