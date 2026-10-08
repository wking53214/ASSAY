"""CNS-readiness specimen specifications."""
from __future__ import annotations
from typing import List
from .specimen_registry import SpecimenRecord, SpecimenRegistry

CNS_SPECIMEN_SPECS: List[dict] = [
    {"specimen_id": "cns_clean_adapter", "specimen_class": "CNS_READY_REFERENCE",
     "expected_behavior": "Single controlled CNS adapter; preserves authority/scope/provenance/UNKNOWN; fails closed",
     "failure_mode": None, "epistemic_status": "REASONED", "intended_test": "cns_adapter_contract",
     "expected_verdict": "CNS_READY", "tags": ["cns", "adapter", "positive"]},
    {"specimen_id": "cns_malformed_adapter", "specimen_class": "CNS_INVALID_REFERENCE",
     "expected_behavior": "Adapter present but contract malformed", "failure_mode": "malformed_contract",
     "epistemic_status": "REASONED", "intended_test": "cns_adapter_contract", "expected_verdict": "CNS_NOT_READY",
     "tags": ["cns", "negative"]},
    {"specimen_id": "cns_authority_loss", "specimen_class": "CNS_INVALID_REFERENCE",
     "expected_behavior": "Adapter drops or invents authority", "failure_mode": "authority_loss",
     "epistemic_status": "REASONED", "intended_test": "cns_authority_preservation", "expected_verdict": "CNS_NOT_READY",
     "tags": ["cns", "authority", "negative"]},
    {"specimen_id": "cns_scope_loss", "specimen_class": "CNS_INVALID_REFERENCE",
     "expected_behavior": "Adapter expands or truncates scope", "failure_mode": "scope_loss",
     "epistemic_status": "REASONED", "intended_test": "cns_scope_preservation", "expected_verdict": "CNS_NOT_READY",
     "tags": ["cns", "scope", "negative"]},
    {"specimen_id": "cns_provenance_loss", "specimen_class": "CNS_INVALID_REFERENCE",
     "expected_behavior": "Adapter collapses provenance", "failure_mode": "provenance_loss",
     "epistemic_status": "REASONED", "intended_test": "cns_provenance_preservation", "expected_verdict": "CNS_NOT_READY",
     "tags": ["cns", "provenance", "negative"]},
    {"specimen_id": "cns_unknown_collapse", "specimen_class": "CNS_INVALID_REFERENCE",
     "expected_behavior": "Adapter converts UNKNOWN into approval", "failure_mode": "unknown_laundering",
     "epistemic_status": "REASONED", "intended_test": "cns_unknown_preservation", "expected_verdict": "CNS_NOT_READY",
     "tags": ["cns", "unknown", "negative"]},
    {"specimen_id": "cns_authz_bypass", "specimen_class": "CNS_INVALID_REFERENCE",
     "expected_behavior": "Adapter bypasses authorization", "failure_mode": "authorization_bypass",
     "epistemic_status": "REASONED", "intended_test": "cns_authorization_required", "expected_verdict": "CNS_NOT_READY",
     "tags": ["cns", "authorization", "negative"]},
    {"specimen_id": "cns_private_leak", "specimen_class": "CNS_INVALID_REFERENCE",
     "expected_behavior": "Adapter exposes private CNS internals", "failure_mode": "private_interface_leakage",
     "epistemic_status": "REASONED", "intended_test": "cns_no_private_leak", "expected_verdict": "CNS_NOT_READY",
     "tags": ["cns", "privacy", "negative"]},
    {"specimen_id": "cns_multiple_seams", "specimen_class": "CNS_INVALID_REFERENCE",
     "expected_behavior": "Multiple competing CNS paths", "failure_mode": "multiple_seams",
     "epistemic_status": "REASONED", "intended_test": "cns_single_seam", "expected_verdict": "CNS_NOT_READY",
     "tags": ["cns", "seam", "negative"]},
    {"specimen_id": "cns_fail_open", "specimen_class": "CNS_INVALID_REFERENCE",
     "expected_behavior": "Adapter fails open on ambiguity", "failure_mode": "fail_open",
     "epistemic_status": "REASONED", "intended_test": "cns_fail_closed", "expected_verdict": "CNS_NOT_READY",
     "tags": ["cns", "fail_closed", "negative"]},
]

def register_cns_specimens(registry: SpecimenRegistry, source_revision: str = "unspecified"):
    for spec in CNS_SPECIMEN_SPECS:
        registry.register(SpecimenRecord(
            specimen_id=spec["specimen_id"], specimen_version="1.0.0",
            specimen_class=spec["specimen_class"], source_revision=source_revision,
            path=f"specimens/cns/{spec['specimen_id']}.py",
            expected_behavior=spec["expected_behavior"], failure_mode=spec.get("failure_mode"),
            epistemic_status=spec["epistemic_status"], provenance="ASSAY CNS-readiness laboratory",
            intended_test=spec["intended_test"], expected_verdict=spec["expected_verdict"],
            tags=list(spec.get("tags", [])),
        ))
