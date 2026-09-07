# =============================================================================
# UNIFIED SOVEREIGN KERNEL - working end-to-end governance wrapper
#
# Built 2026-08-27, SRE precheck added 2026-09-03. This is the running version
# of the composition that three sketches only described (all now in archive/):
# unified-sovereign-kernel-wrapper.py, sovereign-governance-stack-v1.py,
# sovereign-governance-stack-v2-expanded.py. Those referenced collaborator
# classes that were never defined and could not execute.
#
# Five layers, wired here from the modules that now work in this folder:
#
#   0. SRE precheck - sre_system_resilience_evaluator_adapter.py :
#                    SystemResilienceEvaluator. Per the v1/v2 sketches, this
#                    runs before the perimeter. It differs from those sketches
#                    in one deliberate way: they reject only on
#                    EvaluationVerdict.CRITICAL, but reconstruction verification
#                    found CRITICAL is mathematically unreachable through
#                    evaluate_system_telemetry() as SRE was originally designed
#                    (DEGRADED's energy gate always trips first - see
#                    sre_system_resilience_evaluator_adapter.py's header and its
#                    __main__ regression/search checks). Rejecting on
#                    CRITICAL alone would be a decorative check that can never
#                    fire. This kernel rejects on DEGRADED or CRITICAL instead,
#                    so the precheck is a real gate; SRE's own file is
#                    untouched, this is a wiring-layer decision, not a change
#                    to SRE's reconstructed logic or thresholds.
#
#   1. Perimeter   - vanguard-behavioral-simulation.py : VanguardBehavioralPipeline
#                    Contradiction / anomaly detection. A request flagged as
#                    compromised is rejected here and never reaches execution.
#
#   2. Linguistic  - neutrality scrub. citadel_v1.2.py : Citadel, vendored
#                    verbatim from the CITADEL repo (see that file's own header
#                    for the source commit) - deterministic regex detect / score
#                    / rewrite, not the diverged model-retry variant that's in
#                    archive/. Runs under CITADEL's "default" profile unless
#                    request["citadel_profile"] names another one.
#
#   3. Master      - code-repo-governance-and-gsa-core.py : GsaCoreController +
#                    GsaTemporalDoorwayGate. Rotating-hash exit handshake over a
#                    governed context envelope, carrying the interlock hash-chain
#                    that GsaUniversalAdapter maintains.
#
#   4. Execution   - quorum_state_governance_adapter.py : CoreOrchestratorBinder
#                    Signed multi-node proposals -> signature verification ->
#                    L1 clustering -> quorum decision -> write-ahead audit hash.
#
# execute_governed_request() returns a single trace-bundle dict describing every
# layer. run() is the synchronous convenience wrapper.
#
# NOTE: two sibling files use hyphenated names and cannot be imported by name,
# so this module loads all of its dependencies by path. A future rename pass
# could make that unnecessary.
# =============================================================================
from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import os
import sys
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, Optional, Tuple

_HERE = Path(__file__).resolve().parent


