"""Versioned specimen registry with isolated execution."""
from __future__ import annotations
import ast, json, resource, subprocess, sys, tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

@dataclass
class IsolationResult:
    specimen_id: str
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool
    resource_limited: bool
    success: bool
    error: Optional[str] = None
    def to_dict(self):
        return {"specimen_id": self.specimen_id, "exit_code": self.exit_code,
                "stdout": self.stdout[:8000], "stderr": self.stderr[:8000],
                "timed_out": self.timed_out, "resource_limited": self.resource_limited,
                "success": self.success, "error": self.error}

class IsolationExecutor:
    def __init__(self, timeout_seconds=30.0, memory_mb=256, cpu_seconds=15):
        self.timeout_seconds = timeout_seconds
        self.memory_mb = memory_mb
        self.cpu_seconds = cpu_seconds

    def execute_module(self, specimen_id: str, source_path: Path) -> IsolationResult:
        if not source_path.exists():
            return IsolationResult(specimen_id, -1, "", "", False, False, False, f"missing: {source_path}")
        try:
            ast.parse(source_path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError as e:
            return IsolationResult(specimen_id, -1, "", str(e), False, False, False, f"syntax: {e}")
        preexec = None
        if sys.platform != "win32":
            def _limits():
                if self.cpu_seconds:
                    resource.setrlimit(resource.RLIMIT_CPU, (self.cpu_seconds, self.cpu_seconds))
                if self.memory_mb:
                    mem = self.memory_mb * 1024 * 1024
                    try: resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
                    except Exception: pass
            preexec = _limits
        try:
            proc = subprocess.run([sys.executable, str(source_path)], capture_output=True, text=True,
                                  timeout=self.timeout_seconds, preexec_fn=preexec,
                                  cwd=tempfile.gettempdir(),
                                  env={"PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1"})
            return IsolationResult(specimen_id, proc.returncode, proc.stdout or "", proc.stderr or "",
                                   False, False, proc.returncode == 0)
        except subprocess.TimeoutExpired as e:
            return IsolationResult(specimen_id, -1, str(e.stdout or ""), str(e.stderr or ""), True, False, False, "timeout")
        except Exception as e:
            return IsolationResult(specimen_id, -1, "", str(e), False, False, False, str(e))

@dataclass
class SpecimenRecord:
    specimen_id: str
    specimen_version: str
    specimen_class: str
    source_revision: str
    path: str
    expected_behavior: str
    failure_mode: Optional[str]
    epistemic_status: str
    provenance: str
    intended_test: str
    expected_verdict: str
    manifest_status: str = "ANSWER_KEY_UNVALIDATED"
    isolation_required: bool = True
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self):
        return self.__dict__.copy()

class SpecimenRegistry:
    def __init__(self, root: Path, executor=None):
        self.root = Path(root)
        self.executor = executor or IsolationExecutor()
        self._records = {}
    def register(self, record: SpecimenRecord):
        self._records[record.specimen_id] = record
    def get(self, specimen_id):
        return self._records.get(specimen_id)
    def list_by_class(self, specimen_class):
        return [r for r in self._records.values() if r.specimen_class == specimen_class]
    def execute(self, specimen_id):
        rec = self._records.get(specimen_id)
        if not rec:
            return IsolationResult(specimen_id, -1, "", "", False, False, False, "unknown specimen_id")
        path = self.root / rec.path if not Path(rec.path).is_absolute() else Path(rec.path)
        return self.executor.execute_module(specimen_id, path)
    def save(self, path: Path):
        path.write_text(json.dumps({s: r.to_dict() for s, r in self._records.items()}, indent=2), encoding="utf-8")
    def load(self, path: Path):
        data = json.loads(path.read_text(encoding="utf-8"))
        for sid, d in data.items():
            self._records[sid] = SpecimenRecord(**d)
