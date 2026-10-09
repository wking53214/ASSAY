"""Shared helpers: a throw-away copy of the corpus to tamper with, and a way to run the verifier on it."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

COPY_ITEMS = ["specimens", "assay_production", "MANIFEST.md", "README.md", "verify_manifest.py", ".gitattributes"]


def make_corpus(dest: Path) -> Path:
    """Copy the corpus (no git history, no caches) so a test can break it freely."""
    dest.mkdir(parents=True, exist_ok=True)
    for item in COPY_ITEMS:
        src = ROOT / item
        if src.is_dir():
            shutil.copytree(src, dest / item, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        elif src.exists():
            shutil.copy2(src, dest / item)
    return dest


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    return make_corpus(tmp_path / "corpus")


def _env() -> dict:
    # No PYTHONPATH: the copy must use its own assay_production package.
    return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": os.environ.get("HOME", "/tmp"),
            "LANG": "C.UTF-8"}


def run_verify(corpus: Path, *args: str) -> subprocess.CompletedProcess:
    """Run the copy's verify_manifest.py from an unrelated working directory."""
    elsewhere = corpus.parent / "elsewhere"
    elsewhere.mkdir(exist_ok=True)
    return subprocess.run([sys.executable, str(corpus / "verify_manifest.py"), *args], cwd=elsewhere,
                          capture_output=True, text=True, env=_env(), timeout=600)


def run_write(corpus: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "assay_production.manifest_registry", "--write"], cwd=corpus,
                          capture_output=True, text=True, env=_env(), timeout=600)


def edit(path: Path, old: str, new: str, count: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{old!r} not found in {path}"
    path.write_text(text.replace(old, new, count), encoding="utf-8", newline="")
