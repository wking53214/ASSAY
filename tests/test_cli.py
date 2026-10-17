"""The command line fails closed: an argument the verifier does not know exits 2 and checks nothing."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from assay_production import __version__
from assay_production import cli
from assay_production import verification as vf
from assay_production import manifest_registry as mr

from conftest import ROOT, _env, run_verify

SUMMARY = re.compile(r"^ASSAY-SUMMARY: (\{.*\})$", re.M)
TYPOS = ["--stirct", "--strictt", "--stric", "--str", "-strict", "strict", "--strict=yes", "--wirte", "--no-such-flag",
         "-x"]


def run_module(module: str, *args: str, cwd: Path, extra_env: "dict | None" = None, timeout: int = 600):
    """Run `python -I -m module` with the checkout on the path (the way an installed command would see the package)."""
    env = _env()
    env["PYTHONPATH"] = str(ROOT)
    env.update(extra_env or {})
    return subprocess.run([sys.executable, "-m", module, *args], cwd=cwd, capture_output=True, text=True, env=env,
                          timeout=timeout)


def tree_digest(base: Path) -> str:
    """One digest over MANIFEST.md, registry.json and README.md: the files --write would change."""
    h = hashlib.sha256()
    for rel in ("MANIFEST.md", "assay_production/registry.json", "README.md"):
        h.update((base / rel).read_bytes())
    return h.hexdigest()


@pytest.mark.parametrize("flag", TYPOS)
def test_verify_manifest_rejects_a_mistyped_flag(corpus, flag):
    before = tree_digest(corpus)
    proc = run_verify(corpus, flag)
    assert proc.returncode == 2, (flag, proc.returncode, proc.stdout[-300:], proc.stderr[-300:])
    assert "unrecognized arguments" in proc.stderr or "error:" in proc.stderr
    # Nothing ran: no report, no summary line, and not a single file touched.
    assert proc.stdout == "" and not SUMMARY.search(proc.stdout)
    assert tree_digest(corpus) == before


def test_a_typo_next_to_a_good_flag_is_still_an_error(corpus):
    proc = run_verify(corpus, "--strict", "--stirct")
    assert proc.returncode == 2 and proc.stdout == ""


@pytest.mark.parametrize("flag", ["--wirte", "--writ", "--strict", "--root=/nowhere/x", "extra"])
def test_manifest_registry_rejects_unknown_arguments_and_changes_nothing(corpus, flag):
    # --strict and --root are not flags of the print/--write command in the form tried here (`--root` needs a
    # real checkout), so each must stop at the parser or at the checkout check, never fall through to a write.
    before = tree_digest(corpus)
    proc = run_module("assay_production.manifest_registry", flag, cwd=corpus)
    assert proc.returncode == 2, (flag, proc.returncode, proc.stdout[-200:], proc.stderr[-300:])
    assert proc.stdout == ""
    assert tree_digest(corpus) == before


def test_in_process_main_exits_2_on_a_typo():
    with pytest.raises(SystemExit) as raised:
        vf.main(ROOT, ["--stirct"])
    assert raised.value.code == 2
    with pytest.raises(SystemExit) as raised:
        mr.main(["--wirte"])
    assert raised.value.code == 2
    with pytest.raises(SystemExit) as raised:
        cli.verify(["--stirct"])
    assert raised.value.code == 2
    with pytest.raises(SystemExit) as raised:
        cli.manifest(["--stirct"])
    assert raised.value.code == 2


def test_the_installed_commands_do_not_take_a_root_on_the_checkout_script(corpus):
    # verify_manifest.py proves the checkout it sits in; --root belongs to the installed command only.
    proc = run_verify(corpus, "--root", str(corpus))
    assert proc.returncode == 2 and proc.stdout == ""


def test_help_and_version_exit_0_before_checking_anything(corpus):
    helped = run_verify(corpus, "--help")
    assert helped.returncode == 0 and "Exit codes: 0" in helped.stdout and "--strict" in helped.stdout
    assert not SUMMARY.search(helped.stdout)
    versioned = run_verify(corpus, "--version")
    assert versioned.returncode == 0 and versioned.stdout.strip() == f"verify_manifest.py {__version__}"


def test_module_entry_points_report_the_same_version(tmp_path):
    for module in ("assay_production", "assay_production.manifest_registry"):
        proc = run_module(module, "--version", cwd=tmp_path)
        assert proc.returncode == 0, proc.stderr
        assert proc.stdout.strip().endswith(__version__), (module, proc.stdout)
    assert "assay-verify" in run_module("assay_production", "--version", cwd=tmp_path).stdout
    # The commands the entry points call, in-process.
    with pytest.raises(SystemExit) as raised:
        cli.verify(["--version"])
    assert raised.value.code == 0
    # manifest_registry run as `-m` shows the module path, the installed command shows its own name.
    assert "assay-manifest" in subprocess.run(
        [sys.executable, "-c", "from assay_production import cli; cli.manifest(['--version'])"],
        cwd=tmp_path, capture_output=True, text=True, env={**_env(), "PYTHONPATH": str(ROOT)}).stdout


def test_installed_command_needs_a_checkout_and_says_so(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    proc = run_module("assay_production", "--root", str(empty), cwd=tmp_path)
    assert proc.returncode == 2
    assert "not an ASSAY checkout" in proc.stderr and proc.stdout == ""
    proc = run_module("assay_production.manifest_registry", "--root", str(empty), cwd=tmp_path)
    assert proc.returncode == 2 and "not an ASSAY checkout" in proc.stderr


def test_installed_command_proves_a_checkout_and_keeps_the_summary_contract(corpus, tmp_path):
    """`python -m assay_production --root X` is what `assay-verify --root X` runs (including the restart)."""
    proc = run_module("assay_production", "--root", str(corpus), "--strict", cwd=tmp_path)
    assert proc.returncode == 0, proc.stdout[-800:] + proc.stderr[-800:]
    lines = proc.stdout.rstrip("\n").splitlines()
    assert lines[-1].startswith("ASSAY-SUMMARY: ")
    data = json.loads(lines[-1][len("ASSAY-SUMMARY: "):])
    assert data["all_claims_hold"] is True and data["claims"]["failed"] == 0
    assert proc.stderr == ""


def test_installed_command_failure_exits_1_with_the_summary_last(corpus, tmp_path):
    target = corpus / "specimens" / "reference" / "citadel_v1.2.py"
    target.write_bytes(target.read_bytes() + b"# edited\n")
    proc = run_module("assay_production", "--root", str(corpus), cwd=tmp_path)
    assert proc.returncode == 1
    assert proc.stdout.rstrip("\n").splitlines()[-1].startswith("ASSAY-SUMMARY: ")
    assert "NOT PROVEN" in proc.stderr.strip().splitlines()[-1]


# ------------------------------------------------------------------ logging

def test_log_level_adds_stderr_diagnostics_and_leaves_stdout_alone(corpus):
    quiet = run_verify(corpus)
    assert quiet.returncode == 0 and quiet.stderr == ""
    env = _env()
    env["ASSAY_LOG_LEVEL"] = "DEBUG"
    loud = subprocess.run([sys.executable, str(corpus / "verify_manifest.py")], cwd=corpus.parent, env=env,
                          capture_output=True, text=True, timeout=600)
    assert loud.returncode == 0
    assert "assay[DEBUG]" in loud.stderr and "assay.verify" in loud.stderr
    # stdout is the same contract: same report text, summary last.
    assert loud.stdout.rstrip("\n").splitlines()[-1] == quiet.stdout.rstrip("\n").splitlines()[-1]


def test_a_bad_log_level_is_reported_and_does_not_change_the_verdict(corpus):
    env = _env()
    env["ASSAY_LOG_LEVEL"] = "LOUD"
    proc = subprocess.run([sys.executable, str(corpus / "verify_manifest.py")], cwd=corpus.parent, env=env,
                          capture_output=True, text=True, timeout=600)
    assert proc.returncode == 0
    assert "ASSAY_LOG_LEVEL='LOUD'" in proc.stderr and "using WARNING" in proc.stderr