def _load_by_path(module_alias: str, filename: str) -> Any:
    """Load a sibling governance-stack file that cannot be imported by name."""
    spec = importlib.util.spec_from_file_location(module_alias, _HERE / filename)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class UnifiedSovereignKernel:
    """Master governance layer in front of a hybrid quorum-consensus engine."""

    def __init__(self, keystone_secret: str = "default-keystone-secret") -> None:
        self._sre = _load_by_path("_sk_sre", "sre_system_resilience_evaluator_adapter.py")
        self._vanguard = _load_by_path("_sk_vanguard", "vanguard-behavioral-simulation.py")
        self._gsa_core = _load_by_path("_sk_gsa_core", "code-repo-governance-and-gsa-core.py")
        self._quorum = _load_by_path("_sk_quorum", "quorum_state_governance_adapter.py")
        self._citadel = _load_by_path("_sk_citadel", "citadel_v1.2.py")
        self._keystone_secret = keystone_secret
        # flips to True now that a real scrub is wired into _linguistic_scrub
        self.linguistic_scrub_implemented = True

    # ---- layer 0: SRE stability precheck ----------------------------------
    def _run_sre_precheck(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Compare request telemetry (request["sre_telemetry"]) against a
        neutral baseline. Rejects on DEGRADED or CRITICAL - see this file's
        header for why CRITICAL alone isn't enough."""
        sre = self._sre
        baseline = sre.TelemetryMetrics()
        telemetry_fields = (
            "containment_ratio", "processing_latency", "recurrent_request_ratio",
            "termination_ratio", "determinism_coefficient", "duplicate_execution_ratio",
            "reentry_coefficient", "escalation_ratio", "buffer_backlog_depth",
        )
        supplied = request.get("sre_telemetry", {})
        current = sre.TelemetryMetrics(**{
            field: float(supplied[field]) for field in telemetry_fields if field in supplied
        })
        report = sre.SystemResilienceEvaluator().evaluate_system_telemetry(baseline, current)
        if report.verdict == sre.EvaluationVerdict.CRITICAL:
            reject_reason = "SRE_CRITICAL_DRIFT"
        elif report.verdict == sre.EvaluationVerdict.DEGRADED:
            reject_reason = "SRE_DEGRADED_DRIFT"
        else:
            reject_reason = None
        return {
            "verdict": report.verdict.value,
            "explanation": report.explanation,
            "weighted_squared_delta_sum": report.weighted_squared_delta_sum,
            "activation_threat_score": report.activation_threat_score,
            "rejected": reject_reason is not None,
            "reject_reason": reject_reason,
        }

    # ---- layer 2: linguistic-neutrality scrub ------------------------------
    def _linguistic_scrub(self, text: str, profile: str = "default") -> Tuple[str, Dict[str, Any]]:
        """CITADEL deterministic detect / score / rewrite. Returns (final_text, note)."""
        result = self._citadel.Citadel().enforce(text, profile=profile)
        return result["final"], {
            "applied": True,
            "changed": result["changed"],
            "score": result["score"],
            "violations": result["violations"],
            "profile_used": result["profile_used"],
            "original_text": result["original"],
            "final_text": result["final"],
        }

    # ---- layer 1: perimeter ----------------------------------------------
    def _run_perimeter(self, request: Dict[str, Any]) -> Dict[str, Any]:
        pipeline = self._vanguard.VanguardBehavioralPipeline()
        structure = self._vanguard.SystemInputStructure(
            text_content_body=str(request.get("text", "")),
            numeric_metric_value=float(request.get("metric", 100.0)),
        )
        return pipeline.process_pipeline_iteration(
            input_structure=structure,
            observed_error_value=float(request.get("error", 0.0)),
            intended_target_value=float(request.get("target", request.get("metric", 100.0))),
            raw_actuation_delta=float(request.get("delta", 0.0)),
        )

    # ---- layer 3: master governance -------------------------------------
    async def _run_master_layer(self, governed_text: str) -> Dict[str, Any]:
        core = self._gsa_core
        controller = core.GsaCoreController()
        controller.initialize_pipeline_component(
            "GSA_TEMPORAL_DOORWAY_GATE",
            rotation_seed=self._keystone_secret,
            rotation_interval_seconds=0.01,
        )
        gate = controller.active_adapters["GSA_TEMPORAL_DOORWAY_GATE"].module
        await gate.start_gate_engine()
        try:
            await asyncio.sleep(0.03)  # let the hash rotate at least once
            target_hash = gate._current_doorway_hash
            envelope = core.GsaContextEnvelope(
                payload_data=MappingProxyType({"governed_text": governed_text}),
                header_mapping=MappingProxyType({
                    "gsa_target_exit_hash": target_hash,
                    "gsa_doorway_timeout_seconds": 1.0,
                }),
            )
            result = await controller.forward_envelope("GSA_TEMPORAL_DOORWAY_GATE", envelope)
        finally:
            await gate.shutdown_gate_engine()

        headers = dict(result.header_mapping)
        return {
            "envelope_status": result.status_string,
            "exit_handshake_secured": result.status_string == "GSA_EXIT_HANDSHAKE_COMPLETED",
            "interlock_hash": headers.get("gsa_interlock_hash"),
            "loop_iteration": headers.get("gsa_loop_iteration"),
        }

    # ---- layer 4: quorum consensus execution ---------------------------
    def _run_execution(self, request: Dict[str, Any]) -> Dict[str, Any]:
        quorum = self._quorum
        nodes = ["compute_node_0", "compute_node_1", "compute_node_2"]
        key_registry = {
            n: hashlib.sha256(f"secure_key_{n}".encode()).digest() for n in nodes
        }
        payload = {
            "current_state": {
                "system_entropy": float(request.get("entropy", 0.4)),
                "network_stability": float(request.get("stability", 0.7)),
            },
            "nodes": nodes,
            "key_registry": key_registry,
        }
        out = quorum.CoreOrchestratorBinder().process(payload)
        headers = out.get("_gaps_headers", {})
        return {
            "leader_id": headers.get("metadata", {}).get("leader_id"),
            "quorum_achieved": headers.get("risk_metrics", {}).get("quorum_achieved"),
            "quorum_votes": headers.get("risk_metrics", {}).get("quorum_votes"),
            "wal_commit_hash": headers.get("structural_indices", {}).get("wal_commit_hash"),
            "finalized_state": out.get("finalized_state"),
        }

    # ---- entry point ---------------------------------------------------
    async def execute_governed_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route one request through all five layers; return a trace bundle."""
        sre_precheck = self._run_sre_precheck(request)
        if sre_precheck["rejected"]:
            return {
                "status": "REJECTED_AT_SRE_PRECHECK",
                "sre_precheck": sre_precheck,
                "perimeter": None,
                "linguistic_scrub": None,
                "master_layer": None,
                "execution": None,
            }

        perimeter = self._run_perimeter(request)
        if perimeter.get("system_compromise_detected"):
            return {
                "status": "REJECTED_AT_PERIMETER",
                "sre_precheck": sre_precheck,
                "perimeter": perimeter,
                "linguistic_scrub": None,
                "master_layer": None,
                "execution": None,
            }

        scrubbed_text, scrub_note = self._linguistic_scrub(
            str(request.get("text", "")), profile=request.get("citadel_profile", "default")
        )
        master_layer = await self._run_master_layer(scrubbed_text)
        execution = self._run_execution(request)

        return {
            "status": "COMPLETED",
            "sre_precheck": sre_precheck,
            "perimeter": perimeter,
            "linguistic_scrub": scrub_note,
            "master_layer": master_layer,
            "execution": execution,
        }

    def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous convenience wrapper around execute_governed_request."""
        return asyncio.run(self.execute_governed_request(request))


if __name__ == "__main__":
    import json

    os.environ.setdefault("VANGUARD_AUDIT_LOG_PATH", os.devnull)  # keep demo tidy
    kernel = UnifiedSovereignKernel()

    benign = kernel.run({
        "text": "All operational tracking parameters remain fully balanced.",
        "metric": 120.0, "error": 4.5, "target": 110.0, "delta": -12.5,
    })
    print("--- benign request (no sre_telemetry -> neutral baseline, passes precheck) ---")
    print(json.dumps(benign, indent=2, default=str))
    assert benign["sre_precheck"]["verdict"] == "NEUTRAL"
    assert benign["status"] == "COMPLETED"
    assert benign["linguistic_scrub"]["applied"] is True
    assert benign["linguistic_scrub"]["changed"] is False  # no CITADEL violations in this text

    unscrubbed = kernel.run({
        "text": "I think this might improve throughput, though results seem inconsistent.",
        "metric": 120.0, "error": 4.5, "target": 110.0, "delta": -12.5,
    })
    print("--- request with hedging/identity language (CITADEL rewrites it, layer 2) ---")
    print(json.dumps(unscrubbed, indent=2, default=str))
    assert unscrubbed["status"] == "COMPLETED"
    assert unscrubbed["linguistic_scrub"]["changed"] is True
    assert unscrubbed["linguistic_scrub"]["score"] < 100
    violation_types = {v["type"] for v in unscrubbed["linguistic_scrub"]["violations"]}
    assert "identity" in violation_types and "hedging" in violation_types
    print(f"before: {unscrubbed['linguistic_scrub']['original_text']!r}")
    print(f"after:  {unscrubbed['linguistic_scrub']['final_text']!r}")
    assert "might" not in unscrubbed["linguistic_scrub"]["final_text"].lower()

    hostile = kernel.run({
        "text": "The system is stable but broken, safe yet a total failure.",
        "metric": 120.0, "error": 5.0, "target": 110.0, "delta": 0.0,
    })
    print("--- contradictory request (rejected at the VANGUARD perimeter) ---")
    print(json.dumps(hostile, indent=2, default=str))
    assert hostile["status"] == "REJECTED_AT_PERIMETER"

    drifted = kernel.run({
        "text": "All operational tracking parameters remain fully balanced.",
        "metric": 120.0, "error": 4.5, "target": 110.0, "delta": -12.5,
        "sre_telemetry": {"termination_ratio": 0.2},
    })
    print("--- drifted request (rejected at the new SRE precheck, step 0) ---")
    print(json.dumps(drifted, indent=2, default=str))
    assert drifted["status"] == "REJECTED_AT_SRE_PRECHECK"
    assert drifted["sre_precheck"]["reject_reason"] == "SRE_DEGRADED_DRIFT"

    print("\nALL SOVEREIGN_KERNEL DEMO CHECKS PASSED")
