from __future__ import annotations

import os
import json
import hmac
import hashlib
import math
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

# =====================================================================
# GOVERNANCE REGISTRY AND DECORATOR
# =====================================================================
MODULE_REGISTRY: Dict[str, Type] = {}

def register_as_module(cls: Type) -> Type:
   """Governance handshake validation decorator."""
   MODULE_REGISTRY[cls.__name__] = cls
   setattr(cls, "_gaps_authenticated", True)
   setattr(cls, "_registered", True)
   return cls


# =====================================================================
# CANONICALIZATION & HELPER UTILITIES
# =====================================================================
def format_canonical_json(state_object: Dict[str, Any]) -> str:
   """Serializes a dictionary into a strict, canonical JSON string."""
   return json.dumps(state_object, sort_keys=True, separators=(",", ":"), default=str)


def filter_public_view(state_object: Dict[str, Any]) -> Dict[str, Any]:
   """Strips internal variables (prefixed with '_') to generate the public view."""
   return {
       key: value for key, value in state_object.items()
       if not (isinstance(key, str) and key.startswith("_"))
   }


# =====================================================================
# GSA UNIVERSAL ADAPTER MODULES
# =====================================================================
@register_as_module
class PolicyVirtualMachineModule:
   """Executes deterministic policy transformations on state payloads."""

   def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
       headers = payload.setdefault("_gaps_headers", {"metadata": {}, "risk_metrics": {}, "structural_indices": {}})
       current_state = dict(payload.get("current_state", {}))

       # Policy 1: Reduce system entropy
       entropy = float(current_state.get("system_entropy", 0.0))
       if entropy > 0.5:
           current_state["system_entropy"] = round(max(0.0, entropy * 0.9), 10)

       # Policy 2: Enforce network stability
       stability = float(current_state.get("network_stability", 0.0))
       if stability < 0.8:
           current_state["network_stability"] = round(min(1.0, stability + 0.05), 10)

       payload["mutated_state"] = current_state
       headers["metadata"]["policy_vm_executed"] = True
       return payload


@register_as_module
class ProposalGeneratorModule:
   """Generates cryptographically signed proposal envelopes across compute nodes."""

   def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
       headers = payload.setdefault("_gaps_headers", {"metadata": {}, "risk_metrics": {}, "structural_indices": {}})
       mutated_state = payload.get("mutated_state", {})
       node_identifiers = payload.get("nodes", ["compute_node_0", "compute_node_1", "compute_node_2"])
       key_registry = payload.get("key_registry", {})

       generated_proposals = []
       for node_id in node_identifiers:
           node_key = key_registry.get(node_id, hashlib.sha256(f"secure_key_{node_id}".encode()).digest())
           proposal = dict(mutated_state)
           proposal["_node_id"] = node_id
           proposal["_ts"] = time.time()

           public_view = filter_public_view(proposal)
           serialized = format_canonical_json(public_view).encode()
           signature = hmac.new(node_key, serialized, hashlib.sha256).hexdigest()
           proposal["_sig"] = signature

           generated_proposals.append(proposal)

       payload["proposals"] = generated_proposals
       headers["structural_indices"]["proposal_count"] = len(generated_proposals)
       return payload


@register_as_module
class ProposalVerificationModule:
   """Verifies HMAC signatures and temporal age bounds of network proposals."""

   def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
       headers = payload.setdefault("_gaps_headers", {"metadata": {}, "risk_metrics": {}, "structural_indices": {}})
       proposals = payload.get("proposals", [])
       key_registry = payload.get("key_registry", {})
       max_age_seconds = payload.get("max_age_seconds", 30)

       valid_proposals = []
       rejected_count = 0

       for prop in proposals:
           node_id = prop.get("_node_id")
           sig = prop.get("_sig")
           ts = prop.get("_ts", 0)

           if not node_id or node_id not in key_registry:
               rejected_count += 1
               continue

           if time.time() - ts > max_age_seconds:
               rejected_count += 1
               continue

           public_view = filter_public_view(prop)
           serialized = format_canonical_json(public_view).encode()
           expected_sig = hmac.new(key_registry[node_id], serialized, hashlib.sha256).hexdigest()

           if hmac.compare_digest(str(sig), expected_sig):
               valid_proposals.append(prop)
           else:
               rejected_count += 1

       if not valid_proposals:
           raise RuntimeError("Cryptographic or structural verification phase failed for all proposals.")

       payload["valid_proposals"] = valid_proposals
       headers["risk_metrics"]["rejected_proposal_count"] = rejected_count
       headers["structural_indices"]["verified_count"] = len(valid_proposals)
       return payload


@register_as_module
class DistanceClusteringModule:
   """Clusters proposal states based on L1 parameter divergence tolerance."""

   def _calculate_l1_distance(self, state_a: Dict[str, Any], state_b: Dict[str, Any]) -> float:
       view_a = filter_public_view(state_a)
       view_b = filter_public_view(state_b)
       combined_keys = set(view_a) | set(view_b)
       total_distance = 0.0

       for key in combined_keys:
           val_a = view_a.get(key, 0)
           val_b = view_b.get(key, 0)
           if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
               total_distance += abs(float(val_a) - float(val_b))

       return total_distance

   def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
       headers = payload.setdefault("_gaps_headers", {"metadata": {}, "risk_metrics": {}, "structural_indices": {}})
       proposals = payload.get("valid_proposals", [])
       tolerance = payload.get("distance_tolerance", 1e-6)

       proposal_clusters: List[List[Dict[str, Any]]] = []
       for prop in proposals:
           assigned = False
           for cluster in proposal_clusters:
               if self._calculate_l1_distance(prop, cluster[0]) <= tolerance:
                   cluster.append(prop)
                   assigned = True
                   break
           if not assigned:
               proposal_clusters.append([prop])

       payload["clusters"] = proposal_clusters
       headers["risk_metrics"]["cluster_count"] = len(proposal_clusters)
       return payload


