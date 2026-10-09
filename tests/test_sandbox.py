"""The sandbox: what a specimen run can and cannot do."""
import os
import socket
import sys
from pathlib import Path

import pytest

from assay_production.sandbox import clean_environment, run_in_sandbox
from assay_production.specimen_registry import IsolationExecutor


def script(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "specimen.py"
    path.write_text(body, encoding="utf-8")
    return path


def test_environment_is_stripped_and_cwd_is_scratch(tmp_path, monkeypatch):
    monkeypatch.setenv("ASSAY_TEST_SECRET", "hunter2")
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_secret")
    res = run_in_sandbox("script", script(tmp_path, "import os\nprint('ENV', sorted(os.environ))\nprint('CWD', os.getcwd())\n"))
    assert res.completed and res.exit_code == 0
    assert "ASSAY_TEST_SECRET" not in res.stdout and "GITHUB_TOKEN" not in res.stdout
    assert "assay-sandbox-" in res.stdout.split("CWD")[1]
    assert set(clean_environment("/x")) <= {"PATH", "LANG", "HOME", "TMPDIR", "PYTHONDONTWRITEBYTECODE",
                                            "PYTHONHASHSEED", "MPLBACKEND", "MPLCONFIGDIR", "XDG_CACHE_HOME",
                                            "XDG_CONFIG_HOME"}


def test_writes_inside_scratch_are_allowed_outside_are_refused(tmp_path):
    outside = tmp_path / "outside.txt"
    res = run_in_sandbox("script", script(tmp_path, f"""
open('inside.txt', 'w').write('fine')
try:
    open({str(outside)!r}, 'w').write('nope')
except PermissionError:
    pass
"""))
    assert not outside.exists()
    assert any("outside the scratch directory" in v for v in res.violations)
    assert not res.clean


def test_catching_the_error_does_not_hide_the_violation(tmp_path):
    res = run_in_sandbox("script", script(tmp_path, "import os\ntry:\n    os.mkdir('/tmp/assay-x-never')\nexcept Exception:\n    pass\n"))
    assert res.violations and not Path("/tmp/assay-x-never").exists()


def test_starting_programs_and_network_are_refused(tmp_path):
    res = run_in_sandbox("script", script(tmp_path, """
import os, socket, subprocess
for fn in (lambda: os.system('true'), lambda: subprocess.run(['true']),
           lambda: socket.create_connection(('127.0.0.1', 9), timeout=1)):
    try:
        fn()
    except Exception:
        pass
"""))
    text = " ".join(res.violations)
    assert "another program" in text and "network" in text


def test_timeout_is_enforced(tmp_path):
    res = run_in_sandbox("script", script(tmp_path, "while True:\n    pass\n"), timeout=2)
    assert res.timed_out and not res.completed


def test_a_bypass_of_the_guard_is_caught_by_the_temp_listing(tmp_path):
    """ctypes talks to the C library directly, past Python's audit hook. The temp listing still sees the file."""
    import ctypes

    try:
        ctypes.CDLL(None).creat
    except (OSError, AttributeError):
        pytest.skip("no C library handle")
    name = f"/tmp/assay-bypass-{os.getpid()}"
    try:
        res = run_in_sandbox("script", script(tmp_path, f"""
import ctypes
ctypes.CDLL(None).creat({name!r}.encode(), 0o600)
"""))
        assert not res.violations                 # the hook did not see it ...
        assert os.path.basename(name) in res.stray_files   # ... the listing did, on both runs
    finally:
        if os.path.exists(name):
            os.unlink(name)


def test_unrelated_temp_noise_is_dismissed(tmp_path, monkeypatch):
    """One stray name that does not come back on the repeat run is not believed."""
    import assay_production.sandbox as sb

    calls = []
    real = sb._run_once

    def flaky(*a, **k):
        res = real(*a, **k)
        calls.append(1)
        if len(calls) == 1:
            res.stray_files = ["someone-elses-file"]
        return res

    monkeypatch.setattr(sb, "_run_once", flaky)
    res = sb.run_in_sandbox("script", script(tmp_path, "pass\n"))
    assert res.stray_files == [] and res.dismissed_strays == ["someone-elses-file"]


def test_existing_executor_now_uses_the_sandbox(tmp_path):
    ok = IsolationExecutor().execute_module("ok", script(tmp_path, "print('hi')\n"))
    assert ok.success and "hi" in ok.stdout
    bad = IsolationExecutor().execute_module("bad", script(tmp_path, "open('/tmp/assay-exec-never', 'w')\n"))
    assert not bad.success and "sandbox violation" in (bad.error or "")
    assert not Path("/tmp/assay-exec-never").exists()
    broken = IsolationExecutor().execute_module("syn", script(tmp_path, "def (:\n"))
    assert not broken.success and broken.error.startswith("syntax")
