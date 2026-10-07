"""The MANIFEST.md answer key, as a machine-readable registry.

MANIFEST.md is written for people. Consumers such as Elegant need the same
answers as data: which file, what class of specimen, what verdict a working
verifier must reach. This module is that translation, and nothing more.

Rules this file keeps:

- Every verdict below is copied from MANIFEST.md, with its section number.
  No answer is invented here. If MANIFEST.md changes an answer, this table
  must change with it, or the two disagree and the corpus is lying.
- Only specimens whose files exist are registered. `cns_specimens.py`
  describes a CNS-readiness catalogue whose files (`specimens/cns/`) have not
  been built yet; those are deliberately absent from the published registry
  until they exist, so no consumer is handed a path to nothing.
- `registry.json` is generated from this table, never hand-edited.
  `verify_manifest.py` rebuilds it and fails if the committed copy differs.

    python3 -m touchstone_production.manifest_registry          # print
    python3 -m touchstone_production.manifest_registry --write  # regenerate
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

from .specimen_registry import SpecimenRecord, SpecimenRegistry

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = Path(__file__).resolve().parent / "registry.json"

P = "specimens/pairs/"
R = "specimens/reference/"
S = "specimens/superseded/"
U = "specimens/progressions/uztc/"

# (specimen_id, class, primary path, companion paths, expected verdict,
#  failure mode, manifest section, what it is)
MANIFEST_SPECIMENS: List[dict] = [
    # --- 1. Reconstruction pairs ------------------------------------------
    dict(id="pair_governance_os_security", cls="RECONSTRUCTION_PAIR",
         path=P + "governance_os_security_source.py",
         companions=[P + "governance_os_security_adapter.py"],
         verdict="FAITHFUL", failure_mode=None, section="1",
         what="Flattened source and its reconstruction; 7 of 13 debris classes covered after normalisation."),
    dict(id="pair_quorum_state_governance", cls="RECONSTRUCTION_PAIR",
         path=P + "quorum_state_governance_source.py",
         companions=[P + "quorum_state_governance_adapter.py"],
         verdict="CONSOLIDATED_LOSSY", failure_mode="lossy_reconstruction", section="1",
         what="Re-architecture into *Module classes; 2 of 7 debris classes covered."),
    dict(id="pair_solvar_stability_governance", cls="RECONSTRUCTION_PAIR",
         path=P + "solvar_stability_governance_source.py",
         companions=[P + "solvar_stability_governance_cleanup.py"],
         verdict="FAITHFUL", failure_mode=None, section="1",
         what="Paired with _cleanup: 31 of 32 debris classes covered."),
    dict(id="pair_solvar_stability_consolidation", cls="RECONSTRUCTION_PAIR",
         path=P + "solvar_stability_governance_source.py",
         companions=[P + "solvar_stability_governance_adapter.py"],
         verdict="CONSOLIDATION_OF_SAME_SOURCE", failure_mode="lossy_reconstruction", section="1",
         what="Second, lossier reconstruction of the same source: 3 of 32 debris classes covered."),
    dict(id="pair_sre_system_resilience", cls="RECONSTRUCTION_PAIR",
         path=P + "sre-system-resilience-evaluator-flattened.py",
         companions=[P + "sre_system_resilience_evaluator_adapter.py"],
         verdict="FAITHFUL", failure_mode=None, section="1",
         what="11 of 11 debris classes covered; thresholds made configurable."),
    dict(id="pair_vanguard_behavioral_simulation", cls="RECONSTRUCTION_PAIR",
         path=P + "vanguard-behavioral-simulation-flattened.py",
         companions=[P + "vanguard-behavioral-simulation.py"],
         verdict="FAITHFUL", failure_mode=None, section="1",
         what="5 of 6 covered; the miss is a deliberate, documented rename."),
    # --- 2. Version progression -------------------------------------------
    dict(id="uztc_progression", cls="VERSION_PROGRESSION",
         path=U + "uztc-construct-v1.2-validated.py",
         companions=[U + "uztc-construct-v1.0-flattened.py", U + "uztc-construct-v1.1-purged.py"],
         verdict="NOT_MONOTONIC_IMPROVEMENT", failure_mode="false_progression", section="2",
         what="Looks better at every step by parses/imports; the endpoint is the least functional."),
    # --- 3. Failure modes -------------------------------------------------
    dict(id="fm_3_1_silent_pass", cls="FAILURE_MODE",
         path=P + "governance_os_security_source.py", companions=[],
         verdict="REFUSE", failure_mode="silent_pass", section="3.1",
         what="Whole file is one comment: imports cleanly, defines zero names."),
    dict(id="fm_3_2_overclaim", cls="FAILURE_MODE",
         path=U + "uztc-construct-v1.2-validated.py", companions=[],
         verdict="CLAIM_FALSE", failure_mode="overclaim", section="3.2",
         what="Described as a 7-layer construct; its only method raises AttributeError."),
    dict(id="fm_3_3_flattening_duplicate", cls="FAILURE_MODE",
         path=R + "wrapper/artifact_3.py", companions=[R + "secure/artifact_1.py"],
         verdict="SAME_CONTENT", failure_mode="flattening_duplicate", section="3.3",
         what="Same content twice, one flattened; wrapper/artifact_3.py is canonical."),
    dict(id="fm_3_4_unreachable_branch", cls="FAILURE_MODE",
         path=P + "sre_system_resilience_evaluator_adapter.py", companions=[],
         verdict="UNREACHABLE", failure_mode="unreachable_branch", section="3.4",
         what="EvaluationVerdict.CRITICAL cannot be reached through evaluate_system_telemetry()."),
    dict(id="fm_3_5_reskinned_duplicate", cls="FAILURE_MODE",
         path=P + "solvar_stability_governance_adapter.py",
         companions=[P + "sre_system_resilience_evaluator_adapter.py"],
         verdict="SAME_DESIGN_RESKINNED", failure_mode="reskinned_duplicate", section="3.5",
         what="Identical energy formula and thresholds under different class names."),
]

# --- 4. Superseded: negative examples --------------------------------------
for _name in ["sovereign-governance-stack-v1.py", "sovereign-governance-stack-v2-expanded.py",
              "unified-sovereign-kernel-wrapper.py", "vanguard-unified-governance-wrapper.py",
              "citadel-processor-router-flattened.py", "resilience-config-dataclass.py",
              "ure-universal-resilience-engine-flattened.py"]:
    MANIFEST_SPECIMENS.append(dict(
        id="superseded_" + _name[:-3].replace("-", "_"), cls="SUPERSEDED",
        path=S + _name, companions=[], verdict="NOT_BEST_AVAILABLE",
        failure_mode="superseded", section="4",
        what="Tried and replaced; a verifier picking the best implementation must not choose this."))

# --- 5. Reference implementations: must be accepted ------------------------
for _rel in ["sovereign_kernel.py", "secure/artifact_2.py", "code-repo-governance-and-gsa-core.py",
             "resilience_stability_kernel.py", "citadel_v1.2.py", "agent-factory-tactical-agents.py"]:
    MANIFEST_SPECIMENS.append(dict(
        id="reference_" + _rel[:-3].replace("/", "_").replace("-", "_").replace(".", "_"),
        cls="REFERENCE", path=R + _rel, companions=[], verdict="ACCEPT",
        failure_mode=None, section="5",
        what="Genuinely runs; refusing it is a false refusal."))
MANIFEST_SPECIMENS.append(dict(
    id="reference_solvar_stability_governance_cleanup", cls="REFERENCE",
    path=P + "solvar_stability_governance_cleanup.py", companions=[], verdict="ACCEPT",
    failure_mode=None, section="5",
    what="Genuinely runs (needs matplotlib); refusing it is a false refusal."))


def build_manifest_registry(root: Path = ROOT) -> SpecimenRegistry:
    registry = SpecimenRegistry(root)
    for spec in MANIFEST_SPECIMENS:
        registry.register(SpecimenRecord(
            specimen_id=spec["id"], specimen_version="1.0.0",
            specimen_class=spec["cls"], source_revision="MANIFEST.md",
            path=spec["path"], expected_behavior=spec["what"],
            failure_mode=spec["failure_mode"], epistemic_status="RECORDED_IN_MANIFEST",
            provenance=f"TOUCHSTONE MANIFEST.md section {spec['section']}",
            intended_test=spec["cls"].lower(), expected_verdict=spec["verdict"],
            tags=[spec["cls"].lower()],
            metadata={"manifest_section": spec["section"], "companions": list(spec["companions"])},
        ))
    return registry


def missing_paths(root: Path = ROOT) -> List[str]:
    """Every registered path, primary or companion, that does not exist."""
    out = []
    for spec in MANIFEST_SPECIMENS:
        for rel in [spec["path"], *spec["companions"]]:
            if not (root / rel).is_file():
                out.append(f"{spec['id']}: {rel}")
    return out


def render(root: Path = ROOT) -> str:
    reg = build_manifest_registry(root)
    data: Dict[str, dict] = {sid: rec.to_dict() for sid, rec in reg._records.items()}
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main(argv: List[str]) -> int:
    missing = missing_paths()
    if missing:
        print("refusing to publish a registry that points at missing files:", file=sys.stderr)
        for m in missing:
            print("  " + m, file=sys.stderr)
        return 1
    text = render()
    if "--write" in argv:
        REGISTRY_PATH.write_text(text, encoding="utf-8")
        print(f"wrote {REGISTRY_PATH.relative_to(ROOT)} ({len(MANIFEST_SPECIMENS)} specimens)")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