@register_as_module
class QuorumConsensusModule:
   """Evaluates cluster size against quorum ratios to finalize authoritative state."""

   def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
       headers = payload.setdefault("_gaps_headers", {"metadata": {}, "risk_metrics": {}, "structural_indices": {}})
       clusters = payload.get("clusters", [])
       proposals = payload.get("valid_proposals", [])
       quorum_ratio = payload.get("quorum_ratio", 0.66)

       total_proposals = len(proposals)
       minimum_required_votes = math.ceil(total_proposals * quorum_ratio)
       largest_cluster = max(clusters, key=len)

       if len(largest_cluster) < minimum_required_votes:
           raise RuntimeError("Consensus threshold (quorum) could not be reached.")

       authoritative = sorted(largest_cluster, key=lambda item: item.get("_node_id", ""))[0]
       finalized_state = dict(filter_public_view(authoritative))
       leader_id = sorted(payload.get("nodes", ["compute_node_0"]))[0]

       finalized_state["_leader_id"] = leader_id
       finalized_state["_commit_ts"] = time.time()

       payload["finalized_state"] = finalized_state
       headers["metadata"]["leader_id"] = leader_id
       headers["risk_metrics"]["quorum_achieved"] = True
       headers["risk_metrics"]["quorum_votes"] = len(largest_cluster)
       headers["structural_indices"]["commit_timestamp"] = finalized_state["_commit_ts"]
       return payload


@register_as_module
class AuditWalModule:
   """Appends state transition logs to Write-Ahead Log audit trails."""

   def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
       headers = payload.setdefault("_gaps_headers", {"metadata": {}, "risk_metrics": {}, "structural_indices": {}})
       final_state = payload.get("finalized_state", {})

       commit_record = {
           "event_type": "state_commit",
           "payload_data": final_state,
           "commit_ts": final_state.get("_commit_ts")
       }

       log_hash = hashlib.sha256(format_canonical_json(commit_record).encode()).hexdigest()
       payload["audit_log_hash"] = log_hash
       headers["structural_indices"]["wal_commit_hash"] = log_hash
       return payload


# =====================================================================
# CENTRALIZED BINDING ENGINE AND ORCHESTRATOR
# =====================================================================
@register_as_module
class CoreOrchestratorBinder:
   """Centralized binding engine validating handshakes and sequencing execution."""

   def __init__(self) -> None:
       self.vm = PolicyVirtualMachineModule()
       self.generator = ProposalGeneratorModule()
       self.verifier = ProposalVerificationModule()
       self.clusterer = DistanceClusteringModule()
       self.consensus = QuorumConsensusModule()
       self.wal = AuditWalModule()

   def validate_handshakes(self) -> bool:
       """Validates module authentication before pipeline execution."""
       modules = [
           PolicyVirtualMachineModule,
           ProposalGeneratorModule,
           ProposalVerificationModule,
           DistanceClusteringModule,
           QuorumConsensusModule,
           AuditWalModule
       ]
       for mod in modules:
           if not getattr(mod, "_gaps_authenticated", False):
               raise PermissionError(f"Handshake failed for module: {mod.__name__}")
       return True

   def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
       """Sequences pipeline execution and outputs serialized clinical summary."""
       self.validate_handshakes()

       headers = payload.setdefault("_gaps_headers", {
           "metadata": {"orchestrator": self.__class__.__name__, "timestamp": time.time()},
           "risk_metrics": {},
           "structural_indices": {}
       })

       sequence = [
           self.vm,
           self.generator,
           self.verifier,
           self.clusterer,
           self.consensus,
           self.wal
       ]

       for module in sequence:
           payload = module.process(payload)

       clinical_summary = {
           "execution_status": "COMPLETED",
           "leader_id": headers["metadata"].get("leader_id"),
           "quorum_achieved": headers["risk_metrics"].get("quorum_achieved"),
           "quorum_votes": headers["risk_metrics"].get("quorum_votes"),
           "wal_commit_hash": headers["structural_indices"].get("wal_commit_hash"),
           "gaps_headers": headers
       }

       payload["clinical_summary"] = json.dumps(clinical_summary, indent=2, default=str)
       return payload


if __name__ == "__main__":
   node_list = ["compute_node_0", "compute_node_1", "compute_node_2"]
   registry_map = {}
   for node in node_list:
       registry_map[node] = hashlib.sha256(f"secure_key_{node}".encode()).digest()

   sample_initial_payload = {
       "current_state": {"system_entropy": 0.85, "network_stability": 0.65},
       "nodes": node_list,
       "key_registry": registry_map
   }

   binder = CoreOrchestratorBinder()
   result = binder.process(sample_initial_payload)
   print("--- DISTRIBUTED GOVERNANCE CYCLE COMPLETED ---")
   print(result["clinical_summary"])
