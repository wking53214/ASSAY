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


def _find(env_name: str, *names: str):
    """The checkout named by the environment variable, else a sibling folder of this repository.

    Siblings are matched without regard to case, so ``WARDEN``, ``Warden`` and ``warden`` all count, and a folder
    that merely shares the name but is a file is ignored. None when nothing is found (the caller then skips).
    """
    named = os.environ.get(env_name)
    if named and Path(named).is_dir():
        return Path(named)
    wanted = {n.lower() for n in names}
    try:
        siblings = sorted(ROOT.parent.iterdir())
    except OSError:
        return None
    for candidate in siblings:
        if candidate.is_dir() and candidate.name.lower() in wanted:
            return candidate
    return None


def test_old_fields_are_all_still_there():
    data = json.loads(REGISTRY.read_text())
    assert len(data) == 27
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
    assert len(reg._records) == 27
    assert reg.get("fm_3_1_silent_pass").sha256


def test_swizzle_still_loads_and_proves_the_key():
    swizzle = _find("SWIZZLE_ROOT", "swizzle")
    if swizzle is None:
        pytest.skip("SWIZZLE checkout not found (set SWIZZLE_ROOT)")
    sys.path.insert(0, str(swizzle))
    try:
        from swizzle import assay
    finally:
        sys.path.remove(str(swizzle))
    key = assay.load_answer_key(ROOT)
    assert len(key) == 27
    proven, summary = assay.prove_answer_key(ROOT)
    assert proven, summary


def test_warden_still_loads_the_registry():
    warden = _find("WARDEN_ROOT", "warden")
    if warden is None:
        pytest.skip("Warden checkout not found (set WARDEN_ROOT)")
    sys.path.insert(0, str(warden))
    try:
        from warden.horsemen import AssayAdapter
    finally:
        sys.path.remove(str(warden))
    refs = AssayAdapter(ROOT).load_registry()
    assert len(refs) == 27
    assert {r.expected_verdict for r in refs} >= {"REFUSE", "ACCEPT", "SAME_CONTENT"}


# ------------------------------------------------ how the sibling checkouts are found

def test_find_honours_the_environment_variable(tmp_path, monkeypatch):
    elsewhere = tmp_path / "anywhere-at-all"
    elsewhere.mkdir()
    monkeypatch.setenv("WARDEN_ROOT", str(elsewhere))
    assert _find("WARDEN_ROOT", "warden") == elsewhere


@pytest.mark.parametrize("folder", ["WARDEN", "Warden", "warden"])
def test_find_matches_a_sibling_whatever_its_capitalisation(tmp_path, monkeypatch, folder):
    here = tmp_path / "ASSAY"
    here.mkdir()
    (tmp_path / folder).mkdir()
    (tmp_path / "other").mkdir()
    monkeypatch.delenv("WARDEN_ROOT", raising=False)
    monkeypatch.setitem(globals(), "ROOT", here)
    assert _find("WARDEN_ROOT", "warden") == tmp_path / folder


def test_find_returns_none_when_nothing_is_there(tmp_path, monkeypatch):
    here = tmp_path / "ASSAY"
    here.mkdir()
    (tmp_path / "warden.txt").write_text("a file, not a checkout")
    monkeypatch.delenv("WARDEN_ROOT", raising=False)
    monkeypatch.setitem(globals(), "ROOT", here)
    assert _find("WARDEN_ROOT", "warden") is None
