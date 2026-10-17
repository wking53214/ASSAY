"""Another process (Warden's run record) can read ASSAY's version in one documented, stable way.

pyproject.toml has no static ``[project] version`` (it is dynamic, from assay_production/_version.py), so a reader of
pyproject.toml gets None. The package attribute, the installed distribution metadata and the commands must all
carry the same string, and the README must show the exact command.
"""
import importlib.metadata
import re
import shlex
import subprocess
import sys
import tomllib

import pytest

import assay_production
from assay_production import _version

from conftest import ROOT, _env

README = (ROOT / "README.md").read_text(encoding="utf-8")
WARDEN_COMMAND = 'python3 -c "import assay_production; print(assay_production.__version__)"'
METADATA_COMMAND = "python3 -c \"import importlib.metadata as m; print(m.version('assay'))\""


def source_version() -> str:
    text = (ROOT / "assay_production" / "_version.py").read_text(encoding="utf-8")
    found = re.search(r'^__version__ = "([^"]+)"$', text, re.M)
    assert found is not None
    return found.group(1)


def run_documented(command: str, cwd, pythonpath: bool):
    """Run a command line from the README with python3 replaced by this interpreter."""
    argv = shlex.split(command)
    assert argv[0] == "python3"
    env = _env()
    if pythonpath:
        env["PYTHONPATH"] = str(ROOT)
    return subprocess.run([sys.executable, *argv[1:]], cwd=cwd, env=env, capture_output=True, text=True, timeout=120)


def test_the_package_exposes_the_version_and_pyproject_stays_dynamic():
    assert assay_production.__version__ == _version.__version__ == source_version()
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert "version" in project["dynamic"] and "version" not in project


def test_the_installed_distribution_exposes_the_same_version():
    # Installed (pip install -e . or a wheel) the distribution metadata is the second source of the version.
    try:
        installed = importlib.metadata.version("assay")
    except importlib.metadata.PackageNotFoundError:
        # Not installed in this environment: the wheel job in CI installs the wheel and compares both.
        assert (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8").count("metadata.version") >= 1
        return
    assert installed == assay_production.__version__


def test_readme_shows_the_exact_command_and_says_why():
    assert WARDEN_COMMAND in README and METADATA_COMMAND in README
    assert "versions.assay.version = null" in README and "no static `[project] version`" in README
    # the command sits in a fenced block, not only in prose
    blocks = re.findall(r"```bash\n(.*?)```", README, re.S)
    assert any(WARDEN_COMMAND in block for block in blocks)


@pytest.mark.parametrize("cwd_is_checkout", [True, False], ids=["inside-checkout", "pythonpath-from-elsewhere"])
def test_the_documented_command_prints_exactly_the_version(tmp_path, cwd_is_checkout):
    proc = run_documented(WARDEN_COMMAND, ROOT if cwd_is_checkout else tmp_path, pythonpath=not cwd_is_checkout)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == source_version() + "\n"
    assert proc.stderr == ""


def test_the_documented_metadata_command_agrees_where_installed(tmp_path):
    try:
        importlib.metadata.version("assay")
    except importlib.metadata.PackageNotFoundError:
        return
    proc = run_documented(METADATA_COMMAND, tmp_path, pythonpath=False)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == source_version() + "\n"


def test_every_command_reports_the_same_version(tmp_path):
    expected = source_version()
    seen = {}
    for label, argv in {
        "verify_manifest.py": [str(ROOT / "verify_manifest.py"), "--version"],
        "assay_production": ["-m", "assay_production", "--version"],
        "manifest_registry": ["-m", "assay_production.manifest_registry", "--version"],
    }.items():
        env = _env()
        env["PYTHONPATH"] = str(ROOT)
        proc = subprocess.run([sys.executable, *argv], cwd=tmp_path, env=env, capture_output=True, text=True,
                              timeout=120)
        assert proc.returncode == 0, (label, proc.stderr)
        seen[label] = proc.stdout.strip().split()[-1]
    assert set(seen.values()) == {expected}, seen
