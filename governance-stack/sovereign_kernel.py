# =============================================================================
# UNIFIED SOVEREIGN KERNEL - working end-to-end governance wrapper
#
# Built 2026-08-27. This is the running version of the composition that three
# sketches only described (all now in archive/): unified-sovereign-kernel-
# wrapper.py, sovereign-governance-stack-v1.py, sovereign-governance-stack-
# v2-expanded.py. Those referenced collaborator classes that were never defined
# and could not execute.
#
# Four layers, wired here from the modules that now work in this folder:
#
#   1. Perimeter   - vanguard-behavioral-simulation.py : VanguardBehavioralPipeline
#                    Contradiction / anomaly detection. A request flagged as
#                    compromised is rejected here and never reaches execution.
#
#   2. Linguistic  - neutrality scrub. NOT IMPLEMENTED. `_linguistic_scrub` is a
#                    labelled pass-through: it returns the text unchanged and the
#                    trace bundle records the step as not applied. The engine to
#                    wire in here is CITADEL's deterministic detect / score /
#                    transform engine (the CITADEL repo, citadel_v1.2.py) - the
#                    diverged model-retry variant that was in this folder is now
#                    in archive/. Nothing else in this file needs to change.
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
# NOT wired yet (the v1/v2 sketches in archive/ show it as step 1, before the
# perimeter): an SRE / system-resilience stability pre-check. The SRE modules in
# this folder are still flattened.
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
        self._vanguard = _load_by_path("_sk_vanguard", "vanguard-behavioral-simulation.py")
        self._gsa_core = _load_by_path("_sk_gsa_core", "code-repo-governance-and-gsa-core.py")
        self._quorum = _load_by_path("_sk_quorum", "quorum_state_governance_adapter.py")
        self._keystone_secret = keystone_secret
        # flips to True only when a real scrub is wired into _linguistic_scrub
        self.linguistic_scrub_implemented = False

    # ---- layer 2: linguistic-neutrality scrub (pass-through hook) ----------
    def _linguistic_scrub(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Placeholder for CITADEL linguistic-neutrality enforcement.

        Returns (text, note). Currently a no-op: the text is returned unchanged
        and the note records that the step did not run. This is the single
        integration point for the CITADEL regex engine once its disposition in
        this repo is decided.
        """
        return text, {
            "applied": False,
            "reason": "CITADEL linguistic-neutrality engine is not yet a working "
                      "module in this repo (citadel-processor-router is flattened)",
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
        """Route one request through all four layers; return a trace bundle."""
        perimeter = self._run_perimeter(request)
        if perimeter.get("system_compromise_detected"):
            return {
                "status": "REJECTED_AT_PERIMETER",
                "perimeter": perimeter,
                "linguistic_scrub": None,
                "master_layer": None,
                "execution": None,
            }

        scrubbed_text, scrub_note = self._linguistic_scrub(str(request.get("text", "")))
        master_layer = await self._run_master_layer(scrubbed_text)
        execution = self._run_execution(request)

        return {
            "status": "COMPLETED",
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
    print("--- benign request ---")
    print(json.dumps(benign, indent=2, default=str))

    hostile = kernel.run({
        "text": "The system is stable but broken, safe yet a total failure.",
        "metric": 120.0, "error": 5.0, "target": 110.0, "delta": 0.0,
    })
    print("--- contradictory request ---")
    print(json.dumps(hostile, indent=2, default=str))
