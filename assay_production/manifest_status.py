"""Separate answer-key integrity from answer-key correctness."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass
class ManifestCheckResult:
    manifest_consistent: bool
    answer_key_validated: bool
    inconsistencies: List[str]
    unvalidated_entries: List[str]
    @property
    def status(self) -> str:
        if not self.manifest_consistent:
            return "MANIFEST_INCONSISTENT"
        if self.answer_key_validated:
            return "ANSWER_KEY_VALIDATED"
        return "ANSWER_KEY_UNVALIDATED"

class ManifestVerifier:
    def __init__(self, root: Path, manifest_path: Optional[Path] = None):
        self.root = Path(root)
        self.manifest_path = manifest_path or (self.root / "MANIFEST.md")
    def check_consistency(self, registered_paths: List[str]) -> ManifestCheckResult:
        inconsistencies, unvalidated = [], []
        for rel in registered_paths:
            p = self.root / rel if not Path(rel).is_absolute() else Path(rel)
            if not p.exists():
                inconsistencies.append(f"missing specimen file: {rel}")
            else:
                unvalidated.append(rel)
        if not self.manifest_path.exists():
            inconsistencies.append(f"manifest missing: {self.manifest_path}")
        return ManifestCheckResult(len(inconsistencies) == 0, False, inconsistencies, unvalidated)
    def mark_validated(self, result: ManifestCheckResult, validated_ids: List[str]) -> ManifestCheckResult:
        remaining = [e for e in result.unvalidated_entries if e not in validated_ids]
        return ManifestCheckResult(result.manifest_consistent, result.manifest_consistent and len(remaining) == 0,
                                   result.inconsistencies, remaining)
