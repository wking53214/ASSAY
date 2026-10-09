"""Run specimen code somewhere it cannot do much harm.

Specimens are real, damaged code. Some of it is untrusted in the plain sense
that nobody has read every line. The verifier has to run it to prove the
answer key, so it runs it here, never in its own process.

What a run gets
---------------
- A separate Python process, started with ``-I`` (ignores PYTHONPATH and the
  user site directory).
- A fresh scratch directory as its working directory, HOME and TMPDIR. The
  scratch directory is deleted afterwards.
- A stripped environment: PATH, a locale, and a few harmless variables. No
  tokens, keys or any other variable of the caller is passed on.
- A timeout, CPU time, memory, file-size and open-file limits.
- No network, when the machine allows it (``unshare -n``, or ``unshare -rn``).
  Where it does not, the result says so and the write/connect guard below
  still blocks sockets inside Python.
- A write guard inside the child (a Python audit hook, installed before the
  specimen is loaded). Any attempt to create, change, rename or delete a file
  outside the scratch directory, to start another program, or to open a
  network connection is refused and recorded as a violation. A violation
  fails the verification even if the specimen catches the error.
- Two outside checks after each run: the top level of the system temp
  directory is listed before and after, and any new entry is reported as a
  stray write. Only items that are new count (a log file another program keeps
  appending to does not). To keep a one-off file from an unrelated program
  from failing a run, the run is repeated once and the item is only believed
  if it shows up again.

Honest limits
-------------
This is a safety net for accidents and careless code, not a security
boundary. A determined hostile program can get around an audit hook (for
example through the ``ctypes`` module calling the C library directly). The
temp-directory listing is the second net for that case, but it only sees new
names at the top of the temp directory and can be fooled by an unrelated
program creating a file at the same moment (the message says so). Real
isolation needs a container or virtual machine. Run this verifier in a
disposable environment if you add specimens you do not trust.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

DEFAULT_TIMEOUT = 120.0

#: Third-party modules a specimen may legitimately need. A run that fails only
#: because one of these is not installed is SKIPPED, never counted as drift.
OPTIONAL_DEPENDENCIES = ("numpy", "matplotlib")

_RESULT_NAME = "__assay_result__.json"
_REQUEST_NAME = "__assay_request__.json"
_HARNESS_NAME = "__assay_harness__.py"

# The program the child runs. It is written into the scratch directory at run
# time, so it is a plain string here. Everything after the guard is installed
# is "specimen time".
HARNESS = r'''
import json, os, sys, traceback, importlib.util, runpy

REQ = json.load(open(sys.argv[1], encoding="utf-8"))
SCRATCH = os.path.realpath(REQ["scratch"])
RESULT = os.path.join(SCRATCH, REQ["result_name"])
sys.dont_write_bytecode = True
VIOLATIONS = []


def _inside(p):
    if isinstance(p, int):
        return True
    try:
        real = os.path.realpath(os.fsdecode(p))
    except Exception:
        return False
    return real == SCRATCH or real.startswith(SCRATCH + os.sep) or real == "/dev/null"


def _violate(what):
    VIOLATIONS.append(what)
    try:
        os.write(2, ("ASSAY-SANDBOX-VIOLATION: " + what + "\n").encode("utf-8", "replace"))
    except Exception:
        pass
    raise PermissionError("ASSAY sandbox refused: " + what)


_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
_PATH_EVENTS = {"os.mkdir", "os.remove", "os.rmdir", "os.truncate", "os.chmod", "os.chown",
                "os.utime", "os.mkfifo", "os.mknod", "os.chflags", "os.lchown", "os.setxattr",
                "os.removexattr", "shutil.chown"}
_PAIR_EVENTS = {"os.rename", "os.link", "shutil.copyfile", "shutil.copymode", "shutil.copystat",
                "shutil.move"}
_SPAWN_EVENTS = {"subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn",
                 "os.fork", "os.forkpty"}
_HARMLESS_PROGRAMS = {"fc-list", "fc-match"}
_NET_EVENTS = {"socket.connect", "socket.bind", "socket.sendto", "socket.sendmsg",
               "socket.getaddrinfo", "socket.gethostbyname", "socket.gethostbyaddr"}


def _hook(event, args):
    try:
        if event == "open":
            path, mode, flags = args[0], args[1], args[2]
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or \
                      (isinstance(flags, int) and bool(flags & _WRITE_FLAGS))
            if writing and not _inside(path):
                _violate("write outside the scratch directory: " + repr(path))
        elif event in _PATH_EVENTS:
            if not _inside(args[0]):
                _violate(event + " outside the scratch directory: " + repr(args[0]))
        elif event in _PAIR_EVENTS:
            for p in args[:2]:
                if not _inside(p):
                    _violate(event + " outside the scratch directory: " + repr(p))
        elif event == "os.symlink":
            if not _inside(args[1]):
                _violate("os.symlink outside the scratch directory: " + repr(args[1]))
        elif event == "subprocess.Popen" and os.path.basename(str(args[0])) in _HARMLESS_PROGRAMS:
            pass  # matplotlib asks fontconfig which fonts exist; that only reads
        elif event in _SPAWN_EVENTS:
            _violate("tried to start another program (" + event + ")")
        elif event in _NET_EVENTS:
            _violate("tried to use the network (" + event + ")")
    except PermissionError:
        raise
    except Exception:
        pass


def _save(payload):
    payload["violations"] = list(VIOLATIONS)
    with open(RESULT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)


def _load(path):
    name = "assay_specimen_" + os.path.basename(path).replace("-", "_").replace(".", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses look the module up here
    spec.loader.exec_module(module)
    return module


def _err(exc):
    return {"type": type(exc).__name__, "message": str(exc)[:300],
            "module_name": getattr(exc, "name", None)}


os.chdir(SCRATCH)
sys.addaudithook(_hook)

out = {"mode": REQ["mode"], "error": None}
try:
    path = REQ["path"]
    if REQ["mode"] == "script":
        sys.argv = [path]
        try:
            runpy.run_path(path, run_name="__main__")
            out["exit_code"] = 0
        except SystemExit as exc:
            code = exc.code
            out["exit_code"] = 0 if code in (None, 0) else (code if isinstance(code, int) else 1)
    else:
        module = _load(path)
        probe = REQ["probe"]
        if probe == "names":
            out["names"] = sorted(n for n in dir(module) if not n.startswith("__"))
        elif probe == "uztc_validate":
            construct = module.Universal_Zero_Trust_Construct({})
            try:
                construct.validate_synthesis({"x": 1})
                out["raised"] = None
            except Exception as exc:
                out["raised"] = type(exc).__name__
        elif probe == "capability_denied":
            try:
                module.validate_capabilities({"net.exfiltrate"})
                out["raised"] = None
            except Exception as exc:
                out["raised"] = type(exc).__name__
        else:
            out["error"] = {"type": "UnknownProbe", "message": probe, "module_name": None}
except BaseException as exc:  # noqa: BLE001 - everything the specimen does is reported
    out["error"] = _err(exc)
    out["traceback"] = traceback.format_exc()[-1500:]
    out.setdefault("exit_code", 1)
_save(out)
'''


@dataclass
class SandboxResult:
    completed: bool                      # the child ran and wrote its report
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool
    probe: Dict = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)
    stray_files: List[str] = field(default_factory=list)
    network_isolated: bool = False
    missing_dependency: Optional[str] = None
    detail: str = ""
    dismissed_strays: List[str] = field(default_factory=list)
    rewritten: List[str] = field(default_factory=list)   # temp items that already existed and were touched

    @property
    def clean(self) -> bool:
        """No guard was tripped and nothing appeared outside the scratch dir."""
        return not self.violations and not self.stray_files

    @property
    def error(self) -> Optional[dict]:
        return self.probe.get("error") if self.probe else None


_UNSHARE: Optional[List[str]] = None


def network_isolation_command() -> List[str]:
    """['unshare', '-n'] (or '-rn') when this machine lets us use it, else []."""
    global _UNSHARE
    if _UNSHARE is not None:
        return _UNSHARE
    _UNSHARE = []
    exe = shutil.which("unshare")
    if exe:
        for flags in ("-n", "-rn"):
            try:
                done = subprocess.run([exe, flags, "true"], capture_output=True, timeout=10)
            except (OSError, subprocess.TimeoutExpired):
                continue
            if done.returncode == 0:
                _UNSHARE = [exe, flags]
                break
    return _UNSHARE


def describe_isolation() -> str:
    cmd = network_isolation_command()
    net = ("no network (%s)" % " ".join(cmd)) if cmd else \
        "network NOT isolated at operating-system level (unshare unavailable); sockets are still blocked inside Python"
    return ("separate process, scratch working directory, stripped environment, timeout and "
            "resource limits, write guard, %s" % net)


def _limits():
    import resource

    def apply():
        for name, soft in (("RLIMIT_CPU", 100), ("RLIMIT_FSIZE", 32 * 1024 * 1024),
                           ("RLIMIT_NOFILE", 256), ("RLIMIT_CORE", 0),
                           ("RLIMIT_AS", 3 * 1024 * 1024 * 1024)):
            try:
                resource.setrlimit(getattr(resource, name), (soft, soft))
            except (ValueError, OSError):
                pass
    return apply


def _top_level(path: str) -> Dict[str, int]:
    """Name -> modification time for everything at the top of a directory."""
    out: Dict[str, int] = {}
    try:
        for name in os.listdir(path):
            try:
                out[name] = os.lstat(os.path.join(path, name)).st_mtime_ns
            except OSError:
                out[name] = -1
    except OSError:
        pass
    return out


def _new(before: Dict[str, int], after: Dict[str, int], ignore: str) -> List[str]:
    """Names that exist after but not before."""
    return sorted(n for n in after if n != ignore and n not in before)


def _rewritten(before: Dict[str, int], after: Dict[str, int]) -> List[str]:
    """Names that existed before and whose modification time changed."""
    return sorted(n for n, t in after.items() if n in before and before[n] != t)


def clean_environment(scratch: str) -> Dict[str, str]:
    """Only what Python needs. No secrets of the caller get through."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8",
           "HOME": scratch, "TMPDIR": scratch, "PYTHONDONTWRITEBYTECODE": "1",
           "PYTHONHASHSEED": "0", "MPLBACKEND": "Agg", "MPLCONFIGDIR": scratch,
           "XDG_CACHE_HOME": scratch, "XDG_CONFIG_HOME": scratch}
    return env


