"""The committed Ghost baseline (.ghost_baseline.json) cannot go stale without a test failing.

Ghost's baseline lists the findings the repository has agreed to stop seeing. It went stale once (rebuilt in 0.11.0,
stale again by 0.11.5 because code moved and `recovered-originals/` arrived), and nothing said so until the circuit
rejected the repository. This test scans the checkout with the options Warden uses and compares the finding ids with
the baseline's, in both directions: a baseline entry that matches nothing, and a finding the baseline does not hold.

It runs where ghost_tools is installed. The `baseline` job in the workflow installs ghost_tools at the commit pinned
there and sets ASSAY_REQUIRE_GHOST_BASELINE=1, which turns "ghost_tools is not installed" from a skip into a failure.

Findings that share an id take a six-character place suffix. In Ghost 1.10.8, the version the `baseline` job tests,
that suffix hashed the absolute path of the checkout, so one finding had a different id in each folder (15 of the
17 suffixed ids). That was a ghost_tools defect, fixed in ghost_tools 1.10.9 (folder-independent ids): the circuit's
ghost_tools no longer has it. The baseline holds no suffixed id (the job tests 1.10.8); those findings stay
reported. This test compares the findings WITHOUT a suffix with the baseline in both directions, and requires the
baseline to hold no suffixed id. To rebuild the baseline, after reading the findings it will accept:

    rm .ghost_baseline.json
    python -m ghost_buster.cli . --single-repo --no-tests --no-secrets --no-ledger --no-structure --no-project \\
        --no-correlate --no-branches --accept
    python - <<'PY'
    import json, re
    p = ".ghost_baseline.json"
    keep = [e for e in json.load(open(p)) if not re.search(r"-[0-9a-f]{6}$", e["id"])]
    open(p, "w").write(json.dumps(keep, indent=2, sort_keys=True))
    PY
"""
import collections
import importlib.util
import json
import os
import re
import subprocess
import sys

import pytest

from conftest import ROOT

GHOST_TOOLS_COMMIT = "5a9154d3c76670f5bf1f46d845acadfed46d7bc8"  # ghost_tools 1.10.8
# The options Warden passes to Ghost, plus --no-branches (a branch finding depends on the clone, not on the code).
GHOST_OPTIONS = ("--single-repo", "--no-tests", "--no-secrets", "--no-ledger", "--no-structure", "--no-project",
                 "--no-correlate", "--no-branches")
WORKFLOW = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")

_SUFFIXED = re.compile(r"-[0-9a-f]{6}$")


def portable(ids):
    """The ids that do not carry Ghost's place suffix, which depends on the checkout's absolute path."""
    return [i for i in ids if not _SUFFIXED.search(i)]


def differences(current_ids, baseline_ids):
    """(baseline entries that match no current finding, current findings the baseline does not hold), as counts."""
    now = collections.Counter(portable(current_ids))
    held = collections.Counter(baseline_ids)
    return dict(held - now), dict(now - held)


def test_the_comparison_sees_a_stale_entry_and_a_new_finding_and_leaves_suffixed_findings_alone():
    base = ["ghost-aaaaaaaaaaaa", "ghost-bbbbbbbbbbbb"]
    assert differences(base, base) == ({}, {})
    # findings with a place suffix are reported by Ghost but are not part of the comparison
    assert differences(base + ["ghost-cccccccccccc-111111"], base) == ({}, {})
    # an entry whose finding is gone is stale
    assert differences(base[:1], base) == ({"ghost-bbbbbbbbbbbb": 1}, {})
    # a finding the baseline does not hold is new
    assert differences(base + ["ghost-dddddddddddd"], base) == ({}, {"ghost-dddddddddddd": 1})
    # a finding that used to collide and now stands alone must be accepted on purpose
    assert differences(base + ["ghost-cccccccccccc"], base) == ({}, {"ghost-cccccccccccc": 1})


def test_the_workflow_installs_ghost_tools_at_the_pinned_commit_and_fails_on_a_skip():
    assert f"ghost_tools.git@{GHOST_TOOLS_COMMIT}" in WORKFLOW
    assert "ASSAY_REQUIRE_GHOST_BASELINE: \"1\"" in WORKFLOW
    assert re.search(r"tests/test_ghost_baseline\.py[^\n]*\n(?:[^\n]*\n){0,3}[^\n]*! grep -q \"skipped\"", WORKFLOW)


def test_the_baseline_file_holds_unique_ids_and_none_with_a_path_dependent_suffix():
    entries = json.loads((ROOT / ".ghost_baseline.json").read_text(encoding="utf-8"))
    ids = [entry["id"] for entry in entries]
    assert ids and len(ids) == len(set(ids))
    assert portable(ids) == ids, [i for i in ids if i not in portable(ids)]


def _ghost_available() -> bool:
    return importlib.util.find_spec("ghost_buster") is not None


def test_the_committed_baseline_matches_what_ghost_finds_now(tmp_path):
    if not _ghost_available():
        if os.environ.get("ASSAY_REQUIRE_GHOST_BASELINE") == "1":
            pytest.fail("ghost_tools is not installed, and ASSAY_REQUIRE_GHOST_BASELINE=1 says it must be")
        pytest.skip("ghost_tools is not installed")
    empty = tmp_path / "empty_baseline.json"
    empty.write_text("[]\n", encoding="utf-8")
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(tmp_path), "LANG": "C.UTF-8",
           "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.run([sys.executable, "-m", "ghost_buster.cli", str(ROOT), *GHOST_OPTIONS, "--baseline",
                           str(empty), "--json"], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=600)
    assert proc.returncode in (0, 1), proc.stderr[-600:]
    current = [finding["id"] for finding in json.loads(proc.stdout)["findings"]]
    held = [entry["id"] for entry in json.loads((ROOT / ".ghost_baseline.json").read_text(encoding="utf-8"))]
    stale, new = differences(current, held)
    assert not stale and not new, (
        f"the Ghost baseline is out of date: {sum(stale.values())} entries match nothing {sorted(stale)[:5]}, "
        f"{sum(new.values())} findings are not in it {sorted(new)[:5]}. Read the findings, then rebuild it "
        "(see this file's docstring).")
