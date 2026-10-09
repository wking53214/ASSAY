"""The registry must stay loadable by the things that read it: SWIZZLE and Warden."""
import json
import os
import sys
from pathlib import Path

import pytest

from assay_production.specimen_registry import SpecimenRegistry

from conftest import ROOT

REGISTRY = ROOT / "assay_production" / "registry.json"
#: Fields SWIZZLE (swizzle/assay.py) and Warden (warden/horsemen/adapters.py) read. Never rename or remove these.
READ_BY_CONSUMERS = ("specimen_id", "specimen_class", "path", "expected_verdict", "epistemic_status",
                     "isolation_required", "metadata")


def _find(env_name: str, sibling: str):
    for candidate in (os.environ.get(env_name), ROOT.parent / sibling):
        if candidate and Path(candidate).is_dir():
            return Path(candidate)
    return None


def test_old_fields_are_all_still_there():
    data = json.loads(REGISTRY.read_text())
    assert len(data) == 25
    for sid, d in data.items():
        for key in READ_BY_CONSUMERS:
            assert key in d, (sid, key)
        assert d["specimen_id"] == sid
        assert isinstance(d["metadata"].get("companions"), list)
        assert (ROOT / d["path"]).is_file()
        # new fields, additive
        for key in ("sha256", "companion_sha256", "manifest_block_sha256", "validation"):
            assert key in d


def test_registry_loads_back_into_the_registry_class():
    reg = SpecimenRegistry(ROOT)
    reg.load(REGISTRY)
    assert len(reg._records) == 25
    assert reg.get("fm_3_1_silent_pass").sha256


def test_swizzle_still_loads_and_proves_the_key():
    swizzle = _find("SWIZZLE_ROOT", "SWIZZLE")
    if swizzle is None:
        pytest.skip("SWIZZLE checkout not found (set SWIZZLE_ROOT)")
    sys.path.insert(0, str(swizzle))
    try:
        from swizzle import assay
    finally:
        sys.path.remove(str(swizzle))
    key = assay.load_answer_key(ROOT)
    assert len(key) == 25
    proven, summary = assay.prove_answer_key(ROOT)
    assert proven, summary


def test_warden_still_loads_the_registry():
    warden = _find("WARDEN_ROOT", "Elegant")
    if warden is None:
        pytest.skip("Warden checkout not found (set WARDEN_ROOT)")
    sys.path.insert(0, str(warden))
    try:
        from warden.horsemen import AssayAdapter
    finally:
        sys.path.remove(str(warden))
    refs = AssayAdapter(ROOT).load_registry()
    assert len(refs) == 25
    assert {r.expected_verdict for r in refs} >= {"REFUSE", "ACCEPT", "SAME_CONTENT"}