def run_in_sandbox(mode: str, target: Path, *, probe: str = "", stage: Sequence[Tuple[Path, str]] = (),
                   timeout: float = DEFAULT_TIMEOUT, python: Optional[str] = None) -> SandboxResult:
    """Run one specimen under the guard (see _run_once for the arguments).

    New items in the system temp directory are only believed if they appear
    again when the run is repeated. A shared temp directory is full of other
    programs' files, and one stray name from an unrelated program must not
    fail a verification; a specimen that really writes there does it every
    time. Dismissed items are kept in ``dismissed_strays`` for the record.
    """
    first = _run_once(mode, target, probe=probe, stage=stage, timeout=timeout, python=python)
    if not first.stray_files:
        return first
    second = _run_once(mode, target, probe=probe, stage=stage, timeout=timeout, python=python)
    # Believed: a new item again (a specimen that picks random names), or the
    # same item written again (a fixed name, which now already exists).
    confirmed = set(second.stray_files) | (set(first.stray_files) & set(second.rewritten))
    if confirmed:
        second.stray_files = sorted(confirmed | set(first.stray_files))
    else:
        second.stray_files = []
        second.dismissed_strays = first.stray_files
    return second


def _run_once(mode: str, target: Path, *, probe: str = "", stage: Sequence[Tuple[Path, str]] = (),
              timeout: float = DEFAULT_TIMEOUT, python: Optional[str] = None) -> SandboxResult:
    """Run one specimen under the guard.

    mode "script": run the file as ``__main__`` and report its exit code.
    mode "probe":  import the file and run a named probe (see HARNESS).
    stage: extra files copied beside the target first, as (source, new name).
           When given, ``target`` is also copied, so the specimen finds its
           siblings next to it exactly as its own code expects.
    """
    tmp_root = tempfile.gettempdir()
    scratch = tempfile.mkdtemp(prefix="assay-sandbox-", dir=tmp_root)
    scratch_name = os.path.basename(scratch)
    before = _top_level(tmp_root)
    try:
        target = Path(target).resolve()
        run_path = target
        if stage:
            for src, name in stage:
                shutil.copyfile(Path(src).resolve(), Path(scratch) / name)
            shutil.copyfile(target, Path(scratch) / Path(target).name)
            run_path = Path(scratch) / Path(target).name
        request = {"mode": mode, "probe": probe, "path": str(run_path), "scratch": scratch,
                   "result_name": _RESULT_NAME}
        (Path(scratch) / _REQUEST_NAME).write_text(json.dumps(request), encoding="utf-8")
        (Path(scratch) / _HARNESS_NAME).write_text(HARNESS, encoding="utf-8")
        iso = network_isolation_command()
        cmd = iso + [python or sys.executable, "-I", str(Path(scratch) / _HARNESS_NAME),
                     str(Path(scratch) / _REQUEST_NAME)]
        timed_out = False
        try:
            done = subprocess.run(cmd, cwd=scratch, env=clean_environment(scratch), capture_output=True,
                                  text=True, errors="replace", timeout=timeout,
                                  preexec_fn=_limits(), start_new_session=True, stdin=subprocess.DEVNULL)
            rc, out, err = done.returncode, done.stdout or "", done.stderr or ""
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            rc, out, err = -1, _text(exc.stdout), _text(exc.stderr)
        report: Dict = {}
        report_file = Path(scratch) / _RESULT_NAME
        if report_file.is_file():
            try:
                report = json.loads(report_file.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                report = {}
        violations = list(report.get("violations", []))
        for line in err.splitlines():
            if line.startswith("ASSAY-SANDBOX-VIOLATION: "):
                text = line[len("ASSAY-SANDBOX-VIOLATION: "):]
                if text not in violations:
                    violations.append(text)
        after_snapshot = _top_level(tmp_root)
        stray = _new(before, after_snapshot, scratch_name)
        rewritten = _rewritten(before, after_snapshot)
        err_info = report.get("error") or {}
        missing = None
        if err_info.get("type") == "ModuleNotFoundError":
            root_name = (err_info.get("module_name") or "").split(".")[0]
            if root_name in OPTIONAL_DEPENDENCIES:
                missing = root_name
        exit_code = report.get("exit_code", rc)
        detail = ""
        if timed_out:
            detail = "timed out after %ss" % timeout
        elif not report:
            detail = "the child process died before reporting (exit %s): %s" % (rc, err.strip()[-300:])
        return SandboxResult(completed=bool(report) and not timed_out, exit_code=exit_code, stdout=out,
                             stderr=err, timed_out=timed_out, probe=report, violations=violations,
                             stray_files=stray, network_isolated=bool(iso), missing_dependency=missing,
                             detail=detail, rewritten=rewritten)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def _text(value) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", "replace") if isinstance(value, bytes) else str(value)
