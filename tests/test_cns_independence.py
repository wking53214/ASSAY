"""ASSAY is independent of CNS, and these tests hold whether or not CNS is installed.

Each one that needs a clean slate runs in a fresh interpreter in which ``cns`` is
blocked outright (``sys.modules['cns'] = None`` makes any import of it fail), so
the result does not depend on what the test environment happens to contain.
They do not need CNS, so they are never skipped.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import textwrap
import tomllib
from pathlib import Path

from conftest import ROOT

PACKAGE = ROOT / "assay_production"
BLOCK = "import sys; sys.modules['cns'] = None; sys.modules['cns.gate'] = None\n"


def _run(code: str, *, block: bool = True) -> subprocess.CompletedProcess:
    env = {"PYTHONPATH": str(ROOT), "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([sys.executable, "-c", (BLOCK if block else "") + textwrap.dedent(code)],
                          capture_output=True, text=True, env=env, timeout=300)


def _ok(done: subprocess.CompletedProcess) -> None:
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip().endswith("ok"), done.stdout


def _imported_modules(path: Path) -> set:
    names: set = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module)
    return names


def _is_cns(name: str) -> bool:
    return name == "cns" or name.startswith("cns.")


def test_the_package_and_its_connector_import_with_cns_blocked():
    _ok(_run("import assay_production, assay_production.cns_connector; print('ok')"))


def test_the_verifier_still_does_its_job_with_cns_blocked():
    _ok(_run(
        """
        from pathlib import Path
        from assay_production import verification
        report = verification.run_all(Path(%r))
        assert not report.failures, [c.id for c in report.failures]
        assert len(report.claims) > 50
        print('ok')
        """ % str(ROOT)))


def test_the_connector_says_what_is_missing_when_cns_is_blocked():
    _ok(_run(
        """
        from assay_production.cns_connector import AssayKeyGate, CnsNotInstalled, cns_available, key_digest
        assert cns_available() is False
        for build in (AssayKeyGate, lambda: key_digest(%r)):
            try:
                build()
            except CnsNotInstalled as exc:
                assert "pip install 'assay[cns]'" in str(exc)
                assert isinstance(exc, ImportError)
            else:
                raise SystemExit("no error")
        print('ok')
        """ % str(ROOT)))


def test_a_gate_fails_at_construction_not_at_first_use():
    _ok(_run(
        """
        from assay_production.cns_connector import AssayKeyGate, CnsNotInstalled, cns_chain
        for build in (lambda: AssayKeyGate(subject="x"), cns_chain):
            try:
                build()
            except CnsNotInstalled:
                continue
            raise SystemExit("constructed without cns")
        print('ok')
        """))


def test_importing_the_package_does_not_load_cns_even_when_it_is_installed():
    _ok(_run(
        """
        import sys
        import assay_production, assay_production.cns_connector
        assert not [m for m in sys.modules if m == "cns" or m.startswith("cns.")], "cns was loaded"
        print('ok')
        """, block=False))


def test_running_the_verifier_does_not_load_cns_even_when_it_is_installed():
    _ok(_run(
        """
        import sys
        from pathlib import Path
        from assay_production import verification
        report = verification.run_all(Path(%r))
        assert not report.failures
        assert not [m for m in sys.modules if m == "cns" or m.startswith("cns.")], "cns was loaded"
        print('ok')
        """ % str(ROOT), block=False))


def test_no_module_of_the_package_imports_cns_by_statement():
    offenders = {p.name: sorted(n for n in _imported_modules(p) if _is_cns(n)) for p in PACKAGE.glob("*.py")}
    assert {k: v for k, v in offenders.items() if v} == {}


def test_the_verifier_and_the_sandbox_never_mention_importing_cns():
    """Not even in the text of the harness the sandbox writes for a specimen, or in a string the verifier execs."""
    forbidden = re.compile(r"\b(?:import|from)\s+cns\b|import_module\(\s*[\"']cns|__import__\(\s*[\"']cns")
    for name in ("verification.py", "sandbox.py", "manifest_registry.py", "specimen_registry.py"):
        assert not forbidden.search((PACKAGE / name).read_text(encoding="utf-8")), name


def test_the_package_uses_only_the_standard_library():
    stdlib = set(sys.stdlib_module_names)
    for path in PACKAGE.glob("*.py"):
        outside = {n.split(".")[0] for n in _imported_modules(path)} - stdlib - {"assay_production"}
        assert outside == set(), (path.name, outside)


def test_the_package_declares_no_runtime_dependency_and_pins_the_cns_extra():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["dependencies"] == []
    (pin,) = data["project"]["optional-dependencies"]["cns"]
    assert re.fullmatch(r"cns @ git\+https://github\.com/wking53214/CNS\.git@(v\d+\.\d+\.\d+|[0-9a-f]{40})", pin), pin
    assert "cns" not in data["project"]["optional-dependencies"]["dev"]
